# TensorRT-LLM 前端笔记 (tensorrt backend)

---

[TOC]

---

> https://github.com/NVIDIA/TensorRT-LLM/tree/main
>
> TRT python API：https://docs.nvidia.com/deeplearning/tensorrt/latest/_static/python-api/index.html

TRTLLM 分为 cpp runtime 和 python runtime。
对于 python runtime，executor、kv_cache_manager 等组件也均由 C++ 实现，通过 pybind/nanobind 暴露给 python 调用。

cpp runtime 源码在`cpp/tensorrt_llm/runtime`、`cpp/include/tensorrt_llm/runtime`下，binding 在`cpp/tensorrt_llm/pybind`或 nanobind 下。

> `help('tensorrt_llm.bindings.executor')` 查看 binding 的类的文档。
>
> cpp runtime 与 python runtime 的代码应该分别在`cpp/tensorrt_llm/runtime`和`tensorrt_llm/runtime`下。







## Executor

> https://github.com/NVIDIA/TensorRT-LLM/blob/release/1.0/docs/source/advanced/executor.md
>

TRTLLM 用于接收和处理请求，如：enqueueRequest。





---

## trtllm-build

> tensorrt_llm/commands/build.py

过程：

1. 解析参数，构造 BuildConfig。
2. 调用 parallel_build：worker 是 gpu 节点数，用于并行 build engine。
   1. 如果不使用 mpi 且 worker 数为 1，在 gpu 0 上依次 build_and_save world_size 个 engine。
   2. 如果不使用 mpi 且 worker 数 > 1，创建 worker 数大小的进程池，每个进程分别在 gpu 0 ~ world_size % workers 上 build_and_save world_size 个 engine。
   3. 如果使用 mpi，则有 mpi_world_size 个进程同时在 build，当前进程仅处理自己的 rank，在 gpu mpi_local_rank % node_gpu_count 上 build_and_save engine。
3. build_and_save(rank, gpu_id)。

**build_and_save(rank, gpu_id)**

构建 network，导出 engine。

