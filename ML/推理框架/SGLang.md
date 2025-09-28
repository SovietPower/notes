# SGLang 笔记

---

[TOC]

---



> https://github.com/sgl-project/sglang
>
> SGLang 论文：https://arxiv.org/pdf/2312.07104
>
> TODO：
> 与 deepseek 的优化：https://lmsys.org/blog/2024-12-04-sglang-v0-4/，https://docs.sglang.ai/references/deepseek.html

SGLang: Structured Generation Language for LLMs.







---

## 安装，使用

**安装和基本压测**

> https://zhuanlan.zhihu.com/p/29595422062

```shell
# 用 venv 或 conda
python3 -m venv sgl
source sgl/bin/activate
# conda
conda create -n sgl python=3.10
conda activate sgl

pip install --upgrade pip
# 安装SGLang内核
pip install sgl-kernel --force-reinstall --no-deps
# 安装完整依赖（含GPU加速内核）
pip install "sglang[all]>=0.4.5.post3" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python

# 应该不用降级，上一条指令会自动卸载和安装需要的版本
# pip uninstall transformers -y
# pip install transformers==4.48.3 --force-reinstall --no-deps

# 验证
pip show sglang
```



### Engine

注意创建、使用完 engine 后需要调用 eng.shutdown()（或通过 with 使用 engine，让其退出时调用`__exit__`即 shutdown）。

> python 变量销毁时（被 gc 时）只会调用`__del__`，`__exit__`是与上下文管理器（即 with 语句）协议相关的方法，不会因变量销毁而调用。
>
> 与资源清理相关的建议使用 exit，因为：
>
> - `__del__`的调用时机不确定。
> - 可能被循环引用阻止无法 gc。
> - 不保证在程序退出时一定会执行，如程序崩溃。
>
> 也可以使用`import atexit`，`atexit.register(cleanup)`。
>
> - 当`os._exit()`、发生 segfault 或 kill -9 时，上面的清理都不会调用，只是在正常退出和常规的异常退出时，exit 比 del 更可靠。
> - 但即使是普通的 terminate（如 ctrl c），程序会直接停止执行，with 内的释放 (`__exit__`) 不会被执行，因此也不安全，需要定义 sig handler 自行清理或自然退出，避免直接结束（直接 exit(0)）。





---

## 前端代码

> https://docs.sglang.ai/frontend/frontend.html

extend, gen, select 这样的 primitives 会被提交到流异步执行。获取生成结果会阻塞直到它们完成。



### API

**@function**

返回一个 SglFunction。

```python
# 将被装饰的函数包装成一个 SglFunction 实例
@function
def basic_qa(s, question):
    ...

# basic_qa 是一个 SglFunction 对象，(...) 会调用其 __call__
state = basic_qa(...)
```

**system**, **user**, **assistant**

就是 `_role_common("system"/"user"/"assistant", expr)`，即 `SglExprList([SglRoleBegin(name), expr, SglRoleEnd(name)])`。

还有多种同义表达：

```python
@function
def chat_example(s):
	s += system("You are a helpful assistant.")
    # 等价于
    s += s.system("You are a helpful assistant.")
    
    s += user("Q: ...")
    # 等价于
    with s.user():
        s += "Q: ..."

    s += assistant("A: " + gen("ans", ...))
    # 等价于
    s += assistant_begin()
    s += "A: " + gen("ans", ...)
    s += assistant_end()
```



**gen**

调用模型进行生成。

如果指定 choices，则返回 SglSelect，否则返回 SglGen。

**gen 参数**

> 其它见 https://docs.sglang.ai/backend/sampling_params.html

- **regex**：指定 regex 参数可使用约束解码 (constrained decoding)。
- **stream**：将输出流式打印 (?) 给用户。

**fork**

从一个状态 s 产生多个分支。fork 之间可并行。可通过下标 `forks[i]` 获取对应分支的新状态。

**run_batch**

相比直接调用函数 (run)，可以指定多组输入参数。





### SglExpr

SglGen、SglSelect、SglRoleBegin、SglRoleEnd... 都是一个 SglExpr。构造它们时会初始化一个 SglExpr。

SglExpr 可通过 + 或 concatenate_ir 合并成 SglExprList（也是一个 SglExpr，保存 List[SglExpr]）。



### SglFunction

即函数中的状态 s（强制要求函数的第一个参数就叫 `s`）。
调用时会调用 `self.run(*args, **kwargs)` 与 `sglfunc.run(...)` 相同（启用 trace 则是 `self.trace`）。





---

## 后端代码



### Engine

> https://docs.sglang.ai/backend/offline_engine_api.html

