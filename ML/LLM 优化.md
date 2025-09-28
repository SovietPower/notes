# LLM 优化 笔记

---

[TOC]

---

> Attention 相关见 *Attention*。
>
> *Radix Attention*、*Fast Constrained Decoding*、*API Speculative Execution* 见 *SGLang*。







---

## AWQ

> https://zhuanlan.zhihu.com/p/697761176





---

## Weight Sparsity

稀疏性 weight_sparsity 就是 0 权重在所有权重中的比例，可据此进行模型压缩和加速推理。

稀疏性分类：

- 非结构化稀疏 (Unstructured Sparsity)：权重矩阵中零值的位置是随机的，没有任何规律。
  灵活性高，可以最大程度地减少参数数量。但硬件加速困难，因为零值分布不规则。
- 结构化稀疏性 (Structured Sparsity)：权重矩阵中零值的位置遵循特定的模式，例如整行、整列或整块为零。
  硬件友好，适合高效的计算和存储。但灵活性较低，可能导致模型性能下降。
- 半结构化稀疏性 (Semi-structured Sparsity)：零值的位置部分遵循某种规律，但不像完全结构化稀疏性那样严格，比如某行或列中大部分元素为零，但不要求整行或整列完全为零，在灵活性和硬件效率之间取得平衡。

**semi-structured sparsity**

半结构化稀疏是稀疏性的一种特定形式，介于非结构化稀疏性（unstructured sparsity）和完全结构化稀疏性（structured sparsity）之间，是兼顾灵活性和硬件效率的稀疏性形式。

典型模式：

- N:M 稀疏性：在权重矩阵的每一组 N 个元素中，至少有 M 个元素为零。比如 2:4 稀疏性表示每 4 个元素中至少有 2 个为零。
- 块稀疏性：权重矩阵被划分为多个小块，每个块中有一定比例的元素为零。





---

## Continuous Batching

LLM 通常是自回归的 transformer，常规的 batching 有三个问题：

- Early-finished Requests：不同请求生成的文本长度不一致，可能差别很大且不易预测。如果没有将已完成生成的请求从 batch 中移除并提前返回结果的机制，那么只能等一个 batch 内所有请求都完成后才返回结果，导致生成短文本的请求耗时白白增加很多。
- Late-joining Requests：完整生成一段文本需要数秒或数十秒的时间，如果没有将新请求插入到推理 batch 的机制，晚来一两秒的请求可能会因错过 batch 排队多等数十秒，增加响应时间。
- Batching an arbitrary set of requests：每个请求的 QKV tensor 的维度不同（token 数量维），batching 时通常通过 padding+mask 处理，会浪费算力和显存。
  - prefill 阶段（即请求第一次开始推理）的输入长度会相差很大；后续 decode 阶段推理长度都是 1（有了 KVCache 就只需要处理上次 decode 生成的 token）。

*Continuous Batching* 也叫 *Iteration-level Scheduling* / *dynamic batching*，也就是 batch 每完成一次迭代、为里面的请求生成一个 token 后，检查一下 batch 中有没有请求已完成（生成结束符）或已被用户取消，如果 batch 未满按请求到来时间顺序，尝试将请求加入 batch。

此外会为每个请求的 KV cache 预留 slot，将请求加入 batch 时需要有足够的 slot；移出 slot 时释放其 slot 及 cache。这样动态的 batch 可以减少内存浪费。

> 可以优化 cache 的释放时机以便复用。

为了解决请求在 prefill 与 decode 阶段长度不一的问题，OCRA 在计算 QKV 时先将所有请求 concat 到一起处理，在算 attention 时再将请求 split 独自计算（因为 prefill 需要算 self-attention，decode 需要用 KV cache），计算完后再 concat 继续。