1. set_device(gpu_id)，然后进行以下的 build_model：
2. 根据 model arch 选择 model_cls，如`'Qwen3ForCausalLM': QWenForCausalLM`。
3. `model = model_cls(rank_config)`或`model = model_cls.from_checkpoint(ckpt_dir)`创建 model。见下 *models - 创建 model*。
4. `build_model(build_config)` -> `build(model, build_config)`构建 engine：
   1. `model = optimize_model_with_config(model, build_config)`调用`model = optimize_model(model, ...)`：应用少量 opt pass，比如：
      1. parallelize_embedding：在 embedding layer 中加入 tp 配置进行分片。默认沿 vocab_size 分片，也可设置 embedding_sharding_dim 改为沿 hidden_size。
      1. share_embedding_table：如果 embedding table 与 lm_head 权重一样，仅在 ckpt 中保留一份。
      1. fuse_gate_mlp：将 silu/gelu 的 GatedMLP layer 替换为 FusedGatedMLP（图里应该会插一个 plugin）。
   2. `builder = Builder()`
   3. `network = builder.create_network()`
   4. `inputs = model.prepare_inputs(**prepare_input_args)`创建 Tensor 构造网络输入，并作为模型 forward 输入。
      Tensor 包含 tensor_name, dtype, 各 dim 各 profile 的 range（静态 shape 或动态 min/opt/max）。
      多数模型使用 PretrainedModel 的 **prerare_inputs**：
      1. prepare_basic_inputs：
         1. get_profiles_ranges 获取几个常用维的 profiles range。如：
            （range 的格式见 *dim_range*，是每个 dim 多个 profile 下的 [min, opt, max]）
            1. bb_range_ctx：context phase 时 batch_size 维的 profile。如果设置了 opt_batch_size 则为 [1, opt_batch_size, max_batch_size]，否则用 default_range 生成 range（默认为 [1, (1+max_bs)/2, max_bs]）。
            2. bb_range_gen：generation phase 时 batch_size 维的 profile，就是 bb_range_ctx 乘 max_beam_width。
            3. 如果 enable_ctx_gen_opt_profiles 即 ctx, gen 阶段使用不同 profile，则创建两个 profile，实际的 bb_range = [bb_range_ctx, bb_range_gen]。
               否则仅使用 bb_range_gen 作为 bb_range 用于 batch_size * beam_width 维。
            4. num_tokens_range：如果启用 multiple_profiles，创建多个：split_point = [64, 128, 256, 512, 1024]，range 包括 [split_point[i-1], split_point[i], split_point[i]], 
               否则，如果设置了 opt_num_tokens 则为 [1, opt_num_tokens, max_tokens]；否则为 [1, max_bs*max_beam_width, max_tokens]。
         2. 创建基本输入及其 shape 与 dim range，如：
            1. input_ids：如果 remove_input_padding 则 [-1]，num_tokens_range；否则 [-1, -1]，bb_range 与 input_len_range。
            2. position_ids：如果 remove_input_padding 则 [-1]，position_ids_num_tokens_range；否则 [-1, -1]，bb_range 与 position_ids_input_len_range。
            3. hidden_states：如果 remove_input_padding 则 [-1, pp_hidden_size = hidden_size/tp_size]，num_tokens_range 与静态 shape pp_hidden_size；否则 [-1, -1, hidden_size]，bb_range、input_len_range 与静态 hidden_size。
               前两个用于 first pp rank，这个用于非 first pp rank。
            4. 如果 use_lora_plugin，则有 lora_weights_pointers、lora_ranks 输入。
            5. spec_decoding、mrope 相关。
         3. prepare_attention_inputs 创建 attention plugin, kv cache 相关输入，如：
            1. bb_range、mask_len_range、_kv_cache_range：与上面 bb_range 类似，如果启用 enable_ctx_gen_opt_profiles 则有 ctx, gen 两个 profile，否则仅有一个通用的。
            2. 如果 kv cache 为 CONTINUOUS，创建输入 past_key_value_{layer_idx}，[-1, 2, kv_heads, -1, head_size]，-1 分别为 bb_range、kv_cache_range (max_seq_len)。
            3. 如果 kv cache 为 PAGED，创建输入 kv_cache_block_offsets、host_kv_cache_block_offsets、host_kv_cache_pool_pointers、host_kv_cache_pool_mapping，包含 max_blocks_per_seq_range（需要的 cache block 数量）。
            4. 如果 use_gpt_attention_plugin，创建输入：sequence_length、host_request_types、host_past_key_value_lengths、context_lengths，shape 均为 [-1]，bb_range；host_runtime_perf_knobs，shape [16]；host_context_progress，shape [1]。
               否则，创建输入 attention_mask，[-1, -1]，bb_range、mask_len_range；host_max_attention_window_sizes，[num_attn_layers]；host_sink_token_length，[1]。
            5. 如果 use_gpt_attention_plugin 且 remove_input_padding，创建输入 host_context_lengths，[-1]，bb_range。
            6. 如果启用 kv cache，创建 cache_indirection，[-1, -1, -1]，分别为 bs_range，beam_width_range, max_seq_len_range。
      2. 将 kv cache 相关输入封装到 KeyValueCacheParams，attention plugin 相关输入封装到 AttentionParams。
   5. `model(**inputs)` 调用模型的 forward 来构建 network，包括 add_layer/plugin 与 mark_output。
   6. `optimize(network)`：用 RewritePatternManager 改写图，目前只有一个 FuseAttentionWithBiasPass。
   7. 如果启用 auto_parallel，切分 network，取`network = sharded_networks[rank]`。
   8. 如果启用 visualize_network，将图导出为一个 onnx-like 的图。
   9. `builder.build_engine`：
      1. 对 network mark_weights_refittable、_fill_weights。
      2. 通过`trt_builder.build_serialized_network`将 network 转为 serialized trt engine。
   10. 封装 trt engine 为 Engine 返回。
