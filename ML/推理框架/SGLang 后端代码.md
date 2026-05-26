# SGLang 后端代码

---

[TOC]

---

> v0.5.12。





---

## entrypoints



### http_server

SRT (SGLang Runtime) server 包括一个 HTTP server 和 SRT engine。

HTTP server 是 FastAPI server，将请求路由到 engine。

engine 包括三部分：

- TokenizerManager：tokenize 请求，然后发到 scheduler。
- Scheduler：接收 tokenize 结果，调度请求、完成推理，将输出给 DetokenizerManager。
- DetokenizerManager：detokenize 输出，将结果给 TokenizerManager。

HTTP server、engine、TokenizerManager 在主进程运行，其它两个在子进程。
IPC 通过 zmq 完成。
TokenizerManager, DetokenizerManager 全局只需要一个，在多节点中只会在第一个节点运行。

**launch_server**

1. _launch_subprocesses：
   1. 在当前进程启动 TokenizerManager。
   2. _launch_scheduler_processes 启动  Scheduler 子进程。
   3. 启动 detokenizer 子进程。
2. 运行 http server。

**_launch_scheduler_processes**

不启用 dp 即 dp_size = 1 时：

1. 对每个 (pp_rank, tp_rank)，run_scheduler_process_func 启动一个 scheduler（该函数默认是 scheduler 下的 run_scheduler_process）。

dp_size > 1 时：

1. 创建一个子进程执行 run_data_parallel_controller_process (data_parallel_controller.py)，见下。





---

## Engine

> https://docs.sglang.ai/backend/offline_engine_api.html

通过 api 中的 `sglang.engine` 创建一个 `sglang.srt.entrypoints.engine.Engine(*args, **kwargs)`。

Engine 是 infer server 的入口点，提供 infer engine 的接口。





---

## Scheduler

> https://github.com/zhaochenyang20/Awesome-ML-SYS-Tutorial/blob/main/sglang/scheduler/readme.md

**PD 调度策略**

sglang 调度以 prefill 为主导：当存在待执行的 prefill 时，在一轮调度开始（比如一次 decode 完成）总会运行 prefill ，可能暂时中断运行中的 decode 请求。

prefill 优先可以让 TTFT 不过高，并且先执行完它再将其转为 decode 可以与其它 decode batch 并行跑，能提高整体效率。但会导致 TPOT 波动。

**主要成员**

- waiting_queue：等待进行 prefill 的请求，包括新请求和 decode 中被 retract 的请求。
- cur_batch：正被处理的 batch，如果存在 prefill 请求就是 get_new_batch_prefill 返回的 batch，否则是 running_batch。
- running_batch：正在进行 decode 的所有请求。
- chunked_req：保存当前 chunk prefill 的请求（同一时刻只有一个），此时该请求既不在 waiting q 也不在 running batch。该请求也是 prefill 会被优先处理直到最后一个 chunk 完成进入 decode。
  - 从 waiting q 添加 prefill 请求时，如果启用 chunk p 会维护 rem_chunk_tokens=chunked_prefill_size，每次添加 req 时从 rem_chunk_tokens 减掉当前长度，如果目前已添加的请求总长度超过 rem 即 cp size，截断当前 req，作为新的 chunked_req。
  - 处理 prefill 请求时，如果 chunked_req 非空且发现这次调度可以处理完这个 chunked_req（剩余长度 <= cp size），将 chunked_req 设为 None。后续会继续尝试从 q 中加请求，直到没有请求或到达 rem_chunk_tokens 得到新的 chunked_req。

- grammar_queue：正在等待语法（如 JSON Schema）解析的请求，解析完成后移入 waiting_queue。

**相关类**

- **ScheduleBatch**：由 Scheduler 管理，包含高级调度信息，大部分数据位于 CPU 上。
- **ModelWorkerBatch**：由 TpModelWorker 管理，是 ScheduleBatch 的子集，只包含与 GPU 上模型 forward 相关的数据。
- **ForwardBatch**：由 ModelRunner 管理，只包含与 GPU 上模型 forward 相关的数据，包含最底层的 tensor 数据。

**采样** **sampling**

虽然在 cpu 上进行采样（如简单的 topk）同样高效且更方便，但需要 D2H logits [bs, vocab_size]，每次 decode 后都将其搬到 cpu 上开销太大。
因此采样是在 gpu 完成的。





### init

**run_scheduler_process**

1. configure_scheduler_process：
   1. 根据当前 scheduler worker 的 dp/pp/att由 TpModelWorker 管理，只包含与 GPU 上模型 forward 相关的数据n_cp/moe_dp/tp/ep_rank 构造 prefix，用 sglang::scheduler_{prefix} 作为进程名，[%(asctime)s{maybe_ms}{prefix}] 作为 logger format。
   2. 设置 cpu 亲和，将当前 gpu_id 根据 rank 绑定到部分 cpu。
   3. 获取当前 gpu_id 对应的 numa node，绑定。
2. 创建 Scheduler 进行各种初始化。
3. scheduler.run_event_loop() 一直运行 event loop：
   1. 创建 priority=0 的 schedule_stream，在该 stream 上运行 dispatch_event_loop(self)。

**dispatch_event_loop**

根据配置执行不同 event loop：

- 如果没有进行 pd 分离：
  - enable_pdmux -> event_loop_pdmux
  - pp_size > 1 -> event_loop_pp
  - enable_overlap_mlx -> event_loop_overlap_mlx
  - enable_overlap (默认，未设置 —disable-overlap-schedule) -> event_loop_overlap
  - event_loop_normal
