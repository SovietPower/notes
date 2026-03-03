# 语言：C++ 基础 函数 多线程 协程 其它

Tags: 笔记


-----

[TOC]

-----

## 基础

**C 与 C++ 的区别**

C++ 是一个多范式的编程语言，有很强的面向对象支持，也支持面向过程、泛型、元编程等。（C 也可实现面向对象编程，就是多态会麻烦）
C 和 C++ 有一些设计和语法上的差异。比如 C++ 强调类型安全，所以给出了 4 种类型转换运算符，编译器能够检查转换是否成功。
C++ 有或者可以实现很多新特性，比如 RAII、智能指针、泛型、异常。
C++ 的模板库更丰富。

> C++ 与 C 的性能，很难明确说出谁更好。
> 虽然 C++ 引入了大量新功能，但很多都是在编译器上进行的，只影响编译速度。如果用好了 C++ 的新特性，能提高运行效率和编程效率。

**如何看待 C++**

自由，高效，把很多问题交给程序员去解决和决定，也因此很容易出现 bug，写起来比较麻烦。
例：

- 区分左值和右值，允许程序员更加细粒度的处理对象拷贝时的内存开销，提高了对临时对象和不需要的对象的利用率。
- 没有 GC 和它的开销，对象的生命周期完全由程序员确定，不过有 RAII、智能指针等方式帮助解决这个问题。
- 有指针和指针运算，还有 reinterpret_cast，保存访问数据相当自由。但指针也是最容易出问题的地方之一。
- 有宏定义，可以写出非常巧妙的东西，但同样可读性和安全性不是很高。
- 不同实现多，不统一；历史包袱重，难推进。

**某些概念**

编译器与标准库不同，编译器实现语言功能特性（如 gcc, clang, MSVC (cl) ），标准库实现库功能特性（如 GCC libstdc++, Clang libc++, MSVC STL）。
各编译器与标准库对功能的支持见 https://zh.cppreference.com/w/cpp/compiler_support/17

