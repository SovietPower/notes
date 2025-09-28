

# title

---

[TOC]

---



---

## Paged Attention

将 KV cache 分块或分页，每个 block 能存储一部分（如 4 个 token）的 KV 矩阵，使用时动态分配，避免需要对每个请求分配 max_seq_len 长度的 KV cache，提高显存利用率。

除此之外，前缀相同的两个请求可以共享前缀部分的 cache block，减少显存占用；在出现差异时 copy-on-write 分配新的块。

每个请求会记录它所使用的 block id 及 block 分配了哪些 token、有哪些空余。





---

## FlashAttention

> https://github.com/Dao-AILab/flash-attention
>
> https://zhuanlan.zhihu.com/p/664061672

> FA 本质是拿计算优化访存，虽然有TensorCore的GPU默认都是内存墙，但 d_h 很大（如 >256）时以后算力就不够用了。
> FA 的内存访问计算公式中含 d^2，通常 FA 的内存访问会少于普通 attention，但当 d 很大时 FA 的访存反而会多于普通 attention，同时其 FLOPS 也比普通实现高，所以性能会更差。

### 使用

**安装**

```bash
pip install flash-attn --no-build-isolation

# 如果有以下问题：
# import flash_attn_2_cuda as flash_attn_gpu
# ImportError: /usr/lib64/libc.so.6: version `GLIBC_2.32' not found (required by .../flash_attn_2_cuda.cpython-310-x86_64-linux-gnu.so)
# 用 torch <= 2.6 且低版本 flash-attn
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
pip install flash-attn==2.7.4.post1 --no-build-isolation
```

**flash_attn_varlen_func**

> 使用示例：https://66ring.github.io/2024/05/31/universe/ml/flash_attn_varlen_batcing_api_usage/













---

## end