5. `engine.save`导出 serialized engine 与 managed weights。

**network**

network 添加输入 (`default_net()._add_input`)：

- 在创建 Tensor 时指定 is_network_input=True。见上 *prerare_inputs*。

network 添加输出 (`default_net()._mark_output`)：

- forward 中将部分 tensor 标记为输出。
  如：`lm_logits.mark_output('logits', self.config.logits_dtype)`，`present.mark_output(f'present_key_value_{i}', self.config.kv_dtype)`。
- 指定`--enable_debug_output`时，在 forward 后将 _network_outputs 中的 tensor 标记输出。
  应该是用来打印模型中`self.register_network_output`注册到 _network_outputs 的 tensor 用于 debug，非 debug 时它们不会作为输出。





---

## common



### Module

类似 nn.Module，所有 layer 的基类。

- 通过 dict `_modules` 记录所有 Module 成员。
- 通过 dict `_parameters` 记录所有 Parameter 成员。

**\_\_setattr\_\_**

如果 value 是 Parameter 与 Module，注册到 dict；否则设为基类的成员。

1. 如果父类不含该 attr：
   1. 如果 value 是 Parameter/Module，保存在 \_parameters/\_modules 中，key 为 attr name。
   2. 否则赋给父类作为正常成员。
2. 如果父类含该 attr：
   1. 如果 value 是 Parameter/Module，将其从父类成员中移除，保存在 \_parameters/\_modules 中，key 为 attr name。
   2. 否则赋给父类作为正常成员。

`__getattr__`在 \_parameters/\_modules 中查找该属性。

**\_\_call\_\_**

forward 的 wrapper，记录调用栈和每个 Module 影响的 layer 范围。

1. 如果`current_net._module_call_stack.module_names_set()`为空，即这是第一次调用，将当前 Module 作为最顶层模块，为下面的所有 Module 子成员创建名字，保存在这个 _TrtLlmModuleCallStack 的 module_name_map 中。
   1. 创建名字通过`named_modules`进行：枚举当前 Module 下的所有 _modules，将 prefix + attr name 作为每个 module 的名字，然后 DFS 递归。这样可得到`decoder.layers.0.q_proj`这样的名字。
2. 维护一个 module name 的调用栈，
   1. 将当前 module name 加入；记录当前 network 的 layer 数。
   2. 调用 self.forward。
   3. 将 module name 移除；记录当前 network 的 layer 数，可得到 network 中该 Module 生成了哪些 layer。

**ModuleList**

list 不是 Module 不能直接注册，需要用 ModuleList 封装一个 list 的 Module。

- 它本身是 Module，可以被父类注册，如`_modules["layers"]`。
- `__init__`中使用下标字符串作为 key，如`self._modules["0"]`，注册 list 中的各个 Module。
- 重写了`__getitem__`和`__setitem__`，可像 list 一样通过下标/切片返回 Module。

因此，调用 ModuleList 中的某个 Module 时，可生成`__modules["layers"]["0"]["q_proj"]`这样的路径，得到`layers.0.q_proj`。



### Parameter

定义 engine 权重。

成员：

- _dtype：trt type。
- _value：None 或传进来的 np.ndarray。
- _shape：\_value shape 或传进来的 shape。



### Tensor

dense tensor，记录：tensor 各 opt profile 的各 dim shape；location (device/host)。

**\_\_init\_\_**

如果 tensor 是网络输入，将 dim_range 转为各 profile shape，`default_net()._add_input`加到网络中。

