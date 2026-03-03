# MOE 笔记

---

[TOC]

---



TODO：

https://zhuanlan.zhihu.com/p/1903729394792511360

> 1. Qwen3MoE native 实现：[hugging face](https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen3_moe/modeling_qwen3_moe.py)
> 2. FusedMoE优化：[sglang](https://github.com/sgl-project/sglang/blob/4db463b1ad6edcd6b8cd500be377f65ff8e3b419/python/sglang/srt/models/qwen3_moe.py)
> 3. EP Moe: [sglang](https://github.com/sgl-project/sglang/commit/e330f2b86cd23f1acec113378aebd7bee268830b)
> 4. DeepEP: [sglang](https://github.com/sgl-project/sglang/pull/6120)



---

## MOE

> https://huggingface.co/blog/zh/moe



通过 topk 等方式，仅选择部分专家执行的 MOE 称为 **sparse MOE**。



**优势**

1. 神经网络往往是稀疏的，且模型越大越稀疏（模型中许多接近 0 的权重和激活值在推理时不起作用）。
   MOE 在推理时只使用少量的专家网络，在保证效果的同时减少计算量。
2. 不同专家可能专注于不同特征或领域，使模型有更强的任务泛化能力（但 LLM 的 MOE 更侧重引入稀疏性，而不是专一性）。
3. 增加专家数量就可以提升模型容量，且不会显著增加计算成本，可扩展性强。而且专家很容易分布到不同节点上计算，易于并行。

**专家容量** (**expert capacity**)

专家容量定义一个专家处理多少 token。当专家被分配过多 token 时，通常会直接丢弃。

**token 丢弃策略**

当某个专家被分配过多 token 时，通常会直接丢弃多余的 token（该 token 在该层不会产生输出。后面仍会通过残差网络加上原值）。
丢弃 token 时，可以使用一个评分网络来为该专家的 token 排序，然后丢弃分数最靠后的 token（优先丢弃不重要的 token）。

**负载均衡**

如果 token 不均匀地分配给每个 expert，主要的影响：

1. 降低训练效率：如果所有 token 经常被发送到少数几个受欢迎的专家，这些专家会训练的更快，loss 更小，更容易被选择，进一步加深不均匀的问题。
2. 负载不均衡，降低计算效率：可以将不同专家分配到不同 gpu 或不同节点上并行执行。如果某个专家要处理的 token 数更多，该节点的通信和计算代价会更高，拖累其它节点，影响并行效率。
3. 影响推理效果：每个专家有容量限制，溢出的 token 会被丢弃。
   更小的 capacity 会使该影响更大。
4. ~~浪费计算：专家计算的输入 shape 是固定的  expert capacity \* hidden size，超出 capacity 的输入会丢弃，不足 capacity 的输入会在后面补 0，padding 的计算是无意义的。
   更大的 capacity 会导致更多的零填充。~~（推理时 bs 一般是动态的）

**Mixtral-8x7B**

是基于 Mixtral 7B 的 8 个 expert 的 MOE 模型。
整体结构与 Mixtral 7B 类似，但 FFN 层换成了包含 8 个 export 的 MOE 层，总参数量为 47B。
推理时会选择 top2 的 expert，所以推理时执行计算的参数量为 13B。

> 计算：每个 expert 大小约为 0.18B，网络共 32 个 decoder，有两种计算方式：
>
> - 执行 1 个的运算量同 Mixtral 7B 是 7.24B，执行 2 个的运算量是 7.24+0.18\*32=13B（路由网络大小是 H * 8 参数量很小可忽略）。
> - 全部执行 8 个的运算量是 47B，只执行 2 个 expert 的运算量是 47-6\*0.18\*32=13B。
>
> 具体见 https://zhuanlan.zhihu.com/p/673527090 或 https://newsletter.maartengrootendorst.com/i/148217245/active-vs-sparse-parameters-with-mixtral-xb



---

## Switch Transformers

> https://arxiv.org/pdf/2101.03961



**辅助损失函数**

添加了一个辅助损失函数 (auxiliary loss)，用来让模型将 token 均匀的分配给每个 expert。
当 $f_i=分配给专家i的token的比例$ 和 $P_i=每个 token 被分配给专家 i 的概率的平均$ 均为 $1/N$ 时（$N$ 为专家数），损失最小。

> https://zhuanlan.zhihu.com/p/689987124
> 最小值计算：https://zhuanlan.zhihu.com/p/18062746529
>
> $f_i$ 是 argmax 不可求导、进行梯度下降，所以引入了 $P_i$。
>
> 1.它是个充满间断的函数。
> 2.在许多情况下，对这个损失函数进行梯度下降，会导致损失函数变大而不是变小。而变大的过程也能实现辅助的目标。换句话说，对它进行梯度下降的目的并不是找它的最小值，而是实现别的机制来满足我们的要求？







---

## DeepSeek

> https://zhuanlan.zhihu.com/p/21584562624



### V1

引入了两个 *辅助损失函数*：

1. 专家级别的负载均衡损失函数：让一个 batch 内的 token 均匀分布到各个专家。
   与普通的 loss 相比加了一个系数，避免不同 token 激活的专家数量不同时，对训练产生不同的影响。
2. 节点级别的辅助损失函数：将专家分成 D 组、放到 D 个节点上，该损失函数让 token 均匀分布到各个组即各个节点。



### V2

1. 限制每个 token 最多被发给几个节点。token 必须在这些节点中选最合适的专家，即使不是全局最优的。
2. 修改了 V1 的节点级别的辅助损失函数，加了一个系数，避免不同 token 发给的节点数量不同时，对训练产生不同的影响。



### V3

**无辅助损失的负载均衡 (Auxiliary-Loss-Free Load Balancing)**

移除了前面的三个辅助损失函数，使用一个偏置项来实现负载均衡：在计算 top k 时使用 $s_{i,t}+b_i$ 作为专家 i 在 token t 上的取值进行排名。$b_i$ 是可训练的偏置，仅用于计算 top k、决定选择哪些专家。
训练中有一个超参数 $\gamma$，当某个专家负载过高时，会将其偏置 $b_i$ 减去 $\gamma$，减少选择它的 token；某个专家负载过低时，为其偏置加上 $\gamma$，增加选择它的概率。

这种方法比之前复杂的多种辅助 loss 达成的负载均衡的效果更优，几乎不会丢弃任何 token。

**互补序列辅助损失 (Complementary Sequence-Wise Auxiliary Loss)**

前面通过丢弃了所有辅助损失函数、增加偏置项实现 batch 内的 token 负载均衡，但为了防止单个输入序列内出现极端不平衡的情况，还要采用一种序列级别的辅助损失函数。
与 V1 专家级别的 loss 类似，但该 loss 让一个序列（一个样本）而非 batch 内的 token 均匀分布到各个专家，粒度更细。

**No Token-Dropping**

因为负载均衡已经做得很好，所以不再需要丢弃任何 token。





---

## MMOE



> 简单：https://zhuanlan.zhihu.com/p/291406172

MMOE：

- 要求：MMoE 模型建模的几个任务是具有一定相关性的，且所需输入的特征基本一致。
- 相对于多个单目标模型，单个多目标模型的 MMOE 能以基本持平（也可能稍好或稍坏）的性能，成倍地节约训练和维护成本。







---

## end



