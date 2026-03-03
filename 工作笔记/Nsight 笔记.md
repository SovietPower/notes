# Nsight System / Compute 笔记

---
[TOC]

---




>  NVTX：https://developer.nvidia.com/blog/cuda-pro-tip-generate-custom-application-profile-timelines-nvtx/
> https://docs.nvidia.com/nvtx/index.html
>
> Nsight展现给我们的是一个时序图，但是这个图里并没有详细说明每一段时间对应的是哪一段程序。NVTX可以解决这个问题。



## Nsight System

> 历史版本：https://developer.nvidia.com/gameworksdownload


- dGPU (Quadro GP100)：显示 GPU 是否有 context 切换。如果长时间为绿色的 run，则代表没有发生切换。





### 使用



- 深蓝色的条有两种：对 kernel 的调用 kernel launcher 和对应的 kernel 执行。它们都会显示这次 launch 的 latency（前者是箭头向后，后者是箭头向前）。





### 优化方向

整体：

- 避免让 CPU 成为瓶颈；要保持 GPU 忙碌、让 GPU 成为瓶颈。然后再使用 Nsight Compute 降低 GPU 消耗。


细节：

- 在 kernel launch 期间执行异步拷贝，隐藏拷贝的延迟。
- 当 CPU 长时间执行 cudaStreamSynchronize 等待 GPU 完成时，可以先做其它任务，再同步，以实现 CPU 和 GPU 并行。
- 如果 CPU 连续异步调用数个 kernel，因为 GPU 执行相对较慢，所以 CPU 会很快就调用完成进入空闲，此时需安排其它 CPU 任务执行。




---
## Nsight Compute

> https://developer.nvidia.com/blog/using-nsight-compute-to-inspect-your-kernels/
> https://www.nvidia.com/en-us/on-demand/session/gtcsj20-s21771/（https://developer.nvidia.com/gtc/2020/video/s21771-vid）
>
> https://zhuanlan.zhihu.com/p/715022552

Nsys 只能在时间线上展示每个事件的起止时间，kernel 执行的具体工作（运算与访存）需要用 Compute 来看。



### 使用

```shell
ncu --set full -o report -f ./main
```

参数：

- --kernel <regex>：分析指定的 CUDA 内核（默认分析所有内核）
- --metrics <metric1,metric2>：指定分析的性能指标。
  - dram__bytes
  - gputime，sm__throughput，achieved_occupancy（实际占用率）
- --set <config>：使用预配置规则（full 全面分析，default 基础分析）
- -o, --export <filename>：指定输出文件的完整路径和名称（默认 report.ncu-rep）。
- --target-processes all：分析所有与目标程序相关的进程。如果不指定则默认只分析指定进程，可能会遗漏相关进程（子进程）。
- --devices <id>：指定要分析的 GPU 设备 ID
- --page <raw/details>：控制输出格式：
  - details: sections and rule.
  - raw: all collected metrics.
- --report api_trace：生成 API 跟踪报告。其他常用的报告类型包括 summary（概要报告）、concurrent_kernels（并发内核报告）等。
- -f, --force-overwrite：覆盖已有的输出文件。



### Summary

