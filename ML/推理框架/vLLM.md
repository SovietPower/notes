# vLLM 笔记

---

[TOC]

---

> https://docs.vllm.ai/en/latest/design/arch_overview.html#arch-overview
>
> https://www.zhihu.com/column/c_1880282355366855965
>
> https://zhuanlan.zhihu.com/p/1900126076279160869





---

## 使用



### 配置

**engine**

> engine/arg_utils.py

在创建 llm 时传入。

- max_num_seqs：一轮迭代中最多可同时处理的请求数，即 max batchsize。用于 scheduler。默认 128。
  降低该值可以减少 kv cache 占用。
- max_model_len：一个 sequence 的最大长度 (prompt + output)。默认从模型中读取，如果没有则 8192。
  降低该值可以减少 kv cache 占用。





---

## 调度





### 抢占

当显存（block 资源）不足时，为了给更早到达的请求留出显存、避免一直争抢陷入饥饿，后来的请求会被抢占 (preemption)，中断计算并释放 KV cache。

请求被抢占时，有两种可能：

- 释放其所有 block，后续进行 recomputation 重新从 prefill 开始算。
- 不释放其任何 block，但将 block 从 gpu swap 到 cpu 上。





---

## Paged Attention

> https://docs.vllm.ai/en/stable/design/paged_attention.html
>
> TODO：

**基本概念**

- Sequence：一条请求。seq_num 是一个 batch 中的请求数，对于 decode 来说也是正在计算的 q token 数量（每轮每个请求处理一个 token）。
- Context：sequence 中的输入和已经生成的 token。不含最后一次生成的 token，它是当前的输入 q token。
- Vec：一组一同被获取和计算的元素。对 q 和 k，其数量 VEC_SIZE 会使一个线程组每次获取和计算 16B 数据；对于 v，V_VEC_SIZE 会使一个线程每次获取和计算 16B 数据。
  如：如果 scalar_t 是 FP16 (2B)，THREAD_GROUP_SIZE 是 2，VEC_SIZE 就是 16/2/2=4，V_VEC_SIZE 是 16/2=8。
- Thread group：线程组是数量为 THREAD_GROUP_SIZE 的一组线程，会同时获取和计算一个 head 内一个 q token 和 k token。其中的每个线程负责处理 token 的一部分计算。一个线程组处理的元素数量记为 x。
  如：如果线程组包含 2 个线程，head size = 8，则 x = 4，两个线程分别负责 0, 2, 4, 6 和 1, 3, 5, 7 位置的数的计算。
- Block：k v cache 分块存储，每块存储一个 head 的 BLOCK_SIZE 个 token。
  如：如果 block size = 16，head size = 128，则该 head 的该 block 存储 16 * 128 个元素。
- Warp：数量为 WARP_SIZE=32 的一组线程。在该 kernel 中，每轮每个 warp 处理一个 q token 和一个 block 的 k token 的计算。
  如：如果一个 context 包含 6 个 block，共 4 个 warp，则 warp 0 处理 block 0, 4，W1 处理 B1, B5，W2 处理 B2，W3 处理 B3，共需要两轮。
- Thread block：数量为 NUM_THREADS 的一组线程，共享一块 shared memory。每个线程块包含 NUM_WARPS 个 warp。在该 kernel 中，每个 thread block 处理一个 q token 和一整个上下文的所有 k token，即处理一个 sequence。
- Grid：一组线程块，处理一个 batch 的所有 sequence。在该 kernel 中其 shape 为  (num_heads, num_seqs, max_num_partitions)，所以每个线程块会处理一个请求的一个 head 的一个 partition。

组织形式：

1. 一个 thread block 处理一个 head 的一个 sequence，即一个 q token 和整个 context 内的 k token 计算。
2. thread block 内的每个 warp 处理一个 q token 和一个 block 的 k token 计算。
3. warp 内的每个 thread group 处理一个 q token 和一个 k token 计算。
4. thread group 内的每个 thread 处理一对 q, k token 的一部分元素计算。
5. 每个 thread 每次获取和处理一个 VEC，即 VEC_SIZE 或 V_VEC_SIZE 个元素。



### 获取 Query

对一个 thread block，其处理的 q token 向量就位于：

```cpp
// 一个 sequence 的一个 head，大小为 HEAD_SIZE
const scalar_t* q_ptr = q + seq_idx * q_stride + head_idx * HEAD_SIZE;
```

这个向量会分成 HEAD_SIZE / VEC_SIZE 个 VEC，线程组中的每个线程每次取其中的一个 VEC 即 VEC_SIZE 个元素 (16B) 和一个 k token 做计算。
如：HEAD_SIZE = 128，VEC_SIZE = 4，则一个 q 向量会分为 32 个 VEC。

```cpp
__shared__ Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD];
#pragma unroll
  for (int i = thread_group_idx; i < NUM_VECS_PER_THREAD;
       i += NUM_THREAD_GROUPS) {
    const int vec_idx = thread_group_offset + i * THREAD_GROUP_SIZE;
    q_vecs[thread_group_offset][i] =
        *reinterpret_cast<const Q_vec*>(q_ptr + vec_idx * VEC_SIZE);
  }
```

每个 VEC 的起始地址会被读取到 q_vecs，组织成 (线程数, VEC 数) 的二维数组便于线程访问 VEC。

> 线程组中的线程会交替访问 VEC（假设有两个线程，线程 1 访问 0, 2, 4...，线程 2 访问 1, 3, 5...），以利用内存合并 (*memory coalescing*) 优化性能。









---

## end



