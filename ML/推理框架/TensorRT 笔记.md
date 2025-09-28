# TensorRT 笔记

---
[TOC]

---

>https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html
>历史文档：https://docs.nvidia.com/deeplearning/tensorrt/archives/index.html
>
>TRT 10 API：https://docs.nvidia.com/deeplearning/tensorrt/10.8.0/_static/c-api/index.html
>
>TRT 8.6 API：https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-861/operators/docs/index.html
>
>onxx operator：https://github.com/onnx/onnx/blob/main/docs/Operators.md

---
## 基础



**Myelin**

> https://github.com/NVIDIA/TensorRT/issues/2576

myelin 是 TRT 图编译和执行的后端（之一？）。

**engine**

引擎 (Engine) 包含了优化后的神经网络模型及其执行计划。作用是将高层次的神经网络描述转换为高效的低层次计算图，以便在 GPU 上快速执行推理任务。

**构造 engine**

> https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-803/best-practices/index.html#initialize-engine

creating an engine from scratch is an expensive operation. The builder optimizes the given network in various ways, then performs timing tests to choose the highest performance implementation for each layer specific to the actual GPU in the system. As the number of layers in the network increases, the number of possible configurations increases and the time taken to choose the optimal one also increases.

The builder layer timing cache helps to reduce the time taken in the builder phase. The caching should work in all cases and even better than non-caching in some cases, however, there can be cases where turning it off may give you marginally better performance.

构建 engine 主要有以下方式：

1. onnx-tensorrt：利用 `trtexec --onnx` 将 onnx 模型转为 engine（见 *Onnx*）。
2. 用 C++ API 逐层搭建网络，然后生成 engine。
   - 优点：可以精确控制网络中的每一层，避免 onnx 中的冗余结构（但一般差别不大）；后期可以更方便地修改网络中的某一层或加 plugin。
   - 缺点：搭建很麻烦。