> 直接将 prefill 与 decode 分开会更好。
>
> 因为 batch size 在动态变化（尤其是计算量多的 prefill 的比例变化），计算时延会有比较明显的波动。
>
> - 可以根据目前情况动态调整 batch size 上限和序列长度。
> - 可以将 prefill 拆分为多次优化（见[这里](https://zhuanlan.zhihu.com/p/658443665)）。



---

## PD 分离

常规推理框架中 prefill 和 decode 阶段通常由同一个 GPU 执行。推理引擎的调度器会根据显存使用情况及请求队列状态，在 prefill 和 decode 之间切换。
而 Prefill-Decode 分离式架构会将 prefill decode 拆分到不同的 GPU 实例上独立运行。prefill instance 和 decode instance 分别专注于 prefill 和 decode 阶段任务；prefill instance 计算完后会将 kv 传递给 decode instance。

当不分离时，由于两阶段的计算特性差异（prefill 是计算密集，decode 是访存密集），可能难以充分利用 gpu 的资源，难以同时优化 TTFT 和 TPOT（需要取舍）；通过 PD 分离，可以针对不同阶段的特性分别进行优化，同时优化首 token 延迟和吞吐量。

> 在不分离时，vllm 和 sglang 都是 prefill (TTFT) 优先，如果同时有 PD 任务，则只要有空余显存就会先处理 prefill，直到显存不足才会进行 decode 完成请求释放显存；如果进行分离，decode 就不会受 prefill 干扰，降低 TPOT。

**计算与访存优化**

- prefill 计算压力大，但无需读写 KV cache。
- decode 需要频繁访问 KV cache，计算量相对小。

因此 PD 分离架构可以分别针对计算和访存瓶颈进行优化、优化资源分配，降低成本。

**batching 策略优化**

- prefill 阶段增加 batch size 对吞吐量的提升会越来越小，因为受限于计算资源会容易达到瓶颈。
- decode 阶段增加 batch size 会显著提升吞吐量，因为可以提高计算效率（访存呢？）。

decode 适合更大的 batch size。

**并行策略优化**

PD 分离架构可以分别为两个阶段选择最优的并行策略。

- prefill：在请求量较小时，更适合张量并行 (TP, intra-op)；在请求量较大时，更适合流水线并行 (PP, inter-op)。
- decode：GPU 数量增加时，PP 可显著提高吞吐量；TP 可以降低延迟。





---

## Speculative Sampling, MTP

> https://zhuanlan.zhihu.com/p/18056041194
>
> https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/advanced/speculative-decoding.md

主流的大模型都是基于 decoder 的，无论是训练还是推理，在生成序列时都需要 token-by-token。每次生成一个 token 时，都要频繁访存、加载 KV cache，因此访存会成为训练和推理的瓶颈。

投机采样 (*Speculative Sampling*, *Speculative Decoding*) / MTP (Multi-Token Prediction) 指每次迭代时生成多个 token 而非一个，适用于 gpu 因为 batchsize 较小无法充分利用时，降低 token 生成延迟。
在训练阶段，一次生成多个 token，可以一次学习多个位置的 label，提高样本利用效率，提升训练速度；在推理阶段，一次生成多个 token 可成倍加速推理。

投机采样会生成一序列的 token，称为 draft token，然后将这些 token 输入原始模型一次完成验证、决定留下多少 token。

以 TensorRT-LLM 为例，有多种生成 draft tokens 的方式：

- 用一个较小高效的辅助模型生成（称为 draft model）。
- 在主模型上加多个 head、一次生成多个 token。
- 将 prompt 的一部分作为预测 token (Prompt Lookup Decoding)。
- 用 Jacobi-like decoding 预测和验证 token。



**Blockwise Parallel Decoding**

Google 18 年提出的结构：

- 在 decoder 最后加一个共享的 FFN 层（全连接+relu+全连接），将 logit 做宽映射（h 维映射到 4h 维）。
- 然后连接多个 head，每个 head 预估一个 token（分别预估下一个、下下个、下下下个...），是一个非共享的 FFN 层（将 logit 维度还原 (4h->h)）。
- 最后所有 head 连接到同一个词表投影层（vocabulary projection，线性层+softmax；参数共享）得到输出。

主干网络 decoder + head1 称为主干网络，其它 head 是辅助网络 (auxiliary model)。

推理分为三步：

1. 预测：利用 k 个 head 一次性生成 k 个后续 token。
2. 验证：对第 i 个 token 输出，将`原输入 + 1~i-1 的预测 token`作为输入传给网络，检查 head1 的输出是否与第 i 个 token 输出一致。这部分要执行 k-1 次，可作为一个 batch 并行处理。
3. 接受：选择最长的结果与 head1 输出一致的 k' 个 token，作为最终输出。

通过一次预测多个 + 并行验证 来提高效率。





---

## LoRA

低秩分解 (LoRA, Low-Rank Adaptation) 是一种轻量级的微调方法，适用于大型预训练模型。传统的微调通常需要更新整个模型的参数，这在大模型中会带来巨大的计算和存储开销。LoRA 通过引入低秩矩阵来减少需要更新的参数数量，从而显著降低微调的成本。

LoRA 假设模型的权重矩阵在微调过程中可以通过低秩矩阵进行有效更新：对于一个权重矩阵 $W\in R^{m\times n}$，LoRA 认为其更新量 $\Delta W$ 可以用两个低秩矩阵 $A\in R^{m\times r}, B\in R^{r\times n}$ 的乘积来表示：$\Delta W=A\cdot B$，其中 $r\ll m,n$。
这种低秩假设意味着尽管权重矩阵本身可能很大，但其更新量可以用少量参数（低秩矩阵）来捕捉。这大大减少了需要训练的参数数量，同时保留了足够的表达能力。

LoRA 通过限制更新的参数数量，可以有效防止过拟合：由于低秩矩阵 A, B 的参数数量远小于原始权重矩阵，模型的容量被限制，从而降低了过拟合的风险。这在数据量较小的任务中非常重要。

> 从理论上看，LoRA 的有效性可以通过矩阵分解和低秩近似来解释。许多研究表明，高维矩阵的更新量通常具有低秩特性，因此用低秩矩阵来近似更新量是合理的。此外，低秩更新在数学上等价于对模型的某些特征空间进行局部调整，这种调整通常足以捕捉任务特定的信息。







---

## Parallel Scaling

> https://www.zhihu.com/question/1907422978985169131

应用 scaling law 来提升模型效果的主流方式有三种：

- Dense Scaling：增加模型参数量。但会增加推理时间，并显著增加需要的显存和训练代价（需要重训练）。
- MoE Scaling：增加专家数量来增加模型参数量。对推理时间影响小，但显著增加需要的显存和训练代价（需要重训练），且需要负载均衡。
- Inference-Time Scaling：增加模型推理时使用的 reasoning token、增大思维链长度。不需要重训练（可以 post-training，即 SFT、RLHF 或优化 prompt），但会增加推理耗时，且需要 RL 训练数据。

Parallel Scaling 将一个输入通过可学习的变换变为 P 个（在输入前添加 P 个不同的可学习前缀得到 P 个新输入），分别输入给模型并行推理，然后将 P 个输出通过可学习的聚合规则合并为单个输出。
将一个参数量为 N 的模型并行 P 个流，等价于将模型的参数量扩大$O(\log P)$倍。且不太会影响推理时间，占显存少，不需要重训练，没有特殊需求。

> 通过多前缀集成降低方差，同时共享参数 P 控制模型偏差？





---

## CacheBlend

> https://github.com/YaoJiayi/CacheBlend
>
> 上下文改变时（非后缀），改变位置开始的后续 kv cache 就不能用了，但 paper 发现只要第一层重算，后面层重算差异最大的 15% token 就可以。









---

## end





