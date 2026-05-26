# SGLang 部分优化

---

[TOC]

---

> https://arxiv.org/pdf/2312.07104

RadixAttention、Compressed finite state machines、API Speculative Execution 是 SGLang Runtime (SRT, backend) 的主要优化。

**其它优化**

> EP：https://zhuanlan.zhihu.com/p/17790182311



---

## Radix Attention / Prefix Caching

> https://sgl-project-sglang-93.mintlify.app/concepts/radix-attention

RadixAttention 就是利用带压缩前缀树来缓存 KV cache：相同前缀的请求会在树上共享同一个节点、共享 cache。

- 缓存淘汰策略是 LRU。只会淘汰叶节点，然后才能淘汰因失去叶子变成叶节点的节点。

- 在 continuous batching 中，无法在每次 batch 后清理无用节点上的 cache，所以会为每个节点维护引用计数，计数非 0 的节点不会被驱逐。
- cache 会与正在执行的请求共享可用内存，这样当有足够的请求在执行时，系统可以驱逐所有已缓存的 token，以支持更大的 batch size。

**page**

prefix 的匹配以 page 为单位，比如如果 page_size=16，匹配到的缓存 token 数就是 16*n。

序列最后不足 page_size 的部分不会被缓存（因此输入 < page_size 时不会被缓存）。

**cache-aware scheduling**

cache 的命中率为 number of cached prompt tokens / number of prompt tokens。
当等待队列有大量请求（cache 容量不足）时，执行请求的顺序会显著影响缓存命中率。如果调度程序频繁地在不同的、不相关的请求之间切换，会导致 cache 抖动和命中率低。

这个调度算法按公共前缀长度对请求进行排序，并优先处理具有较长匹配前缀的请求，而不是使用 FIFO、按请求到来时间进行调度。

对于一 batch 请求，在 trie 上 DFS 依次处理可以实现最高的 cache 命中率；而按公共前缀长度进行依次处理可以实现接近的效果。

> 这种贪心调度会导致饥饿，还需要和其它公平调度结合。



---

## DP Attention

当 sglang 同时启用 dp+tp 且启用 dp attention 时，以 dp=2, tp=8, gpu num=8 为例，效果会变为：

- 系统分为 dp_size=2 个 dp_group，每个 group 8/2 = 4 gpu。
- 每个 dp group 包含 tp_size/dp_size=4 个 tp rank，如 DP1 包含 TP4~TP7。
- tp 不再是全局 tp，而是在所有 dp rank 之间在 attn, moe 上进行 TP；其它层使用 dp。
- 每个 (dp_rank, tp_rank) 包含 8/(2*4) = 1 gpu，有一份 kv cache；每个 dp group 有一组与其它 group 独立的 cache（dp 内进行 tp 的 cache 是重复的）。







---

## Fast Constrained Decoding / Guided Decoding

> https://github.com/zhaochenyang20/Awesome-ML-SYS-Tutorial/blob/main/sglang/constraint-decoding/readme.md
>
> 约束解码/结构化输出，或称为 grammar-guided structured decode。

Effcient Constrained Decoding with Compressed Finite State Machine：*fast constrained decoding* 允许在特定约束条件下一次生成多个 token，适合结构化输出。

用户可以提供正则表达式来表示该约束，系统会据此构建一个压缩有限状态机，并在推理时维护 FSM 的状态。
当对于给定输入，当前状态机只允许唯一的有效输出时，会直接通过状态机得到后面的若干 token，不经过 LLM decode，直到遇到非唯一的状态。不过还需要一次 prefill。

**Handling Tokenization Artifacts with Retokenization**

状态机是用字符串构建的，所以通过它一次得到多个输出后，还需将字符串转为 token。
需要 retokenization（TODO）。



---

## API Speculative Execution

Effcient Endpoint Calling with API Speculative Execution：SGLang 提供了前端和解释器，而后端可以用 API 访问 API-access-only model。
对于这种 API 访问，SGL 通过投机执行来减少 API 调用次数和延迟：在调用 API 时，SGL 会忽略用户的停止条件，让模型生成更多 token；解释器会保留额外的生成输出，并用它匹配和重用于之后的用户请求。如果成功匹配，可以为用户省下一次 API 调用和耗时。

尤其适用于连续两次调用且之间没有其它内容？可以把下一次调用的格式放在请求里？





---

## end



