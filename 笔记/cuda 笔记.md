# cuda

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
>



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





### GPU

> 一般说的 GPU 计算并不是纯粹由 GPU 完成的，而是由 CPU 调度、GPU 计算共同完成的异构计算任务。
> 其中：CPU + 内存 被称为 Host (主机)，GPU + 显存 被称为 Device (设备)。

流处理器 (SP, streaming processor)：最基本的运算单元 (cuda core)。指令和任务都是在 SP 上执行。

流式多处理器 (SM, streaming multiprocessors)：多个 SP 和其它资源组成一个 SM（类似一个 CPU 核）。
资源包括：warp scheduler、register file (寄存器组)、shared memory/L1 cache、dispatch unit、load/store unit 等。这些资源有限，由 SM 上的所有 thread 共享。
GPU 就是 SM 阵列，包含多个 SM 和许多 SP，由架构和型号决定。

GPU 是数据并行，由每个 thread 执行不同数据的计算（任务是相同的）。
每个 thread 都有自己的物理寄存器组，因此切换 warp 时无需恢复上下文。







### Grid, Block, Thread

> thread 对应 SP (cuda core)，是基本的运算单元。
> thread block 对应 SM，包含许多运算单元。
> grid 对应 GPU (device)，包含可分配到不同 SM 上的多个 block。

为了便于编程和管理线程，cuda 引入了 网格 (grid)、线程块 (thread block)、线程 (thead)、线程束 (warp) 四个概念。
执行 kernel 时，其使用的所有 thread 组成了一个 grid，会使用 GPU 上的部分计算单元。每个 grid 包含若干可并行执行的 block，每个 block 内包含若干 thread。

同一 grid 中的所有线程共享全局内存空间。

同一个 block 中的 thread 只会在同一个 SM 中并行执行，它们可以通过同步或共享内存通信进行协作（不同块之间的 thread 无法协作）。
在执行 kernel、启动 grid 时，该 grid 的 block 就会被分配到可用的 SM 上执行。
一个 block 只会由一个 SM 调度，且一旦被分配好 SM，就会一直在其中执行。不同 block 可由可用的不同 SM 执行。

> GPU 可以创建的 grid、block 数量取决于其计算能力。
>
> grid 中的 block 可以以一维、二维、三维三种组织方式排列；block 中的 thread 也是如此。

`cudaThreadSynchronize()`可同步同一个 block 的所有 thread（均在此阻塞直到全部到达）。

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





### Warp

线程束 (warp) 是 cuda GPU 调度和执行的基本单元（是 SM 执行的基本单元）（是 cuda 软件的概念，但是与硬件直接相关）。
目前 cuda 一个 warp 的大小 (warpSize) 为32个线程（即一个 SM 上只有32个线程能同时执行）。在同一个 warp 中的线程能以任意顺序执行，并会以不同的数据资源执行相同的指令 (SIMT)。

当一个 block 被调度到某个 SM 时，block 中的 thread 会被划分为多个 warp 分别被调度执行，每个 warp 中的 thread 会执行相同指令，但拥有独立的 PC、寄存器和数据。所以 block 的大小（三维总大小）最好是 warpSize (32) 的整数倍，以避免最后一个 warp 中包含无用线程。
在软件 (编程) 角度，block 是线程的集合（可以是一维/二维/三维）；在硬件角度，block 是 warp 的集合（一维）。

> 一个 warp 需要占用一个 SM 运行，多个 warp 需要轮流进入 SM 执行，由 SM 的硬件 warp scheduler 负责调度。
> 所以任意时刻 GPU 上的活跃线程最多只有 SM 数量 * 32 个，不是所有线程都在物理上同时执行（只是逻辑上并行）。

当一个 warp 空闲时，SM 就可以调度驻留在该 SM 中的另一个可用 warp。
在并发的 warp 之间切换没有什么代价，因为硬件资源早就被分配到所有的 thread 和 block，新调度的 warp 的状态已经存储在 SM 中了。这不同于 CPU：CPU 切换线程需要保存/恢复上下文；而 GPU 为每个 thread 提供物理寄存器，无需保存/恢复上下文。

**warp 分支**

一个 warp 中的线程会执行相同指令。如果线程执行的代码中出现分支，则需要分别顺序执行每个分支路径：对于单个分支，如果存在某个线程求值为 true，则并行执行为 true 的线程，其它线程等待 (stall)；执行完  true 分支后，所有为 false 的线程再执行，其它线程等待。
因此要提高并行性，应尽量避免同一 warp 中的线程进入不同分支。





### 确定 Warp, Block 大小