3. [torch-TensorRT](https://github.com/pytorch/TensorRT)
4. [torch2trt](https://github.com/NVIDIA-AI-IOT/torch2trt)：遍历 Pytorch 网络，遍历每一个 op 时将其转换为相应的 TensorRT-op。不维护了。

**implicit batch, explicit batch**

> https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#explicit-implicit-batch
>
> TRT 8.6：https://developer.nvidia.com/docs/drive/drive-os/6.0.8.1/public/drive-os-tensorrt/pdf/NVIDIA-TensorRT-8.6.11-API-Reference-for-DRIVE-OS.pdf

虽然文档里说 implicit batch 做不到 reducing across the batch dimension 和 gathering along the batch size dimension，但目前测试虽然 explicit batch 能这样操作，但得不到正确结果（除非实际 batch 始终等于预设 batch size）。

Explicit batch mode erases the limitations - the batch axis is axis 0. A more accurate term for explicit batch would be "batch oblivious", because in this mode, TensorRT attaches no special semantic meaning to the leading axis, except as required by specific operations. Indeed in explicit batch mode there might not even be a batch dimension (such as a network that handles only a single image) or there might be multiple batch dimensions of unrelated lengths (such as comparison of all possible pairs drawn from two batches).

使用 createNetworkV2 和 kEXPLICIT_BATCH 创建一个 explicit batch 的网络。

以下限制应该对 explicit 也生效：
- IReduceLayer：The input must have at least one non-batch dimension. The batch size dimension cannot be reduced.
- ITopKLayer: The K value must be 3840 or less. Only one axis can be searched to find the top K minimum or maximum values; this axis cannot be the batch dimension.



**debug tensors**

>  https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#debug-tensors
>
> 将 tensor 设为 output 来避免某些层的融合：https://zhuanlan.zhihu.com/p/360843851

可以为 tensor 设置 debug 来输出它的值，而不需要将其加到 outputs 里。

设置 debug 后会阻止层融合吗？

**多线程安全**

TRT 只有[少部分操作](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#threading)是线程安全的，其它基本都是线程不安全。





---

## trtexec

> https://docs.nvidia.com/deeplearning/tensorrt/latest/reference/command-line-programs.html



如果输入中存在可变维度，则需在编译时声明动态维度：

```bash
trtexec --onnx=model.onnx \
        --minShapes=input1:1x1,input2:1x300x1024 \
        --optShapes=input1:8x1,input2:8x300x1024 \
        --maxShapes=input1:16x1,input2:16x300x1024
```

运行时可通过 --shapes 指定实际 batch_size：

```sh
trtexec --loadEngine=model.engine \
        --shapes=input1:4x1,input2:4x300x1024
```







---

## C++ 接口

> 简单示例：https://github.com/NVIDIA/trt-samples-for-hackathon-cn/blob/master/cookbook/01-SimpleDemo/TensorRT-8.6/main.cpp

**IRuntime**

Allows a serialized functionally unsafe engine to be deserialized.

主要用 `ICudaEngine* deserializeCudaEngine(void const *blob, std::size_t size)`，从 engine -> IHostMemory 复制一个 engine：

```cpp
auto trt_engine = builder->buildEngineWithConfig(*network, *builder_config);
auto host_mem = TensorRTUniquePtr<nvinfer1::IHostMemory>(trt_engine->serialize(), TensorRTDeleter());
auto runtime = TensorRTUniquePtr<nvinfer1::IRuntime>(
          nvinfer1::createInferRuntime(TensorRTLogger::Instance()), TensorRTDeleter());
// 得到与之前一样的 engine
auto engine = runtime->deserializeCudaEngine(host_mem->data(), host_mem->size());
```





---

## Python 接口

### Onnx

> https://docs.pytorch.org/docs/stable/onnx.html
>



torch.onnx.export 中的输入顺序应与模型的 forward 中参数的顺序一致；input_names 顺序应与输入顺序一致。







---

## plugin

> https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#extending
> https://github.com/NVIDIA/TensorRT/tree/master/plugin
>
> https://oldpan.me/archives/tensorrt-plugin-one-post-get-it



> 如果要添加自己的算子，可以在官方的plugin库里头进行修改添加，然后编译官方的plugin库。将生成的libnvinfer_plugin.so.7替换原本的.so文件即可。或者自己写一个类似于官方plugin的组件，将名称替换一下，同样生成.so，在TensorRT的推理项目中引用这个动态链接库即可。











---

## 优化

**structured sparsity**

> https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-1070/developer-guide/index.html#structured-sparsity

TODO



### fusion

> https://docs.nvidia.com/deeplearning/tensorrt/latest/performance/best-practices.html#types-of-fusions

通过`network->markOutput(*(layer->getOutput(0)))`将某个 layer 标记为网络输出 会阻止它与其它 layer fuse。当然这可能影响性能，且这些 layer [也需要无意义的 copyOutputToHost](https://github.com/NVIDIA/TensorRT/pull/495)。







### FP16

**BuilderFlag**

> https://docs.nvidia.com/deeplearning/tensorrt/api/python_api/infer/Core/BuilderConfig.html#tensorrt.BuilderFlag

与类型相关的 flag 见 *weak typing network*。

**strong typing network**

在 createNetworkV2 时配置 `NetworkDefinitionCreationFlag::kSTRONGLY_TYPED` 可以创建 [strongly typed networks](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#strongly-typed-networks) (strongly typed mode)，此时 TRT 会根据图中 op 的 dtype 定义推断每个中间值和输出的类型；不允许使用 setPrecision、setOutputType 和设置比 fp32 精度更低的 BuilderFlag。

**weak typing network** / **使用 fp16**

> https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#reduced-precision

网络默认是 [weakly typed network](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#reduced-precision) (weakly typed mode)，TRT 会忽略网络中节点实际的 dtype，自行为 tensor 和 op 选择不同的精度来提高性能、生成最快的 engine（但会减慢构建速度）：

- 所有浮点运算默认是 fp32。
- 如果设置了精度低于 fp32 的 BuilderFlag，TRT 可以选择更低的精度（不低于 Flag）来提高性能（Flag 的意义是允许低精度执行，而非强制；只要图里有 type 为 fp16 的 op，就要设置该 flag 才能执行）。
  - 可选项有 FP16、INT8、*TF32*、BF16，可以同时设置（INT8 可能要一些额外操作，见 *INT8*）。
    当低精度会使效率变低、或不存在该精度的实现时，会 fallback 到设置的较高的精度上尝试。
- TRT 为 layer 选定精度后（该精度必须在 Flag 里可用），会自动按需转换参数来在 layer 上执行：如果前一层的输出或后一层的输入与精度不匹配，会插入 reformat 操作，不需要自己在网络里插 cast。
- BuilderFlag 不影响 engine 输入输出 binding 的 type（仍是 fp32）。需要在 *I/O Formats* 修改。

BuilderFlag 影响整体精度。还可以为 layer 设置 precision 来控制特定 layer 的精度 (precision constraint)：

- ILayer::setPrecision 设置输入和输出的 preferred type。
- ILayer::setOutputType 设置输出的 preferred type。

默认情况下设置的 preferred type 不一定被应用：如果 TRT 发现使用另一种类型的实现效率更高，就会不使用设置的类型，只给 warning。可以添加 flag 控制该行为：

- kPREFER_PRECISION_CONSTRAINTS：总是使用设定的 preferred type，除非没有该精度的实现，此时会给 warning 并选择可用的最快实现。
- kOBEY_PRECISION_CONSTRAINTS：总是使用设定的 preferred type，如果没有该精度的实现，则返回 error。

这两个 flag 只会影响设置了 precision constraint (setPrecision, setOutputType) 的 layer，其它 layer 会根据 allowed builder precisions 由 TRT 选择。

> 可以用 layer->precisionIsSet() 检查某个 layer 是否设置 precision constraint。

> 除非 tensor 是网络的输入输出，否则 ITensor::setType() 不会为该 tensor 设置 precision constraint（要取决于它所在的 layer）。
> 以输出为例，`layer->setOutputType()` 和 `layer->getOutput(i)->setType()` 会有区别：前者是为 layer 设置精度；后者如果 output 不是网络的输出则会被忽略，如果是，则为其设置 type，且如果该 type 与 layer 的 output type 不同 TRT 会插入 cast。
>
> setOutputType 的精度是不是只对浮点有效？对 int32/int64 无影响？

> Note that the layer output type is generally not identical to the data type of the output tensor, as TensorRT may insert implicit reformatting operations to convert the former to the latter. Calling layer->setOutputType(i, type) has no effect on the data type of the i-th output tensor of layer, and users need to call layer->getOutput(i)->setType(type) to change the tensor data type. This is particularly relevant if the tensor is marked as a network output, since only setType() [but not setOutputType()] will affect the data representation in the corresponding output binding.
>
> Strongly-typed networks reject calls to method setOutputType. Instead, the output type can be set only for layers that define method setToType().

**计算精度 (computational precision)**

计算会使用与输入相同的精度，但有两个 layer 可以进一步控制精度：

- INormalizationLayer 提供了 setPrecision 方法来设置累加时的精度。默认累加总使用 fp32，不管 builder flag 是否是 fp32。可以通过该方法将累加改为 fp16。
- IMatrixMultiplyLayer 的累加精度默认根据输入类型和效率决定，且保证累加精度不小于输入精度。
  使用 strongly typed 时，可以将输入 cast 到 fp32 来强制一个 fp16 gemm 使用 fp32 累加。TRT 会识别这个 cast - gemm - cast pattern 并消除 cast，得到单个 fp16 输入但使用 fp32 累加的 gemm。
  （当然只有有累加 kACCUMULATE 的 matmul 才需要管理精度，没有额外加法的 kNONE matmul 不需要）

> 大部分 op 的输入与输出类型相同。
> Convolution, Deconvolution, FullyConnected 支持量化后的 int8 输入和未量化的 fp16, fp32 输出，因为有时保留高精度的输出对准确度很重要。



**TF32**

> https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#tf32-inference-c
>
> Allow (but not require) computations on tensors of type DataType::kFLOAT to use TF32. TF32 computes inner products by rounding the inputs to 10-bit mantissas before multiplying, but accumulates the sum using 23-bit mantissas. Enabled by default.

TF32 通常比 FP32 更快（会使用 TF32 Tensor Cores），比 FP16 精度更好（当然性能一般更差）。

BuilderFlag::kTF32 是默认启用的。可以通过 clearFlag 关闭。





**I/O Formats**

> https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#reformat-free-network-tensors
>
> data format 包括 data type 和 [layout](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#data-format-desc) (TensorFormat)。

为了在 TensorRT 和客户端程序之间实现高效的数据传递，底层的数据格式会在网络的输入输出边界处暴露出来。也就是说，对于网络的边界（输入和输出）tensor，以及从/向插件传输的数据，用户可以调整它们的数据格式进行优化；对于其它 tensor，TRT 会如上文所说选择执行最快的数据格式（可能会在网络中插入 reformat）。

可以通过 `network->getInput(0)->setAllowedFormats(1U << TensorFormat::kHWC8);` 设置某个 format。注意某些可能要求 tensor 通过 `setType` 设置对应的 dtype。

>  注意 `setAllowedFormats` 和 `setType` 只对网络的输入输出有效，否则会被忽略。

可以通过设置 DIRECT_IO builder flag 来避免 TRT 在网络边界插入 reformat，但这通常会导致效果更差。





### INT8

> https://github.com/NVIDIA/TensorRT/tree/main/samples/sampleINT8API





### 量化

> https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-quantized-types.html
>
> https://cloud.tencent.com/developer/article/2346616

**PTQ**

> https://zhuanlan.zhihu.com/p/402074214





---

## 其它

### Refit

**Weight-Stripping**

> https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-1070/developer-guide/index.html#weightless-build

TODO








---
## end

