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
>
> 模型部署文档：https://docs.sglang.io/cookbook/autoregressive/intro

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

见 *SGLang 后端代码*。



---

## FlashInfer

> https://arxiv.org/pdf/2501.01005





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



