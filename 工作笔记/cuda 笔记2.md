# cuda

Tags: 笔记

---

[TOC]

---

TODO：






---

## 优化


### 确定 Warp, Block 大小

通常先确定 block 大小（每维线程数量），然后根据块大小和数据规模计算 warp 大小（每维块数量）。

block 的大小通常需要考虑内核的性能特性和 GPU 的资源限制（比如寄存器和共享内存的大小）。

- 应尽量避免使用小的线程块，因为无法充分利用硬件资源。
- CPU 与 GPU 中均以行为方式访问内存，因此应尽量保证相邻内存只由同一 block（即同一 SM）读写。





### tensor core, tile quantization, wave quantization

> 介绍：https://developer.nvidia.com/blog/programming-tensor-cores-cuda-9/
> 使用时的要求与限制、Dimension Quantization Effects：https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html
> 参考 2：https://docs.nvidia.com/deeplearning/performance/dl-performance-fully-connected/index.html#tc-guidelines
>
> ~~`ll /usr/local/cuda/lib64/libcublas.so*` 和 `ll .../libcudnn.so*` 来查看 cublas 和 cudnn 的版本。~~
> `ldd` 看程序链接的哪个 cublas，然后再 ll 看版本。
>
> 在 cuda 11.0 前，如果不满足要求就不会使用 tensor core，所以必须要注意。

**tensor core**

requirements：见上链接表格。

tensor core 是 Volta 及之后的架构才有的。相比 CUDA core，可提供更高效的矩乘运算。



**typical tile dimensions** in cuBLAS and performance

可用的 tile size：

- 256x128 and 128x256 (most efficient)
- 128x128
- 256x64 and 64x256
- 128x64 and 64x128
- 64x64 (least efficient)：通常只有 GEMM size 特别小时使用。

更大的 tile 有更多的 data reuse，因此会比小 tile 使用更少的带宽、更高效；但可并行的 tile 数量会更少，并行度会更低，可能导致 gpu 利用率低。
当 GEMM 足够大时，即使使用最大的 tile 也能有足够的任务来充分利用 gpu；当 GEMM 较小时，更小的 tile、更小的并行度会一起导致 gpu 利用率更低。
因此增大 GEMM 会提高性能（耗时会增加，但没有 size 增加的快）。有时可以以很小的耗时增加换取更大的 GEMM。



**tile quantization**

设 matmul 结果矩阵的大小是 n\*m，每个 tile 的大小是 a\*b，则 n 等于或接近且小于 a\*k、m 等于或接近且小于 b\*k' 时效率最高。否则会有 tile 包含大量无效的运算。



**wave quantization**

> 同时执行的线程块称为一个 wave。

设 matmul 结果矩阵的大小是 n\*m，每个 tile 的大小是 a\*b，每个 SM 只能执行一个 tile，gpu 共有 S 个 SM。
则 $\lceil n/a\rceil \times \lceil m/b\rceil$ 等于或接近且小于 S 时效率最高。否则需要 gpu 为多余的 tile 执行一轮新的计算。



**测试 tensor core 使用率**

> https://docs.nvidia.com/nsight-systems/UserGuide/index.html#launching-gpu-metrics-from-the-cli

If you run `nsys profile --gpu-metrics-devices all`, the Tensor Core utilization can be found in the GUI under the SM instructions/Tensor Active row.

要先 `nsys profile --gpu-metrics-devices=help` 查看本机哪些 gpu 支持这个操作。







### 矩乘

> https://blog.csdn.net/LostUnravel/article/details/138034380
>
> CPU：https://zhuanlan.zhihu.com/p/593537184





### MPS

> https://docs.nvidia.com/deploy/mps/index.html#
> 控制：https://docs.nvidia.com/deploy/mps/index.html#nvidia-cuda-mps-control
>
> https://www.olcf.ornl.gov/wp-content/uploads/2021/06/MPS_ORNL_20210817.pdf

**MPS**