> **dim_range**：有序 dict，key 为 dim name，value 为该 dim 每个 optimization profile 下的大小（对静态维度，值为 int list: [profile0 value, profile1 value, ...]；对动态维度，值为 [int, int, int] list: [profile0 (min, opt, max), profile1 (min, opt, max), ...]）。
> 如果有 n 个 profile，某 tensor 有 m 维，则 dim_range 有 m*n 个值。
> 只用于网络输入。
>
> **DimRange**：记录某个 tensor 的一个 opt profile 中，每个 dim name 和每个 dim 的 min, opt, max shape。
> dim_range 记录每维的各 profile shape，会转为 DimRange 即每个 profile 的各 shape。



### network

**_set_layer_name**

设置指定 layer 的 name 为一个唯一的名字，格式为：current_module（来自当前调用栈）+ '/' + layer_type（plugin type, op 或 layer type）+ idx。
同时设置 layer 的各输出为 `f"{layer.name}_output_{idx}"`。



### utility function

**_create_tensor**

为某个 ILayer (producer) 的某个输出 ITensor (trt_tensor) 创建一个非 input Tensor 对象，加入到网络中。

1. 创建 Tensor，name, dtype, shape 与 trt_tensor 一致。
1. 如果网络不是 strongly typed，且 layer type 不属于 [shape, constant, gather, concat]，将 layer 的 precision 设为网络的 dtype（tensor 的不改吗？）。







---

## layers

- set_network(network)：设置全局的 Network 对象。
- default_net()：返回全局的 Network 对象。
- default_trtnet()：返回全局的 Network 保存的 trt_network 对象，即 INetworkDefinition。



### Linear

在网络中加入 matmul (Gemm/LowLatencyGemm) layer 与 add bias；如果是 tp linear 则还要 all gather/reduce 聚合结果。

**LinearBase**

对 linear: `Y = X @ W^T + B`，X = (N, K)，W = (M, K)，Y = (N, M)。
K 为 in_features，M 为 out_features。

Linear 分为 ColumnLinear（默认）和 RowLinear，

- ColumnLinear 沿输出维度 (out_features) 切分权重 W，即每个节点权重为 (M/tp_size, K)。
  - 每个节点计算`Y_i = X @ W_i^T`，shape 为 (N, M/tp_size)。
  - All Gather 或拼接得到完整的 Y。
- RowLinear 沿输入维度 (in_features) 切分权重 W，即每个节点权重为 (M, K/tp_size)。
  - 每个节点计算`Y_i = X_i @ W_i^T`，shape 为 (N, M)。
  - All Reduce 或求和得到完整的 Y。

**\_\_init\_\_**

1. 如果 share_weight，使用它作为 weight；如果不 share_weight，创建 (out, in) 的 Parameter weight，设置其 attr weight_loader 为 self.weight_loader：
   1. 获取切分维度`dim = self.tp_split_dim()`，对 ColumnLinear 就是 0，Row 是 1。
   2. 切分后每块的维度大小`shard_size = param.shape[dim]`。
   3. `param.value = loaded_weight.narrow(dim, tp_rank * shard_size, shard_size)`从加载的权重中取出当前节点负责的部分。
2. 如果有 bias，创建 Parameter bias。

**multiply_and_lora**

根据配置选择不同的 GEMM 实现，插入计算矩乘和 lora 的 layer：

1. 如果 low_latency_gemm_plugin，调用 *low_latency_gemm* 使用 LowLatencyGemm plugin。
2. 如果 gemm_plugin，调用 *_gemm_plugin* 使用 Gemm plugin。
3. 否则调用普通的 *matmul*。
4. 如果启用 lora_plugin 且提供了参数 lora_runtime_params，加上`lora(input, lora_param)`。

**collect_and_bias**

加上 bias，collect 聚合输出（tp 的 all_gather 或 all_reduce）。

collect: 如果启用 tp：

1. 对 ColumnLinear：如果在当前 Layer 进行 gather_output，调用 *allgather* 插入一个 allgather plugin，
   1. 这个 plugin 会将所有 tensor 视为一维向量，然后在第 0 维拼接，所以如果 gather_dim 不为 0，需要将结果 slice 再沿 gather_dim concat。