[标准库 (standard library)](https://zh.cppreference.com/w/cpp/standard_library) 是编译器提供的，以头文件的形式提供，不带 .h（如`#include <vector>`），命名空间为 std。

STL (standard template libaray) 属于标准库的一部分。
包括六大部分：容器、分配器、算法、迭代器、仿函数、适配器。

**gcc 与 g++**

> gcc 架构：https://zhuanlan.zhihu.com/p/372526494

GCC (GNU Compiler Collection) 是 GNU 编译器集合项目，包含许多编译器程序，比如：gcc、g++。
（GCC 最早是 GNU C Compiler，专用于 C 的编译器，但后来集成了不同编译器，gcc 本身也不再是编译器，变成了 driver）

gcc 与 g++ 区别很小，只是处理 .c 时调用的编译器和传递给链接器的参数不同：

- gcc 会把 .c 文件当做 C++ 语言，调用 cc1 编译。
    默认不会链接 C++ 标准库。
- g++ 会把 .c 文件当做 C++ 语言，并在 .c 文件前后分别加上 -xc++ 和 -xnone，从而调用 cc1plus 编译。
    默认链接 C++ 标准库（-lstdc++）。
- 两者对 .cpp 的处理是一致的，都调用 cc1plus 编译。

简单来说，g++ 对 .c、.cpp 都按 C++ 处理编译。
g++ 实际就是附加额外参数 然后调用 gcc 的程序，可以认为`g++` = `gcc -xc++ -lstdc++ -shared-libgcc`。

> gcc、g++、cpp 程序都是 compiler driver（类似驱动程序）。
> driver 不负责编译代码，只负责根据文件后缀名，去调用真正的编译器 (compiler proper)，把源码编译到汇编代码；然后再调用 as，把汇编代码变成二进制代码；最后调用 ld，把二进制代码拼在一起。
>
> 比如：在 GCC 这个项目中，真正负责编译 C 代码的程序叫做 cc1，负责编译 C++ 代码的程序叫做 cc1plus，那么这些 driver 在遇到 .c 时就会调用 cc1、遇到 .cpp 时就调用 cc1plus；生成汇编后再调用其它程序。

**debug 与 release**

如果有 NDEBUG 宏就是 release，否则是 debug。
所以可以用`#ifdef NDEBUG`判。

**源文件**

> 为什么要 include .h 文件而不是 .cpp？
> [ODR](https://zh.cppreference.com/w/cpp/language/definition)：任何变量、函数、类、枚举、概念 (C++20 起) 或模板，在每个翻译单元中都只允许有一个定义（例外见文档）。
>
> 每个 cpp 都是一个翻译单元。编译时，预处理阶段会将所有 include 的文件内容放进去，再编译。
> 编译时，会为预处理后的文件（也就是原文件加上所有 include 的文件）中的函数/静态变量/全局变量定义分配符号。如果 include 文件里面的 cpp 或某个 h 有与当前文件同名的定义，出现多个强符号，自然就会编译错误（这与在同一个文件内重定义是一样的）。
>
> 链接时类似，如果链接的两个编译单元有同样的强符号，也会错误。主要通过 namespace 避免。
>
> .h 文件中除了 inline 对象外，也不应该给出定义。
> include 只是将文本复制到该位置。任何后缀的文本文件都可导入（.h 只是规范。Linux 中的文件也不会用后缀名做类型）。

> .hpp 指无源头文件，没有cpp，也不用链接库，只要包含了 hpp 就能编译。但好像编译速度比较慢？
>
> .ipp 常用于写模板实现。有时会将模板接口与实现分开，但不能用 .hpp 两次，也不适合用 .cpp，所以引入了保存实现的文件 .ipp。

**翻译单元**

见 *OS*。

**源程序到可执行程序的过程**

见 *OS*。

**LTO (Link-Time Optimization)**

TODO

可能导致链接时间延长，所以 release 时用，debug 时一般不用？
可以跨编译单元决策优化项。

**main 函数**

程序应当有一个名字是 [main 的全局函数](https://zh.cppreference.com/w/cpp/language/main_function)，它被指定为程序的启动点。

程序的实际起始和结束点都不是main函数。在链接时，编译器还会自动链接 libc、crt1.o、crti.o、crtn.o，这些是不可缺少的。
链接后，程序的正式入口是`<_start>`，会调用`__libc_start_main`，这个函数中会进行初始化`<_init>`、注册退出处理程序`<_fini>`（main退出后执行的），然后调用main函数。
main函数的返回值会被用做`exit`的参数，也就是正常情况下，main return后仍会调用`exit(0)`。
0除了在惯例上表示无错误外，也是因为在 stdlib.h 中定义了`EXIT_SUCCESS`为0（exit 函数成功时要返回的值）。

C99起标准要求`int main`（只要返回类型与 int 兼容）在没有返回值时，默认`return 0;`。
在 C 中`int main()`并不是标准的无参 main 写法，`int main(void)`才是。前者表示该函数可以接收任意数量的参数，但是不需要处理，后者只能在无参的情况下调用。
在 C++ 中无参 main 不需要再加 void 了。

**头文件**

头文件可以分为 header-only file 和 index file（不确定）。
header-only file 的所有声明和定义都包含在一个文件内，`#include`后会包含这个源码进行编译。
index file 类似索引文件，`#include`后可以去链接对应的静态、动态库。

**header-only file/library** 是因为编译器不支持模块分离（C++20才支持），不得不将模板的实现写在头文件中。
Boost 提出用hpp做为 header-only library 的文件后缀。
优点：

1. 使用方便，只需要指明路径、包含头文件。
    不需要考虑平台的特殊性，不需要为不同环境做多个版本的库文件，因为是用户自己编译。
2. 给出所有代码的情况下，编译器在编译时可能做出更好的优化（而不是只能在链接时优化）。

缺点：

1. 编译慢，每次编译都要编译整个头文件的所有实现。对大项目影响更大。
    划分编译单元，将代码拆分，可以缓解该问题。
2. 如果修改了库的实现，所有使用该库的编译单元都要重新编译。
    所以 header-only library 应尽量为相对稳定的功能库,而不是接口库。适合变动需求不大，对灵活性要求高。

> 重复定义问题如何解决？
> 类定义写在头文件，多文件包含那么 ifdef 也解决不了重复定义问题，inline 关键字才能解决。这个关键字有两个作用，一是规避ODR（One Definition Rule）规则，链接器对于ODR Linkage的符号，不会报重复定义错误，视为等价保留一份。二是字面意思提示编译器进行内联优化。
> 如果要在头文件声明变量，可以用 extern 声明，然后在源文件中定义。
>
> TODO：https://maskray.me/blog/2022-11-13-odr-violation-detection

**index file** 指的就是声明和实现分离，使用时只需要`#include`声明，编译后链接相应的编译好的库（lib, .dll, .so）。

> 动态加载 so/dll：https://lqxhub.github.io/posts/b810e905/

**ODR**

[单一定义规则](https://zh.cppreference.com/w/cpp/language/definition) (One Definition Rule)：任何变量、函数、类类型、枚举类型、概念或模板，在每个翻译单元中都只允许有一个定义（其中部分可以有多个声明）。

例外：类类型、枚举类型、内联函数、内联变量、模板，在满足以下条件时允许有多个定义：每个定义都出现在不同单元；不同单元中的定义均相同；...。

在整个程序（包括所有的标准库）中，被 ODR 使用的非内联函数或变量必须有且仅有一个定义；内联函数或变量必须在每个 ODR 使用它的单元都有一个定义。否则非良构，但不要求诊断。见 [odr#10,11](https://timsong-cpp.github.io/cppwp/n4861/basic.def.odr#10)（definition domain 定义中的 module 是 20 的模块，一般就是指 TU，可以看 17 的标准）。

**ODR 使用** / **ODR use**

简单来说：

- 一个对象在它被读取（除非它是编译时常量）、写入、取地址或被引用绑定时，这个对象被 ODR 使用。
- 如果一个引用所引用的对象在编译期未知，则使用该引用时，引用被 ODR 使用。
- 一个函数在被调用或取地址时，被 ODR 使用（内联了不算调用）。

具体见 [ref](https://zh.cppreference.com/w/cpp/language/definition#ODR_.E4.BD.BF.E7.94.A8) 或[标准](https://timsong-cpp.github.io/cppwp/n4861/basic.def.odr#4)。

**name mangling** / **mangle**

C++ 编译器会将函数的名字、参数类型、参数个数、所在类和命名空间等信息（即 *函数 - 函数签名*）编码成一个唯一的字符串，用做链接符号（因此参数不同的函数有不同符号，实现了重载）。这个过程叫 name mangling 或命名修饰、命名重整。
extern "C" 会避免函数进行 mangling。

比如：命名空间 Name 中的类 Class 的方法`void Func(int)`可能会被编码成 _ZN4Name5Class4FuncEi。

> [demangler 网站](http://demangler.com/) 可以在线 demangle 获得函数原本的名字。
> 也可通过`c++filt -t`恢复。
> godbolt 生成的汇编可以选择 demangle identifiers，显示正常的结果。
>
> Itanium C++ ABI 规定 [type_info::name](https://zh.cppreference.com/w/cpp/types/type_info/name) 返回类型 mangle 后的名字，这包括 gcc 和 clang。
>
> 通过`<cxxabi.h>`中的`char* abi::__cxa_demangle(const char* mangled_name, char* output_buffer, size_t*   length, int* status)`可以将 mangle 后的名字恢复，如：
>
> ```cpp
> char* p = abi::__cxa_demangle(typeid(func).name(), NULL, NULL, NULL);
> cout << p << '\n';
> std::free(p);
> ```
>
> 见 https://www.zhihu.com/question/278587865。
>
> gcc 的 mangle 中可能有如下规则：开头的 Z 代表 C++ 的符号，4 代表后面的字符串长度，如 4func。
> 如果是指针则在最前加 P；内建类型使用短字符串表示（如 _Z4funcid 后的 int, double），类名或函数名通过数字和对应个数的字母表示；N 代表一个 namespace 的起始，后接数字和对应个数的字母，表示命名空间名称，以 E 结束（如 _ZN4Name4funcEid）；如果是 std 命名空间则是 St 而非 N（如 _ZSt4funcid）。

> 汇编层面，读写某个非局部变量时，实际就是读写它的符号（类似的，调用某个函数，实际就是 call 它的符号）。链接就是将没有的符号定义导入。
> 因此如果知道一个变量 mangle 后的名字 x，就可以通过该名字直接访问它（生成的汇编都是访问符号 x），比如：https://godbolt.org/z/YaE63sc6s（需要 extern 给出它的声明；如果不 extern 则是该符号重定义。全局作用域的变量可能不会被 mangle。extern 声明的函数会附加一个前缀，所以不行）。
>
> C++ 的函数重载在 ABI 层面就是靠 name mangling 实现的。
>
> 对于 Itanium ABI (gcc, clang)，mangle 时不会考虑函数返回类型，因此即使函数声明与外部链接的函数定义的返回类型不同，也能够链接并成功调用；MSVC ABI mangle 后会包含返回类型。

**ABI**

> https://en.wikipedia.org/wiki/Calling_convention
> https://zhuanlan.zhihu.com/p/692886292
>
> 当提到库的 ABI 时，一般是说二进制库的*二进制兼容性*。
> 设应用程序引用了某个二进制库 A，当 A 更新版本时，如果其 API 和调用方式没变、程序源码不需要改动，只需要重新编译应用程序就可以完成更新，那么称这个库的新旧版本是 源码兼容 (source compatible) 的；如果连重新编译都不需要，那么称两个版本之间是 二进制兼容 (binary compatible) 的（更强约束）。
>
> x86_64-linux-gnu 这种就是 ABI 的名字？由 架构名-内核-平台 构成。

二进制接口 ABI (Application Binary Interface) 大概指一个翻译单元内的各实体（函数、类型等）如何进行交互。
当应用程序引用了一个以二进制形式发布的库时，在源代码层面，程序使用了这个库的 API；而在编译、链接之后，即运行时，应用程序通过 ABI 与这个库通信。从这个角度看，ABI 是 API 机器层面的底层实现，多数时候不需要关心这个问题。只有在以二进制非源码形式发布库时需要关心（比如不希望公开源码）。
（API 定义了源码中的数据如何访问，ABI 定义了机器码中的数据如何访问）

x86-64 平台上主要有两套 ABI：

- 用于64位 windows 的 [微软 x64 ABI](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions?view=msvc-170)。
- 用于64位 Unix-like 系统的 [AMD64 System V ABI](https://refspecs.linuxbase.org/elf/x86_64-abi-0.99.pdf)。

> System V 是1983年发布的 Unix 重要版本，System V ABI 就是源自 UNIX System V。
> 它原本是针对32位 x86 架构指定的规范，在 AMD 最早推出64位 x86-64 架构时推出了新的 ABI 标准，所以叫 System V AMD64 ABI。这个标准后来也被 Intel 的64位处理器所采用。

保持接口的二进制兼容性需要在 ABI 的各个方面保持一致（只需要接口定义满足条件，接口内部实现无所谓），包括：

- 目标文件格式 (Object File Format)：决定如何解析目标文件（动态库、可执行文件等）。

Windows x64 使用 PE32+ 格式（Portable Executable 32-bit 的64位版本），System V 使用 ELF (Executable Linkable Format)。
可能也不算做 ABI 的一部分。

- 数据表示 (Data Representation / Data Layout)：规定基础类型的大小和对齐（即 *数据模型*？）。
- 平台、编译器

不同的架构、总线宽度、不同寄存器组、大端小端存储、类型大小，都会导致机器码之间不能兼容。

不同的编译器和版本可能导致 ABI 不一致。gcc 的 [-fabi-version](https://gcc.gnu.org/onlinedocs/gcc/C_002b_002b-Dialect-Options.html#index-fabi-version) 可以用来控制 ABI 版本。
不同的编译选项也可能导致程序间的 ABI 不一致，比如：`-fno-strict-aliasing`关闭严格别名，`-fno-exceptions`关闭异常，`-fno-rtti`关闭 RTTI。

- **调用约定** ([**Calling Convention**](https://en.wikipedia.org/wiki/Calling_convention))

> x86 的各种调用约定：https://en.wikipedia.org/wiki/X86_calling_conventions
> MSVC 调用约定：https://learn.microsoft.com/zh-cn/cpp/cpp/argument-passing-and-naming-conventions?view=msvc-170

**关于函数（即 API）调用方式的约定**，包括参数如何传递、返回值放在哪、栈由谁清理、哪些寄存器要由调用者保存、哪些寄存器要由被调用者保存（在调用前后保持不变）、如何处理可变实参等。
与优化等级或编译选项无关，只与调用约定有关。

32位 windows 有三类调用约定：\_\_cdecl、\_\_stdcall、\_\_fastcall。
stdcall 是32位 win 平台上 API 默认的约定，但实际非常混乱。

> cdecl 是最传统的约定，调用者需要将参数从左到右入栈、调用函数、最后将参数出栈（清理栈），比如一个调用 f 的过程为：`push arg1`、`push arg2`、`call f`、`add sp, 8`（或`pop; pop`）。
> stdcall 则要求参数从右到左入栈，函数要自己清理栈，调用者不需要将参数出栈，因此调用 f 的过程为：`push arg1`、`push arg2`、`call f`。f 内部需自行 pop。
> 两者的所有参数均保存在栈中。
>
> thiscall 是 x86 用于 C++ 非静态成员函数的默认调用约定，其它函数则使用其它的调用约定。
> 该约定中成员函数的第一个参数（this 指针）是隐式传递的，不需要显式地放在参数列表中。thiscall 的两个不同版本和其它区别见 wiki。

64位程序中的调用约定基本统一，主要就是微软 x64 和 System V 分别定义的两种调用约定。

> System V ABI 的调用约定最常见，用于各种 Unix 系统。
> 它使用 rdi rsi rdx rcx r8 r9 传递参数中的前1~6个整型/指针实参，使用 xmm0~xmm7 传递参数中的前1~8个浮点实参；其余实参从右到左入栈。
> 如果返回值为64位整型，则保存在 rax 中；如果为128位整型，则保存在 rax 和 rdx。浮点返回值类似，可保存在 xmm0 和 xmm1 中。
> rbx rsp rbp r12~r15 这七个寄存器在调用前后保持不变（如果被调用者要使用它们，需要保存原值并在返回前恢复）。
>
> 微软 x64 ABI 中，使用 rcx rdx r8 r9 存储前4个整型/指针实参，使用 xmm0~xmm3 存储前4个浮点实参；其余实参从右到左入栈。
>
> 注意，如果实参类型不是整数、指针、浮点，则会通过引用传递（传递它的地址到寄存器或栈，然后通过地址访问）。
> 但如果参数是16B的整数或包含两个整数的结构体，对于 System V ABI，允许将其拆分到两个寄存器内传递；微软 ABI 则不能。

> 注意，对于 Itanium C++ ABI，对于一个非平凡的对象，即使大小不超过8B，也不能使用寄存器传参。
> 这里的[非平凡](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#non-trivial)与 C++ 的语义不同：如果类型没有非平凡的拷贝构造、移动构造、析构函数，并且拷贝和移动构造没有都被显式弃置，那么该类型是平凡的。
>
> Itanium C++ ABI 规定：如果参数类型对于函数调用来说是非平凡的，那么调用者必须为临时对象分配空间，然后通过引用传递该临时对象，不能通过寄存器。因此使用值传递与引用传递，传递非平凡类型的参数时，传参所使用的汇编是一样的。
> 原因：函数可以对参数取地址。如果某个参数通过寄存器传递，且函数内需要对其取地址时（包括将其绑定到某个应用），需要将其拷贝到栈内，然后传递该地址。因此该参数的拷贝必须是平凡的，以避免有副作用、对用户产生影响。
> 如果类有非平凡的拷贝构造，且通过寄存器传递，就可能会导致上述额外的拷贝构造，可能会产生副作用，因此只能定义在栈里，然后传递其地址，与引用相同。
>
> 因此 unqiue_ptr 会比裸指针开销更高：它无法直接保存在寄存器中传递，只能通过引用传递。单链表 forward_list 也是如此。
> 自定义类最好使用平凡的拷贝、移动和析构函数。

- **命名重整** ([Name Mangling](https://en.wikipedia.org/wiki/Name_mangling))

介绍见 *name mangling*。
不同的编译器、版本不同的相同编译器，mangling 算法都可能不同，因此想要二进制兼容，一般要 extern "C" 声明函数避免 mangle：

```cpp
#ifdef __cplusplus
extern "C" {
#endif

// codes

#ifdef __cplusplus
}
#endif
```

- 避免使用 STL 或非 POD 类型

不同的标准库、版本不同的相同标准库不是二进制兼容的（？），因此使用它们也不是（而且用户还可以替换它们）。
所以接口应使用基本类型、POD 和确定的类，甚至不使用类（？），只使用纯虚接口类（抽象类）；或者用兼容 C 的 API。

> 当确定编译器、os、硬件架构后，STL 也是 ABI 兼容的。此时用 function 做接口也可以。

- 内存管理

通常内存分配和释放、构造与析构调用 不应该跨越 DLL Boundary，即一个模块创建的对象应该由它自己销毁。因为不同模块使用的内存分配器很可能是不同的。
因此如果库提供了创建对象的 API，也应提供销毁对象的 API，而不是由应用程序自行销毁。

- 继承、虚函数

包括虚基类的位置、类的内存布局、如何调用虚函数、vptr 的位置（在类内的偏移）、vtable 的内容与格式（某个虚函数在虚表内的偏移）等。

综合上面几点的例子：

```cpp
#ifdef WIN32
  #define CALL __stdcall
#else
  #define CALL
#endif

class Window {
public:
  // 销毁需要由库提供的实现完成
  virtual void CALL destroy() = 0;
  virtual void CALL setTitle(const char* title) = 0;
  virtual const char* CALL getTitle() = 0;
};

extern "C"
Window* CALL CreateWindow(const char* title);
```

如果想在 API 改变的情况下保证 ABI 兼容，有时能通过对接口的版本管理解决。
比如：`Interface* queryInterface(int version)`提供一套 queryInterface 接口，可通过版本号获取对应的接口。这样使用旧版本接口的程序仍能工作，新版本程序也可以用新接口。

影响 ABI 兼容性的因素中，除了调用约定和架构外，很多都是 C++ 带来的问题（语言特性和不同编译器），C 本身没有，因此 C++ 程序更难做到二进制兼容。
因此对 C++ 来说 ABI 可以分为两方面：语言/编译器 ABI；库本身的 ABI。

**C++ 的 ABI 标准**

ABI 规定了代码怎样变成二进制文件，但 C++ 标准没有规定 ABI，只是定义了少数规则。
所以 C++ 编译器自己也有一套 ABI 规则（微软 x64 和 System V ABI 主要是针对 C 的 ABI？）。只要编译器遵循同一标准，那么生成的二进制文件基本就是二进制兼容的。

目前 C++ 有两套主流 ABI 标准：

- [Intel Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html)，gcc 和 clang 使用。
- MSVC ABI（不公开）。

> 有些编译器可以手动指定使用的 ABI，比如 windows 上的 clang `--target`。
>
> C++ 标准会尽可能保证 ABI 兼容性，但仍存在例外：
>
> - C++17 把 noexcept 异常说明作为了函数类型的一部分，这会影响函数生成的 mangling name。
> - C++20 引入的属性 no_unique_address。
>

Itanium C++ ABI 主要涉及4大方面：

1. 程序中的各种数据结构如何正确一致地在内存中布局 (Data Layout)（以及数据类型的大小和对齐）
2. 在二进制层面如何调用其他函数 (调用约定，Calling Convention)
3. 为 C++ 的异常处理机制提供正确的实现 (Exception Handling)
4. 输入到链接器的目标文件的格式 (Linkage & Object Files)

**开洞**

> https://zhuanlan.zhihu.com/p/348365662

有三种情况：

- 用户无法实现的。
    比如：type_info，有很高重载优先级的 initializer_list。
- 标准库难以实现，需要编译器暴露 intrinsics？
    比如：source_location，launder，constexpr 的 bit_cast，is_trivially_copyable。
- 可以实现，但是很难做好，编译器可以做的更好。
    比如：许多 type_traits，make_index_sequence，variant/tuple 在类型列表中获取某个类型，它们需要实例化大量模板，影响编译速度。

intrinsic 指某些用户代码无法实现的东西。大多用类似函数调用的语法，但语义上不被当成函数？
来自 rust：https://doc.rust-lang.org/std/intrinsics/index.html

**最大吞噬**

[*最大吞噬* (maximal munch principle)](https://zh.cppreference.com/w/cpp/language/translation_phases)：词法分析器会读取尽量多的字符，来构成一个有效的 token，即使这可能导致后续的分析失败（例外情况见 ref）。

例：

```cpp
a+++++b; // 编译器当成了 a++ ++ +b
// 正确：a++ + ++b;

int m = n/*p; // 编译器将/*当成了注释
// 正确：int m = n / *p;

void f(const char *= nullptr); // 当成了复合运算符*=
// 正确：void f(const char * = nullptr);
```

**独立实现**与**宿主实现**

C++ 标准规定了[两种实现](https://zh.cppreference.com/w/cpp/freestanding)：独立 (freestanding) 与宿主 (hosted) 实现。
独立实现的程序可能在没有操作系统的情况下运行，要求更宽松、支持的功能更少：标准不要求程序定义 main 函数，且只需要实现部分标准库头文件。







---

## 函数

**函数声明**

只要各个声明间没有冲突，函数可以声明多次，并且后面的声明可以为之前的声明补充默认实参（前提是该实参后的实参都已定义默认值）。

```cpp
void f(int, int = 2);
void f(int = 1, int);
void f(int a, int b) {
	cout << a << b;
}
f(); // ok
```

**形参与实参**

函数调用时，形参会通过实参进行初始化：如果是传值（按值绑定实参），则对于每个实参 e 通过 forward<E>(e) 直接非列表初始化一个 decay_t<E> 类型的子对象作为实际的参数。

**成员函数**

成员函数与普通函数不太一样，不能隐式转换成函数指针，需要显式加 &，在调用时要传 this。

创建 thread 执行成员函数：

```cpp
thread t{&func, this, args};  // 可能需要为 &Class::func
// 或者用 lambda
thread t{[this]{ func(args); }};
```

**函数指针**

*成员函数指针* 见 *C++ - 成员指针*。

表达式可分为两种：数值表达式、类型表达式。类型表达式可分为两种：数值类型表达式、函数类型表达式。
`int(int)`就是一个函数类型表达式，可用于声明函数，如：

```cpp
int f(int x) // int(int) 类型的函数
{ return x; }
int g(int x) // int(int) 类型的函数
{ return x + 1; }
int h(int func(int), int x) // 形参是 int(int) 类型的函数
{ return func(x); }
int main() {
	h(f, 1); // 1
    h(g, 1); // 2
}
```

`int *a(int)`是一个函数签名，该函数接收一个 int 参数，返回 int*。
（函数签名：一个函数的信息，如函数名、输入输出等）
`int (*a)(int)`中 a 是一个函数指针（即`int(*)(int)`类型的变量），指向一个接收一个 int、返回 int 的函数（即`int(int)`类型的函数）。

注意，**非静态成员函数有一个 this 参数**，参数列表中需要加一个`ClassName&`。

```cpp
// 4种定义函数指针的方法。&f前的&可不写，会隐式转换为函数的指针。
int (*p)(int) = &f; // 1
typedef int (*)(int) Fn; // 2
typedef int (*Fn)(int); // 2-2
using Fn = int(*)(int); // 3
Fn p = &f;
auto p = &f; // 4
```

> 为什么用函数指针变量，不直接用`int(int)`的函数类型变量？
> 因为在C++中，函数类型不是一等公民 ，大概就是不能直接复制一个函数，因此在传递参数的时候只能用指向这个函数的指针来代替它。

**函数类型**

函数的类型由以下几点决定，如果它们都相同则函数类型相同：

- 返回值类型是否相同。
- 所有形参类型是否相同：确定每个形参的类型（就是声明中的类型），然后将“T 类型数组”和“函数类型 T”的参数类型替换成“T 类型指针”，然后将 top-level 的 cv 修饰符去除，得到参数类型列表。（可见 *C++ - top-level const*）
- 是否有 noexcept（C++17 起）。
- （对于非静态成员函数）cv 限定 (4种) 和引用限定 (3种)。

所以`int(*)(const int, decltype(p)*)`和`int(*)(int, const int*)`是相同的类型， `void(int)`和`void(const int)`相同，而`is_same_v<void(int*), void(const int*)>`是 false。

> 对一种类型 T，可以产生 48 种函数形参类型 (?)：有无引用 (3)、有无 volatile (2)、有无 const (2)、有无 noexcept (2)、有无 variadic (2)（C 的变参）。

函数类型不影响重载，它由函数签名决定。

> 注意函数类型本身不存在 cv 限定，函数或返回值的那个 cv 限定是函数的一部分，不是修饰函数类型的 cv。给函数类型添加的 cv 会被忽略。
>
> 函数类型会被 mangle，所以上面这些都会出现在 mangle 后的名字中。
>
> 因为在确定函数类型时，会进行数组和函数类型到指针的转换，并去除顶层 cv，所以`f(char(*)[2])`与`f(char[3][2])`、`g(const int)`与`g(int)`是同一个函数：它们的函数类型相同，名字也相同。

**函数签名** / **(function signature)**

函数签名包含一个函数的信息，包括：函数名、参数类型、参数个数、函数限定符（cv, 引用）、所在类和命名空间等。
编译器将源代码编译成目标文件时，~~用函数签名的信息对函数名进行改编，~~会用函数类型而非函数签名来形成修饰名（符号修饰，见 *基础 - name mangling*）。

如果两个同名函数签名不同，则可重载。
（对 C++）签名中不包含返回值类型，所以只有返回类型不同的函数不能形成重载。
不包含异常说明（是否 noexcept）。

> 通过模板特化可以实现多个只有返回值不同的函数，但这不是重载。
> 如：`template<class T> T func() {return T{};}`、`template<class T> auto func() {return T{};}`。

**invocable** **regular_invocable**

[invocable 与 regular_invocable](https://zh.cppreference.com/w/cpp/concepts/invocable) 是 C++20 引入的 concept。
`invocable<F, Args...>`表示类型 F 是能通过`std::invoke(args...)`调用的可调用类型。
`regular_invocable`除了蕴函 invocable 外，还要求调用必须*保持相等性*，且不会修改可调用对象本身和实参。

谓词约束 [predicate](https://zh.cppreference.com/w/cpp/concepts/predicate) 是典型的 regular_invocable：谓词是无状态的（对相同实参不能第一次判断成功、第二次失败；使用时无需移动、可随意拷贝）。

**保持相等性**

[保持相等性 (equality-preserving)](https://zh.cppreference.com/w/cpp/concepts) 指表达式在输入不变时，输出也一定相等。与纯函数类似。

**仿函数 (functor)**

重载了`operator()`的类称为 functor，**这种类的对象**不仅能像函数一样调用，还可以拥有额外状态。
函数指针、function、仿函数都是[*函数对象*](https://zh.cppreference.com/w/cpp/named_req/FunctionObject)，可被调用 ([callable](https://zh.cppreference.com/w/cpp/named_req/Callable))（函数本身不是对象，自然也不是函数对象）。
通过仿函数类对象调用 operator () 时不需要传递 this；通过函数成员指针调用函数时需要传递 this。

注意如果仿函数 f 带模板参数，那`f<int>(1)`是不行的，这与函数不同。因为模板参数是在类的 operator() 上，而非在类上，所以要用重载运算符的方式调用。
[重载的运算符](https://zh.cppreference.com/w/cpp/language/operators)可作为成员函数调用，比如：`f.operator()(1);`。如果有模板参数，则需要用 template 消歧义（见[链接](https://zh.cppreference.com/w/cpp/language/dependent_name)最下），如：`f.template operator()<int>(1)`。

例：找出数组中的 x 的倍数：

```cpp
struct Rule {
    int x;
    int& cnt;
    Rule(const int& x, int& cnt): x(x), cnt(cnt) {}
    bool operator()(int num) const { // 对于类应该是const T&
        ++cnt;
        return num % x == 0;
    }
};
int a[5] = {1, 3, 5, 7, 9};
int cnt = 0;
Rule rule(3, cnt);
std::find_if(a, a+5, rule);
```

注：find_if 需要传入一个[谓词](https://zh.cppreference.com/w/cpp/named_req/Predicate)。

返回 bool 的函数、函数指针、仿函数都可以作为 sort 比较的规则，比如[less](https://zh.cppreference.com/w/cpp/utility/functional/less)就是一个仿函数：

```cpp
template<typename T>
struct Less {
	constexpr bool operator ()(const T& a, const T& b) const {
		return a < b;
	}
};
```

**move_only_function**

> function 能保存、复制、调用任何**可复制构造的**可调用对象。
> move_only_function 能保存、复制、调用任何**可构造的** move-only 可调用对象。
>
> 调用空的 function 会抛出 std::bad_function_call 异常，但调用空的 move_only_function 是 UB。

[move_only_function](https://zh.cppreference.com/w/cpp/utility/functional/move_only_function) 与 function 类似，能保存所有可调用对象，但要求保存的对象是 move-only 的。
function 满足可复制构造（包括可移动构造）与可复制赋值（包括可移动赋值）；move_only_function 只满足可移动构造与可移动赋值，不满足可复制构造与可复制赋值。

```cpp
function<void(void)> f1, f2 = std::move(f1), f3 = f1; // ok
move_only_function<void(void)> f1, f2 = std::move(f1); // ok
	// f3 = f1; // error: 不可拷贝
```

由于 function 必须满足可复制构造与赋值，因此其保存的对象（即捕获的变量）也必须是可复制的，不能是 move-only 的，比如：unique_ptr。
move_only_function 没有要求，只要对象可构造即可（拷贝或移动）。

```cpp
struct MoveOnly {
	MoveOnly() {}
	MoveOnly(MoveOnly&&) {}
};
MoveOnly m;
function<void()> f1 = [m = std::move(m)]() {}; // error
function<void()> f2 = [a = make_unique<int>(2)]() {}; // error

template <class... T>
using mof = std::move_only_function<T...>;
mof<void()> f1 = [m = std::move(m)]() {}; // ok
mof<void()> f2 = [a = make_unique<int>(2)]() {}; // ok
```

此外 move_only_function 的模板参数中可以加*成员函数限定符*，只有在当前 move_only_function 对象满足限定符时（类似 this），才可调用，否则 CE。function 则不能加限定符。

```cpp
// CE: const 对象不能调用非 const 函数
const mof<void()> f1 = [](){};
f1();
// ok
const mof<void() const> f2 = [](){};
f2();

// CE: 不能赋值一个非 noexcept 的函数
mof<void() noexcept> f1 = [](){};
f1();
// ok
mof<void() noexcept> f2 = []() noexcept {};
f2();
```

> const 的 move_only_function 不能通过 move 赋值给其它 mof，因为它是 const&&，赋值时仍要拷贝。
>
> 复制一个类时，要复制它保存的所有对象，因此需要对象都可复制；而移动一个类时，复制还是移动它的对象都可以，甚至可以将对象保存在资源块内、直接移动资源块，不触发对象的复制或移动，因此只需要对象可构造。

**function**

[std::function](https://zh.cppreference.com/w/cpp/utility/functional/function) 是一个函数包装器模板类，可将所有的[可调用对象](https://zh.cppreference.com/w/cpp/named_req/Callable)抽象成一个 function，简化回调函数。包括：（成员）函数指针、成员对象指针（数据成员指针）、仿函数 (包括 lambda)、bind 表达式。（function 本身也是仿函数）
C 函数指针只能保存普通函数，不能保存成员函数指针和仿函数及其状态（即闭包），function 可以。

function 效率略低：

- 为了实现动态绑定（能保存所有可调用对象。function 不需要擦除函数的类型），需要通过函数指针间接调用对象（如果实现的不好，**约等于调虚函数**。好的实现可以避免使用虚函数）。
- 它其实是函数的一份拷贝。对于有捕获 lambda 等有状态的函数，它需要拷贝捕获的变量（lambda 值捕获会拷贝一次，赋给 function 又会拷贝一次）。
    此外，它本身不知道有多大的数据被捕获，它的生命周期也不一定与保存的可调用对象相同（可以更长），所以**需要在堆上为捕获的变量分配空间**（new）。
    不过 function 有 SSO (small size optimization) 优化，一般在捕获对象大小不超过两个指针、且满足一些条件（可平凡拷贝等）时，将其分配在栈上，不动态分配。
    （普通函数指针大小为 8B，成员函数指针为 16B，lambda 或仿函数取决于捕获的变量多少）
- 普通函数和 lambda 可以被内联以提高效率，但 function 是动态的**不能内联**（不过调 operator () 这个函数可以内联）。
- 构造析构和拷贝可能有较大开销，这与普通对象类似，所以该传引用的地方传引用。

所以如果没必要（只在作用域内使用），或可方便传递 lambda（函数需要通过模板传递 lambda，因为类型是匿名的），可以考虑不使用 function（但模板函数需要在头文件中就给出实现）。
**滥用 function 可能会有性能问题**（lambda 用 auto 获取类型即可）。

如果可以，也可以使用 *function_ref*。
使用模板参数替换 function，并用 concept 限制实参的函数类型，也能做到接收任意可调用对象，提高一点点效率，但很麻烦没必要。

> 避免动态分配的一种方式是：如果 lambda 捕获的变量太大，就用一个新的 lambda 去引用捕获旧的 lambda，保存在 function 里，这样捕获的变量只有 8B 不需要动态分配。但 function 不能在函数返回后使用，因为捕获的变量还在旧的局部 lambda 中。
> 其它方法见上链接。
>
> 源码分析：https://www.zhihu.com/question/314660217/answer/2658608964

例（见 *Codes - C++ - function*）：

```cpp
// #1 存储普通函数指针
int add(int x) {
	return x + 1;
}
function<int (int)> f_add = add;
cout << f_add(1) << '\n';

// #2 存储成员函数指针
// 注意成员指针有一个指向当前实例的参数！如果想忽略需要用bind，在里面绑定某个实例
struct Node {
	Node(int x): x(x) {}
	int f(int v) {
		cout << "Node::f(" << v << ") x:" << x << '\n';
		return x;
	}
	int const_f(int v) const {
		cout << "Node::const_f(" << v << ") x:" << x << '\n';
		return x;
	}
	int x;
};
Node node{1};
function<int (Node&, int)> fp = &Node::f; // 通过Node&实例调用（也可以是const Node&）
cout << fp(node, 2) << '\n';

function<int (const Node&, int)> fpc = &Node::const_f; // 通过const Node&实例调用
cout << fpc(1, 2) << '\n'; // 右值可以绑定到const左值引用

// #3 存储数据成员指针
function<int& (Node&)> fr = &Node::x; // 也可以是 int (const Node&)
cout << fr(node) << '\n'; // 1
fr(node) = 3;
cout << node.x << '\n'; // 3

// #4 存储仿函数
function<int (int)> ff = Func();
cout << ff(3) << '\n'; // 4
```

可以用虚函数来接收不同可调用对象，以实现类型擦除和 function（但效率略低，实际并不这样？）。实现可见 *Codes - C++ - any、function*。

```cpp
// 特化前需要先声明模板类，但无需实现
template<typename>
class Function;

// 特化，指定模板参数的格式为R(Args...)
template<typename R, typename... Args> // 返回值与参数列表
class Function<R(Args...)>;
```

> 从 *Codes - function* 的实现中可以看出，其内部保存了一个函数指针。在调用仿函数即调用它的 operator () 时，参数会通过 forward 传递给函数指针。
> function<Ret(Args...)> 定义中的模板参数类型，是 operator () 返回值和参数的类型，并非保存的函数指针 fp 的参数类型，两者不需要完全匹配。能接收的类型取决于 function 的定义：只要传入的实参能匹配 Args...，且 Args... 和 Ret 均能隐式转换到 fp 的参数类型和返回值类型，就不会编译错误。
>
>```cpp
> // ok，int 可隐式转换到 const int&
> function<int(int,int)> f = [](const int &a, const int &b) {return a+b;}
> // ok，float、double 可分别隐式转换到 int、long
> std::function<double(float)> f = [](int x) -> long {
> return x;
>  };
> cout << f(1.2f); // 1
> ```

> 虽然它能够传入 lambda 表达式生成的匿名结构体，以便调用，但两者并不相同。
>
> 注意，**如果 function 的返回类型为引用，并赋值一个没有声明返回类型（无尾随返回类型）的 lambda**，由于返回类型由 auto 推导，其实际返回值将是一个纯右值，而非引用，其生命周期限制在`function::operator()`内，因此 function 将返回悬垂引用。
>
> ```cpp
> function<const int&()> F([] { return 3; }); // UB，返回悬垂引用。C++23起将直接错误
> function<const int&()> F([] -> const int& { return 3; }); // ok
> ```

**lambda**

> 过长的 lambda 可能不是好选择，用 static 或在匿名空间定义一个新函数可能更好。
> 不管是函数还是 lambda，最好都别过长，可拆分成多个函数/多个 lambda。
>
> ~~lambda 会生成一个类，并在调用时传一个 this，所以在大量使用时，会略微影响内存和效率。~~
> lambda 本身只在作用域内生效，当其捕获的变量较少时，是直接分配在栈上的（捕获的多仍然要动态分配）。
> 但总得来说，lambda 和普通函数相比差别不大（只要逻辑功能一致）。
>
> 一般无状态的 lambda 没必要设成 static，编译器可以直接把这个栈对象的分配优化掉，直接内联 operator ()。

[lambda 表达式](https://zh.cppreference.com/w/cpp/language/lambda)用于定义匿名函数。与来自 C 的函数指针、仿函数，是定义可调用对象的不同方式。
相比常规函数，lambda 表达式可以直接看到上下文，更灵活和简洁，可读性也更强。
适用于函数比较简单，逻辑不需要复用的情况。

语法为：`[captures](params) -> return_type { body };`
或：`[捕获列表] (函数参数) 说明符 异常说明 -> 返回值类型 {函数体}`
说明符包括：mutable、constexpr（C++17。如果可以则会自动 constexpr）、consteval（C++20）、static（C++23）。
异常说明为 noexcept 说明符。

捕获列表用来说明外部变量的使用方式，表示函数体中用到的、定义在外面的变量是怎么被传入，在函数体中是否能被修改。说明符可以是 = 或 &（称为默认捕获符），= 表示值传递/复制捕获，不会修改原对象（如果不声明 mutable，也无法修改拷贝的对象）；& 表示引用捕获，可以直接修改。
包括 5 种格式：

1. []：不捕获任何变量。
2. [=]：按值传递的方法捕获 odr 使用到的自动存储期变量。
3. [&]：按引用传递的方法捕获 odr 使用到的自动存储期变量。
4. [=, &a, &b]：按引用捕获变量a, b，但按值捕获使用到的其它自动存储期变量。
5. [&, a]：但按值捕获变量a，但按引用捕获使用到的其它自动存储期变量。

不建议使用 2, 3，更推荐显式写出所有变量的捕获方式。

> 块作用域中的 lambda 函数仅能捕获父作用域中的自动存储期变量。非局部变量（也不能捕获）、常量表达式初始化的引用、const 且非 volatile 的整型/枚举已初始化变量，不需要捕获（直接用就可，可直接影响该变量，即使是`[=]`，因为根本不捕获；但只要不是非局部变量，`[=]`也可能会捕获它；对于第三者，只是在读取它的值时不需要捕获，如果对它进行其它使用 (如取地址) 还是要）。
> 块作用域以外的 lambda 函数的捕获列表必须为空。
>
> lambda 实际是结构体，所以也有大小，取决于捕获的变量。没有就是空类，大小为 1。
> 当捕获一个 bool 变量时，大小也为 1。

> 当 lambda 位于成员函数中时，只要捕获列表出现了 = 或 &（无论哪种形式），就会隐式引用捕获当前对象/值捕获 this（即`[=/&]`相当于`[=/&, this]`）。
> C++20 起，使用 = 时不再会隐式捕获当前对象，需要`[=, this]`。
>
> 捕获 this 后，会获得与 this 一样的成员访问权限：读写成员变量、调用成员函数（如果是 *this 复制捕获则无法修改）。
> 不能直接捕获成员变量，只能通过捕获 this 来使用成员变量。
> 也可以显式捕获 this 或 *this。注意，**值捕获 this 相当于引用捕获当前对象（注意 this 是指针），值捕获 *this 相当于复制捕获当前对象**（但 C++17 起才有）。没有 &this。
>
> 但注意 lambda 可以被传到类外，需要保证使用时 this 指向的对象没有被销毁；多线程中也要保证 lambda 执行时对象没有被销毁。可以用 shared_ptr 和 enable_shared_from_this 。
>
> 被 lambda 捕获的实体会被 ODR 使用。如果捕获的实体不可被 ODR 使用，则程序非良构。

除了捕获列表和函数体外，其它都可以忽略（但 C++23 前，在有 mutable 的情况下，参数`()`不可忽略，即使为空）（返回值类型可以自动推导。注意推导时不会进行隐式转换，返回两个能转换但不同的类型无法推导）。

**默认情况下，lambda 函数（指 operator ()）是 const 函数，不能修改值捕获的对象**。但引用捕获的可以，因为 const 不会限制引用和指针成员指向值的修改，它们始终是非 const 的（除非引用指向的是 const 对象，比如 const int&，这与指针 const int* 是一样的）。
mutable 可以去除它的 const 属性。

例：

```cpp
auto plus = [] (int x, int y) -> int { return x + y; }
int sum = plus(1, 2);

// 一元运算符需要接收一个指针，所以可便于推导成函数指针（当然需要lambda不捕获）
auto p = +[] {return 1;};

// 捕获this，以访问类成员。this不能引用捕获
class Foo {
 public:
  Foo(const string& s, int i) : s_(s), i_(i) {}
  void Update(const string& s, int i) {
    auto do_update = [this, &s, i](){
      s_ = s;
      i_ = i;
    };
    do_update();
  }
 private:
  std::string s_;
  int i_;
};
```

C++14 起可以在捕获时带初始化器，不仅能用新的名字指代捕获变量，还可以 move 捕获的变量（C++14 前也不允许直接捕获 move-only 对象）。也可以定义一个状态变量、不用 static。

```cpp
// #1 重命名
auto cnt =
    std::count_if(books.begin(), books.end(), [v = target](const Book& book) { // 或 &v = target
        return book.title.find(v) != std::string::npos;
    });

// #2 移动对象
std::unique_ptr<int> uptr = std::make_unique<int>(123);
auto callback = [uptr = std::move(uptr)]() { // 移动捕获的变量到lambda内的参数。
    // 引用捕获并不适合，因为lambda的生命周期很可能和uptr不一致
    cout << *uptr << std::endl;
};

// #3 获取指针
auto cnt =
    std::count_if(books.begin(), books.end(), [p = &target](const Book& book) {
        return book.title.find(*p) != std::string::npos;
    });

// #4 定义和初始化参数，让它更像函数
// 它没有捕获任何变量，实际上是定义了 static int x, y;
auto f = [x{0}, y = 1] mutable {
    return (x++) + y; // 生成器
};

// #5 捕获const引用
auto f = [&r = std::as_const(x)] {}; // C++17起，as_const可将参数转为const左值引用

// #6 C++20起可以使用`...标识符 初始化器`初始化形参包
template<class... Args>
void f_(Args&&... args) {
	[... args = std::forward<Args>(args)] {g(args...); }();
}
// 这之前形参包不能完美转发
template<class... Args>
void f(Args&&... args) {
	[args...] { g(args...); }();
}
```

> 用 lambda 值捕获 shared_ptr<T> 时要注意，lambda 内部会拷贝一个 shared_ptr 使用，导致引用计数增加；而且会保存在生成的结构体内，不会随函数的结束而释放。所以如果 T 保存了这个 lambda，就会产生自引用：T 内包含一个指向自己的 shared_ptr，保存在 lambda 内。然后会导致内存泄露（例子见[这里](https://floating.io/2017/07/lambda-shared_ptr-memory-leak/)）。
> 这种情况下可以用 weak_ptr：lambda 捕获 weak_ptr，在函数体内使用时 lock 转为 shared_ptr，函数结束后就会释放了。

**lambda 的类型**

**虽然仿函数、lambda 能像普通函数一样用，但它们的类型并不是函数类型**（比如`void()`、`int(int, int)`，is_same 结果是 false）。
`void()`类型只是代表普通函数，只是在 lambda 没有捕获变量时，允许转换成函数指针。
`std::function<void()>`能接收任意的 lambda，但它是一个模板类，与 lambda 原本的类型（一个匿名结构体）并不相同。它在构造函数里有个模板参数，即使`void()`并不是 lambda 类型，也还是能传入仿函数与 lambda（见*function*）。

> 当 lambda 没有捕获任何变量时，可以隐式转换为函数指针（编译器会为该类生成到函数指针的转换函数），比如上面的代码可以写成：`int (*plus)(int, int) = [](int x, int y) -> int { return x + y; } `。
> 但它的实际类型是一个仿函数结构体，以在里面存放捕获到的变量（函数指针也是成员之一）。只要捕获了变量，就不能赋给一个标准函数指针，需要用`std::function<int(int, int)> plus = [=]...`或`auto`（但两者的类型并不相同，只有 auto 是原本的 lambda 类型）。
>
> lambda 一般没必要转为 function，会有性能损失。

每个 lambda 表达式都会生成一个唯一的、不具名的非联合类的实例，其类型叫做闭包类型 (closure type)，用来保存捕获到的变量。
这个类是一个*仿函数*，其名称为 lambda + 唯一uuid。因此 lambda 对象之间不能相互赋值，即使看起来类型相同。
可在 cppinsights 上测试。

如果函数体内有 static 变量，则也存在该结构体内，因此每次调用该 lambda 都会使用同一个 static 变量（当然任何捕获的变量使用的都是同一个变量，这和其它语言的闭包一样）。

**lambda 其它**

> https://zh.cppreference.com/w/cpp/language/lambda

- lambda 内部可以嵌套定义其它 lambda，以便使用甚至返回。
- 当参数类型为 auto 时，将生成*泛型 lambda*，auto 会被 operator () 函数上的模板参数替代，从而允许接收不同类型。(C++14)
    也可以使用形参包`[](auto... args) {}`。
- lambda 类型是一个仿函数，因此也可以被继承或传入模板。

```cpp
// #1 继承lambda
// 需要C++20，否则不允许在未计算的表达式中使用lambda
struct F: decltype([] { cout << "F\n"; }) {}; // 不过没什么用，因为没法using基类的operator()

// #2 模板继承多个lambda，即实现多个operator()
template<class... Ts>
struct overloaded: Ts... {
	using Ts::operator()...; // C++17 起
};
auto c = overloaded {
    [](int arg) { cout << arg << ' '; },
    [](double arg) { cout << arg << ' '; },
    [](auto arg) { cout << arg << ' '; }
};
c(10);
c(1.2);
c("qwq");

// C++17需要加上推导指引，20前无法完成推导
template<class... Ts>
overloaded(Ts...) -> overloaded<Ts...>;
```

类模板推导指引 (CTAD)：

- 可以用`new auto(lambda)`创建一个指向 lambda 类的指针。

- lambda 可以捕获形参包。

```cpp
template<class... Args>
void f(Args... args) {
	auto lm = [&args...] {  };
	std::cout << sizeof lm << '\n';
}
f(1, 1.f); // 捕获2个变量，输出16
```

**泛型 lambda**

C++14 起可以指定 lambda 的形参类型为 auto，创建泛型 lambda。
C++20 起才可以为 lambda 显式指定模板参数。

```cpp
// C++20
auto f = [] <typename T> (const vector<T>& v) {
    cout << size(v);
};
```

**递归 lambda**

> 静态语言中，对于函数的类型检查往往都是基于“结构”的：只要参数类型、返回值类型都相同，就认为是同一个函数，即使函数名可能不同。
> 因此在写递归时，比如`f(int x) {return f(x);}`，编译器想要检查返回值类型，就要一层层展开 f，导致无限循环。
> 这个问题的解决方式有两种：
>
> - 将函数的类型检查改为基于“命名”的：不同名字的函数或对象就具有不同的类型，不需要检查参数和返回值类型。
>
> 结构体就是这样的，所以才能写出链表这种 在结构体内保存该结构体指针的 结构体。
> 所以只要用结构体去实现函数（即仿函数），就能将函数的类型检查变成基于“命名”的，从而能够递归。
> lambda 也是结构体，因此是基于名义的，即使两个 lambda 各方面都相同，也是不同的类型。
>
> ```cpp
> struct F {
>     int limit;
>     template <typename T>
>         requires std::totally_ordered_with<T, int>
>     const F& operator()(T v) const & {
>         cout << v << " ";
>         if (v > limit) {
>             cout << '\n';
>             return *this; // 返回*this便于链式调用
>         }
>         return (*this)(v + 1); // 通过(*this)()调用函数以递归
>     }
> };
> F f{2};
> f(1)(2.0)('a');
> // 1 2 3
> // 2 3
> // a
> ```
>
> - 类型擦除，将函数的返回值改为 Any、Object 这种通用类型。
>
> （但是下面的代码还是不能执行）
>
> ```cpp
> std::any f(int v) {
>     cout << v << " ";
>     return f;
> }
>
> f(1);
> std::any_cast<std::any (*)(int)>(
>     std::any_cast<std::any (*)(int)>(f(1))(2))(3);
> ```
>
> 第一种方式对应递归类型 (recursive types) 中的 isorecursive types，在需要递归的处手动标记（这里就是给它取了特定的名字）。
> 第二种方式是动态语言的实现方式，其类型正确性在运行时检查。细节见[这里](https://www.zhihu.com/question/600355316)。

lambda 递归有几种方式：

- 将自身作为一个额外形参（比如`self`），递归时使用`self(self, ...)`（称为 y 组合子？）。
    （lambda 就是类，其类型在定义完成前就能确定，因此与成员函数有隐式实参 this 类似，只要在函数内加一个识别自身的参数就可以了）

```cpp
auto dfs = [&](auto&& self, int x) {
    if (x == destination)
        return true;
    vis[x] = true;
    for (int nxt : adj[x])
        if (!vis[nxt] && self(self, nxt))
            return true;
    return false;
};
// 为了使用时不需要写 dfs(dfs, x)，可以再封装一层
auto f = [](int x) {
    auto f = [](auto&& f, int x) -> int {
        return x ? f(f, x-1) : 1;
    };
    return f(f, x);
};
```

- 将 lambda 转为 function，引用捕获该对象名，递归 function。
    但因为 function 本身效率略低，频繁递归自然更低。

```cpp
function<void(int, int)> dfs = [&dfs](int x, int n) -> void {
    if (x > n) return;
    cout << x << ' ';
    dfs(x + 1, n);
};
```

- C++23 允许在参数列表中声明`this auto xxx`来指代当前函数。
    具体见 *C++23 - 显式对象形参*。代码：https://leetcode.cn/circle/discuss/nkNj76/

**function_ref**

> [function_ref]() 将在 C++26 中推出，在[该提案](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p0792r14.html)提出。
> 其大小为两个指针，不拥有可调用对象的所有权（类似 string_view），可以支持各种可调用类型。
> 当虚函数使用频率高、函数体短（即调用函数的代价占比高）、已知类型信息时，可直接保存函数指针，代替基类调用虚函数以提高性能。

function 不单单是函数指针，还可能包含函数的状态（捕获的变量）与虚函数调用，因此开销略大、可能包含动态分配。但普通函数指针无法保存（有捕获的）lambda 或仿函数。
类似 string_view，可以设计不包含函数所有权、只是简单使用的轻量级 function_ref，能够赋值任何可调用对象，但比 function 高效轻巧。它不负责函数捕获变量的生命周期，一定要在引用值的生命周期内使用。

实现见 *Codes - C++ - function_ref*。
void* 可以保存一切指针，但还需要保存、恢复函数的类型信息。而模板参数会作为模板定义类型的一部分，以便使用，因此可以保存一个模板函数或模板类，将函数类型放在模板参数上，模板内部将 void* 指针转为模板参数（即原本函数）的类型返回或直接调用。

**bind**

> 传引用时见 *thread 传递引用参数*。

TODO
https://zh.cppreference.com/w/cpp/utility/functional/bind
https://abseil.io/tips/108
https://stackoverflow.com/questions/62807743/why-use-stdbind-front-over-lambdas-in-c20

bind 就是预先填充好一部分参数，得到一个只用传剩下参数的可调用对象。常用于调用成员函数，因为需要传 this。

C++20 引入了 bind_front，

> bind 也是生成一个 functor，其中保存了函数指针和已传入的实参（不含 placeholder），operator () 会调用函数和传入实参。
> 如果需要传进去实参异步调用然后释放旧实参，可以 move 实参进去（会被保存到 functor 内）。
>
> 注意，虽然 bind 更简洁，但它会保存函数指针，导致比 lambda 对象略大（lambda 会在 operator () 内写出要调用的函数，不需要保存）；当需要通过 *function* 保存函数对象时，应使用 lambda 而非 bind，因为 function 的 SSO：1. 在 function 保存的函数对象较大时（通常为大于 16B）不可用；2. 在对象不是可平凡拷贝时不可用，而 bind 就是不可平凡拷贝的。所以将 bind 传入 function 需要动态分配内存来保存 bind 函数对象。
> 所以应尽可能使用 lambda 代替 bind？见[这里](https://www.zhihu.com/question/38097768)。
>
> 但如果向 function 传递`ref(bind_obj)`或`ref(lam_obj)`，则不管 bind 或 lambda 对象有多大，都不需要动态分配。
>
> ```cpp
> void* operator new(size_t size) {
> 	cout << "new: " << size << '\n';
> 	if (void* ptr = std::malloc(size)) return ptr;
>  throw std::bad_alloc{};
> }
> void operator delete(void* ptr, size_t size) noexcept {
> 	cout << "delete: " << size << '\n';
> 	std::free(ptr);
> }
>
> void f(function<void(int)> func) {
> 	func(1);
> }
> void g(int x) {
> 	cout << x;
> }
>
> auto b = bind(g, std::placeholders::_1);
> f(b); // 调用 new 分配 16B
> f(std::ref(b)); // 不调用 new
> f([](int x) { g(x); }); // 不调用 new
> cout << sizeof(b) << ' ' << sizeof([](int x) { g(x); }) << '\n'; // 16 1
> ```

invoke？

**显式弃置**

通过定义特殊的重载函数，并将其声明为`= delete`，可以避免不希望的隐式转换。
如：`void f(int);`可以通过`f(1.0)`调用，但加上`void f(double) = delete;`重载，`f(1.0)`将匹配该弃置的函数，避免隐式转换。

**函数的默认参数**

> https://timsong-cpp.github.io/cppwp/n4659/dcl.fct.default#9

- 默认参数不需要是常量，它在每次函数调用时，都会进行一次求值。

```cpp
int x{0};
int g() {
	return x++;
}
void f(int v = g()) { // int v = x++ 效果一样
	printf("%d\n", v);
}
f(); // 0
f(-1); // -1
f(); // 1
```

- 函数的其它参数 不能出现在默认参数的求值表达式中。
- 如果函数是成员函数，则类的非静态变量 不能出现在默认参数的求值表达式中。
    因为在求值时，类对象 (*this) 还不存在。

```cpp
struct A {
    int a;
    static int b;
	void f(int v = a++) {} // error
	void f(int v = b++) {} // ok
};
int A::b = 0;
```



















---

## 多线程

**数据竞争**

当某个表达式的求值写入某个内存位置，而另一表达式求值读或写同一内存位置时，称这两个表达式冲突。拥有两个冲突的求值的程序存在[数据竞争](https://zh.cppreference.com/w/cpp/language/multithread)，除非满足以下条件之一：

- 两个求值都在同一线程，或者在同一信号处理函数中执行。
- 两个冲突的求值都是原子操作（atomic）。
- 其中的一个求值早于另一个发生（memory_order）。

如果出现数据竞争，那么程序的行为未定义。

> C++11 起，标准要求：库版本的 operator new 和 operator delete 是线程安全的；用户定义的全局 operator new 和 operator delete 是线程安全的（需要自己保证）。即非自定义的内存分配和释放是线程安全的。
>
> 注意不要在临界区内将共享数据的指针或引用传递给临界区外的变量。

**thread**

线程 [thread](https://zh.cppreference.com/w/cpp/thread/thread/thread) 可通过`thread()`、`thread(thread&&)`和`thread(Callable&&, Args&&...)`创建，除了无参构造外，其它构造均会创建新的线程并与 thread 对象关联。

> 调用非静态成员函数时，需要取成员函数指针作为函数对象，然后传入 this，比如：`thread(&A::f, this, args)`（如果在类外，则用 &x 获取指针替代 this）。
>
> 函数模板不是函数，它不能直接传入 thread 然后传递其它参数调用。可以用 lambda 封装调用模板的语句再传递。
>
> ```cpp
> template <class R, class...Ts, class...Args>
>     requires invocable<packaged_task<R(Ts...)>&, Args...>
> void async_task(packaged_task<R(Ts...)>& task, Args&&...args) {
>         task(forward<Args>(args)...);
> }
> thread t{ [&] { async_task(task, x); } };
> ```

通过创建 thread 对象 t 创建线程后，t 会与新线程关联，此时 t.joinable() 为 true。当 t 被移动、join 或 detach 后会与创建的线程取消关联，此时 t.joinable() 为 false，不可再调用 join。
如果线程对象 t 在与某个线程关联的情况下直接析构，会调用 std::terminate 异常退出。因此通过创建 thread 对象 t 创建新的线程后，必须 t.join 等待关联的线程执行完成，或者 detach 关联的线程。

线程对象 (std::thread) 持有线程，管理线程对象就是在管理线程。

> 无参构造`thread()`会创建不表示线程的 thread 对象，这样创建的对象也不会与当前线程关联。
>
> 注意，如果创建 thread t 到 t.join 之间可能抛出异常，则需要在 catch 中调用 t.join，避免 join 不会被执行。
>
> 可以用 RAII 来创建线程、保证 join 被执行。线程也是一种系统资源。
> 这其实就是 C++20 引入的 jthread，会在析构时调用 join。
>
> ```cpp
> class thread_guard{
>  thread& t;
> public:
>  explicit thread_guard(thread& t): t{t} {}
>  ~thread_guard(){
>      if (t.joinable()) { // 线程对象当前关联了活跃线程
>          t.join();
>      }
>  }
>  thread_guard(const thread_guard&) = delete; // 阻止拷贝与移动
>  thread_guard& operator=(const thread_guard&) = delete;
> };
>
> thread t{ callable{n},10 };
> thread_guard tg(t);
> // 即使抛出异常，t.join 也会在 tg 析构时被调用
> ```

thread 不可复制，所以两个 thread 对象不能拥有同一个线程。可以通过移动将一个 thread 对象的线程资源所有权转移给另一个 thread 对象。

可以在函数内启动线程，然后返回 thread 对象。只需要确保在返回后 join 即可。

```cpp
thread f(){
    thread t{ [] {} };
    return t;
}
// 这个函数调用表达式是纯右值，所以会移动到 t 对象中。C++17 起不需要移动
thread t = f();
t.join();
```

> thread 其实就是创建线程，然后获取一个用来 join 线程的 handle。因为 join 只能调用一次，所以是唯一所有权、不可拷贝。
>
> std::thread 内有一个静态函数 hardware_concurrency()，返回实现理论支持的并发线程数，可用作参考。
> 一台机器可并行执行的线程一般取决于核数，但可能会因为超线程技术多于该值。

**thread 传递引用参数**

需要向 thread 的函数对象传递参数时，只需要传递给 thread 的构造函数。
注意，当函数对象的参数是引用类型时，向 thread 传递该参数并不会按引用传递，而是会值传递、产生复制；并且此时参数的引用类型只能是 const& 或 &&，不能是 &。这是*thread 实现* 导致的。

```cpp
void f(int, const int& n); // int& n 会 CE

int n = 1;
thread t(f, 3, n); // f 内的 n 的地址与这个 n 的地址不同，是不同变量
```

想要通过引用传递，需要使用 *std::ref* 或 *cref* 传递给 thread。此时也可使用 & 类型参数。

```cpp
void f(int, int& n);

int n = 1;
thread t(f, 3, std::ref(n)); // ok
```

ref 返回一个 reference_wrapper 对象，包装对象，并可以隐式转换为被包装对象的引用。

> thread 传参默认按值复制，必须使用 reference_wrapper 对象才能传递引用，因为内部会将保有的参数副本转换为右值表达式进行传递。这是为了支持 move-only 的类型，左值引用没办法引用右值表达式。所以如果不使用 std::ref，这里 void f(int&) 就会导致编译错误。
> *async*、*bind* 也是如此。
>
> 注意，**在多线程中传递引用非常容易出错**（所以使用 ref 显式写明也更好），更多会通过移动捕获（创建新对象但转移所有权）或 shared_ptr（使用引用计数安全共享所有权）来代替引用。
> **thread 调用的函数一般不要有引用参数，因为线程很容易访问已泄露的资源；如果想避免复制，可以用 move 传参数。**
>
> 原因：thread 会将形参拷贝到内部，在调用时进行传参（类似 lambda），但是它内部不包含任何引用（没有引用初始化。否则也无法移动），只会进行复制传值，所以需要用值对象包装引用才能传递引用。

**thread 实现** / **thread 传参方式**

TODO

https://mq-b.github.io/ModernCpp-ConcurrentProgramming-Tutorial/md/%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90/01thread%E7%9A%84%E6%9E%84%E9%80%A0%E4%B8%8E%E6%BA%90%E7%A0%81%E8%A7%A3%E6%9E%90.html

**join** **detach**

t.join 阻塞当前线程，直到与线程对象 t 关联的线程执行结束。
必须在 joinable 为 true 时才可调用，否则会抛 system_error。比如空的 thread 对象就是不可 join 的。

t.detach 使线程对象 t 与它创建的线程分离，允许线程独立执行，不再受 thread 对象管理。

通常不会使用 detach，线程应该确保所有创建的线程正常退出，释放所有资源并执行必要的清理操作。

**jthread**

[jthread](https://zh.cppreference.com/w/cpp/thread/jthread) 是 C++20 引入的线程对象。它与 thread 类似，但是会在析构时会调用 join，能在特定情况下取消/停止线程。

与 thread 相比，jthread 内部多一个 stop_source 成员，用于维护一个可共享的 stop_token。
jthread 不能实现强制、立刻的线程取消或暂停，也不能自动实现，需要用户在调用的函数中手动检查 stop_token 的状态，在 token 的 stop_requested() 为 true 时手动调用 return。
当用户通过 t.request_stop 请求停止线程时，会修改线程关联的 stop_token，使线程能提前返回。
本质上就是封装了一个共享的原子变量，用于标记是否停止执行。

**sleep_for**

[this_thread::sleep_for](https://zh.cppreference.com/w/cpp/thread/sleep_for) 阻塞当前线程，直到指定时间结束。

参数是 chrono 命名空间中的时间对象（如`std::chrono::seconds(3)`）。
如果支持 C++14，可以`using namespace std::chrono_literals;`然后直接使用时间字面量（如`3s`、`3min`）。

**yield**

[this_thread::yield](https://zh.cppreference.com/w/cpp/thread/yield) 建议实现暂时挂起当前线程、重新调度，以允许其它线程运行。

**共享状态**

async、promise 会创建一个共享状态，它包含一些状态信息和一个结果，结果可能尚未求值、已求值为一个值（可能为 void）、或求值为一个异常。
future 与一个共享状态关联，用于获取共享状态的结果。

**async**

当需要执行一个异步任务、不需要立刻获得它的结果时，可以使用 [async](https://zh.cppreference.com/w/cpp/thread/async) 函数创建线程执行。
它的调用方式与 std::thread 一样，支持任意函数对象，并可通过构造函数传递函数参数（传递方式也一样，引用需要使用 std::ref 传递）。
async 会返回 future<T> 对象，它与异步任务关联，将持有最终计算出的结果或抛出的异常。

> 标准没有规定它的实现，标准库可以启动新线程，也可以维护一个线程池。如果想要高效创建线程，还是要自己写线程池。
> async 的意义是提供一种简单的创建异步任务的方法，并保证一定性能，不需要自行创建和使用 thread（[参考](https://isocpp.org/wiki/faq/cpp11-library-concurrency#std-async)）。
> 所以普通任务可以随意选择 async 或 thread？

调用 async 时，可以传递两种启动策略之一：

- launch::async（异步）：在不同线程上异步执行任务。
- launch::deferred（推迟）：惰性求值，不创建线程，在调用线程首次明确请求结果时（调用 get, wait）再执行任务。

如果不指定，则同时传递两种策略（两个掩码或），将由实现选择哪个策略。可能的选择为：如果系统资源充足，并且异步任务的执行不会导致性能问题，那么系统可能选择在新线程中执行任务；如果系统资源有限，或者延迟执行可以提高性能或节省资源，那么系统可能选择延迟执行。

> 注意，async 有可能使用线程池实现（比如 MSVC），此时 threadlocal 变量将不会在 async 执行完后销毁（不要将 async 视作一定是某线程或线程池）。

**packaged_task**

[packaged_task](https://zh.cppreference.com/w/cpp/thread/packaged_task) 可以将任何可调用目标包装成任务对象，使得能够异步调用它。这样就不需要先创建 promise、获取 future、再向线程传递 promise 了。
当创建 thread 并且需要 promise 时，可以简化调用。

通过 operator () 执行存储的函数。它会将函数的返回值或抛出的异常存储在共享状态中。
通过 get_future 可以获取与该共享状态关联的 future 对象，从而获取返回值。只能调用一次。
get_future 必须在调用 operator () 前调用并赋值给一个 future 对象？

packaged_task 只可移动，不可复制。

```cpp
packaged_task<int(int, int)> task([](int a, int b){
    return std::pow(a, b);
});
future<int> future = task.get_future();

// 可以直接调用、同步执行
task(2, 3); // 同步执行任务
cout << future.get() << '\n'; // 已执行完成，不会堵塞

// 可以异步执行，用 future 获取结果
thread t{ move(task), 2, 3 };
// ...
t.join();
cout << future.get() << '\n'; // 不会阻塞。也可放在 t.join 前，会阻塞
```

**future**

[future](https://zh.cppreference.com/w/cpp/thread/future) 用来获取异步任务的返回值。其模板参数为异步任务的返回类型。

async 和 packaged_task 任务的调用会创建共享状态，并将其关联到返回的 future 对象中。共享状态包括返回值和抛出的异常。
如果 future 没有共享状态（valid() 为 false），则调用 get 或 wait 是 UB。
被移动的 future 没有共享状态。

可以通过 wait_for 或 wait_until 来等待指定时间。

> [future 的析构函数](https://zh.cppreference.com/w/cpp/thread/future/~future)会释放任何共享状态。该操作不会阻塞等待共享状态变为就绪，但若以下条件全为真，则它可能阻塞：
>
> - 共享状态是由对 std::async 的调用创建的。
> - 共享状态尚未就绪。
> - 当前对象是到共享状态的最后一个引用。
>
> 实践中，仅当任务的运行策略为 std::launch::async 时它才会阻塞，因为运行时系统选择这么做，或者说在 std::async 调用中规定如此。
>
> 因为 async 返回 future，如果不将 async 的返回结果赋值或引用绑定到一个 future 对象上，则返回的 future 会在当前函数调用语句后析构，导致阻塞、直到 async 执行完成，使异步任务变成同步任务。可见 *Quiz - 48.*。
>
> ```cpp
> // 因为会阻塞，所以两个 async 都是同步执行
> async(std::launch::async, [&x]() { x = 1; });
> async(std::launch::async, [&x]() { x = 2; });
> ```

**shared_future**

[std::shared_future](https://zh.cppreference.com/w/cpp/thread/shared_future) 与 future 类似。future 只能由一个线程来获取结果，shared_future 允许等待相同任务的多个线程获取结果。
future 可以通过 share() 将自己的共享状态转移到一个 shared_future 对象中。shared_future 也可以直接通过 future&& 构造（比如 promise.get_future()）。

它们与 unique_ptr 和 shared_ptr 类似：

- future 不可复制、只可移动，只有一个线程能够拥有其所有权；shared_future 可复制、可移动，允许多个线程复制同一 shared_future 来共同持有一个共享状态。
- 当多个线程访问同一个 future 或 shared_future 对象时，需要通过锁等保护；当多个线程通过复制产生的多个 shared_future 对象访问同一个共享状态时，是线程安全的。

**promise**

[promise](https://zh.cppreference.com/w/cpp/thread/promise) 用于存储一个值或一个异常，之后可以通过该 promise 对象创建的 future 来获取。它是一次性的。
每个 promise 都与一个共享状态关联。

promise - future 类似一个一次性 channel：向 promise 存储结果的操作 会与 在 future 上等待结果的操作 同步。

promise 只可移动，不可复制。

可以通过 set_value 或 set_exception 来向共享状态存储结果值或异常。共享状态只能存储一次，即 set 只能调用一次。
当 future get 获取到异常时，会抛出该异常，允许外部捕获处理。

```cpp
void f(promise<int> prom) {
    try {
        throw std::runtime_error("re");
    }
    catch (...) {
        prom.set_exception(std::current_exception());
    }
}

promise<int> pro;
future<int> fu = pro.get_future();

std::thread t(f, std::move(prom));

try {
    fu.get();
}
catch (exception& e) {
    cerr << "异常: " << e.what() << '\n';
}
t.join();
```









**latch**

单次使用的 barrier？



**mutex**

> C++ 中，mutex 是普通的锁，lock 是对 mutex 的封装。
> unique 是写锁，shared 是读锁，通过对同一个 std::shared\_mutex 加锁实现安全读写。
>
> mutex 是满足[互斥体](https://zh.cppreference.com/w/cpp/named_req/Mutex)的对象，不可复制、不可移动，需要通过引用或指针传递。

mutex 就是封装的 pthread_mutex，但要注意调它加锁解锁接口时需要检查返回值，返回值不为0时表示操作失败。

lock 就是封装 mutex，构造时加锁、析构时解锁。
**注意禁用拷贝并阻止生成移动，构造函数加 explicit。**
mutex 可通过泛型传入，允许使用不同类型的锁。

可以通过 try_lock 尝试加锁，如果加锁失败会立即返回 false，不会阻塞。

**shared_mutex**

mutex 是互斥锁，[shared\_mutex](https://zh.cppreference.com/w/cpp/thread/shared_mutex) 是读写锁，允许 lock, unlock （排他性锁定）与 lock\_shared, unlock\_shared（共享锁定）（如果当前不可锁则阻塞）。在 C++17 引入。
通过 try\_lock, try\_lock\_shared 尝试以排他/共享模式加锁，如果成功加锁返回 true，不成功则 false，不阻塞。

shared_timed_mutex 与它一样，但支持在 try_lock(_shared) 时指定尝试等待的最长时间。

**recursive_mutex**

[recursive\_mutex](https://zh.cppreference.com/w/cpp/thread/recursive_mutex) 是可重入锁。

**lock_guard**

lock\_guard 与智能指针类似，可以在一个作用域内方便地管理互斥锁（`{ }`就会定义一个作用域）。
创建 lock\_guard 时，它需要获取一个锁的所有权并加锁；在离开 lock\_guard 的作用域时，它会被析构并自动释放锁。

使用例子：`std::mutex m_mutex; std::lock_guard<std::mutex> lock(m_mutex);`。
如果函数可能抛出异常，不使用 lock\_guard 管理锁是非常危险的，很可能死锁。

C++17 起可以省略 lock_guard 的模板参数，可自动推导 (CTAD)。

实现：

```cpp
template <class _Mutex>
class lock_guard { // class with destructor that unlocks a mutex
public:
	// 无adopt_lock参数，构造时就加锁
    explicit lock_guard(_Mutex& _Mtx) : _MyMutex(_Mtx) {
        _MyMutex.lock(); // construct and lock
    }
	// 传入adopt_lock参数时，构造时不加锁。当前线程必须已持有该锁
    // lock_guard 没有 adopt_lock_t 和 try_to_lock_t 的构造函数，需要用 unique_lock
    lock_guard(_Mutex& _Mtx, adopt_lock_t) : _MyMutex(_Mtx) {} // construct but don't lock
	// 析构时解锁
    ~lock_guard() noexcept {
        _MyMutex.unlock();
    }
	// 禁止拷贝，并阻止移动生成
    lock_guard(const lock_guard&) = delete;
    lock_guard& operator =(const lock_guard&) = delete;

private:
    _Mutex& _MyMutex;
};
```

lock\_guard 并不管理锁的生命周期。如果锁在其它地方被回收，lock\_guard 执行析构释放时会发生错误（访问空指针）。

**unique_lock**

[unique_lock](https://zh.cppreference.com/w/cpp/thread/unique_lock) 与 lock\_guard 类似，但是一个更完整、自由的锁管理器：

- unique\_lock 可以手动使用`.unlock()`解锁、放弃锁的所有权（析构时会判断，只有持有锁时才解锁）。
- 在定义时传入 std::defer\_lock 可以不在构造时加锁。可在之后通过`lock()`手动加锁。
    如：`std::unique_lock<mutex> lk(mu, std::defer_lock); lk.lock();`。
    但注意，重复 lock 会死锁、结束程序。

占用的资源相对 lock\_guard 更大：会保存一个 bool 变量记录当前是否持有锁，因为对齐会更大。lock_guard 只有一种锁着的状态。
unique_lock 可移动，lock_guard 不可移动（所以前者会保存 mutex 的指针，后者通常存引用）。

> [lock_tag](https://zh.cppreference.com/w/cpp/thread/lock_tag_t) 有三种：
>
> - try_to_lock_t：尝试获得锁的所有权（即加锁），不阻塞。
> - defer_lock_t：不获得锁的所有权，即不加锁。
> - adopt_lock_t：假设当前线程已拥有锁的所有权，即已经对该锁调用 lock，所以不再额外 lock。
> - 不传递 tag：获得锁的所有权（即加锁），阻塞。
>
> 当调用 lock 时，unique_lock 会获得锁的所有权。

**shared_lock**

[shared\_lock](https://zh.cppreference.com/w/cpp/thread/shared_lock) 是类似 unique\_lock 的包装器，用做读锁（C++14 起）。
多个 shared\_lock 可以同时加锁，会调用 mutex 的 lock\_shared。

**lock**

[std::lock](https://zh.cppreference.com/w/cpp/thread/lock) 是一个函数，可以同时锁定多个锁，并在加锁前调用死锁检测算法检查避免死锁。
很少用，通常用 scoped_lock。

**scoped\_lock**

[scoped_lock](https://zh.cppreference.com/w/cpp/thread/scoped_lock) 可以同时锁定多个锁，并在加锁前调用死锁检测算法检查避免死锁（C++17 起）。
当加锁会发生死锁时，线程会等待直到可安全获取所有锁（在有锁释放时进行检查？）。

**call_once**, **once_flag**

[call\_once](https://zh.cppreference.com/w/cpp/thread/call_once) 与 once\_flag 共同使用，保证同一 once\_flag 对应的函数调用，只会被执行一次，是线程安全的。
当函数执行成功时，反转 flag 避免多次执行；函数抛出异常时，传给 call\_once 的调用方，不设置 flag。

例：

```cpp
// x 只会被输出 1 次
std::once_flag flag;
std::call_once(flag, f, 1); // void f(int x)
std::call_once(flag, [&](int x) {
    printf("lambda(%d)\n", x);
}, 1);
```

> ref 中的例子表明，当 call_once 调用的函数抛出异常时，会回退 once_flag 的状态、允许再次调用。
> 但是 call_once 可能并不支持函数抛出异常，这可能是 UB。

**初始化 static 对象**

call_once 可用来保证仅初始化一次 static 对象：

```cpp
struct A {
	static void f() {
		static std::once_flag flag;
		static vector<int> v;
		std::call_once(flag, []() { // 静态存储期对象不需要捕获
			v.insert(v.begin(), {1, 2, 3});
		});

		for (auto x: v) {
			cout << x << ' ';
		} cout << '\n';
	}
};
int main() {
    thread t1(A::f);
    thread t2(A::f);
    thread t3(A::f);

    t1.join();
    t2.join();
    t3.join();
}
```

不过更简单的是直接写一个初始化函数赋值，C++11 保证了静态对象只会被初始化一次：

```cpp
struct A {
	static void f() {
		static auto GetV = []() { // 可以写到匿名 namespace
			vector<int> v;
			v.insert(v.begin(), {1, 2, 3});
			return v;
		};
		static vector<int> v = GetV();

		for (auto x: v) {
			cout << x << ' ';
		} cout << '\n';
	}
};
int main() {
    thread t1(A::f);
    thread t2(A::f);
    thread t3(A::f);

    t1.join();
    t2.join();
    t3.join();
}
```

**condition_variable**

[condition\_variable](https://zh.cppreference.com/w/cpp/thread/condition_variable) 能够阻塞一个或多个线程，并允许其它线程通过通知唤醒它们。
wait 时需要传入一个绑定 mutex 的 unique\_lock，cv 会解锁它，直到线程被唤醒、重新获得锁后，结束 wait（访问资源肯定是要加锁的，wait 唤醒时自动获取锁，不需要我们再去加锁）。

> condition_variable 只可与 unique_lock<mutex> 一起使用，以允许一些优化（效率更好）。
> condition_variable_any 可与任何支持 lock、unlock 的对象（满足可基本锁定）一起使用。但是也是调 lock，即使传 shared_lock 也没法 lock_shared，所以没法用读写锁。

想要修改共享变量的线程需要：

1. 获得一个 mutex（一般是 std::unique\_lock）。
2. 在持有锁时进行修改。
3. 在 cv 上执行 notify\_one 或 notify\_all。该步可以并且建议不持有锁（在修改完成、notify 前手动释放锁。细节见[这里](https://zh.cppreference.com/w/cpp/thread/condition_variable/notify_one)）：
   1. 如果通知线程在 notify 时持有锁，那么等待线程被唤醒后会立刻因为取不到锁再次阻塞，等通知线程释放锁后再唤醒。
       但一些实现会判断这种情况，会在 notify 时将等待线程直接移出 cv 的队列、转移到锁的队列而无需唤醒它。
   2. 某些情况下确实需要在持有锁的时候进行 notify。

等待 cv 的线程需要：

1. 获得同样的 mutex（一般是 std::unique\_lock）。
2. 调用 wait 检查状态是否已更新，如果没有，wait 会释放锁并阻塞。
    该步骤需通过循环进行，因为 cv 可能发生虚假唤醒（多个线程被唤醒，但只有一个能成功消费，其它继续等待），即线程从 wait 中被唤醒时，状态没有更新完毕。
3. wait 达成条件且被 notify 唤醒后会持有锁，可进行修改。如果仅用于通知需要手动释放锁。

wait 也能传入一个函数或 lambda，简写循环。

```cpp
template <class _Predicate>
void wait(unique_lock<mutex>& _Lck, _Predicate _Pred) { // pred：什么时候可认为成功，以退出 wait
    while (!_Pred()) {
        wait(_Lck);
    }
}
```

例：

```cpp
std::condition_variable cv;
bool flag = false;

void thread1()
{
    std::unique_lock<std::mutex> lock(mu);
    // do something...

    flag = true; // 更新完成
    cv.notify_one();  // 通知线程 2
}

void thread2()
{
    std::unique_lock<std::mutex> lock(mu);
    // !flag 时才等待。flag 为 true 时说明已经通知过了（数据已更新）
    while (!flag)
        cv.wait(lock);  // 等待通知
    // 等价于
    // cv.wait(lock, []{ return flag; }); // 如果调用成员函数，还需捕获 this

    // do something
    // 如果不需要锁需要手动释放
}
```

生产者消费者：

```cpp
std::queue<int> q;
std::mutex mu;
std::condition_variable cv;
void producer(int n)
{
	for (int i=0; i<n; i++)
	{
		// 加锁，操作队列
		std::unique_lock<std::mutex> lock(mu);
		q.push(i);

		// 通知
		cv.notify_one();

		// 如果没有通知，只能通过延时控制同步
//		std::this_thread::sleep_for(std::chrono::milliseconds(20));
	}
}
void consumer()
{
	while (true)
	{
		// 加锁，操作队列
		std::unique_lock<std::mutex> lock(mu);

		// 如果没有数据，等待
		// 唤醒后，确保真的有数据，再进行下一步消费
		while (q.empty())
			cv.wait(lock);

		assert(!q.empty());
		int data = q.front(); q.pop();
		printf("consumer get %d\n", data);

		// 如果没有通知，只能通过延时控制同步
//		std::this_thread::sleep_for(std::chrono::milliseconds(20));
	}
}
```

> notify 存在虚假唤醒的情况。
> 所以应使用`while (!pred) cv.wait(lk);`或`cv.wait(lk, pred)`在被唤醒时检查条件。

**atomic**

[atomic](https://zh.cppreference.com/w/cpp/atomic/atomic) 是原子变量。
提供了 load, store, fetch\_add/sub/and/or/xor（和相关的 +=, -=...），前置/后置 自增/自减。

原子变量对于任何可用类型都支持，即使这个类型非常大（甚至几万字节）。但指令集肯定不能在这么多字节上做 CAS，所以编译器可能会生成其它指令来保证原子性，比如加锁，然后执行一系列非原子操作。
在这种情况下，`compare_exchange`发生伪失败的概率会大大提高，具体见下。

> TODO：https://www.boost.org/doc/libs/1_55_0/doc/html/atomic/usage_examples.html
>
> 读写 atomic 是否需要加锁是未指定的，可以通过 is_lock_free 来判断。对于内建类型，也存在各种`ATOMIC_xxx_LOCK_FREE`宏来进行判断。

**compare_exchange**

> https://stackoverflow.com/questions/25199838/understanding-stdatomiccompare-exchange-weak-in-c11

`a.compare_exchange_weak/strong(exp, tar)` 在 a 等于期望值 exp 时，将 a 赋为 tar 并返回 true；否则将 exp 设为 a 当前的值，返回 false。

weak 版本通常需要跟循环一起使用：

```cpp
// 在当前线程读取 value 进行一系列操作的过程中，不能有其他线程修改 value
expected = value.load();
do desired = function(expected);
while (!value.compare_exchange_weak(expected, desired));
// （但这显然可能有 ABA 问题，需要注意）
// 如果 desired 表达式很简单，可以简化，如：
while (!value.compare_exchange_weak(expected, expected->next));

// 如果不在意是谁修改了 value，只要是预期值就行，可以提前结束
expected = false;
while (!value.compare_exchange_weak(expected, true)
      && !expected);
```

因为 weak 版本可能发生伪失败，也就是原子变量可能已经等于期望值，但由于上下文切换等原因，compare 返回了 false（不过概率并不高）。

strong 版本会进行额外检查，避免伪失败的发生，其内部通常也包括一个小循环，用于重试。

如果代码中不需要循环，一般没必要因为伪失败自己写一个循环，直接用 strong 版本即可。
如果本身就需要循环，那顺便使用 weak 版本允许伪失败的发生，可以提高效率。
如果伪失败发生概率很低，在某些平台上，使用 weak + 循环 可能也会提高效率。

实现一个无锁栈：

```cpp
template<typename T>
class Stack
{
private:
	struct Node
	{
		Node* next;
		std::shared_ptr<T> data;

		Node(const T& _data):
			data(std::make_shared<T>(_data)) {}
	};
	std::atomic<Node*> head;

public:
	void push(const T& data)
	{
	    Node* new_node = new Node(data);
	    new_node->next = head.load(std::memory_order_relaxed);

	    while(!head.compare_exchange_weak(new_node->next, new_node,
	                                      std::memory_order_release,
	                                      std::memory_order_relaxed));
	}
	std::shared_ptr<T> pop()
	{
		Node* old_head = head.load();
	    while (old_head &&
	          !head.compare_exchange_weak(old_head, old_head->next));
	    return old_head ? old_head->data : std::shared_ptr<T>();
	}
};
```

**thread_local**

thread\_local 定义的全局变量，是线程私有的（会在创建线程时拷贝？）。

**信号量** / **semaphore**

信号量是轻量简单的同步机制。它维护一个不能小于0的计数器，支持 释放（增加计数）、等待（减少计数）两个操作。当计数为0时，执行等待的线程将会阻塞，直到计数大于0、可以进行减少。

C++20 引入了两种信号量：[counting_semaphore](https://zh.cppreference.com/w/cpp/thread/counting_semaphore) 和 binary_semaphore，后者只是前者的别名，代表资源数量仅为1：`using binary_semaphore = counting_semaphore<1>;`。

**memory order** / **内存序**

> https://zh.cppreference.com/w/cpp/atomic/memory_order
> https://www.zhihu.com/question/24301047
> 不同系统已有的内存序：https://en.wikipedia.org/wiki/Memory_ordering
>
> Rust atomics and locks：https://marabos.nl/atomics/memory-ordering.html
> 翻译：https://rustcc.github.io/Rust_Atomics_and_Locks/
> https://atomics.rs/memory-ordering.html
>
> 查看程序的内存序：http://svr-pes20-cppmem.cl.cam.ac.uk/cppmem/
>
> 一个没考虑好内存序带来的问题：https://blog.hidva.com/2022/05/13/fetch-add0/
>
> 部分见 *基础 - 多处理器编程 - 内存屏障、内存模型*。

CPU会对指令进行重排或并行执行，以提高效率。
单线程中，CPU会保证重排/并行不会影响程序的正确性。但多线程中没法保证线程之间的逻辑是正确的。默认使用`memory_order_seq_cst`，即（几乎？）不允许重排序，来保证正确性。
但通过指定内存序，可以允许CPU适度的重排，提高效率。

在多处理器系统上，多个线程读写同样的变量时，一个线程能观测到变量值更改的顺序可能不同于另一个线程写它们的顺序。换句话说，多个线程看到的变量更改的顺序可能不一样，即不满足顺序一致性。一些类似的效果还能在单处理器系统上出现，因为内存模型允许编译器变换。

> dependency-ordered before 不用理解，因为没有编译器实现过 consume，会了也没用？
> 只要知道 simply happens-before 就行了。
>
> 在 x86 的机器上加入 memory_order_acq_rel 并不会导致汇编代码中产生屏障指令。原因就是 x86 本身就是强模型，acquire-release 模型中所避免情况 x86 中本身就不存在，所以根本没有必要加入一条屏障。但 memory_order_seq_cst 的一致性语义（顺序一致性）强于 x86，如果写操作使用了这种 memory order，则在汇编代码会产生 mfence 指令。还有就是 x86 机器上 LFENCE 和 SFENCE 指令，一般情况下是没用的。这些的根本原因就是，在 x86 上只会产生 store-load 乱序，所以只有 memory_order_seq_cst 内存序对 x86 有意义，其他的都是一样没有区别的，x86 都自然满足了。

**内存序的典型应用**

mutex：lock 是 acquire，unlock 是 release。

atomic counter：计数器通常与程序上下文的执行无关，所以可以用 relaxed 不严格要求顺序，如 shared_ptr 的计数器增加。



**内存屏障（内存栅栏）**

> （folly用的）https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p1202r4.pdf
> （太长 很难看下去）https://github.com/torvalds/linux/blob/master/Documentation/memory-barriers.txt

也是因为乱序执行导致的多线程下的问题？




---

## 协程

> https://lewissbaker.github.io/
>
> https://zhuanlan.zhihu.com/p/395250667

> future::get 和 future::wait 是标准的 async await 模型，但标准没提供调度器，相当于很多东西都要手写，需要手写 awaiter 和 promise_type（不是 promise）。
>
> 协程就是一个可以随时暂停和返回的函数，每次返回再调用可回到上次暂停的地方。用它做异步编程需要配合调度器。
>
> 示例：
>
> ```cpp
> template <class R>
> class Task {
> public:
> 	class promise_type {
> 		friend class Task;
>
> 	public:
> 		Task get_return_object() {
> 			return std::coroutine_handle<promise_type>::from_promise(*this);
> 		}
> 		std::suspend_always initial_suspend() { return {}; }
> 		std::suspend_always final_suspend() noexcept { return {}; }
> 		std::suspend_always yield_value(int v) { // 好像写错了
> 			result_ = v;
> 			return {};
> 		}
> 		void return_void() {}
> 		void unhandled_exception() {}
>
> 	private:
> 		std::optional<R> result_;
> 	};
>
> 	Task() = default;
> 	~Task() { handle_.destroy(); }
>
> 	bool has_next() const {
> 		if (!handle_.done() && !handle_.promise().result_.has_value()) {
> 			handle_.resume();
> 		}
> 		return handle_.promise().result_.has_value();
> 	}
>
> 	R next() {
> 		if (!handle_.promise().result_.has_value()) {
> 			handle_.resume();
> 		}
> 		R ret = std::move(handle_.promise().result_.value());
> 		handle_.promise().result_.reset();
> 		return ret;
> 	}
>
> private:
> 	Task(std::coroutine_handle<promise_type> h): handle_(h) {}
> 	std::coroutine_handle<promise_type> handle_;
> };
>
> int main() {
> 	using namespace std;
> 	auto generator = [](int l, int r) -> Task<int> {
> 		while (l++ < r) {
> 			co_yield l - 1;
> 		}
> 		co_return;
> 	};
> 	auto gen = generator(3, 9);
> 	while (gen.has_next()) {
> 		cout << gen.next() << ' ';
> 	}
> }
> ```
>
>

> 协程持有锁时被调度，可能会发生死锁。
> 使用可重入锁虽然可能解决问题，但可重入锁会导致调用 unlock 锁却不会释放的情况，不注意的话容易产生问题。
> 最好是避免协程+锁，或者使用无栈协程，或者使用协程锁？（C++ 的锁本来就是面向线程的）



> 在传统语言中，函数调用总是嵌套的，总是会有一个函数是 caller 另一个函数是 callee。
> 在某些场景中这很不方便和自然。在协程中，调用协程的函数与协程本身是平等的协作者。
>
> goroutine 的实现就是用户级轻量线程的实现，它与线程更类似，需要同步或加锁？它实际是用协程池 API 调用的线程池，本质还是多线程？因为它是有栈的？
> 这与协程很不同，协程的状态机集合可重入函数的抽象，方便异步编程中改善 cps 编程？

**协程**

协程可以从多个角度分类：

- 有栈协程与无栈协程。
- 对称协程与非对称协程。

> 原生支持协程的常用语言中，只有 Go 和 PHP 是有栈协程；只有 Go 是对称协程。



**系统级异步与应用级异步**

系统级异步：

- 由操作系统内核管理和调度。可以利用多核处理器的并行能力。
- 资源管理高效、可并行执行。
- 上下文切换开销较大，依赖 os 支持。

应用级异步：

- 由应用程序自身管理和调度。不依赖操作系统。通常通过用户态库实现。
- 上下文切换开销较小，灵活。
- 不能利用多核处理器的并行能力，需要手动管理并发。





**有栈协程与无栈协程**

> 当协程状态的生存期严格内嵌于调用者的生存期，且协程帧的大小在调用点已知，那么可以优化掉对协程栈的动态分配。

总结：
有栈协程：

- 有独立的栈空间。
- 可以直接使用本地变量；支持复杂的控制流，能进行嵌套函数调用。
- 开销较大，需管理和分配栈空间。

无栈协程：

- 基于生成器或状态机，没有独立的栈空间。
- 状态通过闭包等保存。复杂的控制流和嵌套调用需要手动管理状态，增加代码复杂度。
- 开销较小。

协程也是一种函数，需要空间存储局部或临时变量。

如果协程有自己独立的栈空间（比如 go 的协程有默认 2KB 的栈），则可以将局部变量和协程内调用的嵌套函数的栈帧放在自己的栈里，不需要使用程序的栈空间。
因此有栈协程可以很方便的在它调用的内层函数中暂停、继续，因为内层函数的栈帧在协程动态分配的空间内。
有栈协程更像是线程。

如果协程没有独立的栈空间，则会像普通函数一样将局部变量放在程序的栈中，当协程暂停时，会将存活的局部变量保存？当协程调用其它函数时，也会像普通函数一样将函数的栈帧放在程序的栈中。
因此无栈协程很难在内层函数中直接暂停，因为暂停挂起需要销毁它的栈帧。只能像处理协程一样将内层函数的状态依次保存，然后在继续时依次恢复原来的栈帧。所以如果使用无栈协程，通常只有协程本身能够暂停，协程调用的其它非协程函数无法在中间暂停。

**实现有栈协程**

> https://zhuanlan.zhihu.com/p/330606651

创建协程前，分配一片空间作为协程栈，预留几个寄存器的空间用于存储寄存器值（取决于调用约定。也要保存返回地址，这里即为协程的函数入口）。
执行协程时，先进行切换上下文（这里上下文即各协程寄存器的状态）：保存当前的寄存器值，然后从协程栈中读取各寄存器的值赋值给对应寄存器，就可以完成上下文切换，然后将返回地址赋给 PC 执行协程函数入口。

**实现无栈协程**

> https://mthli.xyz/coroutines-in-c/
> https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html
>
> C 实现：https://dunkels.com/adam/pt/

一种简单的方式是，使用普通函数做协程，使用静态局部变量记录协程的状态，再使用静态变量（比如 state）记录协程执行的位置 以便暂停后恢复执行。
对于每个可能的暂停点（就是一个 return 语句），在它之前更新 state 的值，在它之后创建一个标签，然后在恢复执行时根据 state 的值直接跳转到对应的标签，就可以实现继续执行。
可以通过 goto 或达夫设备的 case 实现。

```cpp
#define coBegin static int state=0; switch(state) { case 0:
#define coYield(i,x) do { state=i; return x; case i:; } while (0)
#define coFinish }
int function(void) {
    static int i;
    coBegin;
    for (i = 0; i < 10; i++) {
        coYield(1, i);
    }
    coFinish;
}
// 避免生成的 label 名冲突
// #define coYield(x) do { state=__LINE__; return x; \
                         case __LINE__:; } while (0)
```

通过用宏 crBegin 和 crFinish 将函数体包裹，用 coYield 创建每个 return 语句，不将它们和 switch 一起使用，不将 coYield 写在一行，就可以实现一个协程。

**对称协程与非对称协程**

对称协程：

- 协程之间可以互相调用和切换。没有主协程的概念，任何协程都可以成为调度者。
- 灵活，适合复杂的协作任务。
- 代码结构可能会更复杂，难以维护。

非对称协程：

- 协程只能挂起自己并将控制权返回给调度者。
    典型的实现是 async/await 模式。
- 代码结构清晰，易于维护。
- 灵活性较低，需要明确的调度者。







---

## 日期和时间

TODO

https://zhuanlan.zhihu.com/p/1892632711019073793
https://blog.csdn.net/qq_55125921/article/details/128720696



**纪元 (epoch)**

纪元是一个参照时间，指时间的起点。

C++20 前 system_lock 的纪元未指定；C++20 起为 1970.1.1 0 点，与 Unix 时间一致。
Unix 时间戳 (Unix Timestamp) 为从 UTC/GMT 的1970年1月1日0时0分0秒开始所经过的秒数（不考虑闰秒）。

**壁钟时间**

壁钟时间 (wall time, wall-clock time, real time) 是实际的时间（现实时间），代表程序从开始执行到结束所花费的总时间。
与之相对的是 CPU 时间？仅代表程序在处理器上执行的时间。

**time_t**

[time_t](https://zh.cppreference.com/w/cpp/chrono/c/time_t) 是足以表示时间的**算术类型**（时间戳，通常为整数）。表示自 1970.1.1 00:00 UTC 以来所经过的秒数。

C、C++ 均可通过`time(nullptr)`获取当前时间对应的 time_t。
time_t、time 及相关的获取和转换函数都在 <ctime> 的 namespace std 下。

C++ 可通过`chrono::system_clock::to_time_t(now);`从 time_point 获取 time_t。

**tm**

[tm](https://zh.cppreference.com/w/cpp/chrono/c/tm) 是保存了日期各部分的**结构体**。可通过以下两种方式从 time_t 转换：

- *localtime* 将 time_t 转换为以当地时间表示的日期和时间。
- *gmtime* 将 time_t 转换为以协调世界时 (UTC) 表示的日期和时间。

推荐使用 put_time 输出。
C 风格的 [asctime](https://zh.cppreference.com/w/cpp/chrono/c/asctime) 和 [ctime](https://zh.cppreference.com/w/cpp/chrono/c/ctime) 也可使用，但不能定义格式。ctime(time_t) 等价于 asctime(localtime(time_t))。

注意要用 std::localtime 而非 localtime，否则会匹配到 C 的那个。两者都可能不是线程安全的。
MSVC 会警告 C 的 localtime 已被弃用，因为它返回的 tm 指针指向的对象，实际上分配在静态存储中，容易导致错误释放。推荐 localtime_s 或 localtime_r（区别是？）（仅在 C 有），它要求用户自己提供 tm，并将结果放在里面。

> localtime_s 似乎只能在 windows 上使用？

**put_time**

[put_time](https://zh.cppreference.com/w/cpp/io/manip/put_time) 可将时间 tm 以指定格式进行流输出：`out << puttime(tm_ptr, fmt)`。

常用的符号和时间表示：

- （以下均为十进制）
    Y：年。y：年的后二位。m：月。d：日。
    H：24制小时。I：12制小时。M：分钟。S：秒。
- F：日期，如 2024-02-22。
    D：日期，如 02/22/24。
    x：本地化的日期表示。
- T：时间，如 13:50:58。
    R：时间，如 13:50。
    x：本地化的时间表示。
- `%F %T`、`%Y-%m-%d %H:%M:%S`：2024-02-22 13:50:58
    c：Thu Feb 22 13:50:58 2024

符号前要加 %。
符号可以组合、任意次的使用，比如：`%F %T`就会输出空格分隔的日期+时间，`%F %F %F`就会输出三个日期。
不能输出毫秒/微秒，以微秒为例只能手动转成 microseconds 模 1e6 获取微秒，然后单独输出。

**time_point**

[time_point](https://zh.cppreference.com/w/cpp/chrono/time_point) 通常从 clock::now() 获取，代表某个时间点。
它存储了一个 duration 类型的值，表示自 Clock 的纪元起始开始的时间间隔（通过 time_since_epoch 获取）。
对它的修改或读取就是对 duration 的读写。

它可以直接输出，也可转为 time_t 再转为 tm 用 put_time 指定格式输出。

可以通过加减乘除运算。

**system_clock**

[system_lock](https://zh.cppreference.com/w/cpp/chrono/system_clock) 表示系统的实时时间。

它可能是不单调的：系统时间可能在任何时候被调节，导致时间值回退。

~~它是唯一能映射其时间点到 C 风格时间（to_time_t）的时钟。~~
~~各个 clock~~只有 system_lock 可以通过 now() 返回 time_point，然后通过静态函数`system_clock::to_time_t`转换到 C 风格时间点 time_t。

**system_clock 与 time**

`system_clock::to_time_t`可以将 time_point 转为时间戳 time_t。这样获得的当前时间戳与`time(nullptr)`是一样的，表示自 1970.1.1 到当前的秒数。

`system_clock::now()`返回一个`time_point`类型的时间点，它通常以纳秒级别的精度表示时间。与`time(nullptr)`返回`time_t`的区别是：

- 两者的精度都是不确定的。但 system_lock 的精度程序可以直接获取（编译时或运行时），time 需要自己去阅读文档。
    time 的精度通常是秒；system_lock 通常更准确，在 gcc 是纳秒，在苹果 LLVM 上是微秒，在 windows 是1/10微秒。由于 chrono 的设计所以其可移植性更强？
- time 的范围不确定，在32位机器上通常是1970+/-68年，在64位上则是1970+/-292billion。system_lock 保证至少是1970+/-292 年（但精度更高），并且可以由程序获取。
- time 的返回值一般只是整数，没有类型安全性。system_lock 的类型很明确。

此外与 time_t 相比，time_point 提供了更高的精度和更大的时间范围？支持更多的时间操作（计算时间间隔和执行时间转换）。

> system_clock::now() 和 time(0) 都测量 Unix 时间，但前者在 C++20 前其实是未指明的（但通常是）。

**steady_clock**

[steady_clock](https://zh.cppreference.com/w/cpp/chrono/steady_clock) 是保证单调的时钟，其时间点绝对不会随物理时间推进而减少。因此它可能与现实时间无关。
最适合于度量间隔，不会受系统时间变化影响。

**high_resolution_clock**

[high_resolution_clock](https://zh.cppreference.com/w/cpp/chrono/high_resolution_clock) 是实现提供的精度最高的时钟，通常为 system_lock 或 steady_clock 的别名，但也可是第三方实现的时钟。

**输出当前日期和输出当前时间**

使用 system_clock::now() 获取 time_point，然后转为 time_t（或 time(nullptr) 获取 time_t），再转为 tm\*，用 put_time 输出。

```cpp
// 均在 std 下
std::chrono::time_point now = std::chrono::system_clock::now();
// time_point 可直接输出得到完整、自带格式的时间，但需要 C++20
cout << now << '\n'; // 2025-02-25 03:28:45.071496730

// C++20 前的输出方式
std::time_t tmNow = std::chrono::system_clock::to_time_t(now); // = time(nullptr) 也行
#include <iomanip>
cout << std::put_time(std::localtime(&tmNow), "%F %T") << '\n';
cout << std::put_time(std::localtime(&tmNow), "%Y-%m-%d %H:%M:%S") << '\n';

// put_time 只能获取到秒级，毫秒/微秒需自行获取打印
time_t tm_c = std::chrono::system_clock::to_time_t(now); // now 必须是 system_clock
tm now_tm;
localtime_r(&tm_c, &now_tm); // 注意 localtime 非线程安全，如果要线程安全只能使用 C 的 localtime_r/s
// 获取微秒部分
auto now_us = std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()) % 1000000;
cout << std::put_time(&now_tm, "%Y-%m-%d %H:%M:%S") << '.' << std::setfill('0') << std::setw(6) << now_us.count() << '\n';

// 也可使用 ctime 转换 time_t
string ts = ctime(&tmNow);
cout << ts << '\n';
```

C 的方法（需要 time.h）：
time 获取当前时间，然后通过 [localtime]((https://zh.cppreference.com/w/c/chrono/localtime)) 转换。

```cpp
char buffer_[9];
time_t time_value = time(NULL);
struct tm now;
localtime_r(&time_value, &now);
snprintf(buffer_, sizeof(buffer_), "%02d:%02d:%02d", now.tm_hour, now.tm_min, now.tm_sec); // 也可使用 tm 的其它信息
cout << buffer_ << '\n';
```

**duration**

[std::chrono::duration](https://zh.cppreference.com/w/cpp/chrono/duration) 表示时间间隔。
它由两个模板参数组成：Rep 为记录时钟次数所用的类型，通常为 int 或 double；Period 为计次周期，是一个 std::ratio 类型的分数，表示每隔多少秒计一次。

可以通过加减乘除运算。

当转换没有精度损失时（比如分到秒，反之不可），一个 duration 可以隐式转换到另一种 duration。显式转换需要通过 duration_cast。
用 duration 直接除以 1ms 或 1s 也可以转换到毫秒和秒（需要`using namespace std::literals`）。

```cpp
cout << std::chrono::duration_cast<std::chrono::microseconds>(end - start);
// 等价于
using namespace std::literals;
cout << (end - start) / 1ms;
```

std::chrono 下定义了一系列 duration：

```cpp
using milli = ratio<1, 1000>;
using milliseconds = duration<long long, milli>;
using seconds      = duration<long long>;
using minutes      = duration<int, ratio<60>>;
using hours        = duration<int, ratio<3600>>;
// C++20
using days   = duration<int, ratio_multiply<ratio<24>, hours::period>>;
using weeks  = duration<int, ratio_multiply<ratio<7>, days::period>>;
```

**输出 duration 代表的时间**

似乎没有简单的办法。也可以见上面使用 put_time + count 的方法。

```cpp
// 输出间隔
Time tmp = t;
const auto hour = duration_cast<hours>(tmp); tmp -= hour;
const auto min = duration_cast<minutes>(tmp); tmp -= min;
const auto sec = duration_cast<seconds>(tmp); tmp -= sec;
const auto ms = duration_cast<milliseconds>(tmp);
cout << hour.count() << "h " << min.count() <<
	"m " << sec.count() << "s " << ms.count() << "ms\n";

// 输出日期和时间。但这样输出的时间似乎不准
milliseconds tmp = t;
const auto year = duration_cast<years>(tmp); tmp -= year;
const auto month = duration_cast<months>(tmp); tmp -= month;
const auto day = duration_cast<days>(tmp); tmp -= day;
const auto hour = duration_cast<hours>(tmp); tmp -= hour;
const auto min = duration_cast<minutes>(tmp); tmp -= min;
const auto sec = duration_cast<seconds>(tmp); tmp -= sec;
const auto ms = duration_cast<milliseconds>(tmp);
// 注意日期要加 1970/1/1 才对
cout << year.count() + 1970 << "-" << month.count() + 1 <<
    "-" << day.count() + 1 <<
    " " << hour.count() << ":" << min.count() <<
    ":" << sec.count() << "." << ms.count() << '\n';
```

用 C++20 format 很方便？



---

## 其它

**deprecated**

将要废弃的特性：https://timsong-cpp.github.io/cppwp/n4861/depr

**小参数传值** / **传引用**

对于较小的参数（不超过8B，如 int, double），传值比传引用更好，因为引用会导致访存（不可优化），而传值可以直接存在寄存器内。
MSVC ABI 可能用两个寄存器处理16B的参数，具体可以见 *基础 - 调用约定*。

```cpp
int f(const int& x) { // int&& 同理
	return x * 2;
}
int g(int x) {
	return x * 2;
}
f(int const&):
        mov     eax, DWORD PTR [rdi]
        add     eax, eax
        ret
g(int):
        lea     eax, [rdi+rdi]
        ret
```

**a+=b 与 a=a+b**

对于类类型（比如 string），a+=b 可能比 a=a+b 更好，因为后者会创建一个临时对象，然后移动给 a；而前者可以直接在 a 的空间内完成，即使容量不足需要重分配，也不需要 move。

**通过非类指针调用成员函数 / nullptr 调用成员函数**

一般来说，`obj.f(args)`实际上是`f(&obj, args)`，`p->f(args)`就是`f(p, args)`，因此下面的代码通常可以执行：

```cpp
struct A {
	void f(int x) {
		if (reinterpret_cast<uint64_t>(this) == 1) {
			cout << "1: " << x << '\n';
			return;
		}
		cout << "ok: " << x << '\n';
	}
	void g(int x) {
		cout << "g: " << x << '\n';
	}
};

A a; a.f(3); // ok: 3
reinterpret_cast<A*>(1)->f(3); // 1: 3
(*reinterpret_cast<A*>(1)).f(5); // 1: 5
((A*)(nullptr))->g(3); // g: 3
```

但当然这是 UB。[标准规定](https://www.zhihu.com/question/589273713)`p->f()` 等价于`(*p).f()`。即使成员函数没有用到 this，理论上也要对 *this 进行求值，表达式 *this 必须是合法的，而`*1`或`*nullptr`都是 UB（后者编译器可能会直接给出警告）。
编译器也会假定 this 不是 nullptr，并以此优化。

这种情况下，如果类调用虚函数，就必须访问指针查找虚表，会直接 RE。
（很早）以前某些代码可能会这样做，见[这里](https://www.zhihu.com/question/471186963/answer/2662278344)。

**relocatable** / **重定位**

> 可能会在 C++26 引入，提案：
> https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p1144r11.html
> https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2786r6.pdf
>
> 移动后，原对象依然存在，只是将资源转移到了移动后的新对象。
> 重定位后，原对象不再存活，只可使用重定位后的新对象。

[folly](https://github.com/facebook/folly/blob/main/folly/docs/FBVector.md#object-relocation) 把扩容时 元素从一个位置移动到另一个位置的过程，叫 Object Relocation。
如果一个对象能按位移动到另一个位置，即通过 memcpy 或 memmove 移动到另一个位置、还能保留其实际值的话，就称它为 [*relocatable*](https://github.com/facebook/folly/blob/main/folly/docs/Traits.md?plain=1#L20)。non-relocatable 的对象只能通过移动或拷贝移动到另一个位置。

```cpp
void conservativeMove(T* from, T* to) {
	new(to) T(from);
	(*from).~T();
}
// 如果 T 是 relocatable 的
void optimizedMove(T* from, T* to) {
	memcpy(to, from, sizeof(T));
}
```

memcpy 和 memmove 是高度优化的内建函数，并且能支持 SIMD，或充分利用硬件特性（如 DMA），其效率要比拷贝和移动都高很多。
可平凡拷贝的对象只是 relocatable 对象的一个子集。通过将可平凡拷贝的限制放宽到 relocatable，可以让大多数对象都能使用 memcpy 或 memmove 进行 relocate，这对 vector、hashTable 来说是很大的提升（vector 的 resize, insert, erase 都可以应用。memcpy 稍微便于实现强异常安全，memmove 允许地址重叠）。

> 如果启用高度优化（如 O3），那么编译器可能也会将循环优化为 SIMD（如果知道指针的对齐值）。

但 C++ 只给出了可平凡拷贝这一概念，保守地认为非可平凡拷贝的对象 都是非 relocatable 的。
实际上只有一小部分对象是非 relocatable 的：

- 有一个指向自己成员的指针成员，比如：`char buf[10]; char* data = buf;`。可以避免。
    比如：gcc 的 string sso 优化。
- 被外部指针指向的对象，且它们在移动时要更新外部指针。很少见。

可平凡拷贝的要求是：

- 析构函数、所有拷贝构造、移动构造、拷贝赋值、移动赋值都是平凡的，即不是用户提供的。
- 所有基类和所有非静态成员也是可平凡拷贝的。
- 没有虚基类，没有虚函数。

这个要求过严了。string、vector、unordered_map 都不是可平凡拷贝的，但都是 relocatable 的（string 要取决于实现，见 *STL - string*），可以用 memcpy 拷贝到新的内存空间（可以存在多个，但注意必须有且仅有一个对象调用析构函数；调用析构后任何相关对象都不再合法）。

```cpp
using T = unordered_map<int, string>;
T o = {{1, "abc"}, {2, "123"}, {3, "a"}};

constexpr size_t size = sizeof(T);
unsigned char* buffer = new unsigned char[size * 2];
auto* a1 = new (buffer) T{o};
auto* a2 = new (buffer + size) T{o};
print(*a1);
print(*a2);

unsigned char* buffer2 = new unsigned char[size * 2];
memcpy(buffer2, buffer, size);
auto* b1 = reinterpret_cast<T*>(buffer2);
auto* b2 = new (buffer2 + size) T{*a2};
print(*b1);
print(*b2);

// a1->~T();
a2->~T();

b1->~T();
b2->~T();

delete[] buffer;
delete[] buffer2;
```

map 不行，目前不知道为什么。

> libstdc++ 的 vector 实现中仅对平凡类进行优化，对非平凡但 trivially_copyable 的类型也不会优化。
> 最新的 libc++ 实现了 relocate 优化（见[这里](https://www.zhihu.com/question/660212597/answer/3546214104)）。
>
> 已经有多个提案提出在 C++26 添加 relocatable 概念（见[这里](https://zhuanlan.zhihu.com/p/679782886)）。
> 主要有两种方式：
>
> - 允许给类添加新的属性说明符`[[trivially_relocatable]]`，并要求编译器提供`is_trivially_relocatable_v`，以及对应 [uninitialized_move_n](https://zh.cppreference.com/w/cpp/memory/uninitialized_move_n) 和 [construct_at](https://zh.cppreference.com/w/cpp/memory/construct_at) 的函数 uninitialized_relocate_n 与 relocate_at。
>     不影响原来的 API 和 ABI，兼容性强。
>
>     如果类型满足下列条件之一，则它是 trivally relocatable 的：
>
>     - 是 trivally copyable 的。
>     - 是 trivally relocatable 类型的数组。
>     - 有 trivially_relocatable 属性说明符。
>     - 是一个满足以下所有条件的类：析构函数、所有拷贝构造、移动构造、拷贝赋值、移动赋值都是平凡的；所有基类和非静态成员要么是引用，要么也是 trivally relocatable 的；没有虚基类，没有虚函数。
>
> - 添加新的重定位构造函数 relocate constructor `T(T x)`，接收纯右值，与拷贝构造`T(const T&)`接收左值、移动构造`T(T&&)`接收亡值对应。
>     左值可以通过 reloc 关键字转为纯右值（类似 move）；reloc 后的左值将不能再使用。

> 自己实现时，可以添加一个 type_trait 来判断类是否可 relocate：
>
> ```cpp
> template <class T>
> struct IsRelocatable: false_type {};
> // 可以把下面的定义封装成宏
> template <class T>
> struct IsRelocatable<vector<T>>: true_type {}; // 在该文件外添加需要补充对应的 namespace
> ```
>
> 或者在可 relocate 的类内加一个 tag，然后通过 SFINAE 选择：
>
> ```cpp
> struct A {
> 	struct IsRelocatableTag;
> };
> template <class T>
> concept IsRelocatable = requires(T t) {
> typename T::IsRelocatableTag;
> };
> ```
>
> 也可为其继承一个特殊的基类，然后用 is_base_of。

**三目运算符 / cmov**

[cmov](https://www.cs.tufts.edu/comp/40-2011f/readings/amd-cmovcc.pdf) 即 conditional move，格式为`CMOVxx dst, src`，在满足条件码 xx 时将寄存器 src 的值赋值到 dst 中。
cmov 实现的分支通常包含：一个 test 或 cmp 比较，一个 mov，一个 cmov。

```cpp
int f(int cond, int t, int f) {
    return cond > 1 ? t : f;
}
f(int, int, int):
    cmp     edi, 1
    mov     eax, esi
    cmovle  eax, edx
    ret
```

与使用分支跳转相比，条件传送 cmov 可以避免分支预测错误对 CPU 流水线的影响，在某些场景下效率更高。

但是否使用 cmov 可能与代码无关：不管是三目运算符还是 if else，对于 ARM 和 gcc，无优化则生成分支跳转，有优化则可生成 cmov（对于简单的表达式）。
因此不需要太纠结使用三目运算符还是 if else？

但是，优化产生的 cmov 也无法利用分支预测，在分支结果稳定时性能可能更差（不确定）？不过 cmov 支持 SIMD，在大量分支比较中可能很有优势。

> 如果需要将 bool 值作为01进行运算，那么直接将 bool 表达式作为操作数，而非使用它进行条件判断获得01，可能更好，因为后者太复杂可能不会优化成 cmov。

**大数组的读写会更慢吗**

好像数组的大小一般不太重要，除了关注连续性外（单个数组通常比多个数组更好），更应该关注代码的可读性和易维护性，所以分配一个大数组是可以的（前提是真的必须，并没有多少这样的需求）。

大数组通常是一个结构体的数组。
如果需要遍历结构体数组中的某个元素，为了提高连续性，可能需要把 AoS (结构体数组，Arrray of Structs) 替换为 SoA (包含数组的结构体, Struct of Array)。
比如：对于`struct A{Other o; int x;} a[N]`，如果要经常遍历`a[i].x`，即`for(i=0; i<N; i++) f(a[i].x); `，可能将所有 x 定义成一个连续数组更好，如：`struct SoAofA{Other o[N]; int x[N];} a;`，遍历`a.x[i]`。

结合 SoA，另一种可能的优化是：将冷热字段分成单独两个结构体，分开存储。
例：

```cpp
struct ind_vec_cold {
    // Cold fields not accessed frequently.
    float ind_1[4096];
    float ind_2[4096];
};

struct ind_vec_hot {
    // Hot fields accessed frequently.
    int n;
};

struct ind_vec {
    ind_vec(int n): hot(n), cold(n) {}
    vector<ind_vec_hot> hot;
    vector<ind_vec_hot> cold;
};

ind_vec data(NT);
for(int i = 0; i<100; i++){ // Not slow anymore!
    data.hot[i].n = 1;
}
```

**下取整**

不要用 floor(x+0.5)，在 x 是整数时可能会导致结果为 x+1。
用 std::round 或 std::lround。

**有符号与无符号整数比较**

在汇编中没有类型信息，没有什么有符号无符号的区分，整数之间的比较都是通过一条 cmp 完成，但 cmp 会设置所有标志位，编译器可以根据实际数据类型来使用不同的标志位、生成不同的跳转等指令来完成有符号或无符号之间的比较：

- jl, je, jle, jge：cmp 按有符号比较设置的标志位。
- jb, ja, jbe, jae：cmp 按无符号比较设置的标志位。

所以对于`if (a < b)`：

- a 是有符号、b 是无符号，或 a, b 都是无符号：编译器按照无符号比较生成 jb。
- a, b 都是有符号：编译器按照有符号比较生成 jl。
- 不管怎样三种情况得到的汇编数和效率是一样的（cmp + 跳转）。

**命令行参数解析**

folly/abseil/boost/LLVM 都有，或者 gflags/getopt/popl/arpg (gcc)。

**niebloid**

> https://zh.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of
> http://eel.is/c++draft/algorithms.requirements#2

niebloid 是有以下特点的函数式实体：

- 调用时不能显式指定模板实参。
- 不对实参依赖查找 ADL 可见。
- 通过对函数调用运算符左侧的名字进行无限定查找找到它们时，禁止 ADL（会跳过第二阶段查找）。

函数对象满足上述所有要求，所以是 niebloid。通过编译器扩展也能实现它们。

> 去掉 CPO 中的可定制、受 concept 约束两个条件后的对象就是 niebloid，即 constexpr-constructible 的函数对象。它通过同样的避免二阶段查找的方式避免调用无约束的 std 算法。

算法的 ranges 版本都是 niebloid。ranges 版本提供了 concept 检查，所以称为受约束算法 (constrained algorithm)，相比 std 中的算法更好。
如果 ranges 算法不是 niebloid、只是一个函数，由于它们接收 iterator-sentinel 对，不如 std 算法特化（ranges 更通用、std 更特殊），所以在不加限定时它们不会被重载决议选择。通过将其定为 niebloid（非函数），可以在*无限定的名字查找*时避免第二阶段查找和 ADL，从而调用 ranges 算法。

```cpp
// 无限定查找找到 ranges::find (niebloid)
// 因此不会进行第二阶段，即使 std::find 可见且更合适、且 begin() 来自 std
using namespace std::ranges;
vector<int> vec{1,2};
find(begin(vec), end(vec), 2);
```

> niebloid 是 range v3 作者 Eric Niebler 起的名字。

**定制点对象** (**CPO**)

> 定制点指对于一个特定名称、特定功能的函数调用，可能需要派发给不同的具体实现的调用点（比如视情况决定是 std 还是自定义重载）。
> CPO 的实现原理是：无限定名字查找中，如果在第一阶段找到了同名函数对象，则不会进行第二阶段的 ADL 查找。
>
> http://eel.is/c++draft/customization.point.object
> https://zh.cppreference.com/w/cpp/ranges/cpo
>
> 扩展：https://quuxplusone.github.io/blog/2018/03/19/customization-points-for-functions/
> https://zclll.com/index.php/cpp/cpo_niebloid.html
>
> TODO：https://www.zhihu.com/question/518132411
> https://zhuanlan.zhihu.com/p/431032074
> tag_invoke

定制点对象 (Customization point object) 是一个[字面类类型 (*literal type*)](https://zh.cppreference.com/w/cpp/named_req/LiteralType)的函数对象，它与程序定义的类型进行交换，并在交互时强制实施某些语义要求。
换句话说，CPO 是满足以下条件的对象：

- 可调用（是 const 函数对象）。
- 拥有至少一个 constexpr 非复制/移动构造函数 (constexpr-constructible)（字面类型的要求）。
- 可定制。
- 受 concept 约束 (concept-constrained)（就是标准中的语义要求 semantic requirements，虽然 concept 只能检查语法检查不了语义）（更安全、报错友好）。

因为 ADL 只对函数有效，对函数对象无效，所以 CPO 不对 ADL 可见？当选择该名字时，会禁止 ADL？行为会更可预测？

与具名函数相比，CPO 的好处是将定制点分成了两部分？

1. 用户需要特化的部分。
2. 用户需要调用的部分（不能特化）。

**引入 CPO 的原因**

> https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4381.html
> https://stackoverflow.com/questions/53495848/what-are-customization-point-objects-and-how-to-use-them/
> http://ericniebler.com/2014/10/21/customization-point-design-in-c11-and-beyond/

在涉及泛型时，通常使用以下方式调用某函数：

```cpp
template<class T>
void f(T& a, T& b) {
	using std::swap;
	swap(a, b);
    // std::swap(a, b); // 错误：T 可能自定义了 swap
    // ...
}
```

如果 T 所在的空间自定义了 swap，则 f 会使用它，否则会使用 std::swap。
C++20 引入了 concept 类型约束。即使为 std::swap 添加约束，如果重载选择了自定义的 swap，也会绕过该约束。
所以希望有一种方式能够调用确定的、带有约束检查的 swap，在检查完后再通过上述方式转发到 std::swap 或用户定义的 swap。

> 为 T 类型重载标准库函数，通常意味着 T 满足对应函数的要求。比如：为 T 重载 swap，应该意味着 T 也满足 [std::swap](https://zh.cppreference.com/w/cpp/algorithm/swap) 对实参的约束（毕竟标准库的许多算法可能会调用 T 的 swap，遵守标准库的约定也更好）。
> 但是用户定义的 swap 很可能没有这些约束，如果 T 不满足约束就可能在标准库的某些其它地方出错（用户和标准库都认为 T 可 swap，但实际上 T 不能）。
> 通过统一的 CPO 强制这些约束对用户和标准库都更好。

函数调用时的*无限定的名字查找*有两阶段，如果在第一阶段找到了非函数的对应名字，就会跳过第二阶段和 ADL。因此同名的函数对象 swap 会优先于 std::swap 和通过 ADL 找到的用户定义的 swap 被选中。通过对该函数对象的 operator () 附加约束，就可以保证应用约束。

```cpp
namespace std {
    namespace __detail {
        // std::swap 实现...

        struct __swap_fn {
            template <class T>
                requires ... // 约束检查
            void operator () (T& a, T& b)
				using std::swap;
                swap(a, b); // 一样的调用方式
            }
        };
    }
	namespace {
        // 函数对象，但不是函数
        inline constexpr __detail::__swap_fn swap{};
    }
}
```

> 引入 CPO 的另一个原因是`using std::swap; swap(...);`这样的写法容易错，可能会忘记 直接调用`std::swap(...)`。通过将 std::swap 设计为 CPO、在内部进行派发，就可以直接用 std::swap 也不会出错了，并且兼容原先的 using 写法。

[ranges::swap](https://zh.cppreference.com/w/cpp/utility/ranges/swap)、ranges::begin 等都是 CPO。std 中的 swap 因为兼容性所以没有修改？
CPO 一般只用于编写库函数？begin, size 等通用函数都适合用它实现。

**map<double>, set<double>...**

因为 double 比较的问题，这类容器通常只能自己写比较函数和哈希函数，除非是绝对相等。
但要注意这种比较关系必须可传递，不能像常规的浮点比较一样比较 eps（会出现 a != c 但 a = b & b = c -> a = c 的情况）。所以这种需求通常并不合适。
可以先舍入到指定精度再保存、使用绝对相等比较（或者直接转为整数再存？）。




---

## end