> 注意：实际下面的"进程"实际是指 "cuda ctx"，即同一进程内使用不同 cuda ctx 也会按时间片调度，因此 MPS 也会产生优化（如果不开 MPS 效果则会比单 ctx 更差）（MPS 的目的是让多个 ctx 的不同 stream 上的 kernel 也并行）。
>
> - 单进程下 MPS + multi > no MPS + single ≈ MPS + single > no MPS + multi。
>   多个 cuda ctx 能减少同一 ctx 内不同 stream 间的竞争（如 ctx 级别的锁冲突？），但是会有切换代价，且 ctx 间会需要时间片调度。开启 MPS 后可消除调度带来的影响。
> - 多进程下 本身就相当于多个 cuda ctx，然后通过 MPS 合成一个，效果与单进程 + 多个 ctx 是类似的，所以单进程 2 ctx、双进程各 1 ctx 理论上区别不大；由于过多 ctx 数可能效果不大，所以双进程各 1 ctx、双进程各 2 ctx（就是 2 个和 4 个 ctx）也可能区别不大。
> - 单进程 2 个 ctx 与双进程各 1 个 ctx 的效果类似，所以可能可用来降低显存使用。

MPS (Multi-Process Scheduling) 用于让多进程的 cuda 程序利用 Hyper-Q 真正地在同一 gpu 上并行执行，以提高 gpu 利用率、降低耗时。

关闭 MPS 时，多进程通过时间分片的调度方式共享 GPU、无法并发（见 *基础 - Concurrent*），且有 ctx switch；开启 MPS 后，多任务共享 Server 的 CUDA Context。

意义：

- 提高 GPU 利用率：允许不同进程的 kernel 执行和 mem copy 在同一个 GPU 上同时(并发)执行，使用不同部分的 GPU。
- 降低 GPU 资源消耗：没有 MPS 时，每个使用 GPU 的 CUDA 进程会在 GPU 上分配独立的存储和调度资源。而 MPS server 会分配一份由所有 client 共享的 GPU 存储和调度资源。Volta MPS 支持更高的 client 隔离度，因此降低的不太多？
- 降低 GPU context 切换：没有 MPS 时，当进程共享 GPU 时，它们的调度资源必须在 GPU 上随时间片调度切换。MPS server 在所有 client 之间共享一套调度资源，消除了 client 之间 ctx 切换的开销。

适用于问题规模不变 但计算能力（节点/CPU core/GPU 数）可以提升的场景：

- 单个进程没有足够的工作、无法充分利用 gpu。此时 ctx switch 的数量和耗时占比就会很大。
  这种程序的 blocks-per-grid 会很小。
- 进程的 threads-per-grid 低导致 gpu 占用率低。

> volta 起 MPS client 进程之间的 GPU 地址空间完全隔离，因此不会有读写越界导致 UB 的情况？
>
> 当 GPU 发生 fatal fault 时，MPS server 会拒绝所有请求，直到受影响的 GPU 上的所有 client 都退出、重新创建 GPU context；并且无法得知导致错误的 client 是哪个。具体见文档 2.3.3.2. *Error Containment*。
>
> 每个 device 上 Volta MPS server 支持最多 48 个 client CUDA contexts，该限制由各个进程共享。如果超出，进程会在创建 ctx 时报错。

> **multi context**
>
> ~~虽然 MPS 下同一个 ctx 的 stream 之间一样可以并发执行，但无法并发提交任务 (launch kernel)？只有使用不同 ctx 的 stream 间才可以并发提交？~~

> **MPI**
>
> MPI (Message Passing Interface) 中的概念：
>
> - MPI 允许创建进程组（每个进程可属于多个组），每个组中的进程通过其 rank 标识（范围为 0~n-1）。
>   rank 是一个组内逻辑上的 worker，而进程是实际运行的实例（每个进程可以是多个 rank）。
> - communicators 是处理进程间通信的对象；intra-communicator 处理同一组内进程间的通信，inter-communicator 处理两个组之间的通信。

**3.1 Background**

cuda stream 在 driver 中对应 work queue，worker queue 是表示一个 stream 中任务的有序序列的子集的硬件。
支持 Hyper-Q 的 GPU（Kepler 起都支持）有一个并发调度器 来从 worker queue 调度属于同一个 cuda ctx 的任务；同一个 ctx 上的任务可并发执行。