2. 对 RowLinear：
   1. 如果当前是 expert linear，则加上 bias/tp_size，返回即可。all_reduce 由该 expert 的输入 token 所在的原始节点完成，这里不需要。
      每个 tp expert 都会加一样的 bias，所以除 tp_size。
   2. 如果不是 expert，all_reduce 汇总结果。
      如果 all_reduce_params.fusion_op 为`RESIDUAL_RMS_NORM`，即 all_reduce 会融合 matmul + bias + residual + RMS_norm，把 bias 给 all_reduce_params.bias，自己不需要再加了。否则加上 bias。

**multiply_collect** / **forward**

完成 matmul + bias，并聚合 tp 结果。

- 对 RowLinear 且启用 gemm_allreduce_plugin，用 *gemm_allreduce* 创建 GemmAllReduce plugin 完成 matmul + collect，然后加上 bias。
- 否则，以及对 ColumnLinear：multiply_and_lora + collect_and_bias，

**_gemm_plugin**

创建以指定两个 Tensor 为输入的 Gemm plugin layer，加入网络，并返回代表 output(0) 的 Tensor。

1. `trt.get_plugin_registry().get_plugin_creator("Gemm", "1", TRT_LLM_PLUGIN_NAMESPACE)`获取 Gemm plugin 的 IPluginCreator。
2. 将参数转为 PluginField，包括：trans{a/b}, pad_ld{a/b/c}，use_fp8，type_id (plugin dtype)。封装为 PluginFieldCollection。
   1. pad_ld 用于扩大 ld：当要计算的矩阵如 a [m, k] 是某个矩阵 a' [m, k'] 的子矩阵时，其实际 leading dimension 是 k' 而非 k，可设置 pad_lda = k'-k 以正确计算 a 下一行元素的位置。
3. 创建 gemm plugin。plugin 类型为`network.plugin_config.gemm_plugin`。
4. 在全局 network 即`default_trtnet()`中`add_plugin_v2(plug_inputs, gemm_plug)`，得到 gemm layer。
5. `_add_plugin_info`在全局 network 里添加该 layer name -> plugin_info（plugin name "gemm" 与所有 PluginField）。
6. 将返回的 IPluginV2Layer 的 output(0) 通过`_create_tensor`封装为 Tensor 返回。






---

## models - qwen

> https://nvidia.github.io/TensorRT-LLM/1.0.0/architecture/core-concepts.html#



### 创建 model

**QWenForCausalLM**

包括一个 QwenModel (transformer) 和 lm_head。

1. `transformer = QWenModel(config)`创建 **QwenModel**：包括 emb layer，若干 decoder layer 和最后的 RMSNorm。
   1. 如果 pp_rank == 0，创建`self.vocab_embedding = Embedding(config.vocab_size, config.hidden_size)`。
   2. 通过`DecoderLayerList(ModuleList)`创建 num_hidden_layers 个 **QWenDecoderLayer**：RMSNorm + Attention + post RMSNorm + MLP。
      1. 每个 DecoderLayerList 仅创建属于自己 pp 范围的 QWenDecoderLayer。
      2. `self.input_layernorm = RmsNorm(normalized_shape=config.hidden_size)`。
      3. 将 num_hidden_layers 分为 pp_size 份，然后选择 pp_rank 得到 layers_range。
      4. 创建`self.attention = Attention(...)`。
      5. 根据是否有 moe 决定 MLP type 是 SharedMoE, MOE 还是 GatedMLP。
         创建`self.mlp = ClsMLP(config.hidden_size, intermediate_size, config.hidden_act)`。
      6. 创建`self.post_layernorm = RmsNorm(normalized_shape=config.hidden_size)`。
   3. 如果 pp_rank == pp_size - 1，创建`self.ln_f = RmsNorm(normalized_shape=config.hidden_size)`。
2. 如果 pp_rank == pp_size - 1，创建`lm_head = ColumnLinear(config.hidden_size, vocab_size_padded)`。