- estimated speedup/runtime improvement：该 kernel 最多能有多少性能提升。
- compute throughput：整个采样期间，SM 级别实际执行吞吐 / 理论可持续峰值 的百分比（理论峰值假设每个 SM 内部的 SMSP 负载完全均衡）。
  - 是一系列`sm__instruction_throughput`和`sm__memory_throughput`指标 (Compute Throughput Breakdown) 的最大值，见[这里](https://stackoverflow.com/questions/63403203/terminology-used-in-nsight-compute)。
  - SMSP: SM sub partition，一个SM被分为4个SMSP，每个SMSP管理固定数量的warp。一个SMSP通常包含一个warp scheduler，一个指令发射单元， 一部分寄存器文件，一组执行单元。每个SMSP在一个cycle最多发射1条warp指令。
- memory throughput：计算相关的内存访问流水线，达到了硬件可持续峰值带宽的百分比。
  - 实际上反映了一系列存储单元相关指标 (Memory Throughput Breakdown) 的最大值。
-  num of registers：每个线程分配到的寄存器个数。
- grid/block size



### GPU Speed Of Light Throughput

- Compute (SM) Throughput [%]：即 Summary 中的对应值，一系列子指标的最大值，子指标可见 Compute Throughput Breakdown。
- Memory Throughput [%]：即 Summary 中的对应值，一系列子指标的最大值，子指标可见 Memory Throughput Breakdown。

通过 SOL section (speed of light) 可以初步判断程序的瓶颈：

- Computer Bound：SM 利用率高，memory 利用率低。
- Memory Bound：SM 利用率低，memory 利用率高。
- Latency Bound：SM、memory 利用率均不高。



**Roofline**

屋顶线性能模型 (Roofline Performance Model) 简称屋顶线模型 (Roofline Model)，用于分析模型在特定计算平台上所能达到的理论计算性能上限。由于环境等因素的影响，实际性能测试结果一般差于 Roofline 模型给出的结果。

计算密集度/计算强度 $I=FLOPs/bytes$，计算强度上限 $I_{max}=P_{peak}/b_s$（$P_{peak}$ 是算力，$b_s$ 是带宽，见 *推理优化 - 计算密集度*）。

Roofline 模型定义的模型的计算性能瓶颈 $P=\min\{P_{peak},\ I*b_s\}$。
Roofline 模型的横坐标为 I，纵坐标为 P，当 $P\lt P_{peak}$ 时计算性能会随着 $I$ 增加而增加（斜率为 $b_s$）；当 $I$ 到达平台算力上限 $I_{max}$ 时计算性能 $P$ 到达最大值 $P_{peak}$ 不再增加。因此坐标图就是一条斜线+横线的屋顶状。

因此当横坐标 $I\lt I_{max}$ 时，模型的计算性能受限于宽带，是 memory bound；当 $I\geq I_{max}$ 时，计算性能已达到平台算力上限，是 compute bound。模型的计算强度应尽可能接近 $I_{max}$，但超出后就没意义了。

> 如果模型位于拐点 $I_{max}$ 左侧且位于斜线下方，则说明是 mem bound，且还没有完全利用最大带宽 $b_s$，导致计算性能比理论的最高值 $I*b_s$ 还低。此时模型纵坐标到斜线 $I*b_s$ 的距离（实际值和理论峰值）即为计算性能的提升空间。





### Compute Workload Analysis

> 流水线：https://docs.nvidia.com/nsight-compute/ProfilingGuide/#id27
> 指令：https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#instruction-set-reference

GPU 中不同精度的浮点计算由各自专门的计算单元独立完成。

> 不同架构不同型号的 GPU 之间，FP32 core 与 FP64 core 的数量可能相差很大，如 Turing 没有 FP64 core；Ampere 中两者比例为 64:1，因此单双精度性能也差 64 倍。
>
> 每条指令只有一条合适的流水线，除了 FP32 FADD/FFMA/FMUL 和 FP16 有 FMAHeavy 和 Lite 两条。

Pipe Utilization 显示了主要计算单元的利用率情况，通过每个计算单元活跃的周期数，或该单元执行的 warp 指令数这些指标统计；反映了硬件单元活跃时，各子单元实例实际利用的性能与其理论峰值性能的比例：

- % of active cycles：在 SM 活跃期间，有多少比例的周期该流水线在执行至少一条指令；
- % of peak instructions executed：该流水线实际执行的指令数，占它理论执行指令数峰值的百分比。

> - active cycles高，peak inst高：理想状态。
> - active cycles高，peak inst低：pipeline经常被使用，但每次用得不满，可能是warp数不够或指令之间无法并行。
> - active cycles低，peak inst高：指令mix不平衡，或者该pipeline不是瓶颈。
> - active cycles低，peak inst低：指令类型几乎不用该pipeline，或被其他瓶颈完全压制。

包括：

- FMA (Fused Multiply Add/Accumulate，融合乘加；FP32 core?)：FMA 流水线处理大多数的 FP32 计算 (FADD, FMUL, FMAD, ...)。它还执行整数乘法运算 (IMUL, IMAD) 和整数点积。
  由 FMAHeavy 和 FMALite 两条物理流水线组成。
- FMA (FP16)：表示在逻辑 FMA 流水线内执行的 FP16x2 指令（FP16 也在 FMA 的 FP32 core 上执行，且一次执行两条 FP16 指令）。还包括一个快速的 FP16-to-FP32 converter。
- FP64 (Double Precision ALU, DP unit)：负责大多数 FP64 指令 (DADD, DMUL, DMAD, ...)。
  不同芯片之间的 FP64 实现差异很大，因此其吞吐也会差异很大。
- Tensor (FP)：混合精度（FP16/TF32 和 FP32）浮点矩乘和累加单元。执行 HMMA ops。
- Tensor (INT)：整数矩乘和累加单元。执行 IMMA/BMMA ops。
- Tensor Core (TC)：执行 UTCBAR, UTCCP, UTC\*MMA, UTCSHIFT, UTC\*SWS。与 Tensor pipeline 不同，Tensor 执行不同的 MMA (Matrix Multiply and Accumulate) 指令。
- ALU (Arithmetic Logic Unit，算术逻辑单元)：ALU 负责执行大多数位操作和逻辑指令。还负责执行整数指令（不包括 IMAD 和 IMUL）。
  在 Ampere 架构芯片上，ALU 流水线还执行快速的 FP32-to-FP16 转换。
- LSU (Load Store Unit，加载存储单元)：LSU 流水线向 L1TEX 单元发出用于全局、本地和共享内存的加载、存储、原子和归约指令。它还向 L1TEX 单元发出特殊的寄存器读取 (S2R)、混洗 (shuffle) 和 CTA-level 到达/等待屏障指令。
- TMA (Tensor Memory Access Unit，张量访存单元)：在全局内存和共享内存之间提供高效的数据传输机制，能够理解和遍历多维数据布局。
- ADU (Address Divergence Unit，地址分支单元)：负责分支/跳转的地址分歧处理。还支持常量加载和 block-level 的屏障指令。
- CBU (Convergence Barrier Unit，汇聚屏障单元)：负责 warp-level convergence, barrier 和 branch 指令。
- TEX (Texture Unit，纹理单元)：SM 纹理流水线将纹理和表面指令转发到 L1TEX 单元的 TEXIN 阶段。
  在 FP64 或 Tensor 流水线解耦的 GPU 上，纹理流水线也会转发这些类型的指令。
- Uniform (Uniform Data Path，统一数据路径)：该标量单元负责执行所有线程使用相同输入并生成相同输出的指令。
- XU (Transcendental and Data Type Conversion Unit，超越和数据类型转换单元)：负责特殊函数，如 sin、cos和 rsqrt 倒数平方根。还负责 int-to-float 和 float-to-int 的转换。





### Memory Workload Analysis

当充分利用相关硬件单元 (Mem Busy)、耗尽这些单元之间的可用通信带宽 (Max Bandwidth) 或达到发出内存指令的最大吞吐量 (Mem Pipes Busy) 时，内存可能成为 kernel 性能的限制因素。



### Scheduler Statictics



### Warp State Statictics





### Instruction Statistics



### Occupancy

NCU 中，占用率 *occupancy* 是指每个 SM 上活跃 warp 数量与可能的最大活跃 warp 数量的比率。它也表示了硬件处理 warp 能力的实际使用百分比。
较高的占用率并不总意味着更高的性能，但较低的占用率**总是**会降低隐藏延迟的能力，从而导致整体性能下降。
在执行过程中，理论占用率与实际达到的占用率之间存在较大差异 通常表明工作负载高度不平衡。

下面的表格可以看 是寄存器数量、block size 还是 block shared memory 大小 限制了占用率。




### Warp Scheduler

Warp 被阻塞不被发射 (stall) 的原因大体上可分为：

- 正在获取指令。
- 有内存或执行依赖（需要读某数据、等待数据传输或等待某指令完成）
- 目标运算单元尚未空闲。
- 与其它 Warp 同步。

具体的常见 stall 原因及示例：https://www.bilibili.com/video/BV13w411o7cu?t=2816.9

- long scoreboard：
- short scoreboard：
- LG throttle：
- MIO throttle：

Warp Scheduler 通过数个 warp slot 来同时管理多个 warp。warp slot 有五个状态：

- unused：不存在 warp。
- active：warp 已经常驻在 SM。
- stalled：因前述原因被阻塞。
- eligible：当前周期已准备好。
- selected：当前周期被选择发射。

每个周期 warp scheduler 选择一个 eligible warp issue。如果没有则不发射。
warp scheduler 利用率即：发射 warp 的周期数 / 总周期数。




### Memory Workload

避免 back conflict 产生，会降低利用率。





### 其它

**tensor core**

可以在 details 界面的以下位置看到 tensor core 是否被使用：

- GPU Speed of Light Throughput | GPU Throughput Breakdown | SM: Pipe Tensor Cycles Active [%] 是否 > 0
  - 包含在 `basic` set。
- Compute Workload Analysis | Tensor (All)/Tensor (FP)/Tensor (DP)/Tensor (INT) 是否有某个 > 0
  - 包含在 `ComputeWorkloadAnalysis`（还是 `PmSampling`？）section 和 `full` set。
- Instruction Statistics | Executed Instruction Mix | *MMA 是否 > 0
  - tensor 上的矩乘叫 \*MMA (Matrix Multiply and Accumulate)（\* 是精度，如 F, H），cuda core 上的矩乘叫 FMA (Fused Multiply and Add)。


cuda core 对应一条 FP32 instruction pipeline，tensor core 对应一条 Tensor instruction pipeline，因此两者使用率可以通过 SM FMA Pipe Throughput 和 SM Tensor Pipe Throughput 近似。

> FMA Pipe 可以执行 non-FP32 指令（主要是 FP16x2？）。

**cuda core**

cuda core 就是 fp32 core，每个 fp32 core 在一个周期内可以执行一条单精度 FMA。

> cuda core 是营销术语，不是技术术语。





---

## ncu



### 参数

- --kernel <regex>：分析指定的 CUDA 内核（默认分析所有内核）。
- --metrics <metric1,metric2>：指定要分析的性能指标。一般用来补充 set 没有的。可通过`ncu --query-metrics`查看支持的 hardware counter。
  常用指标：
  - gputime，sm\_\_throughput，achieved_occupancy（实际占用率），dram\_\_bytes。
- --setction=<section>：指定要采集的 section。section 是一组 hardware counter 的集合。
- --set <set>：使用指定的 set 关联的一组 section 指标。可通过`ncu --list-sets`查看已定义的 set 及其对应的 sections，包括：default, detailed, full, source。
- -o, --export <filename>：指定输出文件的完整路径和名称（默认 report.ncu-rep）。
- --target-processes all：分析所有与目标程序相关的进程。如果不指定则默认只分析指定进程，可能会遗漏相关进程（子进程）。
- --devices <id>：指定要分析的GPU设备ID
- --page <raw/details>：控制输出格式：
  - details: sections and rule.
  - raw: all collected metrics.
- --report api_trace：生成 API 跟踪报告。其他常用的报告类型包括 summary（概要报告）、concurrent_kernels（并发内核报告）等。
- -f, --force-overwrite：覆盖已有的输出文件。






---
## end