不同 cuda ctx 上的任务不能并发执行：GPU 有一个时间片调度器 time sliced scheduler 来调度 work queue 上不同 ctx 的任务。如果单个 ctx 上的任务太少，可能导致 GPU 计算资源利用率低。此时需要通过 MPS。

**2.3.5.2 Volta MPS Execution Resource Provisioning**

Volta MPS 可以限制执行资源的提供，即限制 client ctx 只能使用部分的可用线程（限制最大使用量，而非为它预分配）。
意义：

- 降低 client 内存占用：因为(?)每个 MPS client 都有独立的地址空间，每个 client ctx 都会分配独立的 ctx 存储（如栈）和调度资源。这些资源随着 client 可用线程数量的增加而增加。
  默认每个 MPS client 都可以使用所有线程（这允许最大程度的调度自由）。但因为 MPS 通常用来同时运行多个进程，所以让所有线程都对每个 client 可用通常是不必要的，分配完整的 ctx 存储可能浪费内存资源。
  - 可以用 nvidia-smi 看每个 client 进程的内存。
- 提高 QoS：可以限制可用的计算带宽来作为一种 QoS 机制。
- 降低可用线程比例可以将 client 工作限制在特定 SM 内，降低不同 client 的任务之间的影响 (destructive interference?)。

> To provide a per-thread stack, CUDA reserves 1kB of GPU memory per thread
> This is (2048 threads per SM x 1kB per thread) = 2 MB per SM used, or 164 MB per client for V100 (221 MB for A100)
> CUDA_MPS_ACTIVE_THREAD_PERCENTAGE reduces max SM usage, and so reduces memory footprint
> Each MPS process also uploads a new copy of the executable code, which adds to the memory footprint.

限制的方式有两类：

1. 限制活跃线程百分比：可分为两种。设置的值会下取整到最近的硬件支持的线程数限制，可通过 cudaDevAttrMultiProcessorCount 查看。
   1. uniform partitioning：在 client 进程启动时设置其活跃线程比。无法在中途修改。
      可以通过 MPS control 的 set_default_active_thread_percentage / set_active_thread_percentage 设置后续 新创建的 server 创建 client 时的默认比 / 指定 server 上新创建的 client 的百分比。也可以为 MPS 控制进程或 client 设置 CUDA_MPS_ACTIVE_THREAD_PERCENTAGE。
   2. non-uniform partitioning：为每个 client cuda ctx 设置其活跃线程比。可以在进程执行中修改。
      uniform 为进程设置的限制可以与对 ctx 的限制同时生效（取最小值），要设置 CUDA_MPS_ENABLE_PER_CTX_DEVICE_MULTIPROCESSOR_PARTITIONING。