基类 *DecoderModelForCausalLM* 的 \_\_init\_\_：

- `Attention.create_attention_const_params(self, config)`预先创建 RoPE 所需的所有常量张量（只依赖于模型配置），供所有 layer 和调用复用。



### forward

使用基类 *DecoderModelForCausalLM* 的 forward。

1. `attention_params = Attention.fill_attention_params`：如果使用 RoPE 获取之前预计算的相关参数。
1. 如果启用 context parallelism，根据 cp_size, cp_rank 切分 input_ids。
1. `hidden_states = self.transformer.forward(**kwargs)`调用 QwenModel forward：
   1. 如果 pp_rank == 0，`hidden_states = self.vocab_embedding(input_ids, *ptuning_args)`取 embedding；否则`recv(hidden_states, self.mapping.prev_pp_rank())`从前一个 pp 取 hidden_states。
   1. `hidden_states = self.layers.forward`执行每层 decoder layer，见下 *DecoderLayerList*。
   1. 如果 pp_rank == pp_size - 1，`hidden_states = self.ln_f(hidden_states)`计算最后的 RMSNorm；否则`send(hidden_states, self.mapping.next_pp_rank())`将 hidden_states 发给下一个 pp。
   1. 如果启用 kv cache，则返回值有两个 hidden_states 与新的 kv cache presents。

1. 如果启用 cp，allgather 获取完整的 hidden_states。
1. 如果 pp_rank == pp_size - 1，
   1. gather_last_token_logits 取出 hidden_states 中（batch 中每个请求的）最后一个 token 的 hidden_states。
   1. `lm_logits = self.lm_head(hidden_states)`获取 logits 输出。
   1. `lm_logits.mark_output('logits', self.config.logits_dtype)`进行`trt_network.mark_output(tensor.trt_tensor)`，标记为网络输出 logits。

1. 如果启用 kv cache 且非 paged kv cache，遍历 presents 将每层的 kv cache 标记为网络输出 present_key_value_{i}（paged 无需通过 engine 输出维护）。
1. 返回 hidden_states。如启用 kv cache 还返回 presents。如果是最后一个 pp rank 还要返回 lm_logits。

*DecoderLayerList* 的 forward：

1. 枚举当前负责的 layers（通过 pp 划分）及每层的 past kv cache。
   1. 如果启用 reduce_fusion 且当前非最后一层，尝试融合当前层的残差 ResidualAdd 与下一层的 LayerNorm（在 QWenDecoderLayer 中没用）。
      - 如果启用 user_buffer 和 fp8_qdq/nvfp4 量化，获取下一层 qkv_linear 的 qkv activation scaling factor？
   2. 否则如果启用 norm_quant_fusion 且当前非最后一层，尝试融合当前层的 quant kernel 与下一层的 LayerNorm（在 QWenDecoderLayer 中没用）。
   3. 调用 *QWenDecoderLayer* 的 forward：
      1. 执行第一个 RMSNorm self.input_layernorm。
      2. 执行 self.attention。
      3. attention 输出累加残差。
      4. 执行 self.post_layernorm。
      5. 执行 self.mlp。
      6. mlp 输出累加残差。
      7. 如果启用 kv cache，返回 (hidden_states, past_kv_cache)，否则返回 hidden_states。




> PluginConfig (plugin/plugin.py):
>
> - _reduce_fusion: Fuse the ResidualAdd and LayerNorm kernels after AllReduce into a single kernel, resulting in improved end-to-end performance.
> - _user_buffer: Eliminate extra copies from the local buffer to the shared buffer in the communication kernel, leading to improved end-to-end performance. This feature must be enabled with `--reduce_fusion enable` and is currently only supported for the FP8 LLAMA model.
> - _norm_quant_fusion: Fuse the LayerNorm and quantization kernels into a single kernel, resulting in improved end-to-end performance.





---

## end







