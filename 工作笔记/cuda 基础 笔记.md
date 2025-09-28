# cuda 基础

Tags: 笔记

---

[TOC]

---

TODO：

https://developer.nvidia.com/cuda-example
相关笔记：https://zhuanlan.zhihu.com/p/690880124

https://zhuanlan.zhihu.com/p/680075822
cuda 简单应用：https://www.zhihu.com/question/263832290

（https://developer.nvidia.com/blog/even-easier-introduction-cuda/ 下的系列）
https://developer.nvidia.com/blog/how-implement-performance-metrics-cuda-cc/
https://developer.nvidia.com/blog/how-query-device-properties-and-handle-errors-cuda-cc/
https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/
https://developer.nvidia.com/blog/how-overlap-data-transfers-cuda-cc/
https://developer.nvidia.com/blog/how-access-global-memory-efficiently-cuda-c-kernels/
https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/

> Experiment with printf() inside the kernel. Try printing out the values of threadIdx.xand blockIdx.x for some or all of the threads. Do they print in sequential order? Why or why not?



> 官方文档：https://docs.nvidia.com/cuda/
> [cuda C++ programming guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html)
> [cuda C++ best practices guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)



**入门**

> 官方：
> https://developer.nvidia.com/blog/even-easier-introduction-cuda/#where-to-from-here
> 《cuda by example》：https://developer.nvidia.com/cuda-example
> 配套网课 cs344：https://developer.nvidia.com/udacity-cs344-intro-parallel-programming（代码：https://github.com/udacity/cs344 b站视频：https://www.bilibili.com/video/BV1yt411w7h8）
>
> 资料：
> cuda 课程：https://github.com/cuda-mode/lectures
> Learn CUDA Programming：https://github.com/PacktPublishing/Learn-CUDA-Programming
> https://face2ai.com/program-blog/（相关代码：https://github.com/Tony-Tan/CUDA_Freshman）
>
> 项目：
> 官方示例：https://github.com/NVIDIA/cuda-samples
> cuda 训练简单 llm：https://github.com/karpathy/llm.c
>
> 书籍：
> 《CUDA C编程权威指南》（较旧）
> 《GPU编程实战（基于Python和CUDA）》
> 《GPU编程与优化 大众高性能计算》
> 上帝视角看GPU：https://www.bilibili.com/video/BV1P44y1V7bu/

**进阶**

> 一些示例：https://www.zhihu.com/question/62996995/answer/2886019883
>
> cuda 实际应用：https://www.zhihu.com/question/26570985/answer/3465784970


**其它**




---

## 基础

### 安装

> WSL 安装：https://zhuanlan.zhihu.com/p/648330821
> 安装 Miniconda 和 torch：https://zhuanlan.zhihu.com/p/663817616
>
> 编译：在 vscode wsl 中安装插件 Nsight Visual Studio Code Edition
> 设定用于 cuda c++ 的 tasks.json（可选，然后可通过左上角 终端 - 运行任务 完成编译。也可使用 cmake 或手动命令行编译）。
>
> 调试：在左上角的 运行 - 添加配置 生成 launch.json 模板，然后修改要执行的程序（比如`${fileDirname}/${fileBasenameNoExtension}`）。然后编译，在左侧 运行与调试 界面选择 launch 任务调试。
> （但目前无法调试）



### 编译

编译 CUDA 程序需要使用编译器 nvcc。nvcc 会先将所有源代码分离成主机代码和设备代码，主机代码完整支持 C++ 语法，设备代码只支持部分 C++ 语法。nvcc 会将设备代码编译为 PTX (parallel thread execution) 伪汇编代码，再将 PTX 代码编译为二进制的 cubin 目标代码。

> 编译设备代码到 PTX 代码时，需要用 -arch=compute_XY 来指定一个虚拟架构的计算能力；编译 PTX 到 cubin 代码时，需要用 -code=sm_ZW 指定一个真实架构的计算能力。XYZW 是数字，真实架构号必须大于等于虚拟架构号。





### Grid, Block, Thread

> thread 对应 SP (cuda core 或 tensor core)，是基本的运算单元/执行单元。
> block 对应 SM，包含许多运算单元，是能完整独立运行的最小单元。
> grid 对应 GPU (device) 上执行的一个函数，包含可分配到不同 SM 上的多个 block 执行。

为了便于编程和管理线程，cuda 引入了 网格 (grid)、线程块 (thread block)、线程 (thead)、线程束 (warp) 四个概念。
执行 kernel 时，其使用的所有 thread 组成了一个 grid，会使用 GPU 上的部分计算单元。每个 grid 包含若干可并行执行的 block，每个 block 内包含若干 thread。

同一 grid 中的所有线程共享全局内存空间。