2. 通过编程接口 (programmatic interface) 限制可用的 SM 比例：通过 [cuCtxCreate_v3](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__CTX.html#group__CUDA__CTX_1g2a5b565b1fb067f319c98787ddfa4016) 创建 client cuda ctx 并指定 execution affinity `CUexecAffinityParam` 可以限制 ctx 能使用的 SM 数量。设置的值会上取整到最近的硬件支持的 SM 数限制，可通过 cuCtxGetExecAffinity 查看。
   - 好像只有一种 CUexecAffinityParam：CU_EXEC_AFFINITY_TYPE_SM_COUNT：通过 CUexecAffinitySmCount 限制 ctx 可用的 SM 百分比。
   - 比限制线程数更细粒度和灵活。

可参考的限制策略：

- uniformly partition：将线程均匀分给每个 client，比如设置 active thread percentage 为 100% / 0.5n（n 为 client 进程数）。0.5 是允许 client 利用可能有的空闲资源。
- non-uniformly partition：根据每个 client 的工作负载分配活跃线程比。可以使不同 client 的工作集中到不相交的 SM 上，减少 client 间的影响。
- 最优策略：在已知每个 client 的执行需求时，精确地限制每个 client 能用的 SM 数量。

**Compute Mode**

GPU Compute Mode 影响了资源在计算时如何被分配和利用。用来调整 GPU 如何处理多进程。

计算模式有三种：

- DEFAULT：多个进程可同时使用 GPU 资源，这些进程的各线程都可以并行向 GPU 提交任务。
  多进程可能会因为竞争 GPU 资源导致性能下降。
- EXCLUSIVE_PROCESS：同一时间只有一个进程可以使用 GPU，该进程的各线程可以并行向 GPU 提交任务。
  可以减少其它进程对 GPU 资源的影响，提升单个进程的性能和降低延迟。
- PROHIBITED：都不能用 GPU。

通过 `nvidia-smi -c MODE` 调整计算模式。

MPS 可以让所有 MPS client 在 exclusive process 下也像 default 一样 通过 MPS server 同时使用 GPU。
在 shared system 使用 MPS 时，最好使用 exclusive process mode 以保证只有 MPS server 在使用 GPU。








---

## volta

### kernel

**Gemm**

Gemm (general matrix-matrix multiplication) 是密集广义矩阵乘法 kernel，形式为 $C=\alpha AB+\beta C$。计算密集且内存高效。
Gemv (general matrix-vector multiplication) 是稀疏广义矩阵乘法 kernel，形式为 $C=\alpha AB+\beta C$ 且设 A 为 n\*k B 为 k\*m，要么 n=1 要么 m=1，因此其计算密度总会小于 1。所以受限于带宽、内存低效。
因此，Gemm 的计算可以复用数据，会比 Gemv 更快，SM 利用率更高。

Gemmk1, Gemv2T, Gemv2N 是 cuBLAS kernel。T/N 应该指操作矩阵是否转置，2T 代表都转置。
Gemmk1 是 Gemm 的变种，Gemv2T/2N 是 Gemv 的变种。



**volta_sgemm_128_32**
**volta_sgemm_128x32_nn_v1**

- volta: GPU architecture
- s: 累加器类型 (accumulator type)，s 是 single precision
- gemm: kernel type: matrix multiplication in this case
- 128: number of elements per CTA in M dimension of the C matrix
- 32: number of elements per CTA in N dimension of the C matrix
- 128x32：指矩阵乘法内核的块大小（block size）。具体来说，128x32可能表示内核在执行矩阵乘法时，每次处理128行和32列的数据块。这种块大小的选择通常是为了优化内存访问和计算效率。
- nn: storage mode for A and B matrices, respectively: “normal” or “no-transpose” (column-major) in your case.
  矩阵乘法的操作模式。nn 表示两个矩阵都不转置；nt 是第一个矩阵不转置，第二个矩阵转置；tn 是第一个矩阵转置，第二个矩阵不转置；tt 是两个矩阵都转置。
- v1：可能是该 kernel 的实现版本。





---

## DCGM



### Metrics

> https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html#profiling-metrics
>
> `dcgmi dmon --list` 查看所有支持的指标。

- GPUTL (203)：GPU utilization，gpu 利用率，与 Volatile gpu util 类似，有任意 kernel 在执行的时间占比
- MCUTL (204)：memory utilization。
- GRACT (1001)：Graphics Activity，有任意图形或计算单元活跃的时间占比。
  - [一个解释是](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html#understanding-metrics) 已分配的计算资源 / 总计算资源 (SM?)？
- SMACT (1002)：SM Activity，SM 上至少有一个 warp 活跃（至少有一个 SM 活跃）的时间占比，所有 SM 取均值。
  - wrap 正在计算或等待内存请求都被视为活跃。
  - 最好高于 0.8。低于 0.5 说明 GPU 使用很低效。
- SMOCC (1003)：SM Occupancy，SM 上 resident warp 与最大可并发 wrap 数的比例。
  - 如果任务是 compute bound，则更高的 occ 不能代表更好地利用 gpu；如果是 memory bound，则提高 occ 有意义。
- TENSO (1004)：Tensor Activity，tensor pipe (HMMA, IMMA) 活跃的周期数比例。更高的值代表对 tensor core 有更高的利用率。
- DRAMA (1005)：Memory utilization
-  (1006)：不支持 Error setting watches. Result: -6: Feature not supported。
- PCI Bandwidth transmitted (TX) or received (RX)：PCI Bandwidth transmitted (TX) or received (RX)
- NVLTX/RX: NVLink Bandwidth transmitted (TX) or received (RX)
- Power: total power consumption of the GPU.






---

## end