通过 api 中的 `sglang.engine` 创建一个 `sglang.srt.entrypoints.engine.Engine(*args, **kwargs)`。

Engine 是 infer server 的入口点，提供 infer engine 的接口。









---

## FlashInfer

> https://arxiv.org/pdf/2501.01005









---

## 优化

> https://arxiv.org/pdf/2312.07104

RadixAttention、Compressed finite state machines、API Speculative Execution 是 SGLang Runtime (SRT, backend) 的主要优化。

**其它优化**

> EP：https://zhuanlan.zhihu.com/p/17790182311



### Radix Attention / Prefix Caching

RadixAttention 就是利用带压缩前缀树来缓存 KV cache：相同前缀的请求会在树上共享同一个节点、共享 cache。

- 缓存淘汰策略是 LRU。只会淘汰叶节点，然后才能淘汰因失去叶子变成叶节点的节点。
- 在 continuous batching 中，无法在每次 batch 后清理无用节点上的 cache，所以会为每个节点维护引用计数，计数非 0 的节点不会被驱逐。
- cache 会与正在执行的请求共享可用内存，这样当有足够的请求在执行时，系统可以驱逐所有已缓存的 token，以支持更大的 batch size。



**cache-aware scheduling**

cache 的命中率为 number of cached prompt tokens / number of prompt tokens。
当等待队列有大量请求（cache 容量不足）时，执行请求的顺序会显著影响缓存命中率。如果调度程序频繁地在不同的、不相关的请求之间切换，会导致 cache 抖动和命中率低。

这个调度算法按公共前缀长度对请求进行排序，并优先处理具有较长匹配前缀的请求，而不是使用 FIFO、按请求到来时间进行调度。

对于一 batch 请求，在 trie 上 DFS 依次处理可以实现最高的 cache 命中率；而按公共前缀长度进行依次处理可以实现接近的效果。

> 这种贪心调度会导致饥饿，还需要和其它公平调度结合。



### Fast Constrained Decoding / Guided Decoding

> https://github.com/zhaochenyang20/Awesome-ML-SYS-Tutorial/blob/main/sglang/constraint-decoding/readme.md

Effcient Constrained Decoding with Compressed Finite State Machine：*fast constrained decoding* 允许在特定约束条件下一次生成多个 token，适合结构化输出。

用户可以提供正则表达式来表示该约束，系统会据此构建一个压缩有限状态机，并在推理时维护 FSM 的状态。
当对于给定输入，当前状态机只允许唯一的有效输出时，会直接通过状态机得到后面的若干 token，不经过 LLM decode，直到遇到非唯一的状态。不过还需要一次 prefill。

**Handling Tokenization Artifacts with Retokenization**

状态机是用字符串构建的，所以通过它一次得到多个输出后，还需将字符串转为 token。
需要 retokenization（TODO）。



###  API Speculative Execution

Effcient Endpoint Calling with API Speculative Execution：SGLang 提供了前端和解释器，而后端可以用 API 访问 API-access-only model。
对于这种 API 访问，SGL 通过投机执行来减少 API 调用次数和延迟：在调用 API 时，SGL 会忽略用户的停止条件，让模型生成更多 token；解释器会保留额外的生成输出，并用它匹配和重用于之后的用户请求。如果成功匹配，可以为用户省下一次 API 调用和耗时。

尤其适用于连续两次调用且之间没有其它内容？可以把下一次调用的格式放在请求里？





---

## 其它







> https://zhuanlan.zhihu.com/p/714833359
>
> 接着是 running-req 和 queue-req，代表着当前 batch 正在 prefill 的 req（request） 与当前在队列中等待 prefill 的 req。直观上，running-req 越高越好，而 queue-req 则越低越好。
>
> 我个人认为，queue-req 最本质的区别在 0 和非 0。因为前者意味着我们还可以进一步加大请求烈度（而单个请求的 latency 几乎不会受影响），而后者代表着达到了负载上限，再加大烈度会显著加大 latency。
>
> 同样的，我们观察 Decode batch 的 log，在 running/queue-req 之外，还有两个参数值得玩味。首先是 token-usage，大致代表着这张显卡的实际利用率。可以看到上方我的 token usage 是 0.84，这是个相当高的 usage 了，以至于出现了 queue。
>
> 基于本小白如上的一些描述，当 SGLang 运行过程中相关 metric 较小时，可以放心加大请求量。当然，请注意你的请求本身能否维持稳定。在我自己的使用过程中，随着使用时间增大，prompt 会更加复杂，在 system prompt 之外的内容会越来越多，导致 latency 增大了很多。











---

## end



