# Python

---

[TOC]



---







---

## 基础





**signal handler**

terminate 等信号的 handler 中应该调用 sys.exit()，因为如果不调用进程在收到信号、执行完 handler 后就会继续运行。

但如果 handler 中会执行旧的 handler，进程就可以通过默认的 handler 退出了。

```python
def add_sig_handler(sig, f):
  """在 signal handler 中添加一个 handler (prepend) 而非覆盖"""
  old = None
  if callable(signal.getsignal(sig)):
    old = signal.getsignal(sig)
  def helper(*args, **kwargs):
    f(*args, **kwargs)
    if old is not None:  # 信号有默认行为 (default handler)，所以 old 可能是 exit，在前面调用 f 就调不了了
      old(*args, **kwargs)
  signal.signal(sig, helper)
```

**sys.exit**

sys.exit 本质是抛出 SystemExit 异常，会被 Python 的异常处理机制捕获，会按顺序执行 atexit 注册的函数、finally 代码块（如果当前处于 try 内）等。

os._exit() 直接调用系统调用 _exit()，立即终止进程，不执行任何清理。



---

## Memory Management, GC

> https://rushter.com/blog/python-garbage-collector/

**引用计数**

python 中的所有变量都是对一个对象的引用，而非实际值，简单的`a = b`只是在 b 所引用的对象上创建了一个新的引用 a，而非 copy 或创建新对象（除非显式调用 copy）。



**内存释放**

程序正常退出时（包括调用 exit(0)），会调用 gc 释放引用计数为 0 的对象并调用`__del__`（如果没有循环引用）；当程序被外部强制终止时，python 的 gc 不会有机会运行，因此对象的`__del__`不会被调用，将由操作系统回收程序占用的所有内存。
当存在循环引用时，python 会检测这些对象并正确释放内存，但可能不会调用它们的`__del__`，因为可能导致不可预测的行为。







---

## 异步

> https://zhuanlan.zhihu.com/p/14257521465
>
> 一个协程函数还是会被依次执行，只是执行 await 时，会让出 CPU（可以视为暂停，也可以视为仍在执行，只是这部分执行不能有 CPU 参与）允许其它协程拿到 CPU 继续执行。
> 协程可以在执行不需要 CPU 的长耗时异步操作时让出 CPU，允许其它协程执行。
>
> 在协程中使用阻塞操作会阻塞当前线程，从而阻塞事件循环、无法让其它协程继续执行（都在同一个线程内执行），需要用`loop.run_in_executor`创建新线程执行。



多个协程仍然在单线程内执行，没有线程切换，所以可以“同时”访问共享变量而不加锁（如果有需要线程安全的跨越让出 CPU 的 await 的大块逻辑，还是要保证线程安全）。







---

## 多进程

> https://docs.python.org/zh-cn/3.10/library/multiprocessing.html



**multiprocessing.Process**

API：

- terminate：通过 SIGTERM 结束进程 (posix)。注意子进程不会被终止，它们会直接变成孤儿进程（还是变为僵尸进程？），除非手动处理。



**multiprocessing.Pool**

Python 的多进程机制需要将函数和参数序列化 (pickle) 后传递给子进程，因为子进程有独立的内存空间。因此 pool 执行时的函数和参数都要是 picklable 的。
picklable 的类型有：

- 基本类型，容器类型，numpy 数组和基本数据类型。
- 模块级函数，内置函数，类。
  - 模块级函数可以通过名称查找（在子进程中重新导入模块），但局部函数和 lambda 无法通过这种方式访问，即局部函数不可序列化。
  - 类似的类必须是定义在模块顶层的类，不是嵌套类。

**multiprocessing.pool.ThreadPool**

multiprocessing 内也提供了线程池，它与进程池接口一致以方便切换。类似的，concurrent.futures 也提供了接口一致的线程池和进程池？

因为接口可能不适用于线程池，且返回类型 AsyncResult 不与其它库兼容（如 asyncio），因此推荐使用 concurrent.futures.ThreadPoolExecutor？

- IO 密集适合用线程池。
- CPU 密集或两者混合适合用进程池。但进程创建和上下文切换开销更大。

**concurrent.futures.ProcessPoolExecutor**

> https://docs.python.org/zh-cn/3.10/library/concurrent.futures.html

ProcessPoolExecutor 是基于 mp.Pool 实现的 (?) 进程池，区别为：

- 返回可与其它库交互的 Future 对象。
- 前者能取消已提交的任务。
- 前者可通过 future 直接获取任务抛出的异常。
- 后者能通过 terminate 向所有子进程发送 SIGTERM 以强制终止所有子进程，但前者不能。
- 后者提供 6 种 map：map，lazy 版本 imap，starmap 及它们的 async 版。而前者只有一个 map。

**multiprocessing.Pool** - 使用

API：

- close：阻止后续任务提交到进程池，当所有任务执行完成后，工作进程会退出。
- terminate：不必等待未完成的任务，立即停止工作进程。当进程池对象被 gc 时，会调用 terminate。
- join：等待工作进程结束。调用前必须先调用 close 或 terminate。

进程池支持上下文管理器协议：enter 会返回进程池对象，exit 会调用 terminate。



---

## end