- 如果当前是 prefill 节点：
  - pp_size > 1 -> event_loop_pp_disagg_prefill
  - enable_overlap -> event_loop_overlap_disagg_prefill
  - event_loop_normal_disagg_prefill
- 如果当前是 decode 节点：
  - pp_size > 1 -> event_loop_pp_disagg_decode
  - enable_overlap -> event_loop_overlap_disagg_decode
  - event_loop_normal_disagg_decode



### normal scheduling

event_loop_normal 非常直接，各函数见 overlap。

```python
def event_loop_normal(self):
    """A normal scheduler loop."""
    while True:
        # Receive requests
        recv_reqs = self.recv_requests()
        self.process_input_requests(recv_reqs)

        # Get the next batch to run
        batch = self.get_next_batch_to_run()
        self.cur_batch = batch

        # Launch the current batch
        if batch:
            result = self.run_batch(batch)
            self.process_batch_result(batch, result)
        else:
            # When the server is idle, do self-check and re-init some states.
            self.on_idle()

        self.last_batch = batch
```



### overlap scheduling

> https://www.lmsys.org/blog/2024-12-04-sglang-v0-4/#zero-overhead-batch-scheduler
>
> 和 vllm 的 --async-scheduling 一样吗？但 vllm 的很晚才支持。
> trtllm 也有 [overlap scheduler](https://nvidia.github.io/TensorRT-LLM/features/overlap-scheduler.html)。

overlap schedule 允许 cpu scheduling 和工作与 gpu 计算并行，可在推理一个 batch N 时进行 batch N-1 的后处理和 batch N+1 的前处理，提高 gpu 利用率。

cpu 前后处理的 (de)tokenize、构建输入 tensor 较耗时，因此非 overlap (normal) 的调度对低延迟的 decode 影响非常明显，会导致 gpu 明显空隙。

> —num-continuous-decode-steps 可配置连续进行多轮 decode，也能减少 cpu 和调度开销，从而提高吞吐，但可能: 1. 提高 TTFT；2. 导致已完成请求不会及时返回；3. 高优先级请求无法立刻进行处理。

```python
def event_loop_overlap(self):
    self.result_queue: Deque[
        Tuple[ScheduleBatch, Union[GenerationBatchResult, EmbeddingBatchResult]]
    ] = deque()

    while True:
        # Receive requests
        recv_reqs = self.recv_requests()
        self.process_input_requests(recv_reqs)

        # Get the next batch to run
        self.cur_batch = batch = self.get_next_batch_to_run()

        # Launch the current batch
        if batch:
            batch_result = self.run_batch(batch)
            self.result_queue.append((batch.copy(), batch_result))

        # Process the last batch
        if self.last_batch:
			self.process_batch_result(self.result_queue.popleft())

        # Run sample of the current batch
        # It depends on the result of the last batch (e.g., grammar), so we run it after the last batch is processed.
        if self.is_generation:
            self.launch_batch_sample_if_needed(batch_result)

        self.last_batch = batch
```

**event_loop_overlap**

非 pd 分离、启用 overlap 的循环。

1. recv_requests：从 tokenizer 和 engine 接收请求。
2. process_input_requests：通过 _request_dispatcher 根据请求类型调用不同函数，构造请求对象 Req。如：
   1. TokenizedGenerateReqInput -> handle_generate_request，创建请求 Req 并放入 waiting queue。
3. `self.cur_batch = get_next_batch_to_run()`：见下，取到要调度的请求。
4. is_disable_overlap_for_batch 检查是否要禁用 overlap：
   - 如果 SGLANG_DISABLE_CONSECUTIVE_PREFILL_OVERLAP（默认 false）且连续两个 batch 都是 prefill，禁用以降低 TTFT，但会略微影响吞吐。
   - 如果启用 spec + grammar，禁用，暂不支持。
5. 如果禁用 overlap，pop_and_process 先等待处理完上一个 batch，`process_batch_result(self.result_queue.popleft())` 见下。
6. batch_result = self.run_batch(batch)：对 enable_overlap，分配 future id 然后异步推理，将结果放在 future map 中。
   1. _profile_batch_predicate：在这里启用或结束 profile。
   2. 用于测试：如果收到了 /slow_down 的 SlowDownReqInput，sleep 指定时间。
   3. 如果是 prefill batch：为每个 req set_prefill_run_batch_start_time。
   4. 如果是 prebuilt batch（D 节点，表示该 batch 已准备好 kv cache，可开始 decode）：*_run_batch_prebuilt*。
   5. 以下为生成式模型逻辑，区分 emb/reward 生成模型（通过 forward_batch_embedding 推理，不需要采样、 next_token_ids, future map，结果是 EmbeddingBatchResult）。
   6. 从 batch 构造 ModelWorkerBatch 来执行。
   7. a. 如果 enable_overlap：
      1. record_batch_in_overlap：在 batch_record_buf 暂存当前 model_worker_batch，避免本轮调度完 batch 释放后相关 tensor 被 gc 释放？batch_record_buf 是双 buf 仅保留当前和上个 batch。
      1. 在 future_map 中给当前 batch 预留 bs 个 slot。
      1. 切换到 forward_stream 执行后续操作。
         下面的 gpu 操作包括 forward 都是异步的，cpu 会将指令提交到 gpu 继续后面的调度。
      1. 让 forward_stream 与 schedule_stream 同步，等待之前提交的工作完成（不阻塞 cpu）。
      1. resolve_future：非 sepc 时 launch resolve kernel，它会将 input_ids 中的负数即 slot 替换为实际输出 token 即 future_token_ids_map[-value]；spec 时取 draft_input.future_indices.indices...
      1. self.model_worker.*forward_batch_generation* 异步推理和采样得到 batch_result。见 TPModelWorker。
      1. 如果不 delay_sample_func：
         1. future_map.store_to_map：将结果的 next_token_ids 填到预分配的 slot 中 token_ids_buf[interval]（异步）。spec 下则是填 topk_p, topk_index, bonus_tokens, new_seq_lens 到各自 buf。
         2. batch_result.copy_to_cpu：将需要的值 D2H 到 cpu，包括：next_token_ids, accept_lens...；如果 return_logprob，copy next_token_logprobs, input_token_logprobs...；如果 return_hidden_states，copy hidden_states（这里 non_blocking copy，也是异步）。
            copy_done.record 记录此时 event。
   8. a. 如果不 enable_overlap，forward 可直接得到 next_token_ids 无需 future_indices。
   9. batch.output_ids 赋值为 future_indices 或 next_token_ids。
   10. 如果启用 dpa 和 elastic_ep_backend，收集 to_group.active_ranks 将 ActiveRanksOutput send_to_tokenizer。
   11. 返回 batch_result。
7. 将 (batch, batch_result) append 入 result_queue。
8. 如果没禁用 overlap，在这里 pop_and_process 处理完上一个 batch：从 result_queue popleft 取出 batch 调用 *process_batch_result*。result_queue size 应该只有 0 或 1。
9. 如果这次和上次调度都没有请求，*on_idle* 进行部分检查。
10. 如果是生成式模型，launch_batch_sample_if_needed：如果 delay_sample_func（约束解码），在这里（即上个 batch 完全结束后）launch sample, D2H kernel：
    1. `forward_stream.wait_stream(self.schedule_stream)`
    2. 调用 delay_sample_func 即 model_runner.sample 得到 batch_result，同上 store_to_map, copy_to_cpu。

11. last_batch = batch 记录当前 batch，用于下次调度时进行该 batch 的推理同步和后处理。

> 1. `result.copy_done.synchronize()`：同步等待，确保 CPU 读到的 `next_token_ids` 是准确传输完成的数据。
> 2. `req.output_ids.append(next_token_id)`：将 `next_token_id` 追加到 `req.output_ids`。
> 3. `tree_cache.cache_unfinished_req(req)`：更新 LRU 时间戳并锁定路径。
> 4. `tree_cache.cache_finished_req(req)`：该 request 的 radix cache 节点引用计数减一，确保后续可以被释放。
> 5. `stream_output()`：将结果推送给客户端。
> 6. `cache_unfinished_req(req)`：更新 Radix Cache （L1 Cache）的节点，确保后续可以被其他请求共享。
>
> 注意到，`token_to_kv_pool` （L3 Cache）和 `req_to_token_pool` （L2 Cache）的更新是在 Pre Schedule 阶段完成的，而 Radix Cache 的更新是在 Post Schedule 阶段完成的。如果在 Pre Schedule 就插入 Radix Cache，其他并发请求可能会命中这个正在计算中的前缀。只有等到计算完成（或者至少在 `process_batch_result` 里），我们才能确信这部分 KV 已经写入显存，可以安全地被其他请求共享。

**on_idle**

scheduler loop 空闲时执行检查。

1. _check_all_pools, _check_req_pool：检查是否存在内存泄露。
2. _check_tree_cache：进行 tree_cache.sanity_check。
3. _maybe_log_idle_metrics：每隔 30s 进行一次，收集 SchedulerStats 统计，metrics_collector.log_stats(stats) 上报。
4. _publish_kv_events：取出 tree_cache 中所有 kv_event 并 publish。
5. 重置 new_token_ratio 为 init_new_token_ratio。
6. maybe_sleep_on_idle：`self.poller.poll(1000)`？如果设置 SGLANG_EMPTY_CACHE_INTERVAL（默认 -1 禁用），则每隔该时间释放 torch cache，用于解决部分显存持续增长问题。不会释放 sgl kv cache 和 request cache。

**recv_requests**

通过 zmq 从 tokenizer 获取 requests。如果启用 tp 则广播到 tp gourp。

1. a. 如果 pp_rank=0 且 attn_tp_rank=attn_cp_rank=0，接收请求：
   1. 从 tokenizer 的 zmq socket (scheduler_input_ipc_name) 接收请求，直到其中无请求或达到 pull 上限 SGLANG_SCHEDULER_MAX_RECV_PER_POLL（默认 -1 即无上限）。
   2. 从 engine 的 zmq socket (rpc_ipc_name) 接收 rpc 请求（如 health check），同上。
2. a. 如果 pp_rank!=0 且 attn_tp_rank=attn_cp_rank=0：
   1. 从 pp_rank-1 接收请求。
3. b. 如果启用 dp_attention（且之前接收了请求）：
   1. 如果 attn_tp_size > 1，将工作请求广播到 attn_tp group。
   2. 如果 attn_cp_size > 1，将工作请求广播到 attn_cp group。
   3. 如果 tp_size > 1，将控制请求广播到 tp group（工作请求为 TokenizedReqInput 类型请求，控制请求为其它所有）。
4. b. 如果 tp_size > 1（且之前接收了请求）：
   1. 将请求广播到 tp group。
5. ShmPointerMMData 相关的一些处理。
6. 返回接收的请求。

**handle_generate_request**

处理 TokenizedGenerateReqInput 类型请求。
失败时会 _add_request_to_queue。

1. a. 如果请求不带 session id：创建请求 Req。
2. a. 如果请求带 session id：
   1. 如果 id 在 session_controller 中且未关闭，通过对应 session 创建 Req。
   2. 否则创建 Req 并设置 abort，_add_request_to_queue。
3. 如果请求带多模态输入：可能填充、合并多模态输入。
4. 配置请求的部分采样参数。
5. 如果启用约束解码 (grammar-based generation, guided decoding)，配置请求的 grammar, grammar_key，加入 grammar_queue；否则加入 waiting queue。



### get_next_batch_to_run

**get_next_batch_to_run**

1. _abort_on_waiting_timeout：检查 waiting_queue 中每个 req，如果在等待队里的时间 wait_queue_entry_time（每次被调度时更新）超过 *SGLANG_REQ_WAITING_TIMEOUT*（默认 -1 不启用），直接 abort，从 waiting queue 移除。
2. _abort_on_running_timeout：检查 running_batch 中每个 req，如果在一轮 decode 中的运行时间（是每次进行 decode 重新更新？）超过 *SGLANG_REQ_RUNNING_TIMEOUT*（默认 -1 不启用），直接 abort finish。
3. 如果 last_batch 包含 prefill (extend/mixed mode)，即是刚结束的 prefill batch：
   1. 从 last_batch 中移除已完成的请求、chunked_req(?) 以及当前的 self.chunked_req（下一个 batch 可能还不会去 decode）。
   2. 将 last_batch 与 running_batch 合并（下一轮也开始做 decode）。

4. 如果 running_batch 所有请求都是 prefill only 的（不需要 decode，如 max_tokens=0）：filter_batch 移除 running_batch 中已完成的请求，因为它们不需要继续 decode。
5. new_batch = self.*get_new_batch_prefill*() 获取一个 prefill batch。
6. 如果 new_batch 非空即取到 prefill 请求，使用它；否则如果 running_batch 非空，*update_running_batch*(running_batch) 为请求分配空间然后使用它。
7. 如果启用 dp attention，进行 dp_mlp_sync: maybe_prepare_mlp_sync_batch。
8. 为每个请求 set_last_scheduled_time，返回选好的 batch。

**get_new_batch_prefill**

1. 如果启用 prefill_delayer，获取当前 mem pool 的 token usage 创建 prefill_delayer_single_pass。TODO
2. 如果 (running_batch 已满，或 waiting queue 为空) 且 chunked_req 为 None（没有正在 chunk prefill 的请求），跳过后面是否添加 prefill req 的检查，返回 None。
3. 如果当前不可分配更多请求即 running_bs >= pp_max_micro_batch_size，且 chunked_req is None，且未启用 enable_priority_preemption（由 enable_priority_scheduling 启用），返回 None。
   即除了进行中的 chunk prefill，不再处理新的 prefill，因为 decode 满了处理完 prefill 也不能进 decode。
   1. 如果未设置 pp_max_micro_batch_size，则为 max_running_requests / pp_size。未启用 pp 时就是 max_running_requests。
4. calc_priority 根据配置的调度策略对 waiting_queue 进行排序，见 *scheduler policy*。
5. 如果 chunked_req 非 None 且 enable_dynamic_chunking，根据当前 chunked_req seq_len 调整配置的 chunked_prefill_size（让不同 chunk 的执行时间接近？）。
6. 创建 PrefillAdder，包括：
   1. rem_input_tokens=max_prefill_tokens
   2. rem_chunk_tokens=chunked_prefill_size。如果添加的 p 请求长度超过该值，则截断得到新的待处理的 chunked_req。
   3. num_mixed_decode_tokens: batch 中要混合执行 decode 的 token 数。
      如果启用 is_mixed_chunk（启用 chunk prefill 且 enable_mixed_chunk，即允许 chunk prefill 与 decode 混在一个 batch），则为 running_batch 的请求数（每个请求 1 token）；否则 0。
   4. rem_total_token_offset = num_mixed_decode_tokens + running_batch 中所有请求的 min(max_new_tokens-已输出长度, CLIP_MAX_NEW_TOKENS) * new_token_ratio。
      CLIP_MAX_NEW_TOKENS 默认 4096，避免请求 max_token 太长导致调度过保守。
      见下 *new_token_ratio*。
   5. 会为每个请求预留 1 page（paged allocator 会给每个请求额外分配最多 1 page）。
7. 如果 chunked_req 非 None：init_next_round_input；adder.add_chunked_req 加入并更新 budget。即总是先处理 chunk prefill 请求。
   add_chunked_req：
   1. 计算剩余可给 prefill 的 token 数 rem_tokens = min(rem_chunk_tokens, rem_total_tokens) - rem_total_token_offset，rem_total_tokens 为 kv cache 可用 token 数 + cache 可驱逐的 token 数，rem_total_token_offset 是已有请求预留的 token 数。
   2. 在 adder.can_run_list 中加入 req，设置它可 prefill 的长度为 min(req.extend_input_len, rem_tokens)。
   3. _update_prefill_budget：更新 rem_input_tokens 减掉 req prefill 长度；更新 rem_total_token_offset 加上 req prefill 长度。
   4. 如果 chunked_req 可以在这个 batch 完成，即 req.extend_input_len <= rem_tokens，设为 None（后面不需要再 prefill 它了，并且允许后续添加新的 chunk req），且 rem_total_token_offset 额外加 min(max_new_tokens, CLIP_MAX_NEW_TOKENS) 为其后续进行 decode 分配空间。
8. 枚举 waiting q 每个 req：根据 chunked_req 剩下的 budget（如果剩下则代表上轮 chunk req 已要完成，可 batch 其它 prefill req 或选择新的 chunk req），将排序后的 waiting 请求依次加入 can_run_list。
   1. 如果 can_run_list 中请求数 >= 可分配的总请求数 (pp_max_micro_batch_size or max_running_requests) - running_batch 请求数，标记 batch_is_full。
   2. 如果 batch_is_full，且未启用 enable_priority_preemption 或 preempt_to_schedule 没有成功将 req 取代 adder 中某个/些请求，结束。
      preempt_to_schedule：尝试抢占 running_batch 中优先级更低的请求，直到该请求有足够空间运行。
      1. 遍历 running_batch.reqs 得到正在运行的请求 valid_running_reqs，然后按 (优先级, 进入 wait q 时间) 倒序排序。
      2. 计算该请求需要腾出多少 token 空间 min_tokens_to_remove。
      3. 优先级低->高遍历 valid_running_reqs，计算 req 与其的优先级差，如果 > priority_scheduling_preemption_threshold（默认 10），加入 preemptible_reqs，如果腾出的空间已足够则 break；否则优先级不够高也 break。
      4. 如果不能取代任何请求或腾出空间不够，返回 False。
      5. 从 running_batch 中释放每个被抢占的 req，更新 rem_total_token_offset 释放空间，加入 self.preempt_list。
   3. 如果 enable_hicache_storage：check_prefetch_progress (TODO)。
   4. init_next_round_input。
   5. adder.*add_one_req* 加入该请求到 can_run_list。见下。
      如果因输入长度太长被截断处理，则赋给 new_chunked_req 作为新的 chunk p 请求，结束。
      如果加入失败或没有可用 token，也结束。
9. 如果 can_run_list 仍为空，返回 None。
10. 将 can_run_list 中的请求移出 waiting q。
11. 枚举 preempt_list 中每个被抢占的请求，*_add_request_to_queue*(req) 尝试重新加入 waiting q。
12. 如果之前添加了 chunked prefill req，更新`self.chunked_req = adder.new_chunked_req`。
13. 如果 self.chunked_req 非 None，更新计数`chunked_req.is_chunked += 1`。
14. *set_forward_entry_time* 设置 can_run_list 每个 req。
15. 从 can_run_list 创建 new_batch。
16. new_batch.*prepare_for_extend*()：设置`self.forward_mode = ForwardMode.EXTEND`；创建输入相关的 tensor。
17. 如果启用 is_mixed_chunk，且 running_batch 非空，且 new_batch, running_batch 均未启用 return_logprob，且 new_batch 未使用 input_embeds 输入：
    1. running_batch.filter_batch：过滤掉已结束请求，更新相关 tensor。
    2. running_batch.*prepare_for_decode*()。
    3. new_batch.mix_with_running(self.running_batch) 将 prefill req 与 decode req 合并。
       1. self.forward_mode = ForwardMode.MIXED
       2. 拼接 new_batch, running_batch 的 inputs_ids, out_cache_loc
       3. merge_batch 拼接其它数据。
       4. prefix_lens 为每个 req 添加输入长度 + 已输出长度；extend_lens 为每个 req 添加 1；extend_num_tokens += bs。
    4. 清空 running_batch。
18. 返回 new_batch。

**PrefillAdder** **add_one_req**

1. prefill_delayer_single_pass：TODO
2. 如果设置 prefill_max_requests 且 can_run_list 已经有这么多，返回失败。
3. 如果采样参数配置 ignore_eos，转为 add_one_req_ignore_eos。
4. 计算该请求后续可能占用的 token 总数 = extend_input_len + min(max_new_tokens - len(input), CLIP_MAX_NEW_TOKENS) + page_size（预留），如果 >= rem_total_tokens 返回失败。
5. 如果输入长度 >= rem_input_tokens 且 can_run_list 非空，返回失败。
6. _lock_node(req.last_node)
   1. 如果 rem_chunk_tokens 为 None（不启用 chunk prefill）或输入长度 <= rem_chunk_tokens（该请求不需要 chunk prefill），加入 can_run_list，_update_prefill_budget，返回。
   2. 否则输入长度 > rem_chunk_tokens，加入 can_run_list，但截断 extend_input_len 为 rem_chunk_tokens（对齐到 page size），_update_prefill_budget，设置`self.new_chunked_req = req`，返回（该请求是 chunk prefill）。
   3. 继续循环 (?) 并检查 3, 4，直到加入或检查失败。

注：因为 budget 不够了才会截断得到 chunked req，所以一定只有一个。

**update_running_batch**

检查 cache 是否足够下一轮 decode，不够时撤销部分请求；分配好 decode 需要的 cache 和相关 tensor。

1. filter_batch：过滤掉已结束请求，更新相关 tensor。
   如果过滤后为空，返回。
2. 如果 enable_hierarchical_cache，tree_cache.flush_write_through_acks()。
3. batch.check_decode_mem 检查 cache 可用空间是否足够下一轮 decode，如果不够尝试清除未使用的空间。
   1. new_tokens_required_next_decode 计算下一轮需要分配 cache 的 token 数。
      1. 如果未启用 spec，对每个请求如果 kv_committed_len % page_size == 0 则分配 1page，否则不需要，page 数量 * page_size 即为需要空间。
      2. 如果 is_spec_v2，_new_tokens_required_next_decode_spec_v2...
      3. 否则 ...
   2. evict_from_tree_cache：如果可用 token 数小于下一轮所需，tree_cache.evict 淘汰未被引用的 token 直到空间足够。淘汰时如果 enable_kv_cache_events 会将 BlockRemoved 加入 kv_event_queue，用于 dynamo。
   3. 返回现在 available_size 是否足够。
4. 如果还是不够，batch.retract_decode 取消部分请求：
   1. 按 (已生成长度, - 输入长度) 降序排序当前所有请求。
   2. 不断 pop 最后一个即生成长度最短（不容易结束）、输入长度最长（占空间大）的请求，加入 retracted_reqs，release_kv_cache、evict_from_tree_cache 释放其空间，reset_for_retract。
      直到 check_decode_mem 空间足够，或只剩一个请求。
   3. 如果只剩一个请求空间还是不够，直接因为 oom abort 它。
   4. filter_batch 移除被取消的请求。
   5. 用剩余请求的 (生成长度 + SGLANG_RETRACT_DECODE_STEPS) / 总最大生成长度更新 *new_token_ratio*。
   6. 将被取消的请求重新 _add_request_to_queue 放回 waiting q。
5. 如果够，更新 new_token_ratio -= new_token_ratio_decay。
6. batch.*prepare_for_decode*()。

**prepare_for_extend**

> 分配 req_pool_indices，为 Request 在 req_to_token_pool 中申请行索引；计算 new_slots_count，从 token_to_kv_pool 中拨款申请新的物理 Slot；随后更新 req_to_token_pool，将匹配到的已有 Slot 与新申请的 Slot 拼接成该 Request 的专属槽位序列。

**prepare_for_decode**

> 在 token_to_kv_pool 中申请新的物理 Slot，并更新 req_to_token_pool 中的索引。注意，不同于 Prefill 的大块分配，Decode 每次只分配 bs * 1 个新的物理 Slot（alloc_token_slots(bs * 1)）。

分配 decode 需要的 cache 和相关 tensor，更新计数。

1. self.forward_mode = ForwardMode.DECODE
2. 如果 is_spec_v2：draft_input.prepare_for_decode。
   如果是 spec decoding，不在这里初始化。
3. alloc_for_decode 为 decode batch 分配 kv cache。
4. 一些计数更新和 tensor 分配，包括：
   1. `self.input_ids = self.output_ids; self.output_ids = None` 自回归更新。
   2. 每个请求 decode_batch_idx, kv_committed_len, kv_allocated_len, seq_lens, seq_lens_cpu, orig_seq_lens 加 1。

**_add_request_to_queue**

将请求加入 waiting queue。

PD 分离时，不需要 priority，且忽略 max_queued_requests 限制的 queue 大小？

- 如果不启用 pd 分离：
  1. _set_or_validate_priority：如果 enable_priority_scheduling 且未设置 priority，将其设为最低 -inf。还会在 abort_on_priority_when_disabled 时检查请求是否设置 priority。
  2. _abort_on_queued_limit：检查是否超出 q 大小。
     1. 如果未设置 *max_queued_requests*（默认 None）或 len(waiting_queue)+1 未超过，返回。
     2. 如果 enable_priority_scheduling，按 (优先级, 进入 wait q 时间) 尝试取代并 abort 最低的。
     3. 否则将该请求 abort。
  3. _prefetch_kvcache：如果 enable_hicache_storage，prefetch_from_storage。
  4. 加入 waiting q，set_wait_queue_entry_time。
- 如果是 P 节点：
  - _prefetch_kvcache。
  - 加入 disagg_prefill_bootstrap_queue，set_prefill_bootstrap_queue_entry_time。
- 如果是 D 节点：
  - 加入 disagg_decode_prealloc_queue，如果是 retracted 的 set_retract_time，否则 set_decode_prealloc_queue_entry_time。



### process_batch_result

**process_batch_result**

> 更新 Token: 将 next_token_ids 中的值追加到各个请求的 output_ids 中。
> 判断结束: 检查新生成的 token 是否是停止符（EOS），如果是，则将该请求从 running_batch 移除。
> 流式输出: 根据 logits_output 里的 logprob 信息，如果是流式输出请求，则调用 stream_output 将结果推送到前端。
> 释放资源: 如果请求完成，通知 Radix Cache 释放或缓存对应的 KV Cache。

根据 forward mode 走不同函数。

**process_batch_result_prefill**

非 DP 下 prefill mode 处理。
以下为生成式模型逻辑。

1. 如果有 copy_done event，sync 与 D2H 同步。
2. `result.routed_experts_output/indexer_topk_output.finalize()`：D2H 完成后 finalize 将 top k expert 结果 copy 到 TopkCapturer 的 host_cache.buffer。
3. 







### new_token_ratio

new_token_ratio 初值为 init_new_token_ratio = min(*SGLANG_INIT_NEW_TOKEN_RATIO* * schedule_conservativeness, 1)。当 scheduler 空闲即系统没有请求时，也会重置为该值。

- SGLANG_INIT_NEW_TOKEN_RATIO 默认 0.7。
- schedule_conservativeness 默认 1，越大越保守，初值、min_ratio 越高、decay 越小，ratio 也较高、更稳定，更少触发抢占。

- 代表目前系统内已经被占用的内存资源，用于计算 rem_total_token_offset 控制能否调度更多 prefill 请求。
  求和第二项是为每个未完成的 decode 计算其未来的开销，预留 max_new_tokens-已输出长度 的空间以让请求顺利完成。
- 如果每个请求都保留 max_new_tokens 或 CLIP_MAX_NEW_TOKENS，可能浪费大量空间，限制后续能调度的请求数量，因此会 * new_token_ratio 来减少分配量。
- 即 ratio 代表每次调度时为 decode 预留最大生成数量 (max_new_tokens) 乘该比例的显存，会随生成情况不断调整，越低代表生成长度稳定、调度可以更激进（预留更少、调度更多）；越高代表生成长度较长（还是长短不一？），容易发生抢占（导致 context rebuild 和 cache miss），调度需要保守。
- 随着 ratio 降低、调度变激进，batchsize 可以越来越大，直到触发一次 oom 抢占，batchsize 会降到较低值并让后续调度更保守。类似 TCP 拥塞控制*慢启动*的拥塞窗口 CWND。
  这种动态调整机制不仅能够逼近 GPU 显存的最大利用率，还能确保推理性能的相对稳定。

ratio 调整：

- min_new_token_ratio = init_new_token_ratio \* *SGLANG_MIN_NEW_TOKEN_RATIO_FACTOR*，factor 默认 0.14，该值默认 0.7 * 1 * 0.14 = 0.098。
  new_token_ratio_decay = (init_new_token_ratio - min_new_token_ratio) / SGLANG_NEW_TOKEN_RATIO_DECAY_STEPS，decay step 默认 600，即经过 600 次可将其降为最小值，该值默认 0.7 * (1 - 0.14) / 600 = 0.001。
- 每次选择调度 decode batch 时，在 update_running_batch 中：
  - 如果没有 oom 即不需要 retract 任何请求，为 new_token_ratio -= new_token_ratio_decay（下限 min_new_token_ratio）。
  - 如果内存不够需要 retract，retract_decode 中会在驱逐后用 (当前 batch 已生成 token 数 + SGLANG_RETRACT_DECODE_STEPS * bs) / 当前 batch max_tokens 和 计算新的 new_token_ratio，即为后续 batch 预留至少当前这么多 token + 每个请求 STEPS 的空间，减少下次调度的请求数避免 oom。
  - *SGLANG_RETRACT_DECODE_STEPS* 默认 20，保证当前请求至少可再运行 20 轮而不会反复 oom。调大可更保守。
  - 每次 retract 时会打印：`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_tokens_gained: 1472, #new_token_ratio: 0.0980 -> 0.8730`。



### SchedulePolicy

policy 根据是否感知 tree cache 分为两类：CacheAgnosticPolicy, CacheAwarePolicy。

**calc_priority**

根据调度策略排序 waiting_queue。

- CacheAgnosticPolicy.FCFS：如果启用 enable_priority_scheduling，按 (请求优先级, 进入 wait queue 时间) 排序；否则不排。
- CacheAgnosticPolicy.LOF：如果启用 enable_priority_scheduling，按 (请求优先级, max_new_tokens) 排序；否则按 max_new_tokens。让输出长的 longest_output 靠前。
- CacheAgnosticPolicy.RANDOM：random shuffle 随机排序。
- CacheAgnosticPolicy.ROUTING_KEY：优先调度与正在运行的请求属于同一 routing_key 的请求，让同组的请求尽量连续执行。
  routing_key 含义不确定，可能是用户自定义的。

对于 CacheAwarePolicy.LPM，首先 _compute_prefix_matches 计算 waiting queue 每个请求的匹配长度。
此外，如果匹配长度 <= IN_BATCH_PREFIX_CACHING_CHECK_THRESHOLD（默认 32）即匹配长度过短，进行 in-batch matching 检查：为这部分请求建一个 waiting_queue_radix_tree，如果与其中某个请求匹配长度 >= IN_BATCH_PREFIX_CACHING_DEPRIORITIZE_THRESHOLD（默认 32）即与该请求有较长共享前缀，降级该请求延后调度，以避免两个请求同时进行 prefill、浪费计算，提高 cache 命中率。

- CacheAwarePolicy.LPM：按最长匹配前缀排序（如果因 in-batch 检查被降级，排最后）。
- CacheAwarePolicy.DFS_WEIGHT：按 dfs 算权重排序，应该是按深度*匹配请求数。



### FutureMap

overlap schedule 会将 Batch N+1 的前处理与 Batch N 的 infer 并行，而不是与其后处理并行，减少 cpu, gpu 的空闲。

问题：Batch N+1 的推理往往依赖 Batch N 的推理和采样结果。

sglang 通过 future_map 解决：

1. 在 Batch N 推理前，alloc_future_indices 为其分配 bs 个 slot (FutureIndices)。
   - 每个请求只需要预留一个 token 输出。
2. Batch N 推理采样完成前，可正常进行 Batch N+1 的调度和前处理，此时会将对应 slot id 的负值 (<0) 而非实际输出写入 input_ids (symbolic references)。
3. 在 Batch N+1 的推理前，resolve_future_token_ids_cuda 在 forward_stream 上发起一个 resolve kernel，它会将 input_ids 中的负值原地替换为 future_token_ids_map[-value] 即生成的 token。
   - 因为与 Batch N 是在同一个 stream 执行的，所以 resolve kernel 一定在 Batch N 推理、采样、写入 slot 后执行。
   - 对于 cpu backend，逻辑就是：`input_ids[:] = torch.where(input_ids < 0, future_token_ids_map[-input_ids], input_ids)`

通过该机制，cpu 可以在不接触数据的情况下不断调度、向 gpu 发送计算指令。

**alloc_future_indices**

FutureMap 使用 circular buf token_ids_buf 保存每个 batch 未来要输出的 token。该 buffer 会预留足够大的空间: max_running_requests * (5 + max_num_chunks=context_len/chunk_prefill_size)。

因此分配时只需要增加计数器 future_ct，生成该区间的 indices。



> 后文会提及到 Zero Overhead Scheduling 时，也即将 CPU 调度与 GPU 计算进行重叠。在这种调度模式下，GenerationBatchResult 是实现异步非阻塞调度的关键：
>
> 延迟采样 (delay_sample_func): 在重叠模式下，GPU 前向计算完成后，并不会立即阻塞等待采样结果，而是先返回一个包含采样函数（sample function）的 result。Scheduler 可以利用 GPU 采样的空档去处理上一个 batch 的后处理。
> 同步令牌 (copy_done): 它携带了一个 CUDA Event。Scheduler 在真正需要访问 CPU 侧的 token ID 时（比如要把 token 发给用户），会调用 result.copy_done.synchronize()。这确保了 CPU 不会读到还没传输完成的脏数据。
> 占位符管理 (future_indices): 在重叠模式中，当前的输出是下一个 batch 的输入。GenerationBatchResult 记录了这些 token 在 GPU FutureMap 中的位置索引，让下一个 batch 的计算能直接从 GPU 显存中读取结果，而不需要经过 CPU 再传递一遍。









---

## Worker?



### TPModelWorker

**forward_batch_generation**

执行 model_runner.forward 进行推理；如果需要执行 model_runner.sample 完成采样。返回带有 logits_output, next_token_ids 的 batch_result。

1. 如果传递了 model_worker_batch，将其转为 ForwardBatch。
2. 如果当前是 pp last_rank（或未启用 pp）：
   1. `out = self.model_runner.forward`完成推理得到 ModelRunnerOutput，通过 out.logits_output 构造 GenerationBatchResult。
   2. 如果 if_verify，跳过后续采样直接返回 batch_result 即 logits。
   3. a. 如果 enable_overlap 且非 spec 且是约束解码，将采样放到 delay_sample_func 返回。
   4. a. 如果不是 prefill only，`self.model_runner.sample`采样得到 next_token_ids。
   5. a. 如果是 prefill only，无需采样，创建长 seq_len 的 0 tensor 给 next_token_ids。
   6. 返回 batch_result。
3. 如果不是 pp last_rank：
   1. 同上`out = self.model_runner.forward`推理，直接返回 GenerationBatchResult（没有解码，带 pp_hidden_states_proxy_tensors）。



---

## PrefixCache

>  https://github.com/zhaochenyang20/Awesome-ML-SYS-Tutorial/blob/main/sglang/scheduler/readme.md#kv-cache-management

TODO






---

## DP

### start

> python/sglang/srt/managers/data_parallel_controller.py

controller 接收 scheduler 调度的请求，然后 dispatch 到多个 dp worker。

**run_data_parallel_controller_process**

1. 创建 DataParallelController。
2. 如果 rank=0，创建一个 recv_from_tokenizer zmq socket。
3. 根据配置 load_balance_method 决定分发函数 self.dispatching：
   1. ROUND_ROBIN -> round_robin_scheduler
   2. FOLLOW_BOOTSTRAP_ROOM -> follow_bootstrap_room_scheduler
   3. TOTAL_REQUESTS -> total_requests_scheduler
   4. TOTAL_TOKENS -> total_tokens_scheduler
4. 创建 DPBudget 记录负载。
5. 如果启用 dp attention：为每个 dp rank (worker) 分配 port, socket；launch_tensor_parallel_group：
   1. 为每个 (pp_rank, tp_rank)，run_scheduler_process 启动一个 scheduler 进程。

> TODO: [dp attention](https://www.lmsys.org/blog/2024-12-04-sglang-v0-4/#data-parallelism-attention-for-deepseek-models)，https://zhuanlan.zhihu.com/p/1917147937265423211
> 当模型结果中有MLA时, 如果我们在attention层使用了TP, 会导致KV结果被复制到多张卡上, 极大地浪费显存, 通过这个开关可以吧attn单独使用DP实现, 经过attn all_gather后在MOE层再进入TP逻辑. 这个函数中会计算各个device自己的PP/DP/TP rank并初始化到配置里。

6. 如果不启用 dp attention：为每个 dp rank (worker) 分配 port，创建线程执行 launch_tensor_parallel_group_thread；为 rank 0 分配 socket。
   1. launch_tensor_parallel_group_thread 同上 launch_tensor_parallel_group，只是不在主线程执行，由 dp rank 个子线程执行。





---

## Page Attention

存储有两个变量：

- TokenToKVPool：将 token 映射为其在 kv cache 中的地址。key 不是 token id，而是一个逻辑 id（不同前缀的同一 token 是不同的）。token_to_kv_pool
- ReqToTokenPool：将第 i 个请求的第 j 个 token 映射为它的逻辑 id，其对应的 cache 地址就是 token_to_kv_pool[req_to_token_pool[i, j]]。
  原始的 token 值存储在 \_origin\_input\_ids\_。





---

## end