> GPU 可以创建的 grid、block 数量、可支持的线程数量取决于其计算能力（但对于可支持的线程数量来说，目前所有计算能力都一样），见[这里](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#features-and-technical-specifications-technical-specifications-per-compute-capability)。
>
> - 每个 block 可创建的线程数最大为 1024（32 个 warp），最多可使用 64K 个 32 位寄存器。
> - 每个 SM 可同时执行的线程数通常为 1536 (48 warp) 或 2048 (64 warp)，最多可使用 64K 个 32 位寄存器。
> - 每个线程最多可使用 255 个 32 位寄存器（block 或 SM 内并非所有线程都可以使用这么多寄存器）。
>
> grid 中的 block 可以以一维、二维、三维三种组织方式排列；block 中的 thread 也是如此。
> block 的所有线程实际上是一维的（分成若干 warp）；grid 的所有 block 之间也没有空间关系。分三个维度的好处是可以减少一些计算索引时的除法或取余运算，毕竟整数除法和取余的开销较大。

**thread**

GPU 通过切换到其它线程执行，来隐藏有依赖的指令的延迟。因此要想充分利用 GPU，线程数要远高于核数或指令流水线数。

**block**

执行同一函数的多个线程会被划分为多个线程块；每次执行一个函数会启动多个线程块。

一个 SM 可处理多个 block，同一个 block 中的 thread 只会在同一个 SM 中并行执行，它们可以通过同步或共享内存通信进行协作（不同块之间的 thread 不能直接通信，只能通过全局内存和 cooperative group），所以 block 也被称为 Cooperative Thread Array (CTA)。
在执行 kernel、启动 grid 时，该 grid 的 block 就会被分配到可用的 SM 上执行。
一个 block 只会由一个 SM 调度，且一旦被分配好 SM，就会一直在其中以 wrap 为单位执行。不同 block 可由可用的不同 SM 执行。

block 有一些 block 层的资源：

- Shared Memory (共享内存)：block 层最显著的资源。它的容量可以由编译器决定，也可以运行时动态指定，但是一般有上限（见 CUDA Programming Guide: Features and Technical Specifications 的 Table 15）。
  Shared Memory 对于整个 block 内的每个 thread 都是可读可写的，block 外则无法访问。
  较新的架构里 Shared Memory 还支持 atomic 操作，效率比用 global memory 做 atomic 操作有很大提升。
- Synchronize Barrier：block 有一个重要操作就是同步（比如`__syncthreads()`，参考 [Synchronization Functions](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#synchronization-functions)，或 PTX 中 [bar 和 barrier 指令](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-bar)）。
  每个 block 有16个 barrier，每个可以支持独立的同步操作（规定到达线程数，是 arrive 还是 sync 模式等等，具体见 PTX 的 bar 指令。
  注意同步不仅仅是保证 warp 都运行到某个指令的位置，还要求之前的一些操作如 memory load 的 dependency 完成。
- 其它资源：特殊寄存器（blockIdx.x/y/z 等）；内部状态变量，比如 GPR 在整个 register file 里的起始地址、local memory 的起始地址；debug 用的资源等。这些对用户不完全开放，一般不用太过关注。

Block 是 kernel 运行时进行资源分配的最小完整单元：block 的所有资源限制在同一个 SM 内，启动前必须全部分配完成：block运行时的所有资源（包括 GPR、每个 thread 的私有资源、warp 私有资源，block 一级的 shared memory 等），都必须在 block 启动前就绪。如果一个 SM 无法提供足够资源，则 block 无法在这个 SM 上启动。
如果部分 warp 提前退出，它的资源应该可以先被释放，但 shared memory 只能在当前 block 的所有线程完成后才释放。

block 保证了 warp 和 thread 在运行前能分配到所有需要的资源，且这些资源在运行时随时可用，使得 warp 可以高效切换。

每个 SM 需要同时运行足够多的 warp 才能有效隐藏带有依赖的指令的延迟，而 SM 上的 block 数量、block 中的 warp 数量都有限。因此，调整 block 的资源占用（每个线程的 GPR 数量、warp 数、shared memory 大小等），可以影响同一个 SM 上能容纳的 block 数目，从而调整 SM occupancy。

- 每个 SM 的 shared memory 有限（如 48KB），如果启动 kernel 时给每个 block 分配的 s_mem 过大，则每个 SM 只能容纳少量 block，可能导致活跃 warp 数量降低（比如只有一个 block 分成的 warp）。

Block 之间基本相互独立，没有数据交换，理论上能以任意顺序发送到任何空闲的 SM 上。

> 如果 CUDA 支持 block 部分 warp 先退出则资源可以先回收，那一个 SM 可能容纳小数个 block，后进的完整 block 能与之前 block 残留的 warp 同时运行。

**grid**

grid 是一组 thread block，并且定义了这组的形状。

用户可见的 grid 资源，比如 global memory、constant memory、texture/surface reference 或 object 等，都是可以在同一个 context 下的所有 kernel 间继承和共享的。每个 kernel 在 grid 这一层并没有太多的私有资源。


**cudaThreadSynchronize**

`cudaThreadSynchronize()`可同步同一个 block 的所有 thread（均在此阻塞直到全部到达）。

**索引计算**

grid, block 都可以是一维、二维或三维的，grid 的维度的每个元素是 block，block 的每个元素是 thread。

内置变量：

- `blockIdx`：线程块在对应 grid 中的编号。
  `threadIdx`：线程在对应线程块中的编号。
  两者都是`uint3`向量类型，包含 x, y, z 三个 uint 成员。
- `gridDim`：grid 的维度，即每一维的 block 数量。对应调用 kernel 时的 gridSize。
  `blockDim`：block 的维度，即每一维的 thread 数量。对应调用 kernel 时的 blockSize。
  两者都是`dim3`向量类型，包含 x, y, z 三个 uint 成员。

例：

- `gridDim.x`：当前 grid 中线程块的数量（一维）/第一维度的大小（多维）。
- `blockDim.x`：线程块中的线程数量（一维）/第一维度的大小（多维）。

计算：

- 线程块在整个 grid 的编号：
  一维：`blockIdx.x`。
  多维：`blockIdx.x + blockIdx.y * gridDim.x + gridDim.x * gridDim.y * blockIdx.z`。
- 线程在整个 grid 中的编号：
  一维：`blockIdx.x * blockDim.x + threadIdx.x`。
  多维：`blockId * (blockDim.x * blockDim.y * blockDim.z) + (threadIdx.z * (blockDim.x * blockDim.y))  + (threadIdx.y * blockDim.x) + threadIdx.x`。
- grid 中的线程总数量：
  一维：`blockDim.x * gridDim.x`。
  三维：`grid_size.x * grid_size.y * grid_size.z * block_size.x * block_size.y * block_size.z`。
  常用作线程枚举的步长 (stride)（这种循环称为 grid-stride loop）。



### SM

由于一个 block 只会在一个 SM 上执行，且 SM 可同时执行多个 block，因此想要充分利用 GPU，需要启动许多（数倍于 SM 数量）block。

由于 *Wave Quantization*，block 数量最好是 SM 的整数倍（或接近但小于），来降低最后一个 wave (tail wave) 的浪费。

> A10 有 72 个 SM，T4：40，A100：108。



### Warp

线程束 (warp) 是 cuda GPU 调度和执行的基本单元（是 SM 执行的基本单元）（是 cuda 软件的概念，但是与硬件直接相关）。
目前 cuda 一个 warp 的大小 (warpSize) 为32个线程（即一个 SM 上只有32个线程能同时执行）。在同一个 warp 中的线程能以任意顺序执行，并会以不同的数据资源执行相同的指令 (SIMT)。

很多内存指令的访问模式都是以 warp 为单位。

> thread 本意是线，warp 是经纱（线的集合）。
>
> 通过把 warp 中的 thread 同步运行，分摊指令 fetch、decode 等各种开销，可以降低运行调度的复杂度、降低功耗。

当一个 block 被调度到某个 SM 时，block 中的 thread 会被划分为多个 warp 分别被调度执行，每个 warp 中的 thread 会执行相同指令，但拥有独立的 PC、寄存器和数据。所以 block 的大小（三维总大小）最好是 warpSize (32) 的整数倍，以避免最后一个 warp 中包含无用线程。
在软件 (编程) 角度，block 是线程的集合（可以是一维/二维/三维）；在硬件角度，block 是 warp 的集合（一维）。

> 一个 warp 需要占用一个 SM 运行，多个 warp 需要轮流进入 SM 执行，由 SM 的硬件 warp scheduler 负责调度。
> 所以任意时刻 GPU 上的活跃线程最多只有 SM 数量 * 32 个，不是所有线程都在物理上同时执行（只是逻辑上并行）。
>
> 在 Volta 之前每个 wrap 只有一个 PC，

当一个 warp 空闲时，SM 就可以调度驻留在该 SM 中的另一个可用 warp。
**在 SM 上保留足够多的活跃 warp 可以隐藏数据加载（访存或有指令依赖）的延时。**

在并发的 warp 之间切换没有什么代价，因为硬件资源早就被分配到所有的 thread 和 block，新调度的 warp 的状态已经存储在 SM 中了。这不同于 CPU：CPU 切换线程需要保存/恢复上下文；而 GPU 为每个 thread 提供物理寄存器、为每个 block 分配资源，无需保存/恢复上下文。

**warp 分支** / **warp divergence**

一个 warp 中的线程会执行相同指令。如果线程执行的代码中出现分支，则需要分别顺序执行每个分支路径 (warp divergence)：对于单个分支，如果存在某个线程求值为 true，则并行执行为 true 的线程，其它线程等待 (stall)；执行完  true 分支后，所有为 false 的线程再执行，其它线程等待。
因此要提高并行性，应尽量避免同一 warp 中的线程进入不同分支。


**warp shuffle**

Warp 内的各个线程交换数据可以用 warp shuffle，是直接基于寄存器的数据交换，并不需要额外的存储空间。模式可以一个 lane 广播到所有的 lane，也可以有比较复杂的交换 pattern。warp shuffle 与基于 shared memory 的数据交换各有优劣。





### kernel

`__global__`修饰的函数为核函数。具体见下 *global*。

**执行 kernel**

调用：`kernel_name<<<grid_size, block_size>>>(args)`。

`<<<grid_size, block_size>>>`称为执行配置 (*execution configuration*，具体见下)，告诉 CUDA runtime 在该 grid 中使用多少个 block 和 thread 及组织形式。
grid_size 与 block_size 可以是 dim3 类型的结构体（二维或三维）或一个 unsigned int（一维）。

```cpp
dim3 grid_size(2, 3);
dim3 grid_size(2, 2, 3);
```

执行/启动一个 kernel 称为 launch。
执行 kernel 不会阻塞 CPU，可使用`cudaDeviceSynchronize()`阻塞直到 device (GPU) 完成。

从异步调用 kernel launch API 到 kernel 真正执行的这段时间，为 launch latency (或 induction time)。
launch latency 可能比执行 kernel 本身还要长（几~几十微秒，windows 可能更高）。所以会通过算子融合、cuda graph、多个 cuda stream、batching 等方式减少 launch 开销。
latency 会受 kernel 参数大小影响。

> CPU 调用 kernel launch API 通常非常快，而 GPU 执行相对更慢。所以如果 CPU 连续异步调用数个 kernel，会很快就调用完成进入空闲，此时需安排其它 CPU 任务执行；GPU 需要依次执行每个 kernel，所以每个 kernel 的 launch latency 都会越来越大（第一个较短，第二个要加上第一个 kernel 的执行时间，依次类推）。

从任务被加入对列到任务执行完成的时间，称为 task latency (或 total time)。

**execution configuration**

> https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#execution-configuration

任何对`__global__`函数的调用必须声明执行配置`<<<Dg, Db, Ns, S>>>`。参数依次为：

1. Dg (dim3)：grid 的维度、block 的数量。

2. Db (dim3)：block 的维度、thread 的数量。

3. Ns (size_t)：这次调用中需要为每个 block 额外动态分配的 shared memory 字节数（与静态分配的 shared memory 独立）。这些动态分配的内存可以被任何`__shared__`变量使用。

   可选，默认 0。

4. S (cudaStream_t)：要关联的 stream。
   可选，默认 0（0 可直接赋给 cudaStream_t）。如果要指定则必须同时指定 Ns。

**编写 kernel**

kernel 主要有两部分：确定数据与线程的对应；处理对应数据。

**Dynamic Parallelism**

CUDA 5.0 引入了 Dynamic Parallelism。此前 kernel 都只能从 host 端启动，grid 和 block 的 dim 必须在 host 端确定好。这对于形状规则易于均匀划分的计算任务是合适的。但有些应用一些区域任务多、一些区域任务少，有时任务大小需要经过复杂计算，并不能一开始就得到。Dynamic Parallelism 允许 kernel 函数内再启动 kernel，由父 kernel 负责计算子 kernel 所需的 grid、block 的 dimension，也包括分配子 kernel 所需要的一些内存资源等（有一套 device 端的 API）。

**kernel<<<1, N>>> 与 kernel<<<N, 1>>>**

前者是 kernel 以 N 个线程块启动、每个块只有一个线程，通常用于 kernel 需要执行 N 个独立的任务，每个任务由一个单独的线程块完成。
后者是 kernel 以 1 个线程块启动、这个块有 N 个线程，通常用于 kernel 需要执行一个任务，但这个任务可以被分解为 N 个并行任务，由同一个线程块中的 N 个线程并行完成。

当每个线程执行的任务是独立的，且没有线程间同步的需求时，使用前者可能更合适：

- 减少线程块内同步/通信、避免共享内存竞争：同一个线程块内的线程可以协同工作，但这也意味着它们可能需要进行线程间同步/通信、可能会竞争访问共享内存。如果任务是独立的，那同步是不必要的，使用单个线程的线程块可以避免。
- 提高资源利用率：某些情况下，使用单个线程的线程块可以更有效地利用GPU资源？
- 提高启动效率： 启动大量单个线程的线程块可能比启动少量多线程的线程块更有效率，因为每个线程块的启动开销是固定的，而更多的线程块可以更细粒度地利用GPU的并行处理能力？
- 简化线程索引计算：如果每个线程块内只有一个线程，那每个线程的全局索引可以直接用其线程块索引表示（但这差不了多少？）。
- 在某些GPU架构中，可能更适合于处理大量小线程块的情况？







### 内存管理

kernel 中访问的内存必须是位于 GPU 的内存，host 代码中访问的内存必须是位于 CPU 的内存。

`cudaError_t cudaMalloc(void**, uint)`分配位于 GPU 上的内存。
需传入一个二级指针`d_ptr`，分配时会修改它的值。

`cudaError_t cudaMemcpy(void*, void*, uint, enum cudaMemcpyKind)`在 CPU 内存和 GPU 内存之间进行拷贝。可用来初始化或将结果移动回 CPU。
指针参数分别为`d_ptr`和`h_ptr`，前者为 device 上的指针，后者为 host 上的指针。
enum 代表数据传输的方向，包括5种：

- cudaMemcpyHostToDevice
- cudaMemcpyDeviceToHost
- cudaMemcpyHostToHost
- cudaMemcpyDeviceToDevice
- cudaMemcpyDefault

标准的执行流程：

```cpp
// 1. 分别 CPU 内存、初始化
double *h_x = (double*) malloc(M);  // 还是 cudaMallocHost？
for (int n = 0; n < N; ++n) {  // init
    h_x[n] = a;
}
// 2. 分配 GPU 内存
double *d_x;
cudaMalloc((void **)&d_x, sizeof(double) * N);
// 3. H2D
cudaMemcpy(d_x, h_x, M, cudaMemcpyHostToDevice);
// 4. kernel 计算
kernel<<<...>>>...
// 5. D2H
cudaMemcpy(h_x, d_x, M, cudaMemcpyDeviceToHost);
```

**memcpy**

每个 memcpy 都被分成 synchronous 和 asynchronous 版本，但注意同步版本可能异步、异步版本也可能同步：

Synchronous:

- For transfers from pageable host memory to device memory, a stream sync is performed before the copy is initiated. The function will return once the pageable buffer has been copied to the staging memory for DMA transfer to device memory, but the DMA to final destination may not have completed.
- For transfers from pinned host memory to device memory, the function is synchronous with respect to the host.
- For transfers from device to either pageable or pinned host memory, the function returns only once the copy has completed.
- For transfers from device memory to device memory, no host-side synchronization is performed.
- For transfers from any host memory to any host memory, the function is fully synchronous with respect to the host.

Asynchronous:

- For transfers between device memory and pageable host memory, the function might be synchronous with respect to host.
- For transfers from any host memory to any host memory, the function is fully synchronous with respect to the host.
- If pageable memory must first be staged to pinned memory, the driver may synchronize with the stream and stage the copy into pinned memory.
- For all other transfers, the function should be fully asynchronous.




### Unified Memory

Unified Memory (UMA) 是 CPU 和 GPU 都可以访问的内存（也称为 managed memory）。（并且可以在任意 GPU 上访问？）

使用`cudaMallocManaged(void**, uint)`分配统一内存，使用`cudaFree(void*)`释放统一内存。
与 malloc、free 类似，而不是 new、delete。

```cpp
// Allocate Unified Memory (accessible from CPU or GPU)
float *x;
cudaMallocManaged(&x, N * sizeof(float));
cudaFree(x);
```

> cudaMallocHost、cudaMalloc、H2D、kernel launch、D2H 的标准过程太麻烦了，因此用 unified memory 来处理内存、不用管在哪分配、什么时候拷贝。
>
> UM 中 GPU 与 CPU 的虚拟地址 VA 是一致的（GPU 可能多几位）？以便于编程。

> 当访问 unified memory 中的数据时（称为 CUDA *managed* data），cuda 软件和/或硬件会将内存页迁移到正在访问的处理器 (CPU/GPU) 内存中 (migration)（不是真的共享，只是把数据迁移过程隐藏了）。
> 内存迁移时间可在 Unified Memory profiling result 中看到。
>
> 在 Pascal 架构之前的 GPU（如 K80）不能处理 page fault，因此调用 cudaMallocManaged 需要立刻在 GPU 上分配指定数量的内存，并为分配涉及的页创建页表条目。当在 CPU 上访问这些完全位于 GPU 的内存页时，会触发 page fault，然后 GPU 驱动会将访问的页从 device 迁移到 CPU 内存 (device to host)。
> 在 launch kernel 时，由于这些旧的 GPU 没有 page fault 机制，因此需要将先前迁移到 CPU 内存或其它 GPU 中的所有页迁移回来 (host to device)，不管实际是否会用到。因此每次启动 kernel 都可能有不必要的开销。
> 因此，迁移页在 kernel 运行前完成，迁移时间不会被计入运行时间。
>
> 自 Pascal 架构起，调用 cudaMallocManaged 可能不会立刻分配 managed 内存和创建页表条目，而是在访问或预取时分配 (demand paging)；GPU 支持49位虚拟地址和按需的内存迁移。
> 内存页同样需要在 CPU 与 GPU 之间迁移，但是在硬件上支持 page fault 和内存迁移，因此启动 kernel 前不需要迁移页、没有不必要的迁移开销；当访问的页不存在时，GPU 会阻塞对应线程的执行，由 Page Migration Engine 将对应的页迁移到 device。
> 因此，迁移页在 kernel 运行时进行，迁移时间会被计入运行时间。这可能导致新 GPU 的运行时间反而长于旧 GPU。
>
> Pascal 起，程序可以用`cudaMemAdvise()`引导驱动迁移内存，用`cudaMemPrefetchAsync()`显式迁移内存。（见[这里](https://developer.nvidia.com/blog/beyond-gpu-memory-limits-unified-memory-pascal/)）

内存页迁移会影响运行时间。可通过以下方式减少页迁移对运行时间测试的影响：

- 将数据初始化从 CPU 移动到另一个 kernel 中（即 GPU 中），使数据最初就在 GPU 上。
- 通过 [cudaMemPrefetchAsync](https://developer.nvidia.com/blog/unified-memory-cuda-beginners/#prefetching) 在执行 kernel 前将数据预取到 GPU 中。
- 运行 kernel 多次，取最小运行时间。

**并发访问**

自 Pascal 架构起，CPU 和 GPU 可同时访问 managed memory，因为都支持 page fault。但程序需要保证没有 data race（比如通过 cudaDeviceSynchronize 等待后再读取）。

Pascal 和 Volta GPU 支持全局的原子内存操作：可在多个 GPU 上原子地读写值。

> 在 Pascal 架构之前的 GPU，如果 GPU 的 compute capability 低于6.0，则无法同时在 CPU 和 GPU 上访问 managed memory，因为硬件不支持 page fault、难以保证一致性，如果同时访问会导致 segment fault。



### Pinned Memory

Pinned memory（也称为 page-locked memory, pMem, non-pageable, non-swappable）是一种不能被操作系统分页 (swapped out, paged) 的内存。这种内存保存在物理内存中，它的一个显著特性就是不会被操作系统的虚拟内存管理机制移动到磁盘上的交换空间 (swap space)。在某些高性能计算和数据传输场景中很有用，比如 GPU 编程（CUDA 提供了对 pinned memory 的支持）。
因为 pinned memory 不会被分页出内存，因此其物理内存地址是固定的。这使得在进行 DMA（直接内存访问）时，数据传输更加高效，因为硬件可以直接从已知地址进行操作。

优点：

- device 可直接访问 pMem 内存，可显著提高数据在 host 和 device 之间的传输速度。通常情况下，数据需要被拷贝到一个临时的 pMem，然后再传输到 GPU，但如果一开始数据就在 pMem 中，这个过程就可以省去，从而加速传输。驱动会记录 pMem 的虚拟地址范围。
- cuda 不能异步传输 paged 内存(?)中的数据，只有保证数据始终在内存中，即是 pMem 才可异步传输，允许 H2D/D2H/kernel exec 之间并发。
  使用 pageable 内存与 GPU 传递数据可能很影响性能？（可在 nsys - cuda HW - show in events view 中确定）
- 某些 GPU 可将 pMem 映射到 GPU 上的地址空间，消除 host device 间的拷贝（见 *Guide - Mapped Memory*）。

缺点：

- 内存容量限制：pMem 不能被分页，其数量受到物理内存的限制，是稀缺的 os 资源。使用过多的 pMem 会减少可供操作系统和其他应用程序使用的内存、影响系统性能。
- 内存分配时间：分配和释放 pMem 的时间比普通的分页内存更长，也取决于 os 可用资源。

因此不能滥用，适合用于 host 和 device 间频繁交换数据的地方。

使用 cudaMallocHost 和 cudaHostAlloc 分配 pMem（malloc 分配的是 non-pinned memory）。
前者是最初的 API，后者是引入其它功能后新加的 API，区别在于后者可指定 flag 实现更多功能。
cudaHostAlloc 可指定的 flag（互相独立，即可同时指定）：

- cudaHostAllocDefault：默认行为，与 cudaMallocHost 一致。
- cudaHostAllocPortable：分配的内存允许所有 cuda ctx 使用，而不只是执行分配的 ctx。
- cudaHostAllocMapped：将分配映射到 cuda 地址空间。可通过 cudaHostGetDevicePointer 获取该内存在 device 内存上的指针。
- cudaHostAllocWriteCombined：分配 write-combined (WC) memory。在某些系统配置中 WC memory 在 PCI Express bus 上传输会更快，但在大多数 CPU 上的无法高效读取。适用于通过映射 pMem 或 H2D 传输来被 CPU 写、device 读的 buffer。

> pMem 可以实现真正的异步行为？比如拷贝和计算可异步、同时进行？
>
> 如果在分配时 pMem 时指定 cudaHostAllocMapped，则分配的内存会被映射到 GPU 地址空间？此时 GPU 可以直接访问 pMem。
> 在某些条件下（只要支持 unified addressing？）不指定该 flag（使用 cudaHostAllocDefault）也会进行映射 (Automatic Mapping)？

> All host memory allocated through all devices using cudaMallocHost() and cudaHostAlloc() is always directly accessible from all devices that support unified addressing. This is the case regardless of whether or not the flags cudaHostAllocPortable and cudaHostAllocMapped are specified.

因此 pMem 一般可以同时在 device 和 host 上访问而不需拷贝，所以也称为 zero-copy。
但在 device 上的访问速度不如 GPU 本地内存，所以通常还是会拷贝到 GPU。



###  总线

PCIe 连接 GPU L2 cache 和 host、网卡， NVLink 两两连接多个 GPU（但并非所有 GPU 对之间都有直接连接）。





### **Stream**

stream 是独立执行的任务队列（一系列 kernel 执行、copy 等其它命令），用来管理一组并行执行的线程，与特定的线程块关联。
所有用 cuda 在 GPU 上启动的任务都会在一个 stream 上执行（可能是隐式的默认 stream，也可以显式指定）。如果要并行执行需要手动创建并指定 stream。

stream 内的任务可能有依赖关系，但 stream 之间的一定没有。
stream 内的会按序执行；不同 stream 间的任务可以并行执行，以提高 GPU 利用率和 warp occupancy（但仅仅是可以，需要满足 gpu 未被某个 stream 占满等其它要求）；某个 stream 在做内存传输 (h2d/d2h) 时，另一个 stream 可执行 kernel 计算。
将独立的任务划分到独立的 stream 是有必要的。

stream 在 kernel execution configuration 的第四个位置。
当不指定 stream 时，效果取决于 nvcc 选项 [--default-stream](https://docs.nvidia.com/cuda/cuda-runtime-api/stream-sync-behavior.html) 或宏`CUDA_API_PER_THREAD_DEFAULT_STREAM`。
legacy default stream 会与相同 CUcontext 中的所有 blocking stream（创建时未指定 cudaStreamNonBlocking）同步。
per-thread default stream 不与任何线程同步（除了 legacy default stream），与显式创建的 stream 类似。

> 为 kernel 指定 stream 一般没有什么影响，除了会在指定 stream 中执行。
> 例外：当调用`device_array.copy_to_host()`时（不带参数），拷贝始终是同步的；当传递一个 stream 参数`device_array.copy_to_host(stream)`时，如果 device_array 不是 pinned 则同步，否则异步拷贝。即如果传递 stream 且是 pinned，则会异步拷贝。

**stream 与 context**

context 是线程间可以共享的全局资源，而 stream 是局部的用于管理执行某个任务的线程的对象。
stream 创建后会与指定 ctx 关联，其中的线程都会在上面执行。stream 间可以通过 ctx 进行同步。

**stream API**

- cudaStreamCreate(cudaStream_t*)：在线程的 current ctx 上初始化一个 stream。如果没有 current ctx，将 primary ctx 设为 current ctx 并初始化（如果没有）（runtime API 的自动处理）。
- cudaStreamSynchronize(cudaStream_t stream)：阻塞直到指定 stream 上的所有任务完成。
- 

**cudaStreamSynchronize**

如果 gpu 尚未执行完且需要等待其结果，那么会调用 StreamSynchronize 等待其完成，可以在 nsys 上看到两种同步：

- cudaStreamSynchronize：runtime API，一般在 H2D 后、D2H 前要手动调用（最开始和结束），以等待数据传输完成或计算完成。
- cuStreamSynchronize：driver API，在执行过程中出现，等待某个耗时较长的 kernel 完成。







### **Concurrent**

> https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

**Concurrent Kernel Execution**

GPU 可以并发执行多个 kernel，最多可同时执行的 kernel 数取决于计算能力（见 [Table 21](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#features-and-technical-specifications-technical-specifications-per-compute-capability)）。

同一 ctx 中不同 stream 的 kernel 可并发执行；不同 ctx 间的 kernel 不能并发执行 (concurrently)：类似于 CPU 时间片轮转调度，GPU 会为每个 cuda context 分配一定时间片，在每个时间片内，GPU 会执行该 ctx 的任务，然后 switch ctx 切换到下一个 ctx。
（具体见 *MPS - 3.1 Background*）

> 因为不同进程使用不同 ctx，所以进程间不能并发执行，除非通过 MPS。
> 这种调度方式确保了所有进程都能公平地使用 GPU 资源。
>
> 时间片本身应该足够长 来避免 ctx switch 的开销影响性能（在 kernel 执行时占比大）。



**Overlap of Data Transfer and Kernel Execution** / **Concurrent Data Transfers**

H2D/D2H 与 kernel 执行可以并发执行（需要 GPU 的 device property `asyncEngineCount`>0）。
H2D 与 D2H 之间也可并发执行（需要 GPU 的 `asyncEngineCount`==2）。
上面涉及的 host memory 必须是 pin mem。







---

## GPU

> https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html
>
> 各 GPU *计算能力* (*compute capability*)：https://developer.nvidia.com/cuda-gpus#compute
> A10：sm_86
>
> 部分硬件指标：https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#features-and-technical-specifications-technical-specifications-per-compute-capability

**架构**

> 各架构整体：https://zhuanlan.zhihu.com/p/394352476

1. Tesla (SM1.x)
2. Fermi (SM2.x)
3. Kepler (SM3.x)
4. Maxwell (SM4.x)
5. Pascal (SM5.x)
6. Volta (SM6.x)
7. Turing (SM7.x)
8. Ampere (SM8.x)
9. Ada Lovelace (SM8.9)
10. Hopper (SM9.x)
11. Blackwell (SM10~12.x)



**基础**

> 一般说的 GPU 计算并不是纯粹由 GPU 完成的，而是由 CPU 调度、GPU 计算共同完成的异构计算任务。
> 其中：CPU + 内存 被称为 Host (主机)，GPU + 显存 被称为 Device (设备)。

流处理器 (SP, streaming processor)：最基本的运算单元。指令和任务都是在 SP 上执行。
SP 分为 cuda core 和 tensor core，cuda core 支持运算的类型固定，tensor core 可支持混合精度计算且对特定矩乘有硬件优化，由驱动决定 SM 上的线程是在哪些 SP 上执行。

流式多处理器 (SM, streaming multiprocessors)：多个 SP 和其它资源组成一个 SM（类似多核 CPU 的一个 CPU 核）。
资源包括：warp scheduler、register file (寄存器组)、shared memory/L1 cache、dispatch unit、load/store unit 等。这些资源有限，由 SM 上的所有 thread 共享。
GPU 就是 SM 阵列，包含多个 SM 和许多 SP，由架构和型号决定。

GPU 是数据并行，由每个 thread 执行不同数据的计算（任务是相同的）。
每个 thread 都有自己的物理寄存器组，因此切换 warp 时无需恢复上下文。

**SIMT**

CUDA 是*单指令多线程* (SIMT) 架构，与 SIMD 类似，更灵活、但效率略低。
二者都通过将同样的指令广播给多个执行单元来实现并行。主要的不同点是：SIMD 要求所有的 vector element 在一个统一的同步组里同步执行，而 SIMT 允许线程在一个 warp 中独立执行；SIMT 中的每个 thread 拥有自己的 instruction address counter (PC)、状态寄存器和独立的执行路径（可选）。

kernel 按 SIMT 执行，即线程会用不同数据执行相同指令。

**索引地址寄存器**

每个线程有自己在 block 内的索引地址寄存器`SR_TID.X, SR_TID.Y, SR_TID.Z`（对应 threadIdx 的 x、y、z 分量）。
如果需要获得这些值，可以用`S2R R0, SR_TID.X`这种指令。

**predicate**

Predicate 是1位的 bool 谓词，每线程有8个, SASS里用 P0~P7 表示，其中 P7=PT 始终为 true，`@PT`为默认谓词。
Predicate 通常是一些 bool 运算（比如大于、不等于）的输出，用作指令的谓词或操作数。
CUDA 的每个汇编指令都可以用 Predicate 来控制是否真正运行，形式为`@!P0 BRA 0xc40`。这里`@!P0`表示 P0 为假时这行才生效，`!`代表取反。

在指令中，Predicate 由4位编码：3位为索引 (0~7)，1位表示是否取反。

Predicate 与直接 branch 跳转的优点为可以避免 warp divergence，而且开销相比 branch 指令更小（branch 的延迟一般较高，还涉及到指令 Cache 和内部 pipeline 连续性的问题）。
但是，即使 Predicate 为否，这个指令的运行开销也不会被省略，只是指令不写回结果。但由于同一 warp 的线程同时只能发射相同的指令，所以这样也没有影响，反而少了跳转的开销。



### bank conflict

> 此外还有 *register bank conflict*。

为了提高带宽，**共享内存**在物理上被分为 32 个（等于 wrap size）同样宽度、可同时访问的 bank，每个 bank 中的内存地址可以从 0 开始编号。
除了 kepler 架构中每个 bank 的宽度是 8B，其它架构中每个 bank 的宽度都是 4B。
对于 bank 为 4B 宽度的架构，内存上连续的 128B 由 32 个 bank 上的同一位置的 4B 组成，可以并行访问（类似 CPU 的内存，内存带宽的 64B 由 8 个 8B 的 bank 组成）。

当同一个 wrap 中的不同线程并行访问一个 bank 中的不同地址时，这些访问必须被串行处理，即会发生 bank conflict，大大降低内存带宽。
当同一个 wrap 中的不同线程并行访问一个 bank 中的相同地址时，会发生广播、将数据一次传给所有线程，不会发生冲突。

> 在一个 wrap 内对同一 bank 的 n 个地址同时访问将导致 n 次内存事务，称为发生了 n 路 bank conflict。
>
> 不同 wrap 的线程之间不存在 bank 冲突。

通常可以通过改变共享内存数组大小来减少 bank conflict。



### memory hierarchy

整体上，每个 SM 有自己的 L1 cache，多个 SM 共享 on-chip L2 cache，然后 L2 与 DRAM (GPU mem) 相连。

**内存**

> 具体划分可见下 *Turing 内存架构*。

按照存储功能，GPU 内存可以分为：全局内存 (global memory)、局部内存 (local memory)、常量内存 (constant memory)、共享内存 (shared memory)、寄存器 (register)、L1/L2 缓存等。
其中全局内存、局部内存、常量内存都是片下内存 (off-chip)，访问速度一样（较慢），储存在 HBM 上，只是访问方式与可见性不同。

- 全局内存：能被 GPU 的所有线程访问，全局共享。跟 CPU 架构一样，运算单元不能直接使用全局内存的数据，需要经过 cache。HBM 的大部分都用作全局内存。
- 局部内存：每个线程独享的内存资源，线程之间不可以相互访问。
  主要是用来应对寄存器不足时的场景，即在线程申请的变量超过可用的寄存器大小时 (register spill)，nvcc 会将一部分数据放到片下内存里，或在内存中暂存寄存器的值。
  它不是线程自己动态申请的资源，而是整个 kernel 启动时为每个线程分配好的固定大小的资源。大小由编译器决定，运行过程中不能改变。
- 常量内存 (constant memory)：只读内存。会通过特殊的 L1.5 常量缓存 (constant cache) 进行缓存读取，比全局内存快，但依然比片上内存慢。

> **常量内存**
>
> 保存的常量包括：`__constant__` 数据，kernel 调用参数，立即数。
> 主要解决一个 warp scheduler 内多个线程访问相同数据时速度太慢的问题。假设所有线程都需要访问一个 const 的常量，在存储介质上 const 的数据只保存了一份，而内存的物理读取方式决定了多个线程不能在同一时刻读取到该变量，只能串行读取影响并行效率。
> 常量内存支持硬件 broadcasting：当一个 wrap 内的多个线程访问相同地址时，常量内存可将数据同时发送给所有线程；当多个线程访问不同地址时，访问依然会被串行化。

其它内存是 GPU 的片上内存 (on-chip)，都是 SRAM，比片下内存更快。

- L1 cache：每个 SM 有自己的 L1 cache，由该 SM 的 cuda cores 共享。
- L1.5 constant cache：constant cache 被分为 L1, L1.5, L2 三部分。
  每个 SM 有自己的 L1.5 cache，速度介于 L1 与 L2 之间，用于缓存常量内存中的数据。
  在 Pascal 之前还有 L1.5 instruction cache。
- L2 cache：所有 SM（整个 GPU）共享 L2 cache，用于缓存 GPU 上的 DRAM（显存）。
  L2 data cache、L2 instruction cache、L2 constant cache 通常被合并为一个更大的 L2 cache。
- 共享内存 (shared memory)：在一个线程块内各线程能共同访问的内存。是一个小容量的 cache，主要缓存一些需要反复读写的数据。
  共享内存的位置与速度与 L1 接近，区别在于共享内存的控制与生命周期管理与 L1 不同：共享内存受用户控制，L1 受系统控制。共享内存更利于线程块之间数据交互。
- 寄存器：线程能独立访问的资源，用来存储线程的暂存数据。访问最快，但容量较小，而且要被许多线程均分？

此外，在 Volta、Turing 架构中：

- L0 cache：每个 processing block 即每个 wrap 有自己的 L0 指令 cache。
- L1 cache 和 shared memory 被合并为一个更大的  L1 data cache/shared memory（Maxwell 和 Pascal 中是分开的，但更早的 Kepler 是合并的）：This design reduces the cache hit latency and improves the L1 bandwidth。

> https://forums.developer.nvidia.com/t/when-will-we-want-to-use-l1/303566/6
>
> 一个 kernel 可以选择只用 L1，或只用 shared memory，或两者都不用。
>
> - shared memory 能更好的控制数据何时进入和离开缓存；也能控制每个线程访问不同的 bank，减少 coalescing requirements？
> - L1 使用简单，适合难以预测哪些数据会被复用，或情况比较复杂的时候。比如：不同 warp 访问数据的时机无法预测；working set 比 shared memory 更大；程序瓶颈不是访存；程序不需要重复访问数据。
>
> L1 命中率为 0（根本没访问）的原因可能有两种：
>
> 1. 仅使用 shared memory 可能不会被视作 L1 hit。
> 2. 使用 `ld.cg` 直接从 cache at global level（L2 及以下）加载数据，绕过 L1。

 **Turing 内存架构**

> 具体可见 [Dissecting the NVidia Turing T4 GPU via Microbenchmarking](https://arxiv.org/pdf/1903.07486) Chapter 3 Memory hierarchy；每部分的大小和访问周期见 Table 3.1。

以 T4 为例，每个 SM 被划分为 4 个 *processing blocks*，每个处理块有 1 个专门的 warp scheduler 和 dispatch unit。同一个 wrap 的指令会被分到同一个 processing block 中，且只能访问该 block 中的处理单元。
wrap 到 processing block（及 scheduler）的映射很简单：block_id = wrap_id % 4。

因此要充分利用一个 SM，一个 thread block 中的线程数量至少需要是 4 个 wrap（128 个线程）。

**data rate** 与 **speed**

内存数据速率 (data rate) 和内存速度 (speed) 都是传输速度，只是单位不同：速率是 bit (bps)，速度是 bytes (Hz, Bps)，速率 = 速度*8。如：3060 Ti，`rate = 14Gbps = speed * 8 = 1750 MHz * 8`。

**内存带宽**

带宽就是 数据速率（可以视作一条数据线上的速率）* 内存接口（位宽）。
如果位宽为 256 位，单位为 Bps，则 `bandwidth = rate * 256 / 8 = speed * 256`。

> 测内存带宽：https://github.com/NVIDIA/cuda-samples/blob/v11.8/Samples/1_Utilities/bandwidthTest/README.md（make 然后运行即可。结果好像不太稳定）
>
> H2D、D2H、D2D **之间**可以并行，但同类之间需要串行。

A10 带宽：

```sh
 Device 0: NVIDIA A10
 Quick Mode

 Host to Device Bandwidth, 1 Device(s)
 PINNED Memory Transfers
   Transfer Size (Bytes)	Bandwidth(GB/s)
   32000000			25.2

 Device to Host Bandwidth, 1 Device(s)
 PINNED Memory Transfers
   Transfer Size (Bytes)	Bandwidth(GB/s)
   32000000			26.3

 Device to Device Bandwidth, 1 Device(s)
 PINNED Memory Transfers
   Transfer Size (Bytes)	Bandwidth(GB/s)
   32000000			467.6
```



### register

**Register** / **GPR**

通用寄存器 (General Perpose Register, GPR) 有时也直接叫寄存器 (Register)。GPR 通常按个算，一个是32bit，在CUDA的SASS汇编里一般写成 R0，R123 这种格式。
每个线程使用的具体 GPR 数目是编译器根据需要进行配置的。每个 kernel 的所有线程都保有相同数目的 GPR。
最近几代架构单线程最大可用数目是255，因为指令集里 GPR 编码为8位，且 R255=RZ 被用来做恒零的输入，或当输出时表示抛弃输出。

GPU 的 GPR 实际来自于 SRAM 组成的一大块 Register File，每个线程可以分得其中的一部分。一旦线程创建后，物理上的单个 GPR 和线程里的 R0、R1 等就建立了一一对应关系，不再改变，直到退出。

> Turing 有 256 个 regular registers（255 个 general-purpose registers (R0–R254) 和 Zero Register (RZ)）和 64 个 uniform registers。同一个 kernel 最多只能使用 256 个寄存器。

**register file**, **register bank conflict**

以 Turing 和 Volta 为例，每个 processing block 有一个包含 16384 个 32 位元素的寄存器文件，线程可见的逻辑寄存器就是该寄存器文件上第 8k 到 8k+7 个元素的不同位置（对 wrap 来说，就是 32\*8k 到 32\*8k+255 个元素的不同位置）。

每个寄存器文件由 2 个 bank 组成，每个 bank 有 2 个 32 位端口。每个寄存器会根据它的名字 % 2 决定它位于哪个 bank（如 R99 位于 bank 1）。
在一个时钟周期内，每个 32 位端口只能满足一个 32 位读，因此如果某个指令包括 3 个及更多的操作数，且至少有 3 个的源寄存器位于同一个双端口 bank 上，那么就会发生 *register bank conflict，*导致执行时 stall。

以包含三个操作数的 FFMA (single-precision floating-point fused multiply-and-add) 为例：

- FFMA R6, R98, R99, RX 始终不会发生 bank conflict，因为 R98、R99 位于不同 bank（目的寄存器 R6 没有影响）。
- FFMA R6, R98, R100, RX 会在 X 为偶数时发生 bank conflict，因为它们都位于 bank 0。

通过仔细分配寄存器，可以减少 bank conflict。

> 在 Volta 前的架构，寄存器文件为 4 个单端口 bank，因此要注意避免有两个寄存器映射到同一个 bank。



**Uniform Registers**

为了提高 main datapath  (主数据路径？可处理浮点) 的计算吞吐，Turing 引入了一个可以与 main datapath 并行进行的独立的 uniform datapath（但只能处理整数）。

uniform datapath 主要用来优化计算密集的数组运算，它们的 main datapath 中几乎全是浮点指令（比如 FFMA, HMMA），但也有少量的整数运算（比如更新数组下标、循环变量、循环指针、数组下标检查），这些少量的整数运算会打乱 main datapath（不能形成纯粹的 FFMA 序列），影响计算吞吐。
Turing 中，编译器可以选择使用 uniform datapath instructions 将整数运算移到 uniform datapath 中执行。
常规指令可以访问 regular 和 uniform registers，而 uniform datapath 指令几乎只能访问 uniform registers？

> Turing 有 64 个 uniform registers：Uniform Zero Register (URZ) 和 63 个 general-purpose uniform registers (UR0–UR62)。





### scheduling hierarchy

> [Dissecting the CUDA scheduling hierarchy](https://conferences.computer.org/cpsiot/pdfs/RTAS2020-4uXAu5nqG7QNiz5wFYyfj6/549900a210/549900a210.pdf)
>
> https://zhuanlan.zhihu.com/p/713114525





**stream scheduler**

> FIFO：同一流中的操作按FIFO顺序执行，即先提交的先执行。
> 流隔离：CUDA流与单个应用程序相关联，不同应用程序的流互不干扰。例如，如果应用程序A0正在运行，则应用程序A1的流不会干扰A0。 并行执行：不同流中的操作可以并行执行，但同一流中的操作必须顺序执行。
> 流优先级：从Maxwell GPU架构（例如Jetson TX1嵌入式板）开始，CUDA提供了一个运行时函数调用，用于为流分配优先级。
> 当前所有测试过的GPU架构（包括Maxwell、Pascal、Volta和Turing）仅支持两个离散的优先级（高和低）。如果低优先级流占用了一个SM的所有计算资源，则后来提交到高优先级流上的内核可以抢占当前运行的内核。

**thread block scheduler**

> 寻找空闲SM 映射CUDA 语义所表达的grid/block/thread 结构
> 在所有内核被分配到一个流时，线程块会通过所有可用的SM进行循环分配（Round-Robin，RR），先分配到偶数ID的SM，然后是奇数ID的SM
> 在分配线程块到SM之前，线程块调度器会进行一个占用测试，检查每个SM当前的资源利用情况（线程/warps数量， 寄存器，共享内存），以确定是否可以容纳新的线程块。此测试的目的是确保当前的占用率能够满足新内核的需求，从而实现线程块到SM的映射

**warp scheduler**

> 每个SM有若干个warp调度器和相应的指令分发单元。
> 例如，在Pascal架构的GPU中，每个SM有两个warp调度器和两个指令分发单元，每个warp调度器每个时钟周期可以调度两条独立的指令；
> 图灵架构包含4个Warp scheduler 同时对SM 进行了partition，分为4份；
> Maxwell, Pascal, Volta和Turing架构中使用的warp调度策略是松散轮询调度（Loose Round Robin, LRR）。
> 在LRR策略下，warp以轮询方式调度，当一个warp遇到未满足的依赖（如全局内存未命中）时，它会暂停，使下一个准备好的warp被调度。这种调度策略通过足够的ready warp来隐藏内存访问的延迟，并确保warp之间的公平性。
>
> 对于 Turing 每个SM 被划分为4个partition，每个partition 一个scheduler，具体来说：
> 每个SM有4个Warp Scheduler。
> 每个Warp Scheduler可以在同一时间调度32个线程。
> 每个时钟周期内，每个SM可以调度 4*32=128个线程。
> 每个SM最多支持2048个并发线程，但这些线程并不会在同一个时钟周期内同时运行。 因此，对于warp scheduler 来说，多个warp 是通过时分复用的方式实现对scheduler 的占用以及指令的发射，多个warp 间在同一时刻如果处于同一个partition，是串行执行（或者等待前一个warp stall/wait 状态 ），在不同的partion 之间可以实现并行，从编程的角度我们可以利用这一点。
>
> 调度器对warp和SM partition（同时也是调度器id）的映射采用如下简单的方式： scheduler_id = warp_id%4 在同一个block中，warp id 是4 的整数倍的warp 会被调度到同一个partion。 一个极端的情况，假如一个block里只有2个warp要做计算，其余warp直接退出。如果这两个要做计算的warp（称为active的warp）对4同余，那么就会造成因为4个partition负载不均衡而产生可能 50% 的性能损失。







---

## C++ 语法扩展

> https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#c-language-extensions



### Function Execution Space Specifiers

*函数执行空间说明符* 指定一个函数是否是在 host/device 上执行、是否能从 host/device 上调用。

**global**

`__global__`声明函数为核函数 (kernel)：在 device 上执行；可在 host 和 device 上调用。

- kernel 的返回类型只能是 void，如果需要返回值则只能传参指针；不能是成员函数。
- 调用时必须声明 execution configuration。
- kernel 调用是异步的。

global 不能与 device/host 同时声明。

**device**

`__device__`函数为设备函数：只能在 device 上执行；只能在 device 上调用（即只能被 kernel 或其它 device 函数调用）。

**host**

`__host__`函数为主机函数：只能在 host 上执行和调用。当函数不指定任何说明符时会被视作 host。

host 和 device 可同时声明，此时函数会为 host 和 device 分别编译？

**noinline**, **forceinline**

编译器会内联任何合适的 device 函数。

`__noinline__`用来建议编译器不要内联某函数。
 `__forceinline__`用来强制编译器内联某函数。
两者不能一起使用；不能用于 inline 函数。

`__inline_hint__`用来建议编译器内联某函数。主要用于 LTO。

### Variable Memory Space Specifiers

> TODO：https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#variable-memory-space-specifiers

*变量内存空间说明符* 指定一个变量在 device 上的内存空间。

device 代码中 没有任何内存空间说明符修饰的自动存储期变量 通常位于寄存器。在某些情况编译器也会把它放到内存，这可能对性能产生影响（见 *Device Memory Accesses*）。













---

## 其它



**nvidia-smi**

```sh
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.14              Driver Version: 550.54.14      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L20                     On  |   00000000:21:00.0 Off |                    0 |
| N/A   52C    P0             94W /  350W |    8688MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA L20                     On  |   00000000:41:00.0 Off |                    0 |
| N/A   49C    P0             99W /  350W |    8686MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                        
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
+-----------------------------------------------------------------------------------------+
```

输出包括两部分：GPU 的状态；当前在使用 GPU 的进程的状态。
第一部分包括：

- Perf：GPU 当前的性能状态 (performance state)，从最高到最低性能分为 P0~P12。性能状态决定了 GPU 的功耗和性能平衡。不同的性能状态对应不同的功耗和频率设置，从而影响 GPU 的性能和能效。
- Persistence-M：Persistence Mode flag。On 代表即使没有应用在使用 GPU，nvidia driver 也持续运行一个守护进程 (remain loaded / persist)，确保 GPU 始终处于活动状态。这可以降低程序的 driver 加载（启动）延迟。
- Pwr: Usage/Cap：GPU 当前功率 / 最大功率。
- Bus-Id：GPU PCI bus id，格式为`domain:bus:device.function`。
- Disp.A：Display Active flag，表示 GPU 是否正用于显示输出，如连接了显示器或其它显示设备。
- Volatile Uncorr. ECC：显存中检测到的未校正错误的数量。如果非 0 一般是硬件问题。
- GPU-Util：一段时间内有多长时间至少有一个 kernel 在使用 GPU。
- Compute M.：GPU 的计算模式 (Compute Mode)，代表 GPU 是否被配置为允许多个进程或线程同时访问，还是仅允许一个进程独占访问。见 *MPS - Compute Mode*。

**gpu util**

nvidia-smi 中的 gpu util 代表一段时间内有多长时间至少有一个 kernel 在执行。它仅仅反映 gpu **完全**空闲的程度，无法反映 gpu 有多忙、有多少 SM 被使用。

> 因为这是一段时间的统计，所以虽然多个 ctx 或多个进程无法并发执行（不使用 MPS 的话只是并行），但从 gpu util 上看起来是并发的，比如：一个进程是 30%，三个进程可以达到 90%。







### 汇编

CUDA的汇编语言分为两种，一种是 Parallel Thread Execution (PTX)，另一种是 Streaming Assembly (SASS)。
PTX 是一种中间语言，可以在不同的 GPU 上运行；SASS 是一种特定的汇编语言，只能在特定的 GPU 上运行。











---

## 性能测试

**性能分析工具**

[Nsight System](https://developer.nvidia.com/nsight-systems)、Nsight Compute、Nsight VS Code

nsight system 可以获取系统级的各项信息。
nsight compute 可以深入分析某个 cuda kernel。
nvprof 已被前两者取代。

**带宽计算**

> https://developer.nvidia.com/blog/how-implement-performance-metrics-cuda-cc/








---

## end



