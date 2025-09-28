# cuda driver API

Tags: 笔记

---

[TOC]

---



> https://docs.nvidia.com/cuda/cuda-driver-api/index.html




---

## 基础





**cuda driver API**, **cuda runtime API**

> https://docs.nvidia.com/cuda/cuda-runtime-api/driver-vs-runtime-api.html#driver-vs-runtime-api

都是 NVIDIA 提供的用于开发 CUDA 程序的接口，但有所区别：

- CUDA Runtime API：目的是为了简化 CUDA 编程，提供更高层次的抽象，使开发者可以更方便地编写和管理 CUDA 代码。一般都是用这类。隐藏了许多底层细节，使代码更加简洁易读。
  - 提供了更高级别的抽象，例如 cudaMalloc 和 cudaMemcpy 用于内存管理，cudaStreamCreate 和 cudaStreamDestroy 用于流控制，cudaEventCreate 和 cudaEventRecord 用于事件同步等。
  - 会隐式处理：初始化 cuda，context 管理，module 管理。
- CUDA Driver API：目的是为了提供对 CUDA 硬件的低层控制，适合需要精细控制硬件资源的应用场景。提供了更多的灵活性和控制能力，但使用起来复杂。
  - 提供了更细粒度的控制，例如 cuCtxCreate 和 cuCtxDestroy 用于上下文管理，cuModuleLoad 和 cuModuleUnload 用于模块加载和卸载，cuLaunchKernel 用于启动内核等。
  - runtime 的 kernel 会在初始化时自动加载并始终保留，而 driver 可以动态加载 module、只将目前需要的保留。
  - 可以获取 device 更细的信息；需要显式初始化 cuda；可以管理 context 和 module。
  - 接口以 cu 开头。

runtime api 就是对 driver api 的封装 (wrapper)，所以两者性能没有差异，只是 runtime 不能提供更细的优化。

> 在编译方面也有区别：runtime API 需要使用 nvida 的编译器进行编译，并且可以将 CUDA kernel 链接到同一个 executable 中。driver API 则完全可以不依赖 nvida 的编译器，可以通过 NVRTC 库来实现对 kernel code 的在线编译，生成 PTX string。

