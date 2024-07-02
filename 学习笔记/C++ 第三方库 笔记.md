# C++ 第三方库 笔记

---

[TOC]

---





## fmt

> 示例：https://blog.csdn.net/lizhichao410/article/details/132449898









---

## GoogleTest

> https://google.github.io/googletest/

### 安装与运行 (cmake)

**运行测试**

运行项目的主目标时不会进行测试，可通过：

- 在 vscode 的 cmake - 项目大纲 可看到创建的测试目标，可直接运行。
- 或在测试所在的项目构建目录（比如`build`或`build/subproj`）运行`ctest`。
- 或在测试所在的项目构建目录，运行生成的 exe，手动、单个测试。

`ctest --rerun-failed --output-on-failure`可以在测试后仅运行失败的测试，并输出详细信息。
如果要输出调试信息，记得刷新缓存，比如`fflush(stdout);`（更推荐`cout << endl;`）。

**配置测试**

要想通过 ctest 运行，需要：

```cmake
include(CTest)
include(GoogleTest)
gtest_discover_tests(test_target_name)
```

注意，在另一个项目的 CML 生成的目标（比如`src`），也位于`src`下而非原本的项目下。其构建文件位于`build/src`下而非 build 根目录（取决于 CML）。
在当前目录的 Testing 下会生成测试输出。

**获取 gtest**

```cmake
include(FetchContent)
FetchContent_Declare(
	googletest
	URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)

# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)
```

**生成测试**

```cmake
enable_testing()

add_executable(test_hello "${CMAKE_SOURCE_DIR}/src/hello/test/hello_test.cc")
target_link_libraries(test_hello GTest::gtest_main src)
```

链接 gtest_main 后就不需要自己加 main 函数或者链接其它库了。

**cmake 命令**

**gtest_add_tests**

向 CTest 注册测试，替代 add_test。







### 基本概念

**基本概念**

在之前，gtest 把其它地方常说的一组相关测试 test suite 称为 test case；把其它地方说的单个测试 test case 称为 test。
现在 gtest 正在改变该说法，推荐使用 test suite。

一个测试程序可包含多个 test suite；每个 test suite 可包含多个 test。
当同一 test suite 的多个 test 需要共享对象时，可以把它们放到一个 test fixture 类中。
测试名不能含下划线。

只要链接了 gtest_main，测试就不需要写 main 函数。也不推荐写 main，除非要在测试前做框架不能实现的事情。
如果写了 main，则必须调用并返回 RUN_ALL_TESTS()，main 函数返回值是测试是否成功的标志。
模板见 https://google.github.io/googletest/primer.html 最下。

**断言**

测试都是通过断言 (assertion) 来实现的。
只有一个测试的所有断言都成功，该测试才成功。

断言的结果分为：

- success：成功。
- non-fatal failure：失败，但程序和函数可以并继续向下运行。
- fatal failure：失败，且退出当前函数（程序是否退出？），后续测试不会再执行。

gtest 提供了宏`EXPECT_XX`和`ASSERT_XX`，分别会产生 non-fatal/fatal failure，因此后者在失败时会直接结束函数（还是程序？），只需要在完全不用继续执行的情况下使用。
注意 ASSERT fatal failure 时会直接返回，如果不处理可能导致内存泄露，但通常影响不大。

`EXPECT_XX`与`ASSERT_XX`类似，只说前者。

可以通过流提供自定义的错误信息：`EXPECT_EQ(1, 2) << "1 not equal to 2"`。

**可用的谓词**

> https://google.github.io/googletest/reference/assertions.html

可作为`EXPECT_XX`和`ASSERT_XX`后缀的谓词：