通常先确定 block 大小（每维线程数量），然后根据块大小和数据规模计算 warp 大小（每维块数量）。

block 的大小通常需要考虑内核的性能特性和 GPU 的资源限制（比如寄存器和共享内存的大小）。

- 应尽量避免使用小的线程块，因为无法充分利用硬件资源。
- CPU 与 GPU 中均以行为方式访问内存，因此应尽量保证相邻内存只由同一 block（即同一 SM）读写。







### SIMT

CUDA 是*单指令多线程* (SIMT) 架构，与 SIMD 类似，更灵活、但效率略低。
二者都通过将同样的指令广播给多个执行单元来实现并行。主要的不同点是：SIMD 要求所有的 vector element 在一个统一的同步组里同步执行，而 SIMT 允许线程在一个 warp 中独立执行；SIMT 中的每个 thread 拥有自己的 instruction address counter (PC)、状态寄存器和独立的执行路径（可选）。

kernel 按 SIMT 执行，即线程会用不同数据执行相同指令。







### kernel

`__global__`修饰的函数为核函数。

kernel 的返回类型只能是 void，如果需要返回值则只能传参指针。
kernel 不能是成员函数。

> `__device__`修饰的函数为设备函数，只能被核函数或其它 device 函数调用，只能在 device 中执行。
>
> 类似的`__host__`修饰的函数为主机函数，只能由 host 调用和执行，一般不用。

**执行 kernel**

调用：`kernel_name<<<grid_size, block_size>>>(args)`。

`<<<grid_size, block_size>>>`称为执行配置 (execution configuration)，告诉 CUDA runtime 在该 grid 中使用多少个 block 和 thread 及组织形式。
grid_size 与 block_size 可以是 dim3 类型的结构体（二维或三维）或一个 unsigned int（一维）。

```cpp
dim3 grid_size(2, 3);
dim3 grid_size(2, 2, 3);
```

执行一个 kernel 称为 launch。
执行 kernel 默认不会阻塞 CPU，可使用`cudaDeviceSynchronize()`阻塞直到 device (GPU) 完成。

**编写 kernel**

kernel 主要有两部分：确定数据与线程的对应；处理对应数据。









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

例：

```cpp
// 在 CPU 上初始化
double *h_x = (double*) malloc(M);
for (int n = 0; n < N; ++n) {
    h_x[n] = a;
}
// 分配 GPU 内存、拷贝
double *d_x;
cudaMalloc((void **)&d_x, sizeof(double) * N);
cudaMemcpy(d_x, h_x, M, cudaMemcpyHostToDevice);
```









### Unified Memory

Unified Memory 是 CPU 和 GPU 都可以访问的内存（也称为 managed memory）。

使用`cudaMallocManaged(void**, uint)`分配统一内存，使用`cudaFree(void*)`释放统一内存。
与 malloc、free 类似，而不是 new、delete。

```cpp
// Allocate Unified Memory (accessible from CPU or GPU)
float *x;
cudaMallocManaged(&x, N * sizeof(float));
cudaFree(x);
```

> 当访问 unified memory 中的数据时（称为 CUDA *managed* data），cuda 软件和/或硬件会将内存页迁移到正在访问的处理器 (CPU/GPU) 内存中 (migration)。
> 内存迁移时间可在 Unified Memory profiling result 中看到。
>
> 在 Pascal 架构之前的 GPU（如 K80），调用 cudaMallocManaged 会立刻在 GPU 上分配指定数量的内存，并为分配涉及的页创建页表条目。当在 CPU 上访问这些完全位于 GPU 的内存页时，会触发 page fault，然后 GPU 驱动会将访问的页从 device 迁移到 CPU 内存 (device to host)。
> 在 launch kernel 时，由于这些旧的 GPU 没有 page fault 机制，因此需要将先前迁移到 CPU 内存或其它 GPU 中的所有页迁移回来 (host to device)，不管实际是否会用到。因此每次启动 kernel 都可能有不必要的开销。
> 因此，迁移页在 kernel 运行前完成，迁移时间不会被计入运行时间。
>
> 自 Pascal 架构起，调用 cudaMallocManaged 可能不会立刻分配 managed 内存和创建页表条目，而是在访问或预取时分配；GPU 支持49位虚拟地址和按需的内存迁移。
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





---

## 语法

### 常用









---

## 性能测试

**性能分析工具**

Nsight System、Nsight Compute、Nsight VS Code

**带宽计算**

> https://developer.nvidia.com/blog/how-implement-performance-metrics-cuda-cc/





### nvprof

`nvprof <program>`













---

## end