runtime 与 driver 可以混用（见[这里](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#interoperability-between-runtime-and-driver-apis)），但不建议除非真的需要。

**device id** / **gpu id**

为了便于管理，TF 对 gpu 进行了抽象（[代码](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/common_runtime/device/device_id.h)）：

- physical GPU id：物理 gpu id。它不对应用程序（包括 TF）直接可见。
- platform GPU id (visible GPU id)：physical GPU 经过 CUDA_VISIBLE_DEVICES 过滤后的 id（会重新从 0 开始标号），对应用程序（包括 TF）可见，可以用 cuDeviceGet 等获取。
- TF GPU id (virtual GPU id)：TF 生成的暴露给用户程序的 gpu id。允许在一个物理 gpu 上使用多个逻辑 device。







### Context Management

> 相关 API：https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__CTX.html#group__CUDA__CTX
>
> https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#context



**cuda context**

cuda context 保存了控制和使用 device 的所有信息数据，包括：所有分配的 memory 信息，加载的 module（即加载的 kernel 代码？），CPU 和 GPU 之间 unified memory 的 mapping。

cuda ctx 是一个运行时环境，用于执行 CUDA 内核和管理 GPU 资源（内存、流、事件、模块等）。每个上下文都有自己的独立状态，包括内存分配、内核配置等。每个 CUDA 应用程序通常需要至少一个 ctx 来与 GPU 进行交互。

cuda ctx 可以绑定到 host 上的特定线程。同一时刻：每个线程只能有一个 current ctx，可通过`cuCtxSetCurrent`、`cuCtxGetCurrent`切换和获取；一个 ctx 只能被一个线程作为 current ctx。如果需要 ctx 的函数使用了一个非 current 的 ctx 则会返回 `CUDA_ERROR_INVALID_CONTEXT`。

一个线程中创建的上下文只能在该线程中使用，除非显式地切换上下文：使用 cuCtxPushCurrent、cuCtxPopCurrent、cuCtxSetCurrent 可以在不同的线程之间切换当前 CUcontext。

> context 不直接暴露在 runtime API。runtime API 默认使用 device 的 primary context，如果使用 driver API 指定了 current ctx 则使用指定的。
> 即 runtime 下多个线程默认会共享一个 ctx。使用 driver API 创建、切换 ctx 也有很大开销。
>
> 每个 ctx 都有引用计数，可通过 cuCtxCreate、cuCtxAttach 增加，通过 cuCtxDestroy、cuCtxDetach 减少，并在计数为 0 时销毁释放。这使第三方库共享 ctx 很方便。
>
> 每个 ctx 有自己的地址空间，因此不同 ctx 的 CUdeviceptr 指向不同内存地址。
>
> context管理了包括stack memory用于每线程临时变量，stack memory 实际是 global memory，context 内部申请的总显存大小为 SMs \* max thread per SM \* size per thread，因为kernel可能被调度到不同的SM中的物理线程，这样分配保证多个kernel执行时stack memory不冲突，运行时驱动可以动态拓展增加stack memory的总size；用于多device之间同步的cooperative group memory，其作用于cudaLaunchCooperativeKernel()；在多个device上建立页表的显存; 用于临时搬运paged host memory的staging memory，staging memory是pinned host memory，用于src/dst memory来自paged host的cudaMemcpy系列API；还包括用于管理驱动内部同步关系的host/device memory，用作信号量等。module也是按照context进行管理，module包括用户编写CUDA函数的ISA二进制文件也包括驱动内部可能使用到的用户不可见的程序binary，如果同一device创建了多个context，同一份kernel的binary需要被load到不同的context，占用更多显存（其实也有lazy loading的机制）。
>
> ctx 很大（数百 MB），如果要节省显存，需要限制 ctx 数量、限制每个进程可使用的 GPU 数量（单个进程不用创建多个 ctx）。

一个 context 与一个进程类似，所以在 ctx 之间通常会有数据隔离。但两者也有很多不同：

- 从显存可见范围来看：虚拟地址的范围依赖于 CPU 进程，不能在进程之间直接访问，而 ctx 之间可以通过 IPC？

> ctx 不能直接访问其它 ctx 的内存，但 this could be done for example with host-based IPC to pass the address from one process to another, or perhaps a more "manual" method.
>
> The GPU is a collection of multiple independent engines that can run different contexts simultaneously. The two most common engines are the GR (3D + 2D + compute) and the Asynchronous Copy Engine. Each engine can run 1 context at a time. Each engine has a separate page table pointer via the context. On a context switch the TLBs are invalidated.

**CUcontext**

`typedef CUctx_st* CUcontext`：A regular context handle.（这个类型就是一个指针，可以赋值或比较 nullptr）

CUcontext 就是一个 cuda context。

**primary context**

> https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__DRIVER.html

primary context 是一个特殊的 CUDA context，它是 device 的默认 ctx：每个进程在每个 device 上在启动时都会自动创建一个 primary ctx（不需要显式调用 cuCtxCreate，也不能显式销毁；即只能有一个），它在 device 的整个生命周期内始终存在。

可以被多个 host 线程共享，但同其它 ctx 同一时刻只能被一个线程用作 current ctx。

通过`cuDevicePrimaryCtxRetain(CUcontext *pctx, CUdevice dev)` 获取某个 device 上的 primary ctx，通过`cuDevicePrimaryCtxRelease(CUdevice dev)` 释放某个 device 的 primary ctx。它们会更新该 primary ctx 的引用计数，并在计数为 0 时销毁。

相关 driver API：

- cuDevicePrimaryCtxGetState：获取某个 device primary ctx 的 *flag* 和状态（是否 active 即是否是活跃 ctx）。

> 对 runtime API 来说，一个 device 与它的 primary ctx 是等价的。

相关 runtime API：

- cudaInitDevice()：保证 primary ctx 被初始化。
  但 runtime API 会在第一次使用它前自动初始化，所以不需要调用？
- cudaSetDevice()：保证 primary ctx 被初始化，且调用 cuCtxSetCurrent() 将其设为 current ctx。
  如果当前没有 current ctx，则 runtime API 使用 ctx 时会自动将 primary ctx 设为 current 并初始化它，所以不需要调用？
- cudaSetDeviceFlags()：设置（自动或手动）初始化 primary ctx 时的 flag。需要在初始化前调用。
- cudaDeviceReset()：deinitialize 当前 device 上的 primary ctx。它仍然是其它线程的 current ctx。
  deinitialize 之后任意线程上使用它的 runtime API 都会触发对它的 reinitialization。
  因为 primary ctx 是共享的资源，所以只建议在退出或 launch failure 时 reset。

**context 栈**

CUDA 驱动为每个 CPU 线程维护了 context 栈，线程活跃 context (current ctx) 为当前栈顶的 context；同一个 context 可以被进程内所有线程使用。

修改栈顶 context 的 [API](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__CTX.html#group__CUDA__CTX)：

- cuCtxPushCurrent, cuCtxPopCurrent：push/pop。
- cuCtxSetCurrent：相当于 pop + push。
- cuCtxCreate：把新创建的 context 入栈。
- cuCtxDestroy：如果当前线程的栈顶是被销毁的 context 则进行 pop。

注意如果一个 ctx 被放入多个线程的栈中，在某个线程里 destroy，它依然会保留在其它线程 ctx 栈中；并且对于当前线程，如果它不在当前栈顶，也会保留在栈中。之后相关线程必须正确 pop 避免使用它，否则会 CUDA_ERROR_CONTEXT_IS_DESTROYED。

> primary ctx 的 cuDevicePrimaryCtxRetain 和 cuDevicePrimaryCtxRelease 不会对 ctx 栈产生影响。
>
> 一个 ctx 在同一线程中可以被多次入栈，栈中可以保存多个相同 ctx，因此需要用户控制 ctx 出入栈成对使用，且保证调用 destroy 的逻辑正确（有且仅有一次，destroy 后不再使用）。

driver API 和 runtime API 可以混用，*cudaSetDevice* 就是将指定 device 的 primary ctx 绑定到当前线程的 current ctx（放到栈顶），相当于 cuDevicePrimaryCtxRetain（不一定需要） + cuSetCurrentCtx。
runtime API 对 driver API 修改 ctx 栈的操作没有感知，因此可以通过 device API 修改 runtime 当前的使用栈，但要保证逻辑正确。如果只使用 runtime API 开发，primary ctx 其实就是对 Device 的抽象。

**memory**

cudaMalloc/cuMemAlloc 申请的显存和 cudaMallocHost/cuMemAllocHost 申请的 host memory，由当前栈顶的current ctx 管理，其物理位置属于对应 ctx 的 device，但同一 device 创建的所有其它 ctx 都可见。比如：ctx 1 创建的 stream 可以 copy ctx 0 创建的 memory（copy API 不会限制来源）。

如果不同 device 间存在 link (nvlink 或 pcie)，则可通过 cuCtxEnablePeerAccess 允许其它 device 访问 local device memory，即不同 device 创建的 ctx 之间申请的显存也能是相互可见的。

**flag**

可以通过 cuCtxSetFlags、[cuDevicePrimaryCtxSetFlags](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__PRIMARY__CTX.html#group__CUDA__PRIMARY__CTX_1gd779a84f17acdad0d9143d9fe719cfdf) 为 cur ctx / primary ctx 设置 flag。

flag 的低三位 (three LSBs, 3 Least Significant Bit) 用于控制有 cuda ctx 的线程在等待 GPU 返回结果时，如何被 os 调度。scheduling flags 可以设置 8 种中的一个：

- CU_CTX_SCHED_SPIN：自旋，延迟低但占 CPU。
- CU_CTX_SCHED_YIELD：让出 CPU，延迟高但省 CPU。
- CU_CTX_SCHED_BLOCKING_SYNC：在一个同步原语上阻塞该线程。
- CU_CTX_SCHED_AUTO：flag 被设为 0 时的默认方式，用一个启发式的方式自行决定。一般就是：如果进程中活跃的 cuda ctx 数量大于 os 逻辑处理器数量就 yield，否则 spin。
- CU_CTX_LMEM_RESIZE_TO_MAX：让 CUDA 在为某个 kernel 调整 local memory 大小后，不要将本地内存减少到之前的大小。可以避免在启动多个需要大量 local mem 的内核时，要频繁分配和释放本地内存，从而减少内存抖动 (thrashing)。
  该 flag 已 deprecated，现在它是默认行为，且不能被禁用以避免抖动。
- CU_CTX_COREDUMP_ENABLE：如果没通过 cuCoredumpSetAttributeGlobal 或环境变量全局启用 GPU coredump，可以在创建 ctx 设置该 flag 让 cuda 在该 ctx 抛出异常时创建 coredump。
  coredump 输出设置默认来自 global settings，当该 ctx 成为 current ctx 时可以通过 cuCoredumpSetAttribute 设置。
- CU_CTX_USER_COREDUMP_ENABLE：如果没通过 cuCoredumpSetAttributeGlobal 或环境变量全局启用 GPU coredump，可以在创建 ctx 设置该 flag 让 cuda 在数据被写入内核空间的特定 pipe 时创建 coredump。
  在创建该 flag 的 ctx 前必须通过 cuCoredumpSetAttributeGlobal 设置管道名称（如 `/tmp/cuda_coredump_pipe`？），cuda 会监听它并在有写入时触发 coredump。
  设置该 flag 蕴函 CU_CTX_COREDUMP_ENABLE 被设置。coredump 的输出配置也与其一致。
- CU_CTX_SYNC_MEMOPS：确保在该 ctx 中初始化的同步内存操作始终是同步的（同步操作可能导致异步行为，见 *API Synchronization behavior*）。





### 同步 异步



**API Synchronization behavior**

> https://docs.nvidia.com/cuda/cuda-driver-api/api-sync-behavior.html#api-sync-behavior

memcpy 和 memset API 有同步和异步两种形式，异步 API 以 Async 为后缀，但所有这些 API 可能表现出同步行为也可能是异步的（取决于实参）。

> 所有 cuda API 都可能会因为内部资源不可用/竞争等原因导致阻塞或同步。这类行为可能会随版本变化、不能依赖。

- memcpy 行为见 *cuda 笔记 - memcpy* 或文档。
- 对于 memset：异步版本始终是异步的；同步版本只有在目标内存是 pinned host mem 时才是同步的，否则是异步的。
- 所有 kernel launch 相对于 host 都是异步的。





---

## module



> module实际上是一种利用GPU cc的一组class和function，当然这其中也包括我们自己编写的kernel code。nvcc（nvidia cuda compiler）可以输出binary code和一种叫做PTX的中间代码:
>
> Binary code一般分为cubin，也就是只包含特定架构GPU的代码；还有一种是fatbin，包含了支持多种架构的代码；当然，两种binary code都只是包含device code。
>
> 而PTX代码，是在特定架构的汇编语言与C等高级语言中的虚拟抽象层，在运行时通过JIT实时地转化成运行平台支持的bianry code。当然，当GPU的CC（compute capabilities）低于PTX支持的版本时，也会失败的。







---

## 代码

nvcc 默认链接 cuda 运行时库 libcudart (`-lcudart`)。如果要用 driver API 需要链接驱动库 libcuda (`-lcuda`)。

使用 driver API 前需要调用 cuInit(0) 初始化，否则所有 driver API 会返回 CUDA_ERROR_NOT_INITIALIZED。
似乎如果先用 runtime API 就不需要再执行该初始化？（不确定）

runtime API 使用 cudaError_t 作为返回类型，driver API 使用 CUresult。
runtime 可使用 `cudaGetErrorString(cudaError_t)` 输出错误字符串，driver 需使用 `cuGetErrorString(CUresult, const char**)`。

```cpp
#define CUDA_CHECK_ERROR(expr, ...) \
	do { \
		auto err = expr; \
		if (err != CUDA_SUCCESS) { \
			const char* ptr; \
			cuGetErrorString(err, &ptr); \
			COUT("ERROR: ", __VA_ARGS__, "\ninfo: ", ptr); \
			exit(0); \
		} \
	} while (0)
```







---

## end