- 一元：TRUE、FALSE。
- 二元：EQ、NE、LT、LE、GT、GE。
- 浮点：FLOAT_EQ、DOUBLE_EQ（比较浮点是否近似相等）、NEAR（比较相差是否不超过指定误差）。
- [Matcher](https://google.github.io/googletest/reference/matchers.html)：THAT。
    匹配器有很多种，都可以在`EXPECT_THAT(arg, matcher)`中使用，比如：上述谓词、`Optional(v)`、`VariantWith<T>(v)`、`Ref(v)`、`StartsWith`、`MatchesRegex`等。
- 其它：
    - STREQ/STRNE：比较 C 字符串是否相同/不同（传递 const char*）。EQ 只会比较指针本身，即比较地址。
    - 异常：THROW（要求抛出指定类型异常）、NO_THROW、ANY_THROW。

注意，空指针要比较 nullptr 而非 NULL。

**显式正确或错误**

`SUCCEED()`产生一个 success。可以认为没有实际作用，不会导致当前测试成功。

`FAIL()`产生一个 fatal failure，终止当前函数。只能用于返回 void 的函数。

`ADD_FAILURE()`产生一个 non-fatal failure，不会结束当前函数。



### 测试

```cpp
#include <gtest/gtest.h>
TEST(TestSuiteName, TestName) {
  ... statements ...
}
```







### Fixture

当多个测试需要共享数据时，可以用 test *fixture*。
具体见[这里](https://google.github.io/googletest/primer.html)。
示例见[这里](https://github.com/google/googletest/blob/main/googletest/samples/sample3_unittest.cc)。







---

## ZMQ

> https://github.com/zeromq/libzmq
> 更现代：https://github.com/zeromq/cppzmq（对 libzmq 的封装，之后可以看看）
>
> 文档：https://zguide.zeromq.org/（很早的中文翻译：https://github.com/anjuke/zguide-cn）
> https://zeromq.org/get-started/
> API：https://libzmq.readthedocs.io/en/latest/
>
> examples：https://github.com/booksbyus/zguide







### 使用

ZMQ 不知道要传输的类型（除了它的字节数）。使用者需要在发送时正确地编码、接收时解码。

**zero copy**

使用 zmq_msg_init_data 可以传递数据指针，减少一次用户数据到 socket buffer 的拷贝。
如果用户数据有好几部分，也可以这样做，因为 zmq 支持将一个消息分成多组，分别传入一个数据指针，但它们依旧是通过单个系统调用写入到网卡然后发送的。

接收时可以直接使用它的缓冲区指针，减少一次 socket buffer 到用户数据的拷贝。但要注意需要自行 close 和释放 msg。

```cpp
void FreeData(void *data, void *hint) {
	if (hint == NULL) {
		delete[] static_cast<char*>(data);
	} else {
		// 将 T 设为 char 调用析构应该是安全的
		delete static_cast<ps::SVector<char>*>(hint);
	}
}
// 发送
SVector<char>* data = new SVector<char>(msg.data[i]);
int data_size = data->size();
zmq_msg_init_data(&data_msg, data->data(), data->size(), FreeData, data);
// 接收
char* buf = (char *)zmq_msg_data(zmsg);
size_t size = zmq_msg_size(zmsg);
SVector<char> data;
data.reset(buf, size, [zmsg](char* buf) {
    zmq_msg_close(zmsg);
    delete zmsg;
});
```





### API

> https://libzmq.readthedocs.io/en/latest/xxx.html



**zmq_ctx_term**

销毁指定的 context。

所有在当前 context 打开的 socket 上的正在阻塞的行为，都立刻返回，错误码为 ETERM。
后续所有在当前 context 打开的 socket 上执行的行为（除了 zmq_close），都直接失败，错误码为 ETERM。
然后阻塞，直到：所有在当前 context 打开的 socket 被 zmq_close；所有这些 socket 上 zmq_send 的信息，要么成功发送，要么因 LINGER 时间过期丢弃。

**zmq_setsockopt**

`int zmq_setsockopt (void '*socket', int 'option_name', const void '*option_value', size_t 'option_len')`

为指定的 socket 设置某个选项。选项值通过 void* 指针传入，其大小为 option_len，需要符合该选项的要求。

选项：

- ZMQ_LINGER：设置套接字通过 zmq_disconnect / zmq_close 断开/关闭后，如果内存中还有待发消息没发给 peer，则最长等待的时间。socket 的 context 终止也会因此阻塞。

**zmq_tcp**

格式为：`tcp://interface:port`。
interface 可以是 IPv4/6 地址，或 * 表示所有可用 interface。
port 是端口号（通常大于 1024），或 * 表示由 os 分配临时端口（需要通过 ZMQ_LAST_ENDPOINT 获取分配的端口号）。

**zmq_msg**

...

zmq_msg_t 不能被直接访问，必须通过 ZMQ 提供的 zmq_msg 接口。

- zmq_msg_data：msg 中保存的数据地址。
- zmq_msg_more：检查其是否是消息的最后一部分。（也可用 zmq_getsockopt + ZMQ_RCVMORE）

**zmq_msg_init_data**

`int zmq_msg_init_data (zmq_msg_t '*msg', void '*data', size_t 'size', zmq_free_fn '*ffn', void '*hint')`

初始化 msg，使其能使用 data 位置的 buffer（大小为 size 字节）作为传输数据。
该过程不会发生拷贝，ZMQ 需要持有 buffer 的管理权，并在不需要后调用 ffn 释放（如果提供了）。
hint 用于辅助 ffn 正确释放内存。

**zmq_msg_send**

`int zmq_msg_send (zmq_msg_t '*msg', void '*socket', int 'flags')`

在指定的 socket 上发送消息。
发送成功不代表消息已经被上传到网络或被收到，只代表已经进入当前 socket 的队列。

ZMQ 消息可以有一个或多个部分。flags 可被设置 ZMQ_SNDMORE，表示这是一条 有多个部分的消息 的非末尾部分。当发送最后一部分时，需要取消该 flag。
ZMQ 保证这类多部分的消息的发送是原子的，即要么所有部分都收到，要么都不收到。
每部分信息都用一个 zmq_msg_t 表示。

当发送成功时，msg 指向的结构被清空并释放，需要重新初始化。如果要将其发送多次，需要先自行拷贝（比如 zmq_msg_copy）。
发送失败时，msg 不变。如果不再使用，需要 zmq_msg_close 释放避免内存泄露。















