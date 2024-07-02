# 语言：C++

Tags: 笔记


-----

[TOC]

-----

TODO：

RTTI

## C/C++

> cppcon 社区：https://cppcon.org/about/
>
> 资源：https://zh.cppreference.com/w/cpp/links
> C++：https://wg21.link/
> C++ 20：https://timsong-cpp.github.io/cppwp/n4861/ （仓库及各版本：https://github.com/timsong-cpp/cppwp）
> 下载：https://www.open-std.org/jtc1/sc22/wg21/docs/standards
> 最新草案：https://eel.is/c++draft/
>
> Benchmark：https://quick-bench.com
> gdb online：https://www.onlinegdb.com/
>
> 术语表：https://zh.cppreference.com/w/bilingual_glossary
> 缩写术语介绍：https://quuxplusone.github.io/blog/2019/08/02/the-tough-guide-to-cpp-acronyms/
>
> CWG：https://github.com/cplusplus/CWG
>
> 提案：https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/

**对象**

一个[对象](https://zh.cppreference.com/w/cpp/language/object)拥有以下性质：大小，对齐要求，存储期，生存期，类型，值，可选的名字。
以下实体都不是对象：值，引用，函数，枚举项，类型，类的非静态成员，模板，类或函数模板的特化，命名空间，形参包，this。
[对象类型](https://zh.cppreference.com/w/cpp/types/is_object)是除了函数、引用和 void 外的任何可有 cv 限定的类型。

变量由声明引入，是一个对象或一个非静态成员以外的引用。

对象可以使用定义、new 表达式、throw 表达式、更改联合体的活跃成员、求值要求临时对象的表达式显式创建，也可通过隐式对象创建操作进行隐式创建。

> 类型或对象的对象表示中不属于值表示的位是填充位 (padding bits)，用来实现内存对齐和特定大小的位域。
> 读写填充位是 UB。

**生存期 (lifetime)**

每个对象和引用都有[生存期](https://zh.cppreference.com/w/cpp/language/lifetime)。访问生存期外的对象是 UB。
具体见文档、*C++17 - launder*。

**隐式生存期类型 (Implicit Lifetime Type)**

> https://zh.cppreference.com/w/cpp/language/object
> https://zh.cppreference.com/w/cpp/named_req/ImplicitLifetimeType

见 *C++17 - launder*。

**位域** / **(bit field)**

[位域](https://zh.cppreference.com/w/cpp/language/bit_field)允许声明具有以位为单位的明确大小的类数据成员，只能是整型或枚举。
位数可以定义很多，但不会超过原类型的值域，多余位为填充位。

如：类中定义`unsigned int b: 3;`为3位，值域0~7。

多个相邻位域通常会打包在一起（但这是实现定义行为）。
一个 T 类型的位域所使用的位，不能跨过其对齐边界（包括匿名位域占据的填充位），即位域和匿名位域仍要满足对齐要求。
比如 unsigned char 不能使用从某字节开始的 6 ~ 9 位，因为跨越了对齐边界；uint16_t 可以使用第 2k 字节开始的 6 ~ 9 位，但不能是第 2k+1 字节开始的（会跨越 2k+2）。

匿名位域 (unnamed bit field) 会引入指定数量的填充位，并且不会影响对象的对齐。
当经过匿名位域填充后，该类型剩余的位数不足以存放下一个位域，或在此存放将跨越对齐边界时，就需要在新的分配单元开始下一个位域（零大小匿名位域强制进行该过程）。

```cpp
struct S {
    // 通常会占用3个字节：
    unsigned char b1 : 2; // 第1个字节开始，前2位为 b1
    unsigned char : 2; // 下2位被跳过，未使用
    unsigned char b2 : 6; // 第1个字节只剩4位，unsiged char不能跨过字节，因此要开始第2个字节，前6位给 b2
	unsigned char : 0;
    unsigned char b3 : 2; // 即使第2个字节足够，但零填充强制开始新的字节
	unsigned int : 6; // 刚好使用剩下的6位，且不影响结构体的对齐边界（不需要4字节对齐）
};
struct S2 {
    // 通常会占用8个字节：
    unsigned char b1 : 4;
    unsigned int : 29; // 如果放在前面的4字节，会跨越第4字节，因此需要从第5字节开始放
    // 如果是28，则大小为4字节，能正好利用4字节剩下的位不跨越
};
```

C++20 起，允许为位域添加默认初始化器：`int b: 1 = 0;`或`int b: 1 {0};`。

不能对位域使用取地址符 &，因此不存在到位域的指针。非 const 引用不能用位域初始化。**如果某个 const 引用通过位域初始化，则该引用会绑定到一个与位域的值相同的临时量上，并不会引用位域**。
因此，位域限制很多极少用。

**类型**

对象、引用、函数、表达式 都有一种称为[类型](https://zh.cppreference.com/w/cpp/language/type)的性质。

类型分类：

- *基础类型* (is_fundamental)：算术类型、void、nullptr_t。
    - *算术类型* (is_arithmetic)：整数类型 (integral types)（bool、各类 char（见 *字符类型*）、各类 int）、浮点类型 (floating-point types)。
- *复合类型* (is_compound)：引用（包括到对象/函数的左值/右值引用）、指针（包括成员指针）、数组、函数、枚举、类（包括 class 与 union）。

此外还有额外的分类（如果存在，则都包括对应的 cv 限定类型，省略）：

- *对象类型* (is_object)：函数、引用、void 外的类型。
- *标量类型* (is_scalar)：算术类型（整数、浮点）、指针、枚举、nullptr_t。
- *平凡类型* (is_trivial)：标量类型、平凡类（可平凡复制，且至少有一个合格的默认构造，且它们都是平凡的），及它们的数组。
- *POD 类型* (is_pod)：标量类型、POD 类，及它们的数组。
- *字面类型* (literal type)：标量类型、void、引用、特定的类，及它们的数组。是 constexpr 变量可拥有的类型。
- 其它类型，比如各[具名特征要求](https://zh.cppreference.com/w/cpp/named_req)。

**类的内存布局**

对于类 A 的对象 a，A 的每个非静态、非引用数据成员，都在 a 的存储的某个部分分配。引用成员是否占用存储是实现定义。

类的[*布局 (layout)*](https://zh.cppreference.com/w/cpp/language/data_members)：
C++23 前，在相同访问权限的成员之间，保证按照声明顺序从低到高分配内存；不同访问权限的成员之间没有规定，可以交替（未指明）。
C++23 起，要求非零大小的成员按照声明顺序依次分配内存，不受访问权限影响。

**POD**

[POD (plain old data)](https://zh.cppreference.com/w/cpp/language/classes)（*简旧数据类型*）中 plain 指它是一个普通/平凡的类型，old 指与 C 兼容。
POD 是一个与 C 兼容的类型，它没有虚函数、虚继承等 C++ 的新特性，还可以使用 memset 或 memcpy 进行初始化或拷贝。

所有标量类型 (非 数组/类/结构体/联合) 和 满足 平凡的、标准布局的 两个特性、且没有非 POD 类型的非静态成员的类/结构体 是 POD 类型，它们的构成的数组也是 POD 类型（具体见[cppref](https://zh.cppreference.com/w/cpp/language/classes)）。
满足 平凡的、标准布局的 类或结构体，实际上就对应 C 中的 struct（C++ 的 struct 也是为了兼容 C，但在 C++ 中变成了与 class 基本一样）。

内置类型是 POD 的。
只有 POD 类型才可以作为 union 的成员。union 很大部分也是为了兼容 C？

通过`is_pod`判断一个类型是否为 POD。
还有一个`must_be_pod`让编译器确保一个类型一定是 POD 的。

POD 的优点：

- 可以安全地使用 memset 和 memcpy 对 POD 类型进行初始化和拷贝。非 POD 不保证可以。
    通过 memcpy 将对象的数据拷贝到一个 char 数组，然后再拷贝回来，还是原来的对象。
- 数据与 C 的内存布局相同，所以用 POD 数据在 C 与 C++ 间进行交互是安全的。
- 可以进行静态初始化。静态初始化一般比较高效且简单（比如放入目标文件的.bss段，在初始化中直接被赋0）。

POD 的特点：

- 通过 goto 语句从某个变量还不存在的作用域内，跳到它已经存在的作用域内，是非法的（编译器会报错），但对于 POD 类型没有该限制。
- C++ 标准保证 POD 类型的开头不会填充任何内容（虚指针，空基类）。也就是，如果一个 POD 类型 A 的第一个成员是 T 类型的，可以安全地从 A\* 到 T\* 进行 reinterpret_cast，获得一个 T 的指针，反之亦然。

满足下面所有条件的 类/结构体 为**平凡的**/**平凡类** (is_trivial)：

1. 拥有平凡的默认构造函数 (trivial constructor) 和析构函数 (trivial destructor)。
    平凡的构造函数指 编译器给出的默认的（什么都不干的）构造函数，一旦我们定义了任意构造函数，即使这个函数也是空的、什么都不干，因为它不是默认的，所以也不是平凡的构造函数。通过 = default 可以显式定义默认的构造函数。
    析构函数类似。
    **所以对于默认构造和析构，平凡意味着除了调用成员的默认构造/析构函数外，什么都不用干。**
2. 拥有平凡的拷贝构造函数 (trivial copy constructor) 和移动构造函数 (trivial move constructor)。
    同上，平凡的拷贝/移动构造函数是编译器默认给出的实现。
    平凡的拷贝构造函数可以直接用 memcpy 或 memmove 一次完成拷贝，不需要对成员变量依次赋值。
    **所以对于拷贝/移动构造函数，平凡意味着可以通过简单的内存拷贝/移动完成构造。**
3. 拥有平凡的拷贝赋值运算符 (trivial assignment operator) 和移动赋值运算符 (trivial move operator)。
    同拷贝构造函数和移动构造函数。
4. 不能包含虚函数和虚基类。

满足下面所有条件的 类/结构体 为**标准布局** (is_standard_layout)：

1. 所有非静态成员有相同的访问权限 (只有 public/private/protected 一种)。

2. 没有虚函数和虚基类。

3. 要在同一个类中声明所有非静态数据成员（全在派生类或全在某个基类）。即派生类和（多个）基类之间，只能有一个类有非静态成员。

4. 对于一个派生类，其第一个非静态成员的类型不能是其基类。
    如：`struct B : A { A a; };`不满足，`struct B : A { int t; A a; };`满足。

    这个是因为 C++ 要求相同类型的对象必须地址不同而产生的：设一个类 B 中包含了某个空类 A，如果 B 继承自 A，且 B 的第一个成员是一个 A 类型的成员 a，则这个**空类** a 仍然需要占用1字节。如果不分配1字节，则两个 A 类型对象 (B 的实例与成员 a) 会拥有相同的地址。
    如果 B 不继承自 A，或 B 的第一个成员不是 A 类型，则空类不会占用空间，POD 就要满足这点。

5. 所有非静态数据成员均符合标准布局，其基类也符合标准布局。

> C++ 要求相同类型的对象必须地址不同，但不同类型的对象地址可以相同。因为地址也是对象标识的一部分。
> 像构造函数中经常会有自我赋值的检查`if (this != &other)`，如果不同类型的对象可以有相同地址，那这个检查就是无效的了，没办法识别不同对象。

标准布局类型 (Standard Layout Type) 必须应用空基类优化，来保证指向标准布局对象的指针在用 reinterpret_cast 转换后还指向其首成员。这是标准布局要求 3,4 的原因。

静态数据、成员函数是不会影响内存布局的。
标准布局的类不允许编译器在里面加额外的东西，非标准布局的类可以（比如多态类的虚表里可以放 RTTI）。

**未定义行为** / **各类 behavior**

C++ 标准中一共规定有四类 behavior，分别是 well-defined behavior、implementation-defined behavior、unspecified behavior 以及 undefined behavior。

> https://zh.cppreference.com/w/cpp/language/ub
> 正确的 C++ 程序不存在 UB，因此编译器可以在不存在 UB 的假设下进行优化。
>
> 为什么会有未定义行为，不都做出规定？
> 具体见 https://zhuanlan.zhihu.com/p/391088391 ，简单来说：
>
> 1. abstract machine 只是一个假想的模型，实际上的硬件/软件环境太多，在某个平台上的 well-defined behavior 可能是另一个平台上的 undefined behavior。
>     比如大部分 CPU 上，[有符号整数的溢出](https://zh.cppreference.com/w/cpp/language/operator_arithmetic)是一个 perfectly well-defined behavior，但在某些 CPU 芯片上，有符号整数溢出却会导致 trap，或是被保留到最大值或最小值；绝大部分平台上，解引用空指针会 trap，但某些嵌入式平台上，读写 0 地址是完全合法的；而且空指针是否就是 0 也不一定？
>     对这些在不同的平台上存在严重分歧甚至 trap 的行为，将其归为未定义行为，因为程序的结果将取决于更底层的操作系统或硬件设计。
> 2. 再好的语言设计也无法保证程序在关键数据损坏的前提下，仍然拥有预期的行为。
>     比如某 bug 导致某对象的虚表指针被修改、两个类型完全不兼容的指针发生了 alias（见 *严格别名*），都不能指望程序依然拥有预期的行为。因此标准规定在数据受到损坏时，任何与损坏的数据发生交互的行为都是未定义行为。
> 3. 消灭未定义行为的代价就是限制语言的能力（如不能直接读写内存、不能操作指针），以及大量的编译期或运行期检查。但 C++ 设计上就不是受太多限制的，且编译/运行期检查并不能完全检测所有 UB，还会影响编译和运行效率（如数组越界、空指针检查），所以不如直接放弃检测。
> 4. 不约束 UB 如何处理，可以允许编译器有更好的优化能力。
>     编译器通常不会考虑 UB 的影响，甚至假设程序没有任何 UB 并以此进行优化。但这也导致编译器不会对某些错误给出警告。
>     比如：将空指针解引用定为 UB，可以避免指针检查和抛出异常；将修改 const 对象定义为 UB，可以利用语义优化 const 对象的访问。
>     其它例子见上链接。

**well-defined behavior**

标准明确规定的所有的 C++ implementation 都需要实现和遵守的行为。
一个抽象机器从初始状态开始，执行一个仅包含 well-defined behavior 的程序，最终一定处于一个确定的、由标准明确规定的最终状态。

程序必须*良构*、且没有实现定义行为、未指明行为、未定义行为，才能保证其行为是由标准规定的。

**implementation-defined behavior**

标准没有明确规定、但要求每个 C++ implementation 必须在其文档中明确规定的行为。
一个抽象机器从初始状态开始，执行一个仅包含 well-defined behavior 和 implementation-defined behavior 的程序后，abstract machine 一定处于一个确定的、由 C++ implementation 的文档所明确指明的状态。
Well-defined behavior 和 implementation-defined behavior 都规定了 abstract machine 的确定性行为。

比如：表达式`sizeof(int)`、有符号负数右移（C++20 前）、无符号数转到位数相同的有符号数（[C++20 前](https://stackoverflow.com/questions/13150449/efficient-unsigned-to-signed-cast-avoiding-implementation-defined-behavior)）。

**unspecified behavior**

标准没有明确规定、也不要求每个 C++ implementation 必须在其文档中明确规定的行为。但标准会规定一组可能的行为，unspecified behavior 的具体运行时行为只能是这一组可能的行为中的一个或多个。
它规定了抽象机器的非确定性状态转移：抽象机器从一个初始的状态开始，执行一个包含 unspecified behavior 的程序，最终状态可能是标准所限定的若干最终状态中的一个。

比如：求值顺序`f(g1(), g2())`、`g1() + g2()`。

**undefined behavior**

> 一些 UB：https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1705r0.html

标准没有明确规定、不要求每个 C++ implementation 在其文档中明确规定、且标准没有对具体行为施加任何限制的行为。因此任何处理方式都是符合标准要求的，假设它不存在也是合理的。
它规定了抽象机器的非确定性状态转移：抽象机器从一个初始的状态开始，执行一个包含 undefined behavior 的程序，最终状态可能是任何一个状态。标准没有对最终状态施加任何限制。

比如：使用未初始化的标量类型、数组越界、**有符号整数溢出**、有/无符号数左/右移大于等于它的位数（注意移位时需要自行取模，不能左/右移64）、有符号负数左移（C++20 前）、空指针解引用、非 void 函数执行完成但没有返回值（应声明`__attribute__((noreturn))`）、无副作用的死循环、求值不确定值（如默认初始化的基础类型。除了少数例外）、将浮点值赋给无法表示该值的类型（包括赋 DBL_MAX 给 float）。
（C++20 起有符号整数溢出还是 UB，但负数[移位运算](https://zh.cppreference.com/w/cpp/language/operator_arithmetic)不再有 UB）

**非良构 (ill-formed)**

程序拥有语法错误或可诊断的语义错误。遵从标准的编译器通常必须为此给出诊断。
执行非良构程序也是 ub。

*非良构而不要求诊断*：程序拥有通常情况下可能无法诊断的语义错误（例如 ODR 的违规或者其他只能在链接/运行时检测的错误）。

**as-if rule**

[as-if 规则](https://zh.cppreference.com/w/cpp/language/as_if)指：编译器可以对程序进行任何修改，只要保证以下几点：

- 对 volatile 对象的读写 严格按照它们在程序中的**代码语义**（不能优化掉）和**顺序**（和其它 volatile 对象的读写的相对顺序不会改变）进行。（volatile 对象之间会生成屏障，避免重排）
- 程序终止时，写入文件的数据与程序代码所预期的一样（产生的可观测副作用不会改变）。
- 发送到交互式设备的提示文本，将在程序等待输入之前显示出来（同上）。
- 某些情况下产生的浮点异常一样。

由于编译器通常不能分析外部库代码，来确定它是否执行或影响 IO/volatile，所以无法对其进行这种随意优化。
复制消除和 new 表达式是例外，即使它们有可观测副作用，编译器也可以优化掉。

**零开销原则 (zero overhead)**

零(额外)开销原则指：不会为没使用的功能付出代价；对使用了的功能，无法写出更好的代码（它的开销无法忽略、已经是最小的）。
zero overhead 并不是 zero cost，overhead 是额外的、非必要的成本。

C++ 中不满足零开销的只有 RTTI (typeid) 和异常。

**初始化**

> C++ 的初始化和赋值是严格分开的，对于尚不存在的对象，一定是构造而非赋值。
>
> 默认构造是指无参数或所有参数都有默认实参的构造函数，平凡的默认构造一般指编译器生成的具有默认实现的默认构造函数。

C++ 有多种[初始化方式](https://zh.cppreference.com/w/cpp/language/initialization)：

- **常量初始化 (constant initialization)**

设置静态变量（包括 thread_local）的初值为编译时常量。
会在其它初始化之前发生（通常在编译期），并取代默认的零初始化。

- **默认初始化 (default initialization)**

不使用初始化器构造变量时执行的初始化。
如果是类，则检查是否有默认构造函数并调用；如果是数组，对每个元素进行默认初始化；否则不进行初始化。
静态和线程局部变量会进行零初始化，其它变量则为不确定值。const变量则要求必须能进行默认初始化。

注意，对于类会调用基类和成员的默认初始化（如果在初始化列表中定义，则按列表来）；**POD 类型的默认初始化是不进行初始化**。
如果类没有默认构造，则 CE。
编译器隐式生成的默认构造函数不会进行任何初始化，它与拥有空函数体和空初始化器列表的用户定义的构造函数有严格相同的效果。

```cpp
new T;
Node a;
```

- **值初始化 (value initialization)**

以空初始化器列表进行的初始化。**小括号花括号都可。**
如果是类，如果有平凡的默认构造函数，则零初始化，否则调用默认构造函数。
如果是数组，对每个元素进行值初始化。
否则零初始化。

```cpp
new T(); // 空括号即为值初始化
new T{};
Node a{}, b();
```

- **直接初始化 (direct initialization)**

调用对应构造函数初始化。**只能用小括号。**

```cpp
int y(0);
Node a(1, 2);
```

- **复制初始化 (copy initialization)**

C 风格，不提供错误检查和类型安全性。

```cpp
int x = 0;
int h = {0};
return {1};
```

复制初始化选择构造函数时，不会考虑 explicit 构造函数和 explicit 用户定义转换函数。这就是 explicit 的含义或实现方式。

```cpp
struct A {
	explicit A(int) {}
	A(double) {}
};
// 调用 A(int)
A a(1);
A b = A(1);
// 调用 A(double)，因为只有该函数可选
A c = 1; // int只能通过直接初始化构造（即显式使用构造函数）
```

在 C++17 前需要对象可拷贝。所以代码`atomic<int> a = 0;`可能会CE （use of deleted func 'atomic(const atomic<int>&)'），需要直接初始化。C++17 后该写法不需要走拷贝构造（复制消除）。

**当赋值表达式是同类型的临时量时，*复制消除* 允许直接将临时量在对象上进行构造，以消除复制或移动构造函数。**

- **列表初始化 (list initialization)**

**只能用花括号。**

简单来说，依次进行：

- 如果 T 是聚合体，且花括号初始化列表仅包含一个同类型（或子类型）的元素，则直接从该元素构造对象（根据是否有等号，进行复制初始化或直接初始化）。
- 如果 T 是聚合体，进行聚合初始化。
- 如果花括号初始化列表为空，且 T 有默认构造，进行值初始化。
- 检查 T 是否有以 initializer\_list 为唯一形参（或其它形参都有默认值）并且类型匹配的构造函数，如果有则调用；
    否则如果 T 存在一个以 initializer\_list<X> 为唯一形参（或其它形参都有默认值）的构造函数，并且初始化列表内的每个元素都可以非窄式隐式转换到 X（比如 const char\* -> string），则调用；
    否则尝试将初始化列表中的元素进行任意非窄化转换，直到匹配某个构造函数（如果是复制列表初始化，则不能选择到 explicit 的构造）。

> 例外：C++20 起聚合体和数组能用小括号进行聚合初始化，但不能有指派符。
> 但这又导致小括号初始化引用时，不会延长绑定的临时量的生存期。
> 比如：`struct A{ int&& v; };`，`A{1}`会延长右值的生存期，但`A(1)`不会，会有悬垂引用。

```cpp
int arr[] {1, 2}; // 直接列表初始化
int arr[] = {1, 2}; // 复制列表初始化
// 因为 int[] 是聚合体，所以上面实际都是聚合初始化
int arr[] (1, 2); // C++20 起，允许小括号进行聚合初始化

vector<int> v {1, 2};
vector<int> v = {1, 2};
vector<Node> v {1}; // 注意，如果1无法转换成T，那么将选择其它的构造函数而非vector(initializer_list)，比如此处将会选择vector(size)，设置其大小为1
```

[**聚合初始化 (aggregate initialization)**](https://zh.cppreference.com/w/cpp/language/aggregate_initialization) 是列表初始化的一种，只适用于聚合体。
*聚合体*/*聚合类* (aggregate) 包含两种类型：数组，符合下面条件的类：

- 没有用户提供、继承或 explicit 的构造函数（C++20 前）；没有*用户声明*或继承的构造函数（C++20 起）。
- 没有虚函数、没有虚基类。
- 所有基类都是 public。
- 所有非静态数据成员都是 public。

聚合体可以用`{...}`依次初始化类中的各成员（按声明顺序）。如果成员也是聚合体，则用嵌套`{...}`初始化，如：`Node x = {1, {1, 2}};`（如果是用的等号赋值可以忽略内部大括号）。

当初始化器列表数量少于成员数量时，只显式初始化前面这些成员。
没有显式初始化的成员，如果定义了默认成员初始化器（如`int v{3}`）则使用；否则，如果它不是引用，以空初始化器列表初始化它（即值初始化）；否则程序非良构。
如果聚合体是联合体，那么显式初始化的元素不能多于一个，否则非良构。

> C++11 中，默认成员初始化器将导致类不再是聚合体，不能进行聚合初始化。
>
> 聚合初始化限制比较大，且只能依次初始化，只适用于简单的结构体。

C++20 起聚合初始化支持用指派初始化器初始化聚合体。
指派符的顺序必须与声明顺序一致。没有初始化的元素规则同上。

```cpp
struct A {
	int a;
	bool b{true};
	string c;
};

A a {1, true, "abc"};
A b {.a = 2, .c = "abc"};
```

> array 是聚合体（包含一个 T 数组），所以能进行聚合初始化，比如：`array<int, 3> arr {{ 1, 2, 3 }};`。
> 在某些未修正的远古 C++11 中，由于 array 没有接收 init_list 的构造函数，因此`arr {1, 2, 3};`会错误。现在不会，但 array 还是没有构造函数的？不然就不是聚合体。

**零初始化 (zero-initialization)** 的[规则](https://timsong-cpp.github.io/cppwp/n4659/dcl.init#6)为：

- 如果 T 是标量类型，则将 0 转换为 T 进行赋值。
    标量类型见 *C++ - 基础类型*，就是整数、浮点、枚举、指针、nullptr_t。
- 如果 T 是非联合的类，则类的每个非静态数据成员、每个非虚基类子对象被零初始化，且对齐边界为 0。（如果对象不是基类子对象，那么还包括每个虚基类子对象。如果 B 继承 A，那么 A 是 B 的一个基类子对象）
- 如果 T 是联合类型，则其第一个非静态具名数据成员被零初始化，且对齐边界为 0。
- 如果 T 是数组，对其每个元素进行零初始化。
- 如果 T 是引用，不做任何初始化。

注意，在构造函数函数体内写成员的赋值，并不算第一步初始化；如果成员没有使用初始化列表或指定默认值，则会在进入构造函数前调用默认构造完成初始化，构造函数内进行的赋值只是一次额外的赋值操作。
如下例中，x, y 均被默认初始化一次，但随后 y 被额外赋值一次。所以最好使用初始化列表。

```cpp
struct Node {
    Node(int a, int b): x(a) {
        y = b;
    }
    int x, y;
};
```

**使用 {} 初始化 / 列表初始化**

花括号列表可以初始化对象。如果对象有接收 *initializer\_list* 参数的构造函数则完整传入，否则将里面的元素依次传入构造函数。

> 如果涉及容器，可能更推荐复制初始化`T a = T(...)`，因为用 {} 与 () 的结果不同，而且也不会真的发生复制。
>
> 注意，如果对象有 initializer_list 的构造函数重载（或对象是一个模板类型 T），则`T{...}`将调用该重载，而不是其它构造函数。
> 因此如果要避免走初始化列表，要用`T(...)`而非大括号！想走初始化列表应该用`T({...})`。
> 常见的情况是 vector、string：
>
> ```cpp
> cout << string(48, 'a') << '\n'; // 48个a
> cout << string{48, 'a'} << '\n'; // 0a
> 
> auto f = [](auto vec) {
> for (auto v: vec) printf("%d ", v);
> puts("");
> };
> f(vector<int>(3, 1)); // 1 1 1
> f(vector<int>{3, 1}); // 3 1
> ```

更推荐使用现代的大括号初始化（尤其是基本类型），除非类有 initializer_list 构造函数（所以自定义的类需要谨慎设计）。
优势：

- 列表初始化可用的场景更多，能用做任何类型的初始化？所以也叫统一初始化 (uniform initialization)。

```cpp
// 可以初始化容器
vector<int> v{1,2,3,4}; // ok
vector<int> v2(1,2,3,4); // error

// 可以为非静态成员指定默认值。没有在成员初始化器列表中赋值时会使用。
// 见 *面向对象 - 成员初始化*
class Node {
    int x{0}; // ok
    int y = 0; // ok
    int z(0); // error
};
```

- 可避免隐式的*窄化转换* (narrowing conversion)，如 double 值传给 int，{} 不允许。

```cpp
double x, y;
int sum1{ x + y }; // 禁止，编译错误

int sum2(x + y); // 编译通过，但是x + y精度会丢失
int sum3 = x + y; // 同上
```

- 可避免一个歧义的语法解析规则 (*most vexing parse*，见下)。
    该解析规则是：当一条语句可以被编译器解析成函数声明时，会优先将该语句视为函数声明，即使该语句的意图不是函数声明。

```cpp
struct A {
	A() {puts("create A");}
};
A a(); // 声明了一个返回A的函数，而非创建A对象
A b{}; // 调用默认构造，创建A对象
A c(1); // ok，不能看做函数声明
A d(int(val)); // 非变量，可看做函数A func(int val)
A e(A()); // 非变量，可看做函数A func(A)
A(); // 不会被视作函数声明，但也没什么用
```

缺点：

- auto 推导类型时，会推导成 std::initializer_list。
    `auto x{1}`的 x 类型是 int，但`auto x = {1}`的类型是 std::initializer_list<int>。
- 如果不存在以 initializer_list 为形参的构造函数，大小括号就区别不大。
    **但只要存在，编译器就会优先选择该构造函数**（且尽可能将实参隐式转换为 initializer_list 中的类型）。只有实在无法转换时才会选择其它重载（如 string 到 int）。

```cpp
class A{
public:
    A(int i, bool b) {}
    A(int i, double b) {}
    A(string s) {}
    A(initializer_list<long double> l) {
		puts("here");
	}
};

// 调用A(int i, bool b)
A a1(1, true);
// 转换实参类型，都调用initializer_list的重载
A a2{10, true};
A a3{10, 5.0};
// 实参无法转为long double，才选择其它重载
A a4{"abc"};
// 显式调用initializer_list的重载
A a5{{}};
A a6({});
A a7({1, 2});
```

**most vexing parse (最烦人的解析)**

指一个违反直觉的语法解析规则。在以下情况下，C++语法解析器无法区分 对象的创建 和 函数的声明，会统一按函数声明处理。

- 包含强制类型转换的构造函数初始化。
    C 允许在声明变量时附带额外的括号（`int((a))`可以是声明变量 a），所以这类初始化能被视为函数。

```cpp
double v = 0;
// 以下都将被视为函数声明，而非创建对象
int x(int(v)); // int 可替换成任意类型
Node node();
Node node(int(v));

// 解决方法：
// 1. 使用 {}
int x{int(v)};
Node node{};
Node node{int(v)};
// 2. 使用其它类型转换方式
int x(static_cast<int>(v));

// 给 thread 传递仿函数时也常见
struct A {
    void opreator () () {};
};
thread t(A()); // 被视为函数声明：其返回值为 thread，接收一个函数指针（返回值为 A，无参数）
```

- 包含匿名对象的构造函数初始化。

```cpp
struct Timer {};
struct TimeKeeper {
    explicit TimeKeeper(Timer t);
    int get_time();
};
int func() {
    TimeKeeper keeper(Timer());
    return keeper.get_time();
}
// 正确方式：
// 1. 使用列表初始化 {}
// TimeKeeper keeper{Timer()};
// 2. 使用复制初始化
// TimeKeeper keeper = TimeKeeper(Timer());
// 3. 使用额外括号，避免被当做函数
// TimerKeeper keeper((Timer()));
```

keeper 声明语句有两种解释：用一个匿名对象 Timer() 创建和构造 TimeKeeper 对象；声明一个函数，它返回 TimeKeeper，参数为一个函数指针，指向一个返回 Timer 的无参函数。
C++ 将按后者处理，所以 keeper 并不是类对象。

> 注意，如果`T()`不是出现在 {}  内或等号右侧，则很可能被当成一个函数类型（返回 T，无形参）。

**窄化转换 (narrowing conversion)**

列表初始化禁止（顶层的）隐式的[窄化转换](https://zh.cppreference.com/w/cpp/language/list_initialization#Narrowing_conversions)，包括：

- 浮点到整数转换。
- 高精度浮点到低精度浮点转换，除非来源是常量表达式且不会溢出（即使不能精确表示）。
- 整数/无作用域枚举到浮点转换，除非来源是常量表达式，且浮点类型可容纳它的值。，并在转回去时能得到原来的值。
- 整数/无作用域枚举到不能表示其所有值的整数类型的转换，除非 ...（位域相关）或来源是常量表达式，且转换后的类型可容纳它的值。
- 指针或成员指针到 bool 的转换。

**initializer\_list**

> 花括号列表`{1, 2}`不是表达式，因此没有类型，无法其推导类型，`decltype({1, 2})`也非良构。
> 例外：在复制列表初始化中，任何花括号初始化器列表都会被推导为 *initializer\_list*；在直接列表初始化中，花括号初始化器列表必须只含一个元素，推导结果为该元素的类型（见 *auto* 规则）。
>
> 花括号列表不能被用作返回类型未知的函数的返回值，如果从它推导出 initializer\_list，那么返回后会引用不存在的数组。

C++11 引入了[`initializer_list`类型](https://zh.cppreference.com/w/cpp/utility/initializer_list)。当程序 1. 使用花括号初始化列表初始化对象、且对应的实参接收 initializer_list；2. 将花括号初始化列表绑定到 auto 时，就会自动构造一个 initializer\_list 对象。
它实际是一个只读数组（可能分配在常量区），可以作为函数的形参，用 {...} 做实参传递。

初始化列表只是一个模板类`template <class _Elem> class initializer_list{ ... };`，包含两个指针`const _Elem *_First, *_Last`。通过首尾指针就能访问列表的任意元素。
所以 initializer_list 其实是一个语法糖：

```cpp
vector<int> nums = {0, 1, 2};
// 上面与下面的方式等价
int nums_[] = {0, 1, 2};
vector<int> nums = initializer_list<int>(nums_, nums_ + _countof(nums_));

// 提供了迭代器方法，所以可以直接使用
int sum(initializer_list<int> nums)
{
    int res = 0;
    for (const int* it = nums.begin(); it != nums.end(); ++it)
        res += *it;
    return res;
}

// 可以方便地创建临时数组，用来遍历
for (int g : {1, x, y + z}) {
	cout << g << ' ';
}
```

> 因为 initializer_list 只是保存指向常量数组的指针，因此将其直接传入参数也不会发生元素的拷贝（只是拷贝结构体，也就是两个指针）。
> 而通过变量构造它时，会发生变量到数组的拷贝。如：`initializer_list<Node> i{node};`需要将 node 拷贝到指定区域。

因为只读，使用它初始 vector 时，里面的元素要被拷贝到 vector 中，因此它不支持 move-only 对象，所以`vector<unique_ptr<int>>`就不能用它赋值。

> 使用它初始化容器的相关问题 及可能更好的实现：https://zhuanlan.zhihu.com/p/545305641
>
> 它是用来初始化的，不适合存储某些东西。
>
> 它是编译器开洞实现的，以它为参数的函数，在重载时有极高的优先级。

**指针算术**

> https://zh.cppreference.com/w/cpp/language/operator_arithmetic

指针类型表达式 P 加/减整数类型表达式 J 的规则：

- 结果类型与 P 相同。
- 如果 P 求值为空指针值，J 求值为 0，则结果为空指针；
- 如果 P 指向 n 个元素的数组 a，则 P +/- J 的结果必须在 a[0, n] 中，当结果指向 a[n] 时代表该数组的尾指针。
- 如果 P 指向完整对象、基类子对象或成员子对象 o，则 +/- J 的结果只能是0或-1，当是-1时指向 o 的尾指针。

其它情况均为 UB。

**严格别名** (**strict aliasing**)

> https://zhuanlan.zhihu.com/p/595286568
> https://zh.cppreference.com/w/cpp/language/reinterpret_cast
>
> C++ 中，如果有多个左值指向同一内存区域，那它们之间互称为别名 (alias)。比如`int i=1, *p=&i;`，i 是 \*p 的别名，反之同理。
> 类型双关 (type punning) 指绕过类型系统，将一个对象或一块内存解释为不同的类型。
>
> 类型双关的实现方式就是别名。比如定义`int x = 1;`和`float* p = reinterpret_cast<float*>(&x);`，\*p 是 x 的别名，但不是合法别名，因此虽然确实能按 float 的方式访问 int，但在某些情况下，严格别名优化将导致 UB。
> **如果别名类型 P 不是 T 的兼容类型（合法别名），那么通过 P 类型的泛左值修改或读取动态类型为 T 的对象时（比如强制类型转换），行为未定义。**
> 严格别名规则是为了效率，对程序安全性的部分放弃，需要程序员注意。
>
> 想要安全地进行类型双关，见 *pun_cast*（或直接用 bit_cast）。
>
> ```cpp
> double d = 0.1;
> int64_t n;
> // n = *reinterpret_cast<std::int64_t*>(&d); // UB
> std::memcpy(&n, &d, sizeof d);	// OK
> n = std::bit_cast<int64_t>(d);	// OK
> ```
>
> 注意双关除了类型兼容，还要保证两者对齐一致。
> 比如`char[]`与`int`不能直接双关，因为前者的对齐边界为 1。但可以通过`alignas`手动对齐以保证正确。
>
> ```cpp
> char arr[4] = {1,0,0,0}; 
> int x = *reinterpret_cast<int*>(arr); // UB，对齐不同
> // (uintptr_t)(arr) % sizeof(int) != 0 的情况下即违反了对齐要求
> 
> alignas(int) char arr[4] = {1,0,0,0};
> int x = *reinterpret_cast<int*>(arr); // ok
> ```

严格别名是一种优化，通过`-fstrict-aliasing`开启（O2 包括），通过`-fno-strict-aliasing`关闭避免带来错误。
如果编译器始终假设 任何两个指针都可能指向同一地址（正确做法），那么优化空间将会很小、影响效率。
因此，如果 T1, T2 类型并不兼容，或说 T1 类型的指针不是 T2 指针的合法别名，编译器将认为 T1、T2 类型的两个指针绝对不会指向同一地址（也包括引用，毕竟本质是一样的）。
这也被称作 基于类型的别名分析 (*TBAA*, Type Based Alias Analysis)，即根据类型决定两个指针或引用可不可能互为别名。

对于动态类型为 T 的对象，如果类型 P 满足以下条件之一：
（动态类型指 new 时使用的类型，仅 malloc 分配的空间并非已初始化合法内存，还需 placement new）

- P 和 T 类型相似，即在去掉顶层 cv 后满足以下条件之一：
    - P, T 是同一类型。
    - P, T 是指针，且其指向的类型相似。
    - P, T 都是指向相同类的成员指针，且被指向的成员类型相似。
    - P, T 都是数组，且数组元素类型相似。
- P 是 T 的任意 cv 限定版本 或 有/无符号 (signed/unsigned) 版本（cv 与符号性两者可结合）。
- P 是 char、signed char、unsigned char 或 std::byte。

则称 P\* 类型的指针是 T\* 指针的合法别名类型，编译器将假设它们可能指向同一内存，不做激进优化。
不只函数参数，函数内使用的任何指针都遵循该规则进行优化。

> 这个要求很严，基本就是要 P, T 忽略 cv 后类型相同，或者有一个是 char 那些。
> C 与 C++ 的规则不同，C 中的严格别名还允许以下两点：P 是聚合体或 union，并且包含一个非静态成员，它具有上述类型之一；P 是 T 的基类。
>
> 注意，不只是 P 与 T 的关系，如果使用了 P 的某个 V 类型成员，而 V 与 T 相似，那么读写 V 后再读写 T 也会重新访存。
>
> (u)int8_t 可能是 (un)signed char 的别名，所以这两个也可能可以。

```cpp
int x;
// char* 与 int* 兼容，符合严格别名规则，编译器将认为 p1，p2 可能会指向同一内存区域，不做优化
void foo(char *p1, int *p2); 
foo((char*)(&x), &x);

// float* 与 int* 不兼容，不符合严格别名规则，编译器将认为 p1，p2 绝不指向同一内存区域，以此优化
void foo(int *p1, float *p2);
foo(&x, (float*)(&x));

// 产生错误结果的例子
// 编译器认为 i 绝不是 f 的别名，因此直接将返回值优化为 return 1，不关心 f
int foo(int *i, float *f) { 
	*i = 1;               
	*f = 0.f;            
	return *i;
}
int x = 0;
cout << foo(&x, (float*)(&x)); // 输出1
```

因此，**如果 T, P 不兼容，将 T\* 类型的指针强转为 P\* 类型的指针使用，可能导致 UB**。比如`int32_t*`与`int64_t*`。
编译器将假设程序员遵守严格别名规则，只将指针转为与其类型兼容的指针，并以此优化。
(unsigned) char 与 byte 是例外，即任何类型可以安全地转为 char，再从 char 转回**原类型**。（如果 uint8 是 unsigned char 的宏定义，那么自然也 ok）
通过 char 做中转，转为不兼容类型是不行的，因为其动态类型并不是 char，还是原类型。

有时候，编译器遵守严格别名也可能过于保守。如果两个指针类型兼容，但它们不可能指向同一地址，那么可以告诉编译器允许其优化，见下面的 *restrict*。

注意，成员函数中 this 将作为指针参数传递，如果函数用到 char（或相似类型）指针 p，则它们是兼容的，所以编译器会假设 p 与 this 可能指向同一地址，即其修改可能互相影响。如果 p 又是类的成员（即访问需要`this->p`），那么每次修改 p 再使用 p，都需要重新获取 p 的地址，导致无意义的访存（因为编译器认为修改 p 可能修改 this，从而导致 p 变化）。
解决方式可以用 restrict，或者将 p 的地址保存到临时变量，避免每次访问`this->p`。
代码见 https://godbolt.org/z/sGrsjYP8M。
相似的例子：

```cpp
struct S { int a, b; };
 
// int* 和 struct S* 可以别名使用，因为 S 拥有 int 类型的成员
void f2(int *pi, S *ps, S s)
{
    // 每次通过 *ps 写入后，必须重新进行 *pi 的读取
    for (int i = 0; i < *pi; i++)
        *ps++ = s;
}
```

**restrict**

[restrict](https://zh.cppreference.com/w/c/language/restrict)是 C 中的关键字，修饰指针或引用（类似 cv，要放在右侧才是修饰指针），表明该指针不会发生 pointer aliasing（保证该指针不会和其它某个指针指向同一块内存地址）。
当函数内可能存在 aliasing 时，只要对某个指针指向的区域进行修改，后续访问其它指针也必须进行访存。但如果指针之间不会指向同一区域，那么一个指针的修改不会导致某个指针需要重新进行访存。

例：
add1 中因为可能存在 aliasing，因此不能假设 a、b 指向不同区域，因此修改 b 后需要再对 a 进行访存确定其值：当 a、b 指向不同时，结果为 3；指向相同时，结果为 4。
add2 中明确 a、b 指向不同，因此可使用寄存器中的值计算、甚至直接确定返回值为 3，不需要多余访存。

```cpp
int add1(int* a, int* b)
{
    *a = 1;
    *b = 2;
    return *a + *b;
}
int add2(int* __restrict a, int* __restrict b)
{
    *a = 1;
    *b = 2;
    return *a + *b;
}
```

restrict 能允许编译器做更多优化，在使用指针进行运算的函数内应该声明。但注意如果 a、b 指向相同却被声明 restrict，则为 UB。
C++ 标准中没有 restrict，但很多编译器实现了类似功能，如：gcc、clang 的 [__restrict](https://gcc.gnu.org/onlinedocs/gcc/Restricted-Pointers.html)（放在成员函数后可以修饰 this）。

**名字查找** / **如何决定要使用哪个同名函数/同名变量**

为了编译函数调用，编译器必须先进行[名字查找](https://zh.cppreference.com/w/cpp/language/lookup)，对于函数可能涉及实参依赖查找，而对于函数模板可能后随模板实参推导。

**有限定的名字查找**

> https://zh.cppreference.com/w/cpp/language/qualified_lookup

*有限定的标识符*就是在标识表达式前面加上作用域解析运算符`::`，前面加一个命名空间/类/枚举的名字（或表示类/枚举的 decltype 表达式，或者不加代表全局作用域）。

**无限定的名字查找**

> https://zh.cppreference.com/w/cpp/language/unqualified_lookup

未出现在作用域解析运算符 :: 右边的名字是无限定名字，对该名字的查找会检查各个作用域，只要找到任何种类的至少一个声明就停止查找，不再检查别的作用域。

查找函数调用运算符左边的名字时，分为两阶段：

1. 进行常规的无限定名字查找，如果找到同名的以下任何内容，就不进行第二步：
    1. 类成员声明。
    2. 块作用域的函数声明（不考虑 using 声明的）。
    3. 任何非函数和非函数模板的声明（比如同名的函数对象或变量，如果选择到变量则会 CE）。
2. 如果 1. 未找到任何名字，则先进行 *ADL*：对于每个函数调用表达式中的实参，根据它的类型将对应的作用域添加到待查找的关联空间集合。忽略该集合中在类中找到的声明（除了命名空间作用域的友元函数和函数模板）。
    将常规无限定查找所找到的声明集合 与 上述关联空间集合合并，并且：
    1. 忽略关联命名空间中 using 引入的命名空间。
    2. 在关联类中的命名空间作用域声明的友元函数和函数模板通过 ADL 可见。
    3. 忽略除函数和函数模板外的所有名字（不会再考虑函数对象、变量等）。

**实参依赖查找 / ADL**

[实参依赖查找](https://zh.cppreference.com/w/cpp/language/adl) (argument-dependent lookup) 是对无限定函数名进行查找的规则。除了在通常无限定名字查找所考虑的作用域和命名空间外，还会在它的各个实参的命名空间中查找这些函数的定义，使得使用在不同命名空间定义的运算符成为可能。
简单来说，ADL 指：对于无限定函数的调用，C++ 不仅会在当前命名空间查找其定义，还会在它的实参类型所在的命名空间查找其定义（如果之前没找到）。

可以找到隐藏的友元声明（*hidden friend*）。

正因为 ADL，才会有如下写法：
如果 swap 在 obj 所在空间定义，则使用用户定义的 swap；否则使用 std::swap。

```cpp
using std::swap;
swap(obj1, obj2);
```

**重载决议**

> https://zh.cppreference.com/w/cpp/language/overload_resolution

简单来讲就是三步：

1. 建立候选函数集合。
2. 从该集合去除不可行函数，只保留可行函数。
3. 分析可行函数集合，确定唯一的最佳可行函数。若有多个则有歧义。

存在函数模板时，重载决议的过程大致如下：

1. 对所有函数模板进行模板实参推导、检查显式指定的模板实参，以确定最终可用的模板实参。
2. 如果实参推导和检查都成功，通过该实参生成特化，加入到候选函数 (candidate functions) 集合。
    如果推导失败或生成的特化非良构，则不会将其加入到候选集，也不会导致编译失败（即 SFINAE）。
3. 将所有同名的非模板函数添加到候选集。
4. 检验实参与形参是否合法，将候选集缩减为可行函数 (viable functions) 的集合。
5. 分析可行函数集合，确定唯一的最佳可行函数。
    注意只有非模板和主模板重载参与重载决议。特化并不是重载，因此不考虑。只有在重载决议选择最佳匹配的主函数模板后，才检查它的特化以确定最佳匹配。

本题中，先对模板 f 进行模板实参推导，得到 T 是 int& 且合法，所以它是候选函数（与 Quiz 里的解释不同，这一步中并不包含对显式特化的推导和决策，因为它不是重载）。
因为不存在其它函数，所以 f 就是最佳匹配的模板。

> 在涉及模板时，第一步会进行相应类型的模板实例化、建立候选函数（**模板能生成最佳的候选类型**；但除非是万能引用，否则不会自动添加 &；也不会添加 cv）；第二步淘汰不符合 requires 和无法匹配的实例化（比如 SFINAE。它也可能在第一步）。
> 因此，当没有完全与参数类型匹配的非模板函数、且模板函数是万能引用时，模板函数将总是被优先选择，不会考虑隐式转换然后调用普通函数（除非有 SFINAE、requires 等限制）。
> 因此，如果有模板函数`f(T&& x)`与`f(const A&)`，A、A&、A&& 都将匹配前者。这个问题常在模板构造函数中出现。
>
> 函数模板部分见 *模板 - 函数特化的匹配规则*。

简单来说，标准转换的优先级从高到低分为三级：

1. 准确匹配 (Exact Match)：不需要转换的、左值到右值转换、限定性转换（加 cv）、数组/函数到指针的转换等。
2. 提升 (Promotion)：整数提升、浮点提升（见 *隐式转换*）。
3. 转换 (Conversion)：（可能有精度丢失）整数转换、浮点转换、浮点到整型转换、布尔转换（如果类型能转为 bool）、指针转换（任意指针到 void*，空指针到0，子类指针到基类指针，还有0到空指针？）、成员指针转换、派生类到它的基类的用户定义转换。

标准转换序列 由于 需要用户定义的隐式转换的序列 优于 省略号转换序列。
如果两个可选的重载有相同的优先级，则有歧义，会 CE。

> char 到 int 的转换属于整数提升，而 char 到 short/long 的转换属于整数转换。
> 因此对于字符字面量实参，`f(short)`与`f(int)`将匹配后者，而`f(short)`与`f(long)`将产生歧义。

比如：

```cpp
void f(std::string);
void f(bool);
// 调用 f(bool)，因为到 bool 的转换优先于用户定义的到 string 的转换
f("abc");

// 使用模板可以生成最佳匹配，从而保证匹配
// 可以使用简写函数模板，然后用 concept 限制类型
void f(std::convertible_to<std::string> auto &&);
void f(bool);
// 调用 void f(auto:16&&) [with auto:16 = const char (&)[4]]
f("abc");
```

注意，模板能生成最佳匹配的函数（除了引用和 cv 需要注意）。

> C 的重载可通过 [_Generic](https://zh.cppreference.com/w/c/language/generic)（泛型选择）实现：定义接收不同参数的不同名函数（比如 max_int、max_double），然后定义宏（比如 max），利用 _Generic 根据参数类型决定调用哪个函数。

**重载决议** - **确定可行函数**

候选函数包含了所有可能的函数，但不会先进行匹配检验。

为了被包含在可行函数集中，候选函数必须满足下列条件：

1) 如果有 M 个实参，那么刚好具有 M 个形参的候选函数可行。
2) 如果有 M 个实参且候选函数的形参少于 M 个，但具有一个省略号形参，那么它可行。
3) 如果有 M 个实参且候选函数的形参多于 M 个，但是第 M+1 个形参和所有后随形参都具有默认实参，那么它可行。对于剩余的重载决议，形参列表被截断到 M。
4) 如果函数拥有关联的约束，那么必须满足它。
(C++20 起)
5) 对于每个实参，必须至少存在一个隐式转换序列将它转换到对应的形参。
6) 如果任何形参具有引用类型，那么这一步负责引用绑定：如果右值实参对应非 const 左值引用形参，或左值实参对应右值引用形参，那么函数不可行。

**重载决议** - **确定最佳函数**

重载决议分为三步：建立候选函数集合；从该集合去除函数，只保留可行函数；分析可行函数集合，以确定唯一的最佳可行函数。
题目中`f(const string&)`与`f(const void*)`都是可行函数，所以需要按照[以下规则](https://timsong-cpp.github.io/cppwp/n4861/over.match#best)决定谁更好。

定义 ICSi(F) 为：将第 i 个实参类型转换到函数 F 的第 i 个形参类型所需进行的隐式转换序列。
每个实参到形参的隐式转换序列是影响函数优先级的主要条件（但如果 F 是静态成员函数，那么 ICS1(F) 不会参与优先级的比较。换句话说对于任意函数 G，ICS1(F) 不比 ICS1(G) 更差，也不比它更优，不会影响比较）。

对于每对可行函数 F1 和 F2，当且仅当满足以下条件时称 F1 是比 F2 更好的函数：对于所有实参 i，ICSi(F1) 均不劣于 ICSi(F2)，并且满足以下条件之一：

- 存在某个实参 j，ICSj(F1) 优于 ICSj(F2)。（这题只涉及这一点）
- 当前语境是在通过用户定义转换进行初始化，并且将 F1 的返回类型转换到目标类型（即被初始化目标的类型）所需的标准转换序列，优于将 F2 的返回类型转换到目标类型所需的标准转换序列。
- 当前语境是在通过转换函数，对函数类型的引用进行直接引用绑定初始化，并且 F1 的返回类型与被初始化的引用的类型相同（都是左值引用或右值引用），而 F2 不是。
- F1 不是函数模板特化，而 F2 是。
- F1, F2 都是函数模板特化，并且根据[*模板特化的偏序规则*](https://zh.cppreference.com/w/cpp/language/function_template)，F1 更特殊。
    （简单来说，如果函数模板 A 能接收的类型比函数模板 B 更少，那 A 比 B 更特殊，见下或 *250. 251.*）
- ...

编译器会对所有可行函数进行逐对比较。如果恰好有一个可行函数优于所有其它函数，那么重载决议成功并调用该函数。否则编译失败。

[隐式转换序列](https://zh.cppreference.com/w/cpp/language/implicit_conversion)有三种：

- 标准转换序列：0或1个标准转换序列。
- 用户定义转换序列：0或1个标准转换序列、1个用户定义转换、0或1个标准转换序列。
- 省略号转换序列：实参匹配到了省略号形参（此时实参会进行称为[默认实参提升](https://zh.cppreference.com/w/cpp/language/variadic_arguments)的转换）。

> 一个标准转换序列由4部分组成：0或1个值变换（包括：左值到右值转换、数组到指针转换、函数到指针转换）、0或1个数值提升或数值转换（包括：整数提升、浮点提升、整数转换、浮点转换、浮点整数转换、指针转换、成员指针转换、bool 转换）、0或1个函数指针转换、0或1个限定转换。它们称为[标准转换](https://timsong-cpp.github.io/cppwp/n4861/conv#1)。
> 用户定义转换指调用一次非 explicit 单实参构造函数或非 explicit 转换函数。
>
> [标准转换的优先级](https://timsong-cpp.github.io/cppwp/n4861/over.match#over.ics.scs)从高到低分为三级：准确匹配、提升、转换。一个标准转换序列的优先级是它包含的标准转换中的最差等级。

**隐式转换序列的优先级为**：标准转换序列 > 用户定义转换序列 > 省略号转换序列。
如果两个 ICS 的类型相同，则按照[这里的规则](https://timsong-cpp.github.io/cppwp/n4861/over.match#over.ics.rank-3)继续进行区分。

**重载决议** - **模板特化的偏序规则**

[模板特化的偏序规则](https://timsong-cpp.github.io/cppwp/n4861/temp.func.order)：为确定任意两个函数模板中哪个更特殊，偏序处理首先对两个模板之一进行以下变换：对于每个类型、非类型及模板形参，包括形参包，生成一个唯一的虚构类型、值或模板，并将其替换到模板的函数类型中。（此处不是所有的类型都进行该处理，取决于当前语境 (#5)。当语境是函数调用时，只会考虑显式写出的实参对应了的那些形参类型，不会考虑其它有默认实参的形参、形参包、省略号形参）

在按上方描述变换两个模板之一后，以变换后的模板为实参模板，以另一模板的原模板类型为形参模板，执行模板实参推导。然后以第二个模板（进行变换后）为实参，以第一个模板的原始形式为形参重复这一过程。

推导开始前，以下列方式对形参模板的每个形参 P 和实参模板的对应实参 A 进行调整：...（差不多就是忽略 P, A 的引用与 cv）。在这些调整后，遵循[从类型进行模板实参推导规则](https://timsong-cpp.github.io/cppwp/n4861/temp.deduct.type)，从 A 推导 P。
如果变换后的模板 1 的实参 A 可以用来推导模板 2 的对应形参 P，但反之不可，那么对于从这一对 P/A 所推导的类型而言，这个 A 比 P 更特殊。在考虑每个 P 与 A 后，如果对于所考虑的每个类型，

- 对所有类型，模板 1 至少与模板 2 一样特殊。
- 存在某些类型，模板 1 比模板 2 特殊。
- 对所有类型，模板 2 都不比模板 1 更特殊，或者更不特殊。

那么模板 1 比模板 2 更特殊。

**创建对象的过程**

创建对象有两种：
静态，如`A a`，直接移动栈指针，然后在这片栈空间调用构造函数。
动态，如`A *ptr = new A`，会在堆上为a分配空间，然后在栈上创建一个指针，指向堆。

**new operator 与 operator new**

> `new T`会优先使用类重载的 operator new，再尝试全局的 operator new。
> `::new T`将始终使用全局的 operator new。
> `::operator new(size)`与普通函数调用类似，会调用全局 operator new 返回一个 void*。

[new operator](https://zh.cppreference.com/w/cpp/language/new) 是内置的 **new 表达式**，不可被重载（因为就不是函数）。对于`A *a = new A;`，包含两步：调用分配函数`operator new(sizeof(A))`分配内存并传递要分配的字节数（如果是数组则调用`operator new[]`），调用 A 的构造函数初始化，最后返回指针。
[operator new](https://zh.cppreference.com/w/cpp/memory/new/operator_new) 是可重载的分配函数，称为 new 运算符（这和使用 + 运算符会调用`operator +`一样），用户可以在全局重载来替换 new 的实现，也可以为类重载 operator new（会在 new 该类时调用，会被子类继承）。它有三种常用的重载，第三种是 placement new：

```cpp
// 通过 A* a = new A; 调用
// 通过捕获 bad_alloc 异常，检查是否分配成功
void* operator new (size_t size);

// 不会抛出异常，通过 A* a = new(std::nothrow) A; 调用
// 通过判断返回值是否为 nullptr，检查是否分配成功
void* operator new (size_t size, const nothrow_t& tag);

// 通过 new (p) A; 调用，p 是一个指针
void* operator new (std::size_t size, void* ptr) throw();

// [] 版本类似，用于数组
void* operator new[](size_t);
void* operator new[](size_t, const nothrow_t&);
void* operator new (size_t, void*);

// 可以重载其它参数或类型（但第一个参数必须是size_t）
// placement new 的一个重载。如下函数会调用 new (T) A();
// 但注意要定义相应的 delete
void* operator new (size_t size, const T& ptr);
```

普通 new 分配失败时会抛出异常，所以要检测错误，最好是用`new (std::nothrow) A`然后再判指针是否为空。
但通常不会在意这个失败。

operator new 是否调用 malloc、operator delete 是否调用 free 是未指明的。

一个简单的实现：

```cpp
extern void* operator new(size_t size)
{ 
　　// if(size == 0) ... // 处理 new T[0] 这样的语句
　　void* last_alloc;
　　while(!(last_alloc = malloc(size)))
　　{
　　   if(_new_handler)
　　       (*_new_handler)(); //调用handler函数
　    else
　　       return 0;
　　}
　　return last_alloc;
} 
extern void operator delete(void* ptr)
{
　　if(ptr) // delete 空指针是安全的
		free(ptr);
}
```

注意析构函数不应抛出异常，见 *面向对象 - 析构函数抛出异常*。

如果只想处理未被初始化的内存，可直接调用operator new 获取内存和 operator delete 释放内存，如`void *p = operator new(sizeof(A)); operator delete(p);`。

**placement new**

格式：`A *p = new (ptr)type`或`A *p = new (ptr)type(initializer-list)`。

placement new（就地构造）不分配内存，而是直接调用构造函数在 ptr 所指的位置构造一个对象，并返回 ptr。 
placement new 既可以在栈上生成对象，也可以在堆上，取决于参数 ptr。
例：`void *ptr = malloc(sizeof(A)); A *p = new (ptr)A;`或直接`A *ptr = (A*)malloc(sizeof(A)); new (ptr)A;`（调用 A 的构造函数）。

在 placement new 调用构造函数时，如果构造函数抛出异常，将会执行相应的 placement delete 来回收空间，避免内存泄露（返回值将不是一个合法的指针，所以在外部无法回收）。所以如果定义了某种形式的 placement new，就要定义相应的 placement delete。

一般与内存池配合使用，用来调用构造函数初始化。

**new 与 new() （操作符）**

在堆上创建对象分为两步：

1. 执行`void* operator new(size)`函数，在堆空间中搜索合适的内存并进行分配（对于数组是`operator new[]`。用户也可以调用该函数）。
2. 调用构造函数构造对象，初始化这片内存空间。

> 下面的方法不准确但也对。`T x`、`new A`是*默认初始化*，对于类对象将调用默认构造，对于数组对象则依次进行默认初始化，否则不进行初始化。`T x{}`、`new A{}`是*值初始化*，带有初始化器（括号）。

对于类和结构体来说：

- 如果类没有实现默认构造，则`new A`对于类对象，调用其默认构造（实际效果是除了调用每个成员的默认构造函数外，不会做任何初始化），不会额外的初始化或置 0；`new A()`会调用默认构造并进行初始化清 0。
- 如果类实现了默认构造，则`new A`与`new A()`相同，都执行定义的默认构造，不会做额外的初始化。
- 如果类禁用或删除了默认构造（如定义了有参构造），则`new A`和`new A()`都会编译失败。因为`new A(x, y)`实际就是调用构造函数`A(x, y)`。

基本类型也是这样，但基本类型没有定义默认构造、使用默认构造（实际是什么也不干，不会置 0），所以`new int`仅仅分配内存，后面加`()`（`new int()`）才会进行赋 0 值的初始化。
如：`int *ptr = new int[5]`后对应空间内为随机值，但`int *ptr = new int[5]()`后对应空间为0。

但是编译器有可能会主动初始化为 0，高优化等级可能会使初始化不发生。

**delete 与 delete[]**

> 注：delete 空指针是安全的（不会做任何事）。
> delete 后可以把指针置空，避免指针被释放多次。但这不是必须的，有时这完全无意义（比如析构函数内），有时会隐藏原本的问题：出问题说明程序逻辑上可能有问题，你不能控制资源的释放时机。最好肯定是确保指针恰好只被释放一次、释放后就不再使用。
>
> new[] 和 new 的区别是要不要额外记录对象数量，便于调用析构函数。但对底层的 allocator 来说，只要满足 alloc 传入 size 就可，free 不用传入 size，只需要一个指针。

delete 释放由 new 创建的单个对象，delete[] 释放由 new[] 创建的数组对象。两者不可混用，否则会导致 UB/RE。
但对于没有定义析构函数的类型（如内置类型、未定义析构函数的结构体），两者没有区别，可混用。原因如下。

delete 包含两步：调用指针所指向的对象的析构函数；调用`operator delete()`（默认实现为 free()）回收指针所指向的内存。
delete[] 也包含两步：**调用指针所指向的数组中的每个对象的析构函数**；调用 free() 回收指针所指向的整个数组的内存。

在进行分配内存时，系统会记录分配内存的大小，**如果没有析构函数，就不需要知道每个元素的具体大小、每个元素的位置来逐个调用析构，直接释放这块内存就可以了**。
但**对于有析构函数的类型的数组**，要知道每个元素的大小或位置。编译器会在这种类型的数组首地址前，再申请一块空间，记录分配的元素数量，内存块大小/数量就可以得到元素大小。

```cpp
class TestA
{
public:
    int x;
    TestA() { }
    virtual ~TestA() { cout << "~A" << endl; }
};

int main() {
    int* arr = new int[10];
    cout << *((long long*)arr - 1) << endl; // 输出随机数
    delete[] arr;

    TestA* a = new TestA[10];
    cout << *((long long*)a - 1) << endl; // 输出10。32位是占4B，64位是8B？
    delete[] a; // 输出 10 个 ~A
}
```

所以对于有析构函数的类型的数组，delete[] 会从数组首地址前的个数开始回收：对于`TestA* a = new TestA[10];`，`free((long long*)a-1)`是可以运行的，`free(a)`会出错。

综上，delete 和 delete[] 的处理逻辑是不同的，进行析构的对象不同，执行 free 的方式也不同，可能判断数组元素个数。

> 注意，类似栈变量的释放顺序，delete[] 一个数组时也是从后往前销毁元素的，与 new T[] 时的顺序相反。
> 这很符合逻辑，构造时后面的对象可能会依赖前面的，从后往前释放不会出问题。

**内存分配失败**

> https://zhuanlan.zhihu.com/p/617088259

对于常见的64位系统，应用可分配的内存上限是$2^{48}$B（256TB）而非$2^{64}$B。
但不同系统的处理不同：Windows 上应用分配的内存上限可能是物理内存的 4 倍（通过交换机制扩充内存）。
Linux 上，如果程序不使用内存，则可分配虚拟内存的上限（256TB 或接近）；如果使用内存，则只能是物理内存的一定比例。
因此只有在 Windows 或关闭超额分配内存的 Linux 上，分配明显不合理数量的内存时，应用才会发生内存分配失败；在普通的 Linux 上，应用通常不会发生内存分配失败的错误。
因此检查这一错误的收益可能很低。

使用 new 分配失败时有两种情况：抛出 bad_alloc 异常；使用 new (nothrow) 不抛出异常，但要检查返回值。由于标准库使用的就是前者，因此除非完全不使用标准库，使用后者 new (nothrow)、不使用异常，是毫无意义的。
因此对于内存分配失败问题，方案从（通常情况下）好到坏依次为：

1. 检测 bad_alloc 异常，并进行处理。
    但异常发生时会终止函数，需要管理好栈对象的生命期（比如通过 RAII）。
2. 内存不足是一种系统设计问题，通常很难在代码里进行局部化的处理。如果发生几率很低，但预防代价很高，不如不进行预防，考虑服务崩溃后的日志输出、恢复和重启。
3. 使用 new (nothrow)，不使用标准库，不检测异常。
    但这样需要到处检查，会很麻烦，但没有异常的开销、也安全。

**栈对象能否用 delete 释放**

注意栈对象/临时作用域对象不能用 delete 释放！退出作用域后它会自行释放，手动调用 delete 将会释放两次导致出错。
换句话说，**delete 的目标必须是用 new 分配的**，不包括 全局的/new[] 的/原地 new 的。

```cpp
class A{
  public:
  void test(){
	delete this;
  }
};
// RE，栈对象不能delete
A a; a.test();
// 会调用delete的方法类似，如shared_ptr
std::shared_ptr<A> p(&a);
p.reset(); // RE
// OK，但之后p就是无效的
A *p = new A();
p->test();
```

**new 与 malloc 的区别**

- new 与 delete、malloc 与 free 必须严格配套，不能交叉使用。前者更加可靠，后者是 C 提供的内存管理方式。
- new 在申请空间后会调用构造函数，但 malloc 不会，且不会初始化（calloc 会初始化为 0）。（new 的申请部分就是调用 malloc）
- new 申请内存不需要指定内存块大小，编译器会自己计算；但 malloc 需要指定大小。
- new 在申请成功后，返回对应类型的指针；但 malloc 会返回 void\*，需要自己强制转换，也不是很安全。
- new 在申请失败后，会抛出 bad\_alloc 异常；malloc 则是返回 NULL。
- new 其实是一个操作符 operator，用户也可以重载 new/delete 操作符。
- delete 与 free 的区别：delete 会先调用对象的析构函数，但 free 不会。（delete 的释放内存部分也是调用 free）

**malloc**

> https://blog.csdn.net/songchuwang1868/article/details/89951543
> https://zhuanlan.zhihu.com/p/462819375
>
> glibc 的 malloc/free 实现与内存管理：https://zhuanlan.zhihu.com/p/428216764
> https://zhuanlan.zhihu.com/p/452686042

TODO

[malloc](https://zh.cppreference.com/w/cpp/memory/c/malloc) 多次分配小内存时，使用 sbrk。
但如果申请空间大，会使用 mmap，是惰性的，即如果不使用申请的内存，不需要发生实际的内存分配（top 查看不到新的内存占用）。
calloc 是分配并初始化，因此会发生内存分配。

**realloc**

realloc 可以在已经申请好内存块的基础上，重新分配指定大小的内存。
`void* realloc (void* ptr, size_t size);`，ptr 为已经申请过的地址（若未申请则填 NULL）。

如果之前没有申请内存，则直接分配，与 malloc 一致；
如果之前已申请过内存，则有两种情况：

1. 新分配的内存块比原来更大：则可能在原内存块后继续分配，也可能分配一个新的内存块，将数据拷贝过去，然后用 free 释放原内存块。
2. 新分配的内存块比原来更小：直接在原内存块的基础上缩小。

不管怎样，调用 realloc 后都不应该使用传入的那个指针。

注意，malloc、realloc 只会进行分配，不会进行初始化，更别提调用构造函数。
所以如果对 new 出来的空间使用 realloc，新的空间是不会被初始化的，旧的空间也不会调用析构函数。所以 new 不应该与 free 或 alloc 函数混用。

**dangling pointer, wild pointer**

悬空指针是指向已删除对象的指针。realloc 如果发生 free，则传入的指针可以看做悬空指针（反正访问是 UB）。
野指针是没初始化的指针。

**栈和堆的区别？为什么栈比堆高效？**

栈是从上往下增长的，用来处理函数调用，不能动态地使用，生命周期被限制在函数内。在某些系统，比如 windows，栈空间可能会有限制。
堆可以动态分配内存，调整已分配的大小。

栈空间的分配快：只需要移动栈指针，不需要分配器参与；也不会产生内存碎片，不需要 gc 或手动回收，用起来方便；连续性也好。
但单论读写效率是没有区别的，都是主存。

**怎么让对象只在栈上分配**

> **事实上这是完全做不到且无意义的**。
> 对于下面的方法，只要通过有限定名字查找`::`指定使用全局的`operator new`，而不是优先使用类内部定义的，就可以实现堆上分配：
>
> ```cpp
> struct X{
>     int n{};
>     X(int v):n{v} {puts("X(int)");}
>     ~X() { puts("~X()"); }
> private:
>     void* operator new(size_t) noexcept {return nullptr;}
>     void operator delete(void*) {}
> };
> X* p = ::new X(1);
> std::cout<< p->n <<'\n';
> ::delete p;
> ```
>
> 实际上只要类本身有一个构造函数，就可以在堆上分配内存，然后用 placement new 初始化它：
>
> ```cpp
> char *pc = new char[sizeof(X)]();
> X *px = ::new ((void*)pc) X(2);
> std::cout<< px->n <<'\n';
> ::delete px;
> ```
>
> 想要阻止它，只能禁用或私有所有构造函数。但如果这样做，只能通过一个友元工厂函数来生产对象，而且生产出来的对象只需要通过拷贝/移动构造就可以 placement new 到堆上。除非禁用拷贝/移动构造，但这样工厂类也没法返回对象了。
>
> 而且也阻止不了静态或线程局部存储期的对象分配到栈外。

> 理论上有些价值，但由于做不到，应该由人自己遵守。
> 如果条件允许，也就是对象不会发生内存逃逸，它的生命周期被限制在某个函数内，就可以分配到这个函数栈上，而不是堆上，以提高效率。
> 内存逃逸有两种，一是方法逃逸，即对象会在方法外部被使用时，就需要分配到堆上（比如变量的地址被作为指针返回，或被外部的变量保存）；二是线程逃逸，是在一个线程中构造的对象，在另一个线程中也会被使用而产生的。
> 通过避免方法逃逸，可以将对象分配到栈上，提高效率；避免线程逃逸，能允许编译器做更好的优化。
> go 和 java 的编译器会进行逃逸分析，使变量尽可能分配到栈上。而 C++ 需要程序员自己决定？

在栈上建立对象，是直接调用类的构造函数；而在堆上建立对象，是执行它的 operator new() 函数，分配空间后，间接调用类的构造函数。

所以，只有使用 operator new，对象才会建立在堆上，只要禁用 operator new 就可以避免它分配在堆上。
可以重载`void *operator new(size_t t) = delete;`，也可以重载该函数为 private。
delete 也要做相同的重载。
（当然前提是不使用 alloc 系列的函数）

**怎么让对象只在堆上分配**

函数返回时，需要调用对象的析构函数。所以如果一个类的析构函数是私有的，它就无法分配到栈上，因为程序没法释放它。
所以将析构函数定义为 private 或 protected，能避免它分配到栈上。
（编译器分配栈空间时, 会检查类的析构函数的可访问性，如果析构函数是私有的，将会编译失败，编程器不能在栈空间上创建该对象）

但是，如果析构函数是私有的，delete p 也会编译失败，我们需要定义一个 public 的销毁方法替换 delete，在里面调用`delete this;`。
（此时 new 与 delete 将不再配对，而是与自定义的 destroy 配对。为此可以再封装一个 create 函数，让它与 destroy 配对，不直接使用 new）

**C++ 的内存管理**

可以通过 C 语言中的内存管理方式，即 malloc, calloc, realloc, free 这些函数；也可通过 C++ 提供的新方式：通过 new 和 delete 操作符、RAII 进行动态内存管理。

**C++ 的内存布局**

（C++ 标准没有规定程序的内存布局，只规定了存储期，下面实际说的是特定 os 上的程序内存布局）

就是 Linux 上的进程格式。
Linux 将虚拟内存组织成一些段（或区域）的集合。一个段就是已分配的虚拟内存的连续片。

Linux 为每个进程维护了一个单独的虚拟地址空间。虚拟内存的地址最底端向上依次是：代码段 .text、已初始化数据段 .data、未初始化数据段 .bss、堆。地址最顶端向下是栈空间。
全局变量和静态变量位于数据段（.data 和 .bss。C++ 不区分数据的初始化和未初始化）。
malloc 等分配的内存块位于堆。

**enum**

[枚举](https://zh.cppreference.com/w/cpp/language/enum)常量代表该枚举类型的变量可能取的值。枚举常量只能以标识符形式表示。

默认情况下，编译器使用 int/uint 作为底层类型，每个枚举值都与一个底层类型的值关联。
如果不为其指定常量值，则默认首个为0，其它的是前一枚举项的值 +1。各枚举常量的值可以重复。
例：

```cpp
enum ColorSet { // 枚举类型名 ColorSet 可省略，直接定义变量
    R, G, B, // 0 1 2
    W=10, B, // 10 11
    GREY=0, YELLOW, // 0 1
    PINK=R+10, // 10
} color1, color2; // 类型名为ColorSet，同时定义两个变量
```

注意，定义的`color1, color2`未初始化，必须指定一个值，否则如果是全局变量则为0，局部则随机，不管它能取哪些值。
初始化变量时，需要赋`ColorSet`类型（如=RED, =BLUE），不能直接赋底层类型如 int。

可以为 enum 指定底层类型以减少内存占用：`enum E: uint8_t {...};`。类型需要能表示所有枚举项。
使用 *属性说明符 - packed* 修饰 enum（或编译选项`-fshort-enums`），可使用最小、最合适的类型做底层类型（1字节能存 256 个）。

**指针与引用**

- 当作为参数传递时，指针和引用传递的都是地址，不过指针实际上仍是值传递。
  注意**非引用传递**都是拷贝值！会创建一个新的临时变量，对这个变量取地址修改，也不会影响函数外的变量。
  这包括指针，所以更改指针也要对它`&`（得到`**p`），不然只能更改指向的值。
- 引用必须初始化，指针可以不初始化；引用初始化以后不能被改变，而指针可以改变指向。
- 不存在指向空值的引用，但是存在指向空值的指针。
- 一个引用可以看作是某个变量的一个“别名”。

> **引用是否占内存？引用是否就是指针？**
> 标准没有规定引用的实现，因此答案不确定。
> 但通常来说，编译器会将引用转为指向对象的 const 指针，因此占 8B，类中的引用成员就是如此。
> 对于非成员引用，编译器可能会将其优化成指向对象的地址（不需要保存指针），甚至是常量（如果指向的对象没被修改）。

**top-level const**

在一个指针类型中可以遇到多个 const。
如果一个 const 修饰的是对象本身，则称为 top-level const (顶层 const)；否则为 low-level const (底层 const)。
指针声明`const int* const p`中，左边的 const 为 low-level，不影响 p 本身；右边的 const 才是影响 p 的 top-level，说明 p 是常量。
函数声明`const int func() const`中同理，右边的是 top-level。

函数参数的 top-level const 不会影响函数类型的确定，见 *函数 - 函数类型*。
变量的 cv 限定就是顶层的 cv 修饰符。
注意 remove_const 去除的也是 top-level 的。

const_cast 可以任意添加和去除指针声明中的 const？不管是 top 还是 low-level const。
但有和无 top const 的指针本来就可互相赋值，只有添加/去除 low const 时需要 cast。

> 引用相当于自带顶层 const（不能更改其指向。但引用不能用 cv 修饰），它的底层 const 与指针类似：const int& 的 const 修饰 int，且在 remove_const 时需要先 remove_ref，因为它是 low-level const。
>
> 引用不能用 cv 修饰。
> 注意，**在模板推导中可能出现对引用添加 cv 的情况，这种情况下类型会被修改且忽略 cv**：设 TR 为指向 T 的引用类型，如果尝试创建指向 cv TR& 的类型，则会生成 T&；如果尝试创建 cv TR&&，则会生成 TR（见[这里](https://eel.is/c++draft/dcl.ref#7)）。
> 比如：以下代码中，T 被显式指定为 int&，所以实参类型为 const (int&) & 实际为 int&，const 会修饰 int& 从而被忽略。
>
> ```cpp
> template <class T>
> void f(const T& t) {
> 	t = t + 1;
> }
> 
> int a = 1;
> f<int&>(a); // a 被修改
> ```

**指针转换**

> cv decomposition (cv分解)：https://timsong-cpp.github.io/cppwp/n4659/conv.qual

如果 cv2 的限定符比 cv1 更多，则“指向 cv1 T 的指针的纯右值”可以转换为“指向 cv2 T 的指针的纯右值”。否则不可。
（即可以额外加 cv，但不能去除）
由于`"abc"`是 const char 数组可被隐式转换为`const char*`，因此`char *s = "abc"`会CE，因为去掉了 const。

**引用初始化**

> https://zh.cppreference.com/w/cpp/language/reference_initialization
> https://timsong-cpp.github.io/cppwp/n4659/dcl.init.ref#4

设一个`cv1 T1`类型的引用，被一个`cv2 T2`类型的表达式初始化：

- 定义：
    T1 与 T2 引用相关 (reference-related)：iff T1 和 T2 是同一类型，或 T1 是 T2 的基类（如果 T1 是 T2 的不可达基类或有歧义，则程序非良构）。
    T1 与 T2 引用兼容 (reference-compatible)：iff
    - T1 与 T2 引用相关，或 T1 是一个函数，T2 是一个相同类型的 noexcept 函数；
    - 且 cv1 的限定符不少于 cv2（cv2 是 cv1 的子集）。

引用初始化规则：

- 如果初始化表达式是初始化列表，则遵循列表初始化。
- 如果引用是左值引用：
    - 且初始化表达式是非位域左值，且`cv1 T1`与`cv2 T2`是引用兼容的，则引用绑定到该左值标识的对象上（或它的基类子对象）。
        比如：`struct B: A {} b; A &ra = b;`可以绑定到 b 中的 A 类子对象）。
    - 且 T2 是类类型，且 T1 与 T2 并非引用相关，但初始化表达式可以转换为`cv3 T3`类型的左值（通过到相等或更少的 cv 限定的左值的转换函数），其中`cv1 T1`和`cv3 T3`是引用兼容的，则引用绑定到转换函数所返回的`cv3 T3`类型的左值对象上（或它的基类子对象）。
        比如：如果 T2 实现了`operator int&()`，那么`int& ir = T2()`是 ok 的，会绑定到 T2::operator int& 的结果。
- 否则，引用必须要么是一个指向非 volatile 的 const 类型的左值引用，要么是一个右值引用。
    - 如果初始化表达式是非位域右值或函数左值，且两者引用兼容，则绑定到表达式表示的泛左值对象上（或它的基类子对象）。
    - 如果 T2 是类类型，且 T1 与 T2 并非引用相关，但初始化表达式可以转换为`cv3 T3`类型的右值或函数左值，其中`cv1 T1`和`cv3 T3`是引用兼容的，则引用绑定到转换函数所返回的`cv3 T3`类型的泛左值对象上（或它的基类子对象）。
    - 以上两种情况中，如果初始化表达式是纯右值，则 C++17 起会先进行临时量实质化将其转换到亡值，将引用绑定到该亡值上。
    - 否则，如果 T1 或 T2 是类类型，且 T1 与 T2 并非引用相关，尝试通过转换函数按照对 T1 进行复制初始化的规则（就是尝试调用 T1 的非 explicit 构造和 T2 的非 explicit 用户定义转换函数？），生成 T1 类型的临时量，将引用绑定到该临时量上（即绑定到转换函数的结果上）。
    - 否则，将初始化表达式隐式转换为 T 类型的临时量，将引用绑定到转换后的临时量上。
    - 以上两种情况中，C++17 起生成的是纯右值，并会进行临时量实质化转换到亡值，将引用绑定到该亡值上。
- 此外，如果 T1 与 T2 引用相关（即 T2 是 T1 或从 T1 派生），那么 T2 必须拥有等于或少于 T1 的 cv 限定；并且如果引用是右值引用，那么初始化表达式不能是左值。

简单来说，**const T&、T&& 可以接受右值（并延长其生命周期），但 T& 不可**。
T 类型的引用只能绑定 T 类型对象，其它情况将尝试类型转换、绑定临时对象。

例：

```cpp
double &d = 1.0; // CE：初始化表达式是非类右值，所以引用类型要么是`const double&`，要么是`double&&`
int i = 1;
double &d = i; // CE：初始化表达式是左值，但不引用兼容，所以同上，引用要么是 const 左值引用要么是右值引用
const double &rd = i; // rd会绑定到一个临时double上，修改i不会影响rd
const string &rs = "abc"; // 同上，字符数组将隐式构造成string，然后引用绑定到该临时string上
```

**临时量的生存期**

临时量的生命周期是在整个表达式求值完才结束的。
此外，一旦临时对象或它的子对象被绑定到某个引用，临时对象的生存期就被延续，以匹配引用的生存期。
生存期不能被进一步传递以延长：通过临时量最初绑定的引用 创建的其它引用，不会延长其生存期（如果新引用生存期能比原来的引用长，本来也是错误的）。

临时对象包括：对象类型的纯右值表达式（C++17 前）/临时量实质化生成的亡值（C++17 起）等。其它见[文档](https://zh.cppreference.com/w/cpp/language/reference_initialization)。

**例外：**

- **函数 return 语句中绑定到返回值的临时量**不会被延续，它会在返回表达式的末尾立即销毁。因此这种 return 始终返回悬垂引用。
    如：`int& f(int a) {int b; return a或b;}`，a b 生命周期都在函数内，因此不能返回引用（会给警告）。

- **在函数调用中绑定到函数形参的临时量**不会被延续，存在到含这次函数调用的全表达式结尾为止。如果函数返回一个生命长于全表达式的引用，那么它会成为悬垂引用。

    如：`std::max`返回 const 引用，所以`const string& rs = max(string("1"), string("2"))`不对，`string("2")`的生命期是该语句（及函数内），而 max 返回的是对该临时量的引用，在该语句结束后就会销毁。所以之后使用 rs 就是 UB，即使部分编译器能执行。
    而非函数调用`auto&& rs = string("2")`是正确的，其生存期会被延续到与 rs 一致。

    临时量在整个表达式结束时才销毁，所以`Node& f(const Node &a) {return a;}`、`f( f( f(Node{})))`中，临时量会在最后一个 f 执行完后才销毁。
    
- 其它见文档。

第一种情况中，如果函数不返回引用，或返回右值引用并在 return 时 move 走对象，那没问题，因为返回值不是绑定到函数形参的临时量。（注意右值引用也是引用，也一样）
如果返回的引用是非局部的也没问题，比如类方法返回成员函数的引用。
（例外：`"abc"`这样的字面量的生存期与程序一致（即使看起来很像局部变量），所以返回`"abc"`的`const char* f()`是没问题的）

**算术运算符**

> https://zh.cppreference.com/w/cpp/language/operator_arithmetic

如果传递给内建算术运算符的操作数是整数或无作用域枚举类型，那么在所有操作前（如果可能，会先进行左值到右值转换）会对操作数实施整数提升。如果操作数之一具有数组或函数类型，那么实施数组到指针和函数到指针转换。
对于除移位之外的二元运算符（也包括内建算术比较、三路比较），如果操作数具有算术或枚举类型（可能需要无作用域），几乎总会对操作数进行[一般算术转换](https://zh.cppreference.com/w/cpp/language/usual_arithmetic_conversions)。
一般算术转换的目的是产生公共类型，并对整数应用整数提升。

**整数提升**

> https://zh.cppreference.com/w/cpp/language/implicit_conversion

小整数类型和无作用域枚举类型的纯右值可转换成较大整数类型的纯右值。因为**算术运算符不接受小于 int 的类型作为实参**，所以在左值到右值转换后，如果适用就会进行整数提升。

具体规则见文档。常用的有：

- bool 会转为 int 0/1。
- 对于 (u)(signed) char 和其它整数类型 T，如果整数转换等级低于 int，则如果 int 可表示 T 的所有值，转为 int，否则转为 uint。
- 对未固定底层类型的无作用域枚举，转换到 (u)int, (u)long, (u)long long 中首个可容纳它的类型。

注意，无符号的较小类型，可能被转为有符号整数（原因没看懂见[这里](https://stackoverflow.com/questions/56604299/why-do-unsigned-small-integers-promote-to-signed-int)）。
对于实现定义的类型，整数提升的结果也可能是实现定义的，如：unsigned short 在`sizeof(short) < sizeof(int)`时转为 int，在`sizeof(short) = sizeof(int)`时转为 uint。

> 整数提升来自 C，是因为有的平台在进行小于 int 类型的运算时，效率会更低。因此（可能）更建议都使用 int/uint 进行运算，在存储时再转回 short。

**指针**

一个指针类型的值有四种情况：

- 指向一个函数或对象，表示该对象所占用的内存的首个字节的地址。
- 是一个*对象末尾后指针*，表示内存中该对象的存储之后的首个字节的地址。
- 该类型的*空指针*值。
- *无效指针*值：不是空指针，且指向对象的生存期已结束。对无效指针进行解引用或解分配 (delete) 是 UB，进行其它求值是实现定义。

**空指针**

每个类型的指针都拥有一个特殊值，称为该类型的[空指针值](https://zh.cppreference.com/w/cpp/language/pointer)。值为空的指针不指向对象或函数，并与所有值同样为空的同类型指针比较相等。

使用*空指针常量 (null pointer constant)*赋值指针可以将其置空，包括：

- 值为 0 的整数字面量。
- nullptr_t 类型的纯右值（通常是 nullptr）。

空指针常量可以隐式转换到任何指针和成员指针。
NULL 是一个空指针常量的宏定义。
零初始化和值初始化也会将指针置空。

> 0 字面量本身是 int，但是 0 也是空指针常量，可隐式转换为任何指针类型。
> 因此对于实参 0，`f(char*)`与`f(int)`将匹配后者（最佳匹配），而`f(char*)`与`f(short)`会导致歧义，因为它们都需要一次隐式转换，并且它们涉及的整数转换与指针转换同级。`f(char*)`与`f(nullptr_t)`也会歧义。
>
> 值为空的非 nullptr_t 类型指针，不能隐式转为 nullptr_t，只能转为 void*。

**NULL**

C++ 中，[NULL](https://zh.cppreference.com/w/cpp/types/NULL) 是一个实现定义的空指针常量的宏定义。

在 C 中它为`(void*)0`，在 C++ 中可能为 0（但不能有 void* 类型）也可能为 nullptr：

```cpp
#ifdef _cplusplus
#define NULL 0
#else
#define NULL (void *)0
#endif
```

C 语言中`void*`和任何指针类型之间可以互相隐式转换：

```c
void *pv0;
float *pf = pv0;
int *pi = pv0;
pv0 = pf;
pv0 = pi;
```

但在 C++ 中，任何指针类型可以隐式转换为`void *`，反过来则必须使用 static_cast 或 C 风格的`T(x)`或`(T)x`显式转换：

```cpp
void *pv0;

float *pf = static_cast<float *>(pv0);
pf = (float*)pv0;
// pf = pv0; error: invalid conversion
int *pi = static_cast<int *>(pv0);

pv0 = pf;
pv0 = pi;
```

如果 NULL 仍是一个`void *`指针的宏定义，在 C++ 中直接写`float *p = NULL;`将无法通过编译，所以 C++ 定义 NULL 为 0，而不是指针类型的0。

允许到`void *`的转换，是为了兼容 C；不允许隐式反向转换，是因为当函数存在多个重载时（函数1使用 int\* 参数，函数2使用 float\* 参数），传递 void\* 参数时可能导致歧义。
C++ 中，对于一个非 void 的 T\* 指针 p，`f(p)`将优先匹配对应参数类型`f(T* p)`，然后才匹配 void\* 参数类型`f(void* p)`。
void\* 的指针 p 由于不能隐式转换，只能匹配`f(void* p)`。如果允许隐式转换，p 将无法确定匹配`f(int* p)`还是`f(float *p)`。

所以，因为函数重载的歧义问题，C++ 不允许 void\* 隐式转换为其它类型，所以将 NULL 从`void*`改为了 0。
0 的取值只是随便设了一个非空指针不可能取到的值（地址不可能为0）。

**nullptr**

> C 语言是没有重载的，T\* 和 void\* 之间可以随意隐式转换。
>
> 但 C++ 规定任何类型的指针可以隐式转换为 void\*，但反过来必须显式转换，否则函数重载时会出现歧义。
> 所以如果 NULL 还是`(void*)0`，任何`T *p = NULL`的隐式转换写法都将无法过编译。
> 为了兼容，C++ 允许 NULL 是空指针常量 0 的宏定义。但这样 NULL 在重载时就会被认为是 int，而非指针（0 是整数字面量，define 不能施加类型信息）。
> 所以，C++ 给出了 nullptr，不仅像 NULL 一样表示空指针，还是一个明确的指针类型。

由于整数字面量 0 是空指针常量，导致了另一种函数重载时的歧义：`f(0)`优先匹配`f(int)`，而不是`f(void*)`或`f(int*)`；而 NULL 实现定义，因此`f(NULL)`也许先匹配`f(int)`（如果它就是0），也许会导致歧义（如果是 nullptr，则`f(nullptr_t)`最优，`f(int)`、`f(void*)`都是次优候选）。
C++11 引入了 nullptr，它是一个安全的空指针，不容易产生歧义，是一个明确的指针类型。`f(nullptr)`将匹配`f(void* p)`。

[nullptr](https://zh.cppreference.com/w/cpp/language/nullptr) 是 nullptr_t 类型的纯右值，可以隐式转换成任何指针或成员指针。
nullptr_t 是空指针字面量 nullptr 的类型，可以隐式转换成任何指针或成员指针类型，但它本身既不是指针类型也不是成员指针类型。

**数组和指针**

数组不是指针，是两个不同的概念。
数组类型是有长度信息的：对于`int a[2]`，`&a`的类型是`int(*)[2]`而非`int*`，且`int(*)[1]`和`int(*)[2]`是不同类型；引用 a 则要通过`int(&)[2]`；`sizeof(a)`也能获取元素数量。
指针类型没有长度信息。由于数组作为参数会退化成指针，所以才需要额外传长度。

“T 元素的数组”可以隐式转换为“指向 T 的指针”的纯右值，该指针指向数组首地址。（C++17 起，如果数组是纯右值，则发生 *C++ - 临时量实质化*）
所以，如果数组出现在不期待数组而期待指针的环境中，就会使用该隐式转换。称为[数组到指针的退化](https://zh.cppreference.com/w/cpp/language/array)（std::array 不会）。（比如：`int arr[10];`，`+arr`就可将其转换为指针；+ (取正数) 是一个一元运算符，会期望一个可以运算的类型）
此外，当数组做函数形参或模板形参时，也会退化。

> unique_ptr 的模板参数对 T[] 有特化，所以不会出现传入 T[] 和 T* 一样的情况。

类似的是函数：“函数类型 T 的左值”，可隐式转换成“指向该函数的指针的纯右值”。
不适用于非静态成员函数，因为不存在指代非静态成员函数的左值。

数组会包含很多信息：起始地址、元素类型、大小。
函数同样，可包含：第一条指令地址、函数签名。

**指针加法**

对于`T *p`，`p+k`表示的地址为`p+k*sizeof(T)`。

对于`int a[5]`，`a`是一个`int`的指针（下面都指隐式转换后），范围为5。
对于`int a[3][5]`，`a`是一个`int (*a)[5]`的指针，范围为3，所以`a+1`指向的是`a[1][0]`，`a+2`为`a[2][0]`。

对于`int a[5]`，`&a`是一个`int a[5]`的指针，范围为1，但大小为5个int。
对于`int a[3][5]`，`&a`是一个`int a[3][5]`的指针，范围为1，但大小为3\*5个int。
`a+1`指向`a+5*4+1`，但`&a+1`指向`a+3*5*4+1`！
**注意取地址符是生成整个整体的指针！**

**sizeof**

`sizeof`的单位为字节，`int`是4，32位指针也是4，64位指针是8，`long (int)`是4或8。

对于字符串`char str[20]="123"`，`sizeof(str)`返回`str`所占空间的大小，为20，包括空字符（结束符）；`strlen(str)`返回字符串的长度，为3，到结束符为止。
对于字符串`char str[]="123"`，会自动指定合适的大小，但会先在后面加`\0`！所以`sizeof(str)`为4！

对于`char *str="123"`，`str`是一个指针！`sizeof(str)`返回4/8。`sizeof(*str)`返回`*str`即一个字符的大小，为1。

注意，当字符串用做参数时，会被转为指针传入。不管是`char s[]`还是`char s[5]`，`s`都会被当做指针！
也就是如果`char s[]`是参数，`sizeof(s)`就是8（`'sizeof' on array function parameter 'acWelcome' will return size of 'char*'`）。

若`char (*p)[5]`，`sizeof(p) = 8`；若`char *p[5]`，`sizeof(p) = 20`。

sizeof 一个类名会返回该类对象的大小，具体见 *面向对象 - 类的大小*。

> 任何对象的大小至少为1，即使类型是空类型（没有非静态数据）（只不过在继承时可能优化掉，见 *面向对象 - 空基类优化*），原因有三点：
>
> 1. 要保证同一类型的不同对象的地址始终不同，才能区分不同对象（才能知道 a1 是 a1、a2 是 a2）。
> 2. 要保证一个对象有明确的地址，否则指针自增`T *p; ++p;`不能确定如何处理。
> 3. C++ 保证 sizeof 的返回值大于0。
>    如果 sizeof 可能为0，则过去的很多代码中的`sizeof(a) / sizeof(a[0])`都会出问题（之前没问题，因为之前就这样保证）。
>    malloc(sizeof(T)) 可能会申请一个 0 大小的空间。这样会无法确定要返回的地址？

类似 Go？sizeof 表达式是一个编译时就确定的值，容器内元素的个数将不影响该值（也是通过指针指向的），其内的语句也不会真正执行。

**数组声明**

声明定长数组时，初始值数量不能超过数组大小。
数组大小只要是个常量整型表达式就可，如`1+2*3`。

**变长数组 (VLA)**

[非常量长度数组](https://zh.cppreference.com/w/c/language/array)（不是真的变长）。
C++ 标准要求声明数组时，[ ] 内的表达式为 求值大于零的整型常量表达式 (C++14 前) / std::size_t 类型的经转换常量表达式 (C++14 起)。但 gcc 和 clang 都支持了 C 中的 VLA 扩展（MSVC 没有），所以允许数组大小为变量。
当使用 sizeof 计算 VLA 大小时，自然要按照[C 的规定](https://zh.cppreference.com/w/c/language/sizeof)：若表达式的类型为 VLA 类型，则在运行时计算其所求值的数组大小，导致该 sizeof 并不是常量表达式。

**柔性数组**

> https://zhuanlan.zhihu.com/p/573081617
> https://gcc.gnu.org/onlinedocs/gcc/Zero-Length.html

C99 中，允许在结构体的最后一个元素声明一个长度为0的数组`char contents[0]`。该数组的长度任意，可以在运行时指定，分配多大就是多大。而且数组不会计入类的 sizeof，因此可以与指针相比，减少类的对齐长度？
与使用指针相比，少占 8 字节，可以减少一次间接寻址，创建时不需要二次分配空间，但不能使结构体间共享该元素。

0长数组实际是不符合标准的，无大小才是柔性数组，但 gcc, clang 支持这种写法。
所以应将这类数组声明为柔性数组/灵活数组 (flexible array)，就是不带长度的数组`char contents[]`，与上面一样。
柔性数组只能作为类的最后一个成员，且前面必须有一个成员。
使用：

```cpp
struct Node {
    size_t len;
    char contents[];
};
Node *a = (Node*)(new char[sizeof(Node) + len * sizeof(char)]()); // static_cast不行
a->contents[0] = 'a';
delete a;
```

**初始化、 sizeof 及赋值运算符忽略柔性数组成员**。拥有柔性数组的结构体，不能作为数组元素或其他结构体的成员（但 gcc 做了扩展，允许这种极易出错的情况）。
注意包含柔性数组的类，赋值时不会考虑柔性数组！应尽量避免赋值（如`Node a = b; map[0] = a;`），直接使用指针？

**不同进制数的字符表示**

默认为十进制，`\123`或`\o123`为8进制，`\x123`为16进制。

**RAII** / **(Resource Acquisition is Initialization, 资源获取即初始化)**

构造函数申请资源，析构函数释放资源，让对象的生命周期和资源绑定。

RAII 是将资源的生命周期绑定到类对象的生命周期上，具体：资源的有效期与持有资源的对象的生命期严格绑定，即由对象的构造函数完成资源的分配（获取），同时由析构函数完成资源的释放。在这种要求下，只要对象能正确地析构，就不会出现**资源泄漏**问题。
（C++ 标准保证任何情况下，已构造的对象最终会销毁，即它的析构函数最终会被调用）

通过 RAII，还可以减少**内存泄露**的产生。智能指针与容器（std::array/vector...）就是这样的，能够减少管理内存的工作量。
还可以帮助实现 *异常安全*。

RAII 更关注资源不会泄露，什么时候创建也无所谓。
内存泄露是一个对象没有被任何对象引用，但内存一直没有释放（直到程序结束）；资源泄露则是程序结束后，对象也没有被正确关闭或结束。

> 内存泄露导致内存无法被重用，使程序占用的内存越来越大。
> 资源泄露指程序使用系统分配的资源，如套接字、文件描述符、管道等，没有释放，导致系统资源浪费、可用资源减少。

应用场景：
最常见的就是，`new`出来的指针（在堆内存）忘记`delete`。
一个自动释放指针的类例子[见这](https://zhuanlan.zhihu.com/p/600337719)。注意禁用拷贝，用`move`赋值，避免内存被`delete`两次。

> 利用 RAII 或智能指针，可以实现 go 中 defer 的用法，因为函数返回时会析构栈内的对象。
> 这在函数可能抛出异常时是很有用的。如果不用 RAII，就必须在异常出现前、函数返回时，手动调用析构函数，这几乎是不可能的。
>
> 正确使用 RAII 可以避免内存泄露与资源泄露。
> 其它语言通过 GC 避免内存泄露，但基本都没有明确的析构函数？为了避免资源泄露，给出了各式 try with resources 的写法，如 java 的 try，python 的 with，go 的 defer。

**智能指针 (smart pointer)**

**裸指针表示没有资源的所有权，shared_ptr 是共享所有权，unique_ptr 是独占所有权。**
裸指针的使用是不安全的，需要程序员保证；不会影响资源的生命周期。

**auto\_ptr 为什么被废弃**

auto\_ptr 是非常早的智能指针，设计理念与 unique\_ptr 一致，指针独占资源。
由于当时没有移动语义，所以它在拷贝构造函数和拷贝赋值运算符中，通过接收非 const 的指针参数获取资源的所有权，然后将参数置为 null。

所以对于两个 auto\_ptr a,b，`a = b`的含义不是拷贝，而是移动，这与直觉是非常不符的。
这样的赋值语义非常容易出错，比如参数调用传参，或对于包含 auto\_ptr 的容器（如`std::vector<std::auto_ptr<int> > vec;`），当操作该容器时，比如遍历和排序，如果不小心用容器中的值进行拷贝，就会导致里面的指针被置为null。
而 unique\_ptr 通过 move 实现资源转移，并禁用了拷贝，不容易出错。

**unique\_ptr**

> 注意，unqiue_ptr 的开销会比裸指针更高：
>
> - unqiue_ptr 有非平凡的析构函数，所以当函数可能抛出异常时，会生成额外的清理代码以便在栈回溯时执行析构。
> - 有非平凡的拷贝构造，无法像裸指针一样直接通过寄存器传参，需要像传引用一样在栈内创建对象，然后传递其地址。见 *基础 - 调用约定*。
>
> unique_ptr 的构造函数更应该是 make_unique，而不是原本需要显式 new 的这种。所以它其实不太符合 RAII。shared_ptr 同理。

`std::unique_ptr<T>`是一个独占资源所有权的指针。
当离开 unique\_ptr 的作用域时，即 unique\_ptr 释放时，指向的资源会自动释放。

unique_ptr 的创建方式只有三种：

1. 调用构造函数，参数必须是一个通过 new 创建的指针（指针会自行析构对象，所以栈内创建的对象将会被析构两次）。
2. 赋值为 std::make\_unique 来创建一个新对象（推荐）。
3. 通过 std::move 移交另一个 unique\_ptr 的内容。不能直接拷贝赋值另一个 unique\_ptr。

```cpp
std::unique_ptr<int> ptrInt(new int(5));
std::unique_ptr<FILE> ptrF(fopen("test_file.txt", "w"));
std::unique_ptr<int> uptr = std::make_unique<int>(200);
// 可以指向一个数组，可访问和赋值 uptr[0],...,uptr[9]
std::unique_ptr<int[]> uptr = std::make_unique<int[]>(10);
// 移交所有权。此时再访问uptr将出错
std::unique_ptr<int> uptr2 = std::move(uptr);
std::unique_ptr<int> uptr3(std::move(uptr2)); // 等价
// 注意一些隐式赋值的情况，也要用move
vector<unique_ptr<int>> vec;
vec.push_back(std::move(uptr)); 
// 如果一个函数返回unique_ptr，由于返回值是右值？所以也可以用来赋值
unique_ptr<int> f(int x);
unique_ptr<int> res = f(3);
```

unique\_ptr 可以自定义回收函数 deleter，方法有3种：

1. 在定义时，加入一个类模板参数，该类要实现`void operator()(type* p) const`。
2. 在初始化时，第二个参数可以指定一个函数`void DeleteFunc(type* p)`。
3. 使用 lambda 函数，既要在类模板参数中写明该函数类型，也要在第二个参数中写明。

> unique_ptr 与 shared_ptr 重载 deleter 的方式不同：
>
> - unique 的 deleter 类型是其类型的一部分，在编译时就确定，需要将该类型传入模板参数。调用时可内联。
>     shared 可以在运行时任意绑定 deleter。但需要通过指针实现，因此调用时多一次跳转。
> - 当 unique 被赋值 nullptr 时，析构不会调用 deleter，但 shared 会。
>
> 共同点是，当传入自定义 deleter 时，需要析构保存的指针（ptr 不会再调用其它 deleter）。
>
> unique\_ptr 只包含一个指针，所以为 8B（以下均为64位）。如果自定义了 deleter，需要保存 deleter 指针对象，所以大小为 16B（可能更大，见下链接）。
> 但如果方法 1 中的类是空类（无捕获的仿函数，只有 operator ()），则 unique\_ptr 可以继承该类，而不是声明一个该类的对象，从而能使用空基类优化，避免 deleter 的额外大小。
> 具体见：https://zhuanlan.zhihu.com/p/367412477。

make\_unique 在 C++14 才提供，不过很好实现：

```cpp
template<typename T, typename... Ts>
std::unique_ptr<T> make_unique(Ts&& ...params) {
    return std::unique_ptr<T>(new T(std::forward<Ts>(params)...));
}
```

**shared\_ptr**

`std::shared_ptr<T>`允许多个指针共享资源的所有权。
为了保证安全回收对象，需要在内部对资源进行引用计数，比 unique\_ptr 更复杂些。
函数`sptr.use_count()`会返回当前的计数。

shared\_ptr 可以通过一个 new 出来的指针进行初始化，也可**直接拷贝赋值**另一个shared\_ptr，也可赋值为 std::make_shared 创建的指针（更推荐，且效率更高。但 C++20 起才支持数组）。

与 unique\_ptr 类似，也可指向数组，可自定义 deleter。
但一个 shared\_ptr 对象要比无 deleter 的 unique\_ptr 略大，除了指向对象的指针外，还有一个指针，指向引用计数等资源信息（这部分在堆中，是共用的）。所以一个 shared\_ptr 为 16B。
如果定义了 deleter，会放到资源信息中，所以大小不变。

> 指向对象的指针，可不可以只放在堆中的共享信息中，而不存在 unique\_ptr 中？
> 不可以，由于继承和多态的存在，一个基类类型的 unique\_ptr 可以拷贝自一个派生类类型的  unique\_ptr，此时堆中资源的信息指向派生类对象，而该指针应该指向基类对象。
>
> shared\_ptr 也不能随便用（事实上很少用，unique\_ptr 更常用），比如以下情况：
>
> 1. shared\_ptr 有“传染性”，如果某个资源在某一处使用了 shared\_ptr，那整个项目内与该资源有关的地方，基本都需要使用 shared\_ptr（否则即使某个普通指针指向了资源，资源还是会被释放）。可能需要重构项目。
>    不过在非异步场景，如果一个函数对传入的指针没有占有性，那么传入原生指针是可以的（但该函数调用的子函数也要保证不占用资源）。
> 2. **对同一个 shared\_ptr 的非 const 操作不是线程安全的**（如：reset、swap、operator =），如果要多线程使用，要每个线程都有自己的 shared\_ptr。因此多线程的环境下，函数要使用拷贝而非 const 引用传递 shared\_ptr，否则可能不安全（C++20 起可以使用`atomic<shared_ptr>`）。
>    但是对引用计数的操作是安全的（atomic 更新）。
>    指针内部管理对象的线程安全，不由 shared_ptr 考虑。这是对象自己的事情。
> 3. 如果资源本身比较小，则 shared\_ptr 需要的资源信息占比就会很大。
>    比指针多占用一些内存，如果内存敏感也不适合。
> 4. 有些代码会在类中写`detete this`，会导致所有 shared\_ptr 的资源失效。
>
> 此外，如果 shared\_ptr 指向一个大对象，在最后一个 shared\_ptr 不再指向它时，会导致大对象的析构（如数组、容器）。
> 这可能导致一句指针赋值，就花费很长时间。
> 如果是在业务中，可以需要避免这种情况，比如外部再令一个 shared\_ptr 指向它，当计数器为 1 时，由后台线程析构。
>
> 智能指针不应指向 static 对象，因为 static 对象生命周期与程序相同，在程序内 delete 它会出问题。

> 通过 make_shared 创建 shared_ptr，能允许它将 ptr 结构体与控制信息（引用计数类）放在一起、一起创建，减少一次 new。
> 更重要的是，它不会暴露裸指针，不易出现使用裸指针产生的错误。

注意，不要对同一个裸指针或对象多次创建 shared_ptr（会重复析构。典型的是 this）；不要随意保存 ptr.get()（可能也会导致重复创建 shared_ptr），不要 delete get 的返回值。
可以写`shared_ptr<int[]> p(new int[5]{});`，但 C++17 前不能很好的支持数组，因为 17 才有 operator []，这之前需要`p.get()[1]`？

> shared_ptr<T> 有一个别名构造函数`template<class Y> shared_ptr(const shared_ptr<Y>& r, T* ptr)`，构造后的 sp 会与 r 共享引用计数，并有相同的 deleter 以便释放 r 的资源，但是 sp 内部指向的指针是 ptr 而非 r.get()（通过 get 得到的是 ptr）（引用计数为 0 时执行 r 的 deleter 而非 delete ptr）。
> 程序员需要保证当 r 的资源有效时，ptr 也一定有效。
> 一般情况下 ptr 是 r.get() 的成员，比如 r 是 shared_ptr<vector<T>>，ptr 是 r.get().data()，通过该构造函数就可以构造指向 vector 的 data 的 sp，并保证引用计数与 vector 一致，以保证安全。也可通过此方法获取 r.get().data() 的切片保存（类似 go 的切片）。
>
> shared_ptr 创建后，deleter 不能改变。
> 但可以给 deleter 一些状态（比如捕获变量），然后通过`get_deleter`获取、修改其状态改变 deleter 的行为。
>
> ```cpp
> struct Deleter {
>     bool d;
>     void operator()(A* p) {
>         cout << "deleting: " << (d ? "true" : "false") << '\n';
>         delete p;
>     }
> };
> shared_ptr<A> a {new A{1}, Deleter{}};
> auto deleter = get_deleter<Deleter>(a);
> deleter->d = true;
> ```
>
> 除了需要写出 Deleter 类、麻烦点外，一般影响不大。不管是否包含 bool 值都是占 1B。

**weak\_ptr**

> 由于要维护 weak 的引用计数，所以 shared_ptr 里实际要有两个 atomic，因此效率会比不支持 weak 的略低。

`std::weak_ptr<T>`是共享资源的观察者，需要和 shared\_ptr 一起使用，它不会影响资源的生命周期。
shared\_ptr 与 weak\_ptr 共享一个资源控制块（所以也是 16B）。
当 shared\_ptr 的资源被释放后，weak\_ptr 会自动变成 nullptr，所以使用前要用`expired()`检查。如果 weak\_ptr 不被释放，则资源控制块也不会被释放。

weak\_ptr 可以从一个 shared\_ptr 或另一个 weak\_ptr 对象构造，获得资源的观测权：可以调用`use_count()`获得资源的引用计数，调用`expired()`检查资源是否被释放。
但是它只能看到资源的共享信息，没有资源的使用权。
通过`lock()`可以创建一个当前正在观察的资源的 shared\_ptr（如`auto sptr = wptr.lock()`）。

由于 weak\_ptr 的引用不会被计数，所以可以用来避免循环引用的问题。
如：类 A 中有一个对 B 的 shared\_ptr，类 B 中也有一个对 A 的 shared\_ptr。在栈中分别创建指向 A, B 的两个 shared\_ptr，并更新 A, B 内部的 shared\_ptr 字段指向对方，那么 A, B 对象的引用计数都为 2（一共 4 个 shared\_ptr）。当函数返回时，2 个栈对象析构，A, B 的引用计数都变为 1（因为内部还互相指向），导致两个对象都无法析构，产生**内存泄露**。
可以将一个 shared\_ptr 改为 weak\_ptr，然后需要使用该资源时，利用 weak\_ptr lock 一个出来（并尽快释放）。
改为普通指针也可以，但就需要自己避免泄露问题。

也常用于订阅者模式或观察者模式中。消息发布者根据订阅者是否存在，来决定是否发送，但不能管理订阅者的生命周期（订阅者使用 weak\_ptr 数组保存）。

**shared_from_this**

如果在类内部的某个方法内，用 this（裸指针）创建 shared\_ptr，那么每次执行方法，都会创建一个新的引用计数类，它们指向的数据相同，引用计数却独立（通过裸指针创建就是这样，而下面的 enable 会在第一次使用时创建 shared_ptr 供使用）。
这显然是不对的。想要用 this 创建，需要继承`public enable_shared_from_this<ClassName>`，它会在对象创建时生成一个指向 this 的 shared\_ptr，之后就可以使用 shared_from_this() 返回相同的引用计数类。

具体见：https://zhuanlan.zhihu.com/p/402055010
原理：https://zhuanlan.zhihu.com/p/638029004
例：

```cpp
struct Foo : public std::enable_shared_from_this<Foo> {
    std::shared_ptr<Foo> GetPtr() {
        return shared_from_this();
    }
};
```

**explicit**

explicit 构造函数和 explicit 用户定义转换函数 只能用于直接初始化和显式类型转换，不能用于复制初始化和隐式类型转换。

例外：在[按语境转换](https://zh.cppreference.com/w/cpp/language/implicit_conversion)中，如果期望的类型是 bool，那么依然会使用`explicit operator bool()`进行隐式转换。

**隐式转换** **(implicit conversion)**

> 规则见 https://zh.cppreference.com/w/cpp/language/implicit_conversion
> 包括值变换、数值提升（*整数提升*、*浮点提升*）、数值转换、临时量实质化、限定性转换。
>
> 此外可以看看 *C++ - implicit_cast*。

当某个语境使用了 T1 类型的表达式，但语境期望一个 T2 类型的表达式时，会进行隐式转换。当且仅当存在一个从 T1 到 T2 的无歧义隐式转换序列时，程序良构。
一次隐式转换为一个隐式转换序列，包含3部分：0或1个标准转换序列、0或1个用户定义转换、0或1个标准转换序列（如果存在用户定义转换）。
标准转换序列包含4部分：0或1个值变换、0或1个数值提升或数值转换、0或1个函数指针转换、0或1个限定转换。
用户定义转换包含0或1个非 explicit 转换构造函数（形参可以多于一个）或非 explicit 转换函数。

> 注意，设 D 继承 B，因为 D 数组可以隐式转换成 D\*，D\* 可以隐式转换成 B\*，所以向形参为`B*`的函数传递 D 数组是可编译但错误的！编译器无法知道实际元素的大小，在循环时会出错。
> 或者说，不要通过数组直接存储多个多态对象，它在传参时会退化、丢失类型的实际大小。只能用`D* a[3]`或`vector<D*>`来存储多态对象？
> 或者说，*I.13: 避免直接传递数组退化成裸指针*。
>
> ```cpp
> struct A {
> 	int x;
> };
> struct B: A {
> 	int y;
> };
> // 预期：接收包含 n 个元素的 A 数组
> void f(A* a, int n) {
> 	for (int i = 0; i < n; ++i) {
> 		cout << a[i].x; // 123
> 	}
> }
> B b[3] = {{1, 2}, {3, 4}, {5, 6}};	
> f(b, 3);
> ```

**值变换**

值变换是更改表达式值类别的隐式转换。每当将表达式用作期待不同值类别的表达式的运算符的操作数时，发生值变换：

- 对于某个要求纯右值作为它的操作数的运算符，每当泛左值被用作操作数，对该表达式应用左值到右值、数组到指针、或函数到指针转换以将它转换成纯右值。
- （C++17 起）对于某个期待泛左值作为它的操作数的运算符，每当纯右值被用作操作数，都会应用临时量实质化将该表达式转换成亡值。

值变换有三种：

- **左值到右值转换**：任何非函数、非数组类型 T 的泛左值，都可隐式转换成纯右值。
- **数组到指针转换**：“T 的任意大小的数组”类型的表达式，可隐式转换成“指向 T 的指针”类型的纯右值。产生的指针指向数组首元素。
    （C++17 起）如果数组是纯右值，进行临时量实质化。
- **函数到指针转换**：“函数类型的左值”可隐式转换成“指向该函数的指针”的纯右值。
    不适用于非静态成员函数，因为不存在指代非静态成员函数的左值。

**临时量实质化** **(temporary materialization conversion)**

> https://zh.cppreference.com/w/cpp/language/implicit_conversion#.E4.B8.B4.E6.97.B6.E9.87.8F.E5.AE.9E.E8.B4.A8.E5.8C.96

C++17 起，任何完整类型 T 的纯右值表达式（不是一个对象），可转换成同类型 T 的亡值表达式（标识一个新的临时对象）。转换会用纯右值初始化一个 T 类型的临时对象，并产生一个代表该临时对象的亡值，作为原本纯右值表达式的求值结果。
如果 T 是类或类数组，则必须有可访问的析构函数。

当操作数是纯右值，但期待泛左值时，会发生实质化，包括：

- 绑定引用到纯右值。
- 在类纯右值上进行成员访问，如：`Node{}.n`中纯右值`Node{}`就会被转换成亡值。
- 在数组纯右值上使用下标或进行数组到指针转换。
- 纯右值用做 sizeof 和 typeid 的不求值操作数。
- 纯右值被用做弃值表达式。

**函数调用表达式的值类别**

- 如果函数返回值类型为 左值引用或到函数的右值引用，则为左值。
- 如果函数返回值类型为 某个对象的右值引用，则为亡值。
- 否则是纯右值。

具体见草案 expr.call。

**值类别 / 表达式的值类别 / 左值和右值**

> https://zh.cppreference.com/w/cpp/language/value_category
>
> 值类别是表达式的属性。
>
> - 拥有身份且不可被移动的表达式被称作 左值表达式；
> - 拥有身份且可被移动的表达式被称作 亡值表达式；
> - （C++17前）不拥有身份且可被移动的表达式被称作 纯右值表达式，不拥有身份且不可被移动的表达式无法使用。
>     （C++17起）不拥有身份且不可被移动的表达式被称作 纯右值表达式。
>
> 拥有身份的表达式被称作“泛左值 (glvalue) 表达式”。左值和亡值都是泛左值表达式。
> 可被移动的表达式被称作“右值 (rvalue) 表达式”。纯右值和亡值都是右值表达式。
> 拥有身份指：可指代某个对象或函数。
>
> C++17 前，纯右值可指代一个临时对象。
> C++17 起纯右值不再指代一个对象，只是用做初始化的表达式，因此返回纯右值的函数不会发生拷贝（没有对象），它只是返回一个纯右值表达式，从而实现了强制复制消除，即使对象不可拷贝或移动；C++17 添加了纯右值到亡值的隐式转换（称为临时量实质化），以保证依旧可以绑定引用到纯右值或取纯右值的成员等（仅使用纯右值进行初始化不需要进行实质化）。
>
> 左值引用只可以绑定左值，右值引用只可以绑定右值，const 左值都可。

每个表达式可按照两种独立的特性进行分辨：结果的**类型和值类别** (value category)（**左值引用、右值引用属于一种类型，左值右值是值类别，两者不同**。表达式的值类别不涉及引用）。
每个表达式只属于三种基本值类别中的一种：左值 (lvalue)、纯右值 (prvalue)、将亡值 (xvalue)。

- **左值** (lvalue)：除了亡值以外的泛左值。
    左值通常在赋值表达式的左边出现（不一定是这样），是表达式结束后依然存在的持久对象，在内存中占有确定的位置。
    如：`x`（变量、函数、数据成员的名字。即使变量的类型是右值引用，由它的名字构成的表达式仍是左值表达式），`*p`，`p->n`，`x.n`（x 需要是左值），返回类型是左值引用的函数调用或重载运算符表达式，转换到左值引用的类型转换表达式。
- **纯右值** (pure rvalue, prvalue)：包括两种表达式：==计算某个运算符的操作数的值表达式==（这种纯右值没有结果对象）；==初始化某个对象的表达式==（这种纯右值有一个结果对象）。*结果对象*是变量、由 new 创建的对象、由临时量实质化创建的临时对象、或前面三类对象的成员。
  字面量、所有内建的算术/逻辑/比较/取地址表达式、返回类型是非引用的函数调用或重载运算符表达式、转换到非引用类型的类型转换表达式。
  纯右值不具有多态：它所标识的对象的动态类型始终是该表达式的类型。不能具有不完整类型（但 void 和 throw 表达式可以）。
  如：`&a`，`str.substr(1, 2)`，`a+b`，`Node{}`。
- **亡值** (expiring value, xvalue)：==代表它的资源能够被重新使用的对象或位域的泛左值。==
  右值对象的成员表达式或成员指针表达式，返回类型为右值引用的函数调用或重载运算符表达式，转换到右值引用的类型转换表达式。
  与纯右值非常像，因为往往用于移动、很快就会消失；但可以是多态的，可以具有不完整类型，也算具名，所以也属于泛左值。
  如：`(a+b).n`，`Node{}.n`，`arr[n]`（arr 是右值，或者`n[arr]`），`std::move(x)`，`static_cast<int&&>(x)`。
- **泛左值** (generalized lvalue, glvalue)：左值和亡值。==是一个求值可确定某个对象或函数的标识的表达式。==
  可以转化为纯右值，可以是多态的（可以有和静态类型不同的动态类型），可以具有不完整类型。
- **右值** (right value, rvalue)：纯右值和亡值。表达式结束后不再存在的临时对象，不在内存中占有确定位置。
  右值可以用来初始化 const 左值引用和右值引用，但该右值所标识的对象的生命周期，将被延长到该引用的作用域结束。
  - 右值不能取地址。
  - 右值不能用作内建赋值运算符及内建复合赋值运算符的左操作数。
  - 右值可以用来初始化 const 左值引用和右值引用，并且其生命周期会被延长（C++17 起，准确来说是亡值可以用来初始化引用，纯右值会被实质化生成亡值）。

> 注意，类的赋值会调用 T& operator =，这并不是内建赋值运算符，而是一个函数调用，因此`A{} = a;`是可以成功的，等价于`A{}.operator=(a)`。string 纯右值调用 operator + 也同理。
> 但要注意其实现（或默认时成员赋值的实现）中不能用内建赋值？
> 如果要避免这种情况，给`A& operator =(const A&)`后面加上引用限定 & 即可。

左值是表达式结束后依然存在的持久对象（对象在内存中占有确定的位置）
右值是表达式结束后不再存在的临时对象（不在内存中占有确定位置的表达式）
可以对左值取地址，但右值不行。
左值不代表一定可以被赋值（如`const T&`），只是可以放在左侧被初始化。
常量字符串是左值！可以`&"abc"`，因为字符串是`const char*`。而`"abc"s`则是纯右值。
非 const 的左值引用不能接收右值。

赋值：
拷贝构造函数为`T(const T& x)`，移动构造函数为`T(T&& x)`。
类似地，`operator =`也分为常量左值（拷贝赋值）和右值版本（移动赋值）。
**C++ 在满足以下条件时，会生成默认的移动构造函数（和右值`=`？）：没有自定义拷贝构造函数、没有自定义`operator =`、没有自定义析构函数。**
通过`= default`也可生成默认的移动构造函数。默认的很简单，就是调用该类所有成员的移动构造函数。
通过`= delete`禁用默认实现。

> 如果声明了拷贝构造函数，那么会自动生成一个拷贝赋值函数；反之亦然。
> 三法则（The Rule of Three）：如果你声明了任何一个拷贝构造函数、拷贝赋值操作或析构函数，那么你应该声明所有的这三个函数。
> 因为：当需要拷贝构造、拷贝赋值或者析构函数时，往往是类要管理某些资源（通常是内存资源）？当需要在拷贝中对资源进行管理，那么也需要在析构函数中对资源也进行管理（通常是释放内存），反之亦然。
> 见 *面向对象 - 三五零法则*。
>
> 初始化使用构造函数，赋值使用`=`赋值函数。

`T t1 = t2`或`T t1(t2)`，会调用拷贝构造函数。
`T t1 = std::move(t2)`，调用移动构造函数。如果没有实现移动构造，由于右值引用也可匹配`const T&`，所以会调用拷贝构造。
`T t1 = t2+t3`，会先通过`+`生成一个临时的`T`（右值，也涉及构造一个`T`，取决于`+`实现），再通过移动构造赋给`t1`。同上，如果没有移动构造，则用拷贝构造。
该语句涉及两次构造，`=`和`+`。
`t1 = t2; t1 = std::move(t2); t1 = t2 + t3;`，与上述情况一致，只是取决于`operator =`的实现情况。

**operator ->**

. 和 -> 是成员访问运算符。

对于 ->：如果是内建的 operator ->，则`E1->E2`与`(*E1).E2`等价；如果是用户定义的 operator ->，则`E1->E2`会先求值 E1（如果中间遇到 -> 则递归求值），得到它返回的指针值 p，然后返回`(*p).E2`。

> 注意 \*p 是左值，而 operator -> 不管是内建还是用户定义版本，本质上都是`(*p).q`，所以如果 q 是成员函数，则始终会匹配左值版本，因为调用者是左值。
> 因此 [move_iterator](https://zh.cppreference.com/w/cpp/iterator/move_iterator/operator*) 的 operator -> 在 C++20 被弃用：我们期望通过 move_iterator 访问成员时将 \*this 视为右值，但 -> 一定会将 \*this 视为左值。
>
> 如果 x 是类对象，则`x()`调用的是`x.operator()()`，`x->v`调用的是`x.operator->(v)`。

**不完整类型**

[不完整类型](https://zh.cppreference.com/w/cpp/language/type#.E4.B8.8D.E5.AE.8C.E6.95.B4.E7.B1.BB.E5.9E.8B) (incomplete type) 包括：
void 类型；已声明但未定义的类型；在声明后，确定底层类型之前的枚举类型；未知边界数组；上述类型的数组。
如果在数组声明中省略关于大小的表达式，则为未知边界数组。多维数组只能在第一维中有未知边界，如`a[][3]`可以，`a[3][]`不可以。

可以定义指向不完整类型的指针或引用；可以声明以不完整类型作为参数或返回值类型的函数（但不能定义）（成员函数可以吗？）。

在创建一个类对象前，类必须被定义，否则编译器无法确定要分配多少空间；在使用类成员前同样，否则编译器无法确定其成员。
只有类的定义全部完成后，类才算被定义，所以一个类的成员不能是本身；但一旦类名出现后，类就算被声明，因此类能够包含指向自己的指针或引用。

**前向声明 / 前置声明**

函数和类都可以将声明和定义分离。
[前置声明](https://zh.cppreference.com/w/cpp/language/class) (forward declaration) 声明一个之后再在此作用域定义的类类型。在定义出现前，此类名是不完整类型。

前置声明允许类之间互相引用；如果某个头文件只用到某个类的指针，也可以减少 include 依赖。

如果前置声明出现在局部作用域，那么它会隐藏外部作用域中出现的 先前声明的相同名字的声明（不会影响当前作用域）。

**前置++ 与 后置++**

前置 `operator++()` 返回一个对操作数本身的引用（一个左值引用）。（因为是左值，在使用该引用赋值时，使用拷贝赋值，即`constructor(const Type &x)`）
后置 `operator++(int)` 返回的是一个 const 临时对象（右值，对操作数的拷贝，是不具名的），只读。
所以`++++i`是合法的，`i++++`是不合法的；`int&& j = i++;`、`int& k = ++i;`是合法的，反过来是不合法的。

由于后置会生成一个拷贝作为返回值，所以影响效率（但对于基本类型，会优化掉，结构体要注意）。

**复制消除 (copy elision)**

[copy elision](https://zh.cppreference.com/w/cpp/language/copy_elision) 也包括 move elision（C++11 起有，C++17 起才保证一定应用）。
在以下两种情况中，可以省略复制和移动构造函数，直接将表达式产生的对象构造到要初始化的对象位置上，不需要类具有可访问的复制/移动构造：

- 初始化时，**如果初始化表达式和被初始化的对象类型相同，且表达式为临时量**（C++17 前，见 *C++ - 临时量实质化*）/**纯右值**（C++17 起）。
- RVO：return 语句中，当操作数是一个与函数返回类型相同（忽略 cv）的类类型的纯右值时。

如：`Node a = Node{1, 2};`在优化前需要一次有参构造、一次复制/移动构造、一次析构，但优化后只需要一次有参构造，并且不需要 Node 有复制构造函数。
只有初始化表达式是左值时才需要拷贝构造。

通过`-fno-elide-constructors`关闭。
是唯二可以不按照 *as-if 规则*  进行的优化：即使拷贝或移动赋值有副作用（比如输出语句），也可将其优化为拷贝或移动构造（即使不会输出）。
(N)RVO 就是复制消除的一种。

> 复制/移动构造不应去做复制/移动之外的事情，不应该有额外的副作用，因为复制消除不会因为它有副作用就不做优化。
> 复制消除发生时，不会调用复制/移动构造。
>
> ```cpp
> struct C {
> 	C(int) {}
> 	C(const C&) = delete;
> };
> C x {1};
> C y = 2; // ok
> ```

**拷贝构造可以去掉引用吗**

标准不允许`T(T x)`这种构造函数写法。去掉引用会多一次无意义的拷贝，影响效率；但更重要的是传参本身就需要一次拷贝构造，会导致拷贝构造无限递归。

当 x 是纯右值时，由于 C++17 起保证了复制消除，可直接在 T 位置上进行构造，故不会出现无限递归的情况。

**返回值优化 RVO**

RVO (Return Value Optimization) 是一种编译优化，可以减少函数返回时产生的临时对象，从而消除部分拷贝或移动操作。
当一个未具名且未绑定到任何引用的临时变量，被移动或复制到一个相同类型的对象时，拷贝和移动构造可以被省略，临时变量会直接构造在要拷贝/移动到的对象上。因此，当函数返回值是未命名临时对象时，可以避免拷贝和移动构造。

RVO 其实就是复制消除的一种情况，因此也可通过`-fno-elide-constructors`关闭。
从 C++17 起是一定进行的。

例：

```cpp
A makeA () {
    return A();
}
int main () {
    A a = makeA();
    return 0;
}
```

在没有 RVO 的情况下，上述过程（整个程序）应包括一次默认构造函数、两次拷贝构造函数和三次析构函数的调用：

- `A()`调用默认构造函数，生成临时对象1。
- `return A()`将临时对象1，通过拷贝构造赋值给返回值，即临时对象2。对象1 析构。
    （通过复制消除，可以避免从栈对象到返回值的拷贝/移动构造）
- 初始化，进行一次`a`的拷贝构造，然后对象2 析构。
    （通过复制消除，可以避免从返回值到 a 的拷贝/移动构造）
- 对象`a`析构。

如果实现了移动构造，也还是要这么多次函数，只是把拷贝构造换成了移动构造。
在 RVO/复制消除 优化后，实际只包含`a`的一次默认构造函数和`a`的一次析构函数。
它相当于将函数优化成直接传入对象进行构造：

```cpp
void makeA (A& a) {
    a.A::A();
}
```

**RVO 优化的条件**：

- 返回值是局部未命名对象（需要在函数内创建，且只能出现在`return`里），且类型和返回值类型相同。

当使用`return std::move(A())`时，会导致 (N)RVO 失效，多一次移动构造和析构。
当函数调用者不是初始化，而是赋值`A a; a = makeA();`时，也会多一次默认构造、析构和移动赋值。
当不能确定返回值时，如通过分支决定返回值，也不能优化。

> return move 一般是没有意义的，如果返回的对象是隐式可移动的，那么编译器自己就会选择移动构造，不需要显式写 move。
> 而且可能影响编译器的 RVO 优化。
>
> 但如果对象不是隐式可移动实体，那么需要确实要加 move，否则重载决议会选择拷贝构造。
> 这主要有几种情况：
>
> - 返回类的成员变量（类对象还要持有成员，所以一般不会移出来）
> - 返回结构化绑定的变量（这种变量与普通变量不太一样）
> - 返回局部对象的一部分，比如：`return move(vec[0]);`。
>
> 具体看 return 规则：https://zh.cppreference.com/w/cpp/language/return

**NRVO**

NRVO (named RVO) 允许函数中的返回值已预先被定义（具名），而不是只能出现在`return`中。
它与复制消除有一点不同：具名栈对象是一个左值，通过它构造返回值时不满足复制消除的右值要求，因此需要一次拷贝/移动构造；NRVO 就是优化了这一次。

RVO 在 C++17 以后才被保证使用。NRVO 则更不确定。
但是，如果每个 return 都返回同一个具名对象，则通常一定应用 NRVO？

> 即使启用 NRVO，如果返回对象的引用，NRVO 也会失效，应该直接返回原对象。
>
> ```cpp
> string f() {
> 	string s;
> 	s += "b";
> 	return s; // ok
> 	// return (s += "b"); // 无法优化，+= 返回 string&
> 	// string& t = s; return t; // 无法优化
> }
> ```

**move**

`std::move`将一个左值 t 转变为右值，以允许匹配右值引用、调用移动构造函数（**但 move 本身不会对参数做修改**）。
实现为：通过 remove_reference 去除类型中的引用，然后通过 static_cast 转为该类型的右值引用类型。

```cpp
template<typename _Tp>
constexpr typename std::remove_reference<_Tp>::type&& move(_Tp&& __t) noexcept
{ 
   return static_cast<typename std::remove_reference<_Tp>::type&&>(__t); 
}
```

move 的参数类型是`T&&`，即通用引用，既可以匹配左值引用、也可匹配右值引用，具体见下。

> 仅 move 本身不会对参数做修改，所以一个函数调用表达式内，同时使用 p 的函数和 move(p) 还是没问题的（`func(p.get(), std::move(p))`），实际的移动发生在函数内，`p.get()`在函数调用前就执行完了。
>
> 当函数参数的类型非引用时，如果传入左值，则参数发生拷贝构造；如果传入右值，则参数发生移动构造（传入的对象将会被移动）。
> 因此，如果要向函数`func(Node a)`传递不再使用的 Node 对象 a，应该使用`func(std::move(a))`以便调用移动构造。
> 相似问题可以见 *规则 - 其它 - pass-by-value*。

**remove_reference**

`remove_reference<T>::type`可以移除类型`T`中的引用，如：`T`是`int&`或`int&&`都返回`int`。

实现就是一个类模板和两个特化的模板，对应非引用、左值引用、右值引用三种模板参数：

```cpp
// 模板
template<typename _Tp> struct remove_reference { typedef _Tp   type; };
// 特化
template<typename _Tp> struct remove_reference<_Tp&> { typedef _Tp   type; };
template<typename _Tp> struct remove_reference<_Tp&&> { typedef _Tp   type; };

template<typename _Tp>
constexpr typename std::remove_reference<_Tp>::type&& move(_Tp&& _t) noexcept
{ 
	return static_cast<typename std::remove_reference<_Tp>::type&&>(_t); 
}
```

**右值引用 / 为什么需要 move**

> 右值引用可为临时对象延长生存期，这点与 const 左值引用一致。但前者可修改，后者只读。
> const 右值引用没有特别意义（因为不能移动），传参时会被当做 const 左值引用。
>
> 更重要的是，当函数同时具有右值引用和左值引用的重载时，**右值引用重载绑定到右值（包含纯右值和亡值），而左值引用重载绑定到左值。这允许在适当时机自动选择移动构造、移动赋值和其它具有移动能力的函数，使得作用域中不再需要的对象可以被移动出去，避免拷贝和不必要的析构。**

> 左值是表达式结束后依然存在的持久对象（对象在内存中占有确定的位置）
> 右值是表达式结束时不再存在的临时对象（不在内存中占有确定位置的表达式）
>
> 很多时候，我们会通过 表达式产生或不再使用的临时对象 去初始化一个对象。如果没有右值引用，就只能通过拷贝临时对象去产生一个新对象，然后临时对象就会析构，多了一次无意义的拷贝和析构。右值引用和移动可以避免这一点。（尤其是某些对象内可能有容器，包含很多数据，拷贝时需要进行深拷贝；而移动则很高效）
>
> **区分左值右值，允许程序员更加精细的处理对象拷贝时的内存开销，提高了对临时对象和不需要的对象的利用率，这是 C++ 很有意思的一点。**
>
> move 将一个左值引用 T& 转为右值引用 T&&，以便调用移动语义的函数。
> 被移动所有权的对象不应再被使用，但不代表一定不能使用。要看移动的实现。比如 [vector](https://zh.cppreference.com/w/cpp/container/vector/vector) 的移动构造中，保证移动后的 vector 是 empty()（但是 vector 的移动赋值只保证移动后的可析构？移动后最好还是要 clear）。

浅拷贝：拷贝结构体时，会值拷贝里面的数据。但如果结构内有指针，指针值依旧会拷贝，导致拷贝后也指向同一个数据。
深拷贝：对于指针拷贝，需创建新对象，遍历指针指向的旧对象复制其元素。
更常用深拷贝。浅拷贝也很简单。

没有右值引用前，通过 拷贝构造函数、赋值运算符重载 实现结构体深拷贝：

```cpp
class Array {
public:
    int *data_, size_;
    Array() {...}
    // 拷贝构造
    Array(const Array& temp_array) {
        size_ = temp_array.size_;
        data_ = new int[size_];
        for (int i = 0; i < size_; i ++) {
            data_[i] = temp_array.data_[i];
        }
    }
    // 拷贝赋值
    Array& operator=(const Array& temp_array) {
        delete[] data_;
 
        size_ = temp_array.size_;
        data_ = new int[size_];
        for (int i = 0; i < size_; i ++) {
            data_[i] = temp_array.data_[i];
        }
    }
    ~Array() {
        delete[] data_;
    }
};
```

**拷贝构造会进行一次深拷贝**。即使参数为左值引用类型，避免了一次参数拷贝（所以要加`const`避免修改原值）。
拷贝会保留原值，但有时候，我们不需要保留原值，可以直接将原值的数据给它，原值就不要了。
比如：`vec.emplace_back(Node{1})`，`Node{1}`会创建一个临时结构体，可以直接将这个结构体内容赋给`vec[i]`，然后清空原结构体（也避免多次delete）。
这个`Node{1}`就是右值引用。它在表达式结束就会销毁，所以不如直接拿它的值来用。
对于一些左值，如果赋值完后不再需要，也可直接拿它的值过来。这个移动就通过右值引用实现。

右值引用允许通过 移动构造函数、重载赋值运算符（使用右值引用做参数）实现：

```cpp
class Array {
public:
    ...
 	int *data_, size_;
    // 移动构造
    Array(Array&& temp_array) {
        data_ = temp_array.data_;
        size_ = temp_array.size_;
        // 为防止temp_array析构时delete data，提前置空其data_      
        temp_array.data_ = nullptr;
    }
};
```

**右值引用避免了深拷贝，提高了拷贝性能。**如果参数在赋值完后不再需要，就可以移动构造。
（但如果没有实现移动构造或赋值（比如被隐式弃置），也会调用拷贝构造或赋值，即 const & 可以匹配右值，但非 const 的 & 不可）

此外，**`move`也相当于移交内部对象的所有权。**
如：`std::unique_ptr`只允许移动构造函数，来保证它拥有对象的所有权，而原指针没有。

**const T&&**

用处：

- 将类型声明为**`const T&&`**可以避免成为万能引用，它只接收右值，不接收左值。
- 在包装器类返回被包装的对象时，使用 const T&& 来同时保留值类别（右值）和 const 限定。这种类型不可移动，除非它是类且某成员有 mutable 修饰，则可移动该成员。
    比如：[optional::value](https://zh.cppreference.com/w/cpp/utility/optional/value)、[get(variant)](https://zh.cppreference.com/w/cpp/utility/variant/get)。

```cpp
template <class T, class... Types>
constexpr T& get(variant<Types...>& v);
template <class T, class... Types>
constexpr T&& get(variant<Types...>&& v);
template <class T, class... Types>
constexpr const T& get(const variant<Types...>& v);
template <class T, class... Types>
constexpr const T&& get(const variant<Types...>&& v);
```

**万能引用** / **通用引用** / **转发引用**

> 万能引用 表示它既可能是个左值引用，也可能是个右值引用。它本身 (T&&) 不是具体的引用类型。
> 右值引用与万能引用的区别是：右值引用是一个明确的类型，如`int&&`；而万能引用指代发生类型推导时的引用类型，如`T&&, auto&&`，可能会是右值引用。
>
> 如果函数模板的形参是同一函数模板的类型模板形参 T 的无 cv 限定的右值引用，或 auto&&，则它是万能引用。
> 例外：如果 auto&& 是通过 { } 初始化式列表赋值和推导，则不是。
>
> 注意，只有`T&&`中对 T 进行类型推导时才是，比如：模板类内的非模板成员函数不是，`template <class T> void vector<T>::push(T&& value)`就不是；`template <class T> void g (vector<T>&& v)`也不是。
>
> 当同时存在左值引用和万能引用的重载时，左值会调用前者。
> 当同时存在非模板 const int& 和模板万能引用重载时，只有 const 左值引用会匹配前者，其它均会匹配后者（模板能生成最佳匹配）。
> 可以将类型声明为`const T&&`来避免万能引用，它只接收右值，不接收左值。

```cpp
template<typename T>
void f(T& param) {
    cout << param << endl;
}
template<typename T>
void func(T&& param) {
    cout << param << endl;
}
```

通用/万能引用 (universal reference)/转发引用 (forward reference)：使用右值引用类型的模板形参，既能接收右值，又能接收左值。所以上述函数只需要写第二个。
注意，只有发生类型推导时，`T&&`才表示万能引用（如模板函数传参就会经过类型推导的过程，所以如果`T`是模板，`T&&`就是万能引用；如果`T`不是模板，`T&&`就是右值引用），否则只表示右值引用。

> 注意，当用函数模板**实例化**，给一个函数指针赋值时，指针的参数类型必须完全匹配函数模板定义中的参数类型。
> 即使函数模板用的是万能引用，也只能匹配参数类型为右值的函数指针（实例化了就不再是万能引用了）。
>
> ```cpp
> template <typename T>
> void f(T&& v) {
>  cout << v << '\n';
> }
> void(*p)(int&&) = f<int>; // ok
> // void(*p)(int&) = f<int>; // error，除非 f 是 f(T& v)
> // void(*p)(int) = f<int>; // error，除非 f 是 f(T v)
> ```
>
> 此外类模板实参推导中，不存在万能引用。

**引用折叠**

> 调用包含通用引用的函数时，会发生实参和形参的引用类型不同的情况，两个引用之间会发生引用折叠，结果只保留一个引用：只有引用都是右值引用时，结果才是右值引用。如：`int& &&`是`int&`，`int &&`才是`int&&`。
>
> 多个引用会发生引用折叠，所以没有多重引用；但是有多重指针。
>注意推导出的模板类型是可能带引用的（不然也没必要 remove_ref）。

当形参类型为万能引用时，传入左/右值会使实参类型为左/右值引用类型，本质是因为引用折叠：
**如果形参为左值引用、或实参为左值，则实际类型为左值引用。否则，即形参是右值引用、且或实参是右值，类型才是右值引用。**

```cpp
template<typename T>
void func(T& param) {
    cout << param << endl;
}
int i = 1;

func(i); // T 是int，param 是int&
func(1); // T 是int，param 是int&

template<typename T>
void func(T&& param) {
    cout << param << endl;
}

func(i); // T 是int&，param 是int&（特殊情况，见 模板 - 模板实参推导）
func(1); // T 是int，param 是int&&
```

**forward 原理 / 完美转发**

> 万能引用函数的实参，可以是左值引用也可以是右值引用。但在函数内，x 构成的标识符表达式始终是左值。
> 如果在函数中再使用参数`x`构成的表达式进行函数调用，并且要保持它的引用类型，需要用`std::forward<T>(x)`。
> forward 就是把左值引用类型的左值转为左值，把右值引用类型的左值转为右值（参数始终都是左值）。
>
> forward 是借助 类型 T 和引用折叠 返回正确的引用类型的：万能引用中，当参数为左值引用时，T 为左值引用，与 forward 中附加的 && 会折叠成左值引用；当参数为右值引用时，T 不带引用，会被 forward 转换成 &&。
>
> 只有万能引用的函数需要完美转发，否则也做不到；而且什么都不加就是左值，用上 move 就是右值。
>
> ```cpp
> struct A {
> 	string s;
>      void setS(string name) noexcept {
>          s = std::move(name);
>      }
>      // or
>      template <typename String, typename = typename
>      std::enable_if_t<!is_same_v<decay_t<String>, std::string>>>
>      void setS(String &&name) noexcept(is_nothrow_assignable_v<std::string&, String>) {
>          s = std::forward<String>(name);
>      }
> };
> ```
>
> 当 forward 中的模板参数 T 是一个值类型时（无引用），`forward<T>(t)`等价于`move(t)`。
>
>在函数相关的模板的转发逻辑中，forward 能根据函数参数的类型（A, A&, const A&）正确转发临时的函数参数。见 *Codes - C++ - function_ref*。

当给函数传递右值引用`T&& x`后，在函数内使用`x`始终是左值表达式。
如果传递参数时要保持`x`的右值类别，必须用`std::forward<T>(x)`传递。
类似的，定义`int&& a=1`，调用`f(a)`传的也还是左值引用，因为`a`是变量名构成的表达式。

例：

```cpp
void overloaded (const int& x) {cout << "[lvalue]\n";}
void overloaded (int&& x) {cout << "[rvalue]\n";}

template <class T>
void fn (T&& x) {
	overloaded (x);                   // always an lvalue
	overloaded (std::move(x));        // always an rvalue
	overloaded (std::forward<T>(x));  // rvalue if argument is rvalue, else lvalue
}

int a;
fn (a);
fn (0);
```

forward 的实现：

```cpp
template<typename T> 
constexpr T&& forward(typename std::remove_reference<T>::type& __t) noexcept
{ 
	return static_cast<T&&>(__t); 
}

template<typename T> 
constexpr T&& forward(typename std::remove_reference<T>::type&& __t) noexcept
{
	static_assert(!std::is_lvalue_reference<T>::value, "template argument"
		" substituting _Tp is an lvalue reference type");
	return static_cast<T&&>(__t);
}
```

在上面的 fn 中，x 始终是左值，所以总是会调用第一个 forward，第二个是没意义的。
forward 是利用类型推导的 T 进行类型转换的：

- 当 fn 的实参为左值引用时，\_Tp 被推导为`int&`（以 int 为例，反正是一个具体类型），cast 转换的类型，即返回的类型会发生引用折叠：`int& &&`即`int&`。
- 当 fn 的实参为右值引用时，\_Tp 被推导为`int`，则返回的类型就是`int&&`。

> 参数是 remove_reference_t<T>&& 而非 T&&，这与 identity_t<T> 相同，可以要求用户显式写出类型而不是使用自动类型推导。
>
> 注意，在进行类型推导时，如果函数的参数是万能引用，即：`template<typename T> void f(T&& x)`，则：
>
> - 调用`f(左值)`，T 会被推导为相应类型的**左值引用**（const 左值则为 const type&，否则为 type &），如：`f<int&>(int&)`。
> - 调用`f(右值)`，T 会被推导为**值**或指针（type 或 type\*，反正不是引用），如：`f<int>(int&&)`。
>
> 具体见[ref](https://zh.cppreference.com/w/cpp/language/template_argument_deduction)。

容器的 [emplace](https://zh.cppreference.com/w/cpp/container/vector/emplace) 系列函数可接收元素 T 的各参数，将参数 args... 作为`std::forward<Args>(args)...`转发给构造函数，完成构造。
而对于 push，必须传递 T 类型，即自己进行构造。

**static_assert**

[static_assert](https://zh.cppreference.com/w/cpp/language/static_assert) 是编译时的静态检查。通过它，可以用编译器来保证某些约束，在编译期间发现更多的错误，来减少 bug 的产生（尤其是涉及模板时）。
它可以出现在命名空间和块作用域中（作为块声明），也可以在类中（作为成员声明），也可以在函数内。
由于是在编译期间进行断言，不会生成目标代码，所以不会影响程序的性能。

```cpp
static_assert(bool-constexpr, message) //(since C++11) message 必须是字符串常量或字面量
static_assert(bool-constexpr) //(since C++17)
```

函数参数不会被认为是立即常量表达式，因此不能出现在 static_assert 里（即使是 constexpr 函数）。
如果想对参数做 assert 校验，并想如果它在编译期能确定时调用 static_assert，需要些别的方法。见[这里](https://stackoverflow.com/questions/59880069/how-to-dispatch-between-assert-and-static-assert-dependend-if-in-constexpr)。

> C++ 的语法检查通常为：对于非待决名（不依赖模板形参），在实例化之前就检查；对于待决名，在实例化之后才检查（这属于实现定义，见[这里的描述](https://timsong-cpp.github.io/cppwp/n4861/temp.res#8)）。
> 因此`static_assert(false)`、`if constexpr(false)`通常会直接编译失败（即使模板使用时不会实例化该语句），而不是在实例化时遇到它才编译失败，所以不能用它去避免某个实例化的发生。可以用一个求值始终为 false 的模板变量代替 false（见[这里](https://zh.cppreference.com/w/cpp/language/if#Constexpr_If)）。
> CWG2518 后（比较新的编译器）解决了这个问题。

**static**

[static](https://zh.cppreference.com/w/cpp/keyword/static) 有多种含义。

静态变量在编译期就可以分配相对内存地址。全局静态变量是在 main 执行之前零初始化（如果是动态链接则是在链接时），局部静态变量是第一次使用时初始化。

**volatile**

C++ 中，[volatile](https://gcc.gnu.org/onlinedocs/gcc-4.1.2/gcc/Volatiles.html) 与原子性（atomic）、内存序（memory_order）、建立线程同步（锁等）无关（应该用括号中的东西）。它不应该被应用于多线程编程。
volatile 意为允许内存映射的 IO 操作（给驱动开发者），仅要求编译器对**它和其它 volatile 数据**的读写按照程序的先后顺序执行，不能对 **volatile 变量内存的读写**重排序。因此它并不是内存屏障。

volatile 表示读会产生副作用。副作用可以认为是会影响全局状态的东西。
编译器优化代码时，默认读取没有副作用，如果有，就需要代码告诉编译器，防止它做出错误的代码优化。
可以参考 [clang 的解释](https://llvm.org/docs/LangRef.html#volatile-memory-accesses)：特定的访存操作，如 load、store、llvm.memcpy 可被标记成 volatile。**优化器不能修改 volatile 操作的数量、不能修改 volatile 操作之间的顺序（相对于其它 volatile 操作）。**
但允许优化器修改 volatile 操作相对于非 volatile 操作的顺序，因此与 Java 不同（Java 用它当做屏障），对 volatile 的读写不是屏障，不能用于多线程。

> 但 MSVC 对标准 C++ 语法做出了扩展，给 volatile 增加了线程间同步的含义，但考虑到可移植性，没有理由新标准库提供了其它解决方案的前提下再使用这种非标准扩展。
> 对于绝大部分程序员而言，用不到、也不应该使用 volatile。

**const**

> define 只是简单的替换，没有类型信息。define 的定义也不能提供任何封装性，可以被全局访问。此外复杂的内容还容易出错。
> 所以应尽可能少的使用 define，可以用 const、inline 函数、enum 去代替。
>
> const 是具体的对象。const 的变量放在只读区域，有时甚至可以优化为立即数（但没有地址）。

const 可以修饰变量，限定它为常量、不允许改变。
尽可能使用 const 可以减少编程错误；编译器对常量的运算还会尽可能优化，所以效率也高。

- 类中的 const 常量，只能在初始化列表中进行赋值。
- const 可以修饰指针，但具体修饰的对象要从右往左确定。
- C++ 禁止将 const 对象的地址赋值给非 const 指针。如果一定要，通过 const_cast 转换。
- const 引用不会对引用对象进行修改。所以函数参数可以使用 const 引用传递来减少拷贝。
- 如果函数返回值的类型为 const，如果返回普通数值则没有什么影响，但如果返回指针，则只能赋给相同类型的 const 指针。

**const 修饰函数**

const 可以修饰成员函数（放在后面）。const 函数无法修改成员变量（其它见 *面向对象 - 成员函数的引用限定*）。

- const 对象只能访问类的 const 方法，而非 const 对象任意。const 引用也是。
- const 方法可以访问所有成员变量，但也只能调用它们的 const 方法，来保证不会发生修改。
- const 方法不能修改任何成员变量，除非变量用 mutable 修饰。
- 如果 const 和非 const 的两个函数构成重载（函数名、参数、返回值相同），则非 const 对象默认调用非 const 函数（const 对象还是只能调 const 的）。
- 如果 const 函数返回一个成员的引用，则返回值类型必须是 const 引用（可以认为 const 函数只能获取到 const 引用信息）。

> 对于非 const 方法，里面的 this 指针类型是`Type * const this;`；对于 const 方法，里面的 this 指针类型是`const Type * const this;`，所以 this 指向 const 对象，无法修改成员。

类似 remove_reference，可以用模板写出一个 remove_const：

```cpp
template<typename T>
struct remove_const {
	typedef T type;
};
template<typename T>
struct remove_const<const T> {
	typedef T type;
};
template <class T>
using remove_const_t = typename remove_const<T>::type;

int main() {
    int a = 1;
    const int b = 2;
    remove_const<decltype(a)>::type aa = 3;
    remove_const_t<decltype(b)> bb = 4;
    cout << std::is_same<decltype(aa), int>::value << endl; // true
    cout << std::is_same<decltype(bb), int>::value << endl; // true
}
```

注意指针的情况，`const int *p`的 const 不是 p 的，用 remove_const 后不会有变化。见 *top-level const*。

**常量表达式 (constant expression)**

[常量表达式](https://zh.cppreference.com/w/cpp/language/constant_expression)指能在编译时求值的表达式。它是结果满足某些条件的*核心常量表达式*（见 ref）。

如果常量表达式的值是指针或引用，则它必须指向静态存储期对象（见下 *编译期取地址*）、函数或空指针。

**明显常量求值的表达式**一定会在编译期执行。可以用 is_constant_evaluated (C++20) 和 if consteval (C++23) 判断当前是否是明显常量求值语境。
它包括以下场景：

- 数组边界。
- if constexpr 的条件。constexpr 变量的初始化表达式。
- consteval 函数的参数等。

**constexpr**

[constexpr](https://zh.cppreference.com/w/cpp/language/constexpr) 可以：

- 声明常量（包含 const）。
- 修饰函数，表明该函数既可在运行期执行，也可在编译期执行。
    只有输入和语句都能在编译期执行/确定时，它才可能在编译期执行，但也仍可能在运行期执行。只有当 constexpr 函数用做*明显常量求值的表达式*（或叫立即常量上下文）时，它才一定会在编译期执行。
    使用 consteval 声明立即函数可以保证编译期执行。

const 能表示两种含义：

- 表示只读变量（如`f(const int x)`），虽然这个变量不能直接修改，但它本质上依旧是变量，且可能通过其它方式进行修改（如一个 const 引用）。
- 表示常量（如`const int x = 1;`），不可修改，常量可以初始化数组，如`array<int, x> arr`。

C++11 中可以将 const 专门用于只读变量声明，将 constexpr 专门用于编译期常量声明。

> 在 C++11 中，对 constexpr 函数要求非常严格，函数体内只能包含如下内容：空语句；`static_assert`；`typedef`；`using`；一个返回值语句（必须。不过返回值可以是逗号表达式，允许执行其它简单语句）。
> C++14 后允许其它语句出现在 constexpr 函数体内，便于使用 if、for 等语句，不需要通过复杂的模板元编程，就能实现编译期计算（且 constexpr 函数的效率要比模板高很多）。
>
> 但是，类型本身不能像值一样，在函数体内执行某些语句或运算。类型只能通过模板参数使用，通过*模板元编程*运算。
>
> C++23 前，程序理论上需要满足：对任意 constexpr 函数，至少存在一组实参取值，使得其能够在编译期调用（满足核心常量表达式要求）。否则非良构。但这并不要求编译器诊断。（有些人希望 constexpr 声明了就该编译期用到）
> C++23 起移除了该限制，即使所有调用都在运行时也可以。

C++20 起，允许 constexpr 函数进行有限制的动态内存分配和使用 std::vector/std::string（C++20 之前只有 std::array 可在编译期使用），要满足：

- constexpr 函数中不能使用 unique_ptr/shared_ptr。
- 动态内存的生命周期必须在 constexpr 函数的上下文中，即不能返回动态内存分配的指针。
- 因此，函数也不能返回 vector/string 对象。

C++20 起，虽然可以在函数中进行 try catch 或内嵌汇编，但是在常量表达式中仍不能抛出异常或执行汇编。

**constexpr if**

[constexpr if 语句](https://zh.cppreference.com/w/cpp/language/if)在编译时求值，并会舍弃条件不满足的语句（直接不编译）。
适用于模板，避免生成某些当前类型无法编译的语句。

**consteval**

（C++20 起）[consteval](https://zh.cppreference.com/w/cpp/language/consteval) 声明函数为*立即函数*，该函数的每次潜在求值的调用，都必须产生编译时常量表达式。这种调用称为立即调用 (immediate invocation)。
constexpr 不严格要求编译期执行，而 consteval 强制函数在编译时求值。

**consteval if**

（C++23 起）[consteval if 语句](https://zh.cppreference.com/w/cpp/language/if#Consteval_if)判断当前的 if 语句是否是在明显常量求值语境下求值的。
格式为：`if !(可选) consteval 复合语句1 else 复合语句2(可选)`。

可用在 constexpr 函数中，根据是否是立即求值而执行不同的逻辑。

**is_constant_evaluated**

[is_constant_evaluated](https://zh.cppreference.com/w/cpp/types/is_constant_evaluated) 检查当前函数调用是否出现在明显常量求值语境中。
注意，直接用在 static_assert 和 constexpr if 语句的条件内时，总是返回 true。

> C++17 中可以用以下方式检测某表达式是否可常量求值（见[这里](https://stackoverflow.com/questions/55288555/c-check-if-statement-can-be-evaluated-constexpr)）：
>
> ```cpp
> template <class Lambda, int=(Lambda{}(), 0)>
> constexpr bool is_consteval(Lambda) { return true; }
> constexpr bool is_consteval(...) { return false; }
> 
> if constexpr (is_consteval([]{ base::get(); }))
> 	f<base::get()>();
> else
> 	f(base::get());
> ```
>
> C++17 起 lambda 表达式可以是 constexpr 的，如果 is_consteval 实参中的 lambda 内的语句均可常量求值，那么该 lambda 才可以用作模板参数，匹配返回 true 的重载。
>
> 用 concept 也可以实现，但每次使用都需要定义一个 concept：
>
> ```cpp
> template <auto>
> struct require_constant;
> template <class T>
> concept has_constexpr_data = requires { typename require_constant<T::get()>; };
> // 如果 T::get() 可常量求值，那么可用作模板参数
> ```

**constinit (C++20)**

（C++20 起）[constinit](https://zh.cppreference.com/w/cpp/language/constinit) 修饰静态或线程局部变量的声明，说明并要求该变量是[静态初始化](https://zh.cppreference.com/w/cpp/language/initialization)，即零初始化或常量初始化（在编译时进行），而非动态初始化。
它只能通过常量表达式初始化（包括 constexpr 与 consteval 函数）。
在静态存储期对象存在依赖时，用来避免动态初始化的不确定性而导致的问题。

constinit 也可用于非初始化声明，减少防卫变量导致的开销：
当使用动态初始化时，静态和 threadlocal 变量需要一个 flag（防卫变量）来标记是否已初始化，并在每次运行时检查 flag。
但对于外部 threadlocal 变量，无法确定其初始化方式，因此必须保留 flag 和检查。但如果其声明 constinit，就可以省掉。

```cpp
extern thread_local constinit int x;
extern thread_local int y;
int f() {
    return x;
}
int g() { // 比 f() 多6条汇编
    return y;
}
```

**存储类说明符**

[存储类说明符](https://zh.cppreference.com/w/cpp/language/storage_duration)是标识符声明中的一部分，除 thread_local 可和 static/extern 一起外，只能出现一个。
与作用域一同决定标识符的存储期与链接。包括：

- 无说明符：自动存储期。如局部非静态变量。
    register 也是自动存储期，提示编译器将此对象放在寄存器，但已弃用。
- static：静态或线程存储期；内部链接。
- extern：静态或线程存储期；外部链接。
- thread_local：线程存储期。
- mutable：不影响存储期或链接，只是控制类成员的访问方式。

通过 extern 声明变量、但没有初始化器时，它仅声明而不定义变量。

```cpp
extern int a;     // 声明但不定义 a
extern int b = 1; // 定义 b
```

> 在词法分析时，C++ 也会把其它关键字当做存储类说明符：mutable、typedef。它们出现的位置与存储说明符相同，但不影响存储期和链接。

**存储期**

所有对象都具有4种存储期之一：

- 自动（automatic）存储期：生命周期为所在代码块。包括非 thread_local、static、extern 的所有局部对象。
- 静态（static）存储期：生命周期与整个程序一致，只存在一个实例。包括所有在命名空间（包含全局命名空间）作用域声明的对象（即全局对象），和带有 **static/extern** 的对象。
    如果未初始化，则被零初始化。
- 线程（thread）存储期：生命周期与线程一致，每个线程有一个该实例。包括声明了 **thread_local** 的对象。
- 动态（dynamic）存储期：生命周期由动态内存分配函数来控制。

> 注意，在非局部作用域中，static 影响的是链接，而非存储期（非局部本身就是静态存储期）；在局部作用域中，static 影响的则是存储期。
>
> 自动存储期对象不一定在栈中，也可能在寄存器等。标准没有规定 C++ 的内存模型是堆栈模型，只是规定了这些存储期。
>
> 编译单元之间的静态对象的析构顺序不可控，所以程序不应依赖静态对象的析构顺序。
> 如果一定要，可以通过 union 跳过静态对象的析构避免问题。

**链接**

链接有三种：

- 无链接：只能在它所在的作用域使用名字。
    在**块作用域声明**的下列任何名字均无链接：非 extern 变量（即使是 static）；局部类和其成员函数；其它名字。
    未指定 static, extern, 模块的名字也是无链接，这与其所在作用域无关。
- 内部链接：可在当前翻译单元中的所有作用域使用名字。
- 外部链接：能在其它翻译单元中的作用域使用名字。

> 使用 extern 并且没有初始化器的声明不是定义。
>
> inline 不是链接，所以会被 static 影响。

**静态存储期对象的初始化**

静态存储期的非局部变量的[初始化](https://zh.cppreference.com/w/cpp/language/initialization)包含两阶段：静态初始化（如果初始化表达式为常量表达式，则常量初始化；否则零初始化）；动态初始化（如果不能进行常量初始化）。

如果变量满足：它的初始化完整表达式是常量表达式（如果有初始化器则需要为常量），或它是类，且调用的构造函数和其子对象调用的构造函数都是 constexpr，则变量进行常量初始化，不进行动态初始化 (constinit)。

对于非局部静态变量，动态初始化是比 main 的第一条语句执行得 早 还是 晚（发生延迟），是实现定义，但保证：它一定早于同一翻译单元中的任何静态/线程存储期的变量和函数（包括构造函数）的首次 *基础 - ODR 使用*（只要翻译单元中 ODR 使用了任何事物，就会初始化所有在初始化或销毁中拥有副作用的非局部变量，即使程序中没有用到它们）。
局部静态变量的动态初始化，会在控制首次经过它的声明时进行。

> 下面代码会输出1：局部静态变量 a 需要进行动态初始化，这会在控制经过对应语句时进行。但在动态初始化之前，依然可以读写 a。此时会读取到它在静态初始化阶段被零初始化后的0。
>
> ```cpp
> int g() { return 1; }
> 
> void f() {
> 	switch(1) {
> 		case 0:
> 			static int a = g();	
> 		case 1:
> 			cout << a << '\n';
> 	}
> }
> ```

静态和线程存储期的对象在[程序退出时](https://zh.cppreference.com/w/cpp/utility/program/exit)进行析构，保证：所有线程局部对象的析构都早于静态对象的析构；如果线程局部或静态变量 a 的构造或动态初始化，早于线程局部或静态变量 b，则 b 的析构早于 a 的析构。
即静态和线程存储期对象的析构顺序与构造顺序相反。

**静态局部变量**

块作用域内声明的 static 或 thread_local 对象是静态局部变量。当程序首次经过其声明时，才会被初始化（这里指动态初始化。如果可以零初始化或常量初始化，则可在编译时进行）。在后续执行中，声明会被跳过。
编译器会生成代码来保证初始化仅发生一次（类似 call_once）。

**编译期取地址**

静态存储期对象可以在编译期取地址，该过程是 constexpr 的（当然编译期取到的地址不是实际地址，在程序运行前这是无法确定的。但编译器可以为其指定相对地址，或运行后建一个映射表，保证运行时能取到实际地址）。
自动存储期对象的地址在编译期是难以确定的，涉及当前栈帧位置。

因此可以用静态存储期对象，初始化 constexpr 引用或指针：

```cpp
int a;
{
	static int b;
	constexpr int& ra = a;
	constexpr int* pb = &b;

	ra = 3; // 与 const 类似，引用的常量性指绑定的对象不变，值可以改变
	*pb = 5;
    
	int c;
	// constexpr int& rc = c; // error: &c 不是常量表达式
}
```

或初始化引用类型的*模板非类型实参*：

```cpp
template <string& s> // string* 也可
struct D {
	void p() {
		cout << s << '\n';
	}
};

string s = "abc";
{
	D<s1> d; // 如果是指针则 D<&s1> d;
	d.p();
}
```

**cast**

> 转换表达式的结果是：
>
> - 如果新类型是左值引用或到函数类型的右值引用，则为左值。
> - 如果新类型是到对象类型的右值引用，则为亡值。
> - 否则（即转换到非引用类型）是纯右值。

[static_cast](https://zh.cppreference.com/w/cpp/language/static_cast)：用于良性转换 (no run-time check)，一般不会导致意外发生，风险很低。
接近旧式 C 转换（其实很不同），如普通类型转换，最常用。

[dynamic_cast](https://zh.cppreference.com/w/cpp/language/dynamic_cast)：借助 RTTI（运行时检查），用于类型安全的向下转型 (downcasting)。
具体来说，可以将基类的指针或引用，安全地转换为派生类的指针或引用。
因为基类对象的起始位置，不一定就是派生类对象的起始位置，直接类型转换会出错。dynamic 会找出某对象的内存起始位置，并在失败时。
（如果可以，dynamic_cast 最好用 static_cast 替代，避免运行时开销？为了其通用性，dynamic_cast 效率有时可能还好，有时可能会很低）

[const_cast](https://zh.cppreference.com/w/cpp/language/const_cast)：用于 const 与非 const、volatile 与非 volatile 之间的转换。
常用于去除某个引用或指针对象中的 const，以便可以调用非 const 的重载函数（但不是为了修改它。写底层是 const 的对象是 UB）。比如：非 const 成员函数 f 调`const_cast<T&>(static_cast<const A&>(*this).f())`就不用 const 与非 const 两个方法写两遍（但这被 deducing this 解决了？）。
简单来说 const_cast 是去除后加的 const，而非把原本 const 的改成非 const。

reinterpret_cast：危险的转换，这种转换仅仅是对二进制位的重新解释，不会借助已有的转换规则对数据进行调整，但是可以实现最灵活的 C++ 类型转换。
只能用于指针到指针、引用到引用、整数与指针的转换。如果想要在浮点与整数间转换，需要用引用或指针：`float f = reinterpret_cast<float&>(&i)`（注意 i 必须是32位与 float 对应）。
不具备移植性，常见用途是转化函数指针类型。可用于进行没有任何关联之间的转换，比如一个字符指针转换为一个 int 指针。
注意，`char*`指针的输出类型与其它不同，不仅输出当前值，还会一直输出char直到遇到`\0`即`0x0`。例：https://zhuanlan.zhihu.com/p/33040213。

static_cast 和隐式转换是在语言/语义层面上做转换，比如：在子类向基类 static 转换时，编译器能够理解这一行为并做出相应处理（通过一点偏移，获取基类的起始位置）。
reinterpret_cast 直接假设一个指针拥有其它类型，可以直接转换。因此用它将子类转成基类可能是错的。

例：

```cpp
struct A { // 4B
    int32_t a;
};
struct B {};
struct S: A, B {} s;
// 输出地址
p(&s); // 假设为0
p(static_cast<B*>(&s)); // 4
p(implicit_cast<B*>(&s)); // 4 代表隐式转换
p(reinterpret_cast<B*>(&s)); // 0 显然不对
p((B*)&s); // 4 类似 static_cast
```

如果代码发生了重构，S 不再继承 B，那么原本的 static_cast 和隐式转换会错误，而 reinterpret 和 C 转换仍然生效：

```cpp
struct S: A {} s;
// 输出地址
p(&s); // 0
p(static_cast<B*>(&s)); // CE
p(implicit_cast<B*>(&s)); // CE
p(reinterpret_cast<B*>(&s)); // 0
p((B*)&s); // 0
```

此时 C 转换的行为反而类似 reinterpret_cast。

**C 风格转换**

不建议使用该转换，不只是因为它不够明确，还有它过于强大（可以代表多种转换），导致非常容易出错：

[C 风格转换](https://zh.cppreference.com/w/cpp/language/explicit_cast)会按顺序尝试多种 cast，直到发现某一种转换方式合适：

1. const_cast：能够去掉或增加 const。
    对于一个`const int *`指针 cp，既可以通过`const_cast<int*>(cp)`获取 int*，也可直接通过`(int*)cp`去掉 const。
2. static_cast：与其类似。
    但是，C 转换不会在意一些访问限定符，比如允许从子类转换一个私有基类（但是实测不可）。
3. static_cast 然后 const_cast。
4. reinterpret_cast：与其相同，比如可将 float\* 转为 int\*。因此 C 转换也非常危险。
5. reinterpret_cast 然后 const_cast。

例子见上面 *cast* 的例子。

**显式类型转换**

[显式类型转换](https://zh.cppreference.com/w/cpp/language/explicit_cast)主要包括 C 风格转换 (`(T)expr`) 与*函数风格转换* (`T(expr)`)。
C 转换见上。

函数风格转型表达式包括一个简单类型说明符（单个单词的类型名，不能多单词和附带 \*、&）和括号加表达式。

- 如果是圆括号加单个表达式，则与 C 转换相同。
- 如果是圆括号加多个表达式，或是花括号初始化列表（含任意个表达式），则它是直接初始化得到的纯右值（目标类型要有对应的构造函数）。
- 如果是圆括号加 0 个表达式，则它是值初始化得到的纯右值。

> 声明变量时，允许附带额外的括号，所以`int(a)`、`int(((a)))`都是可以的。
> 但是这会与函数风格转换产生歧义。因此标准规定：如果`T(expr)`可以被视为声明，则视为声明，而非转换。

**实现其它的 cast**

> https://www.youtube.com/watch?v=SmlLdd1Q2V8

包括 implicit_cast、pun_cast、public_cast。见下。

**implicit_cast**

当能使用隐式转换时，应该避免使用 static_cast 强制转换，因为它可以调用 explicit 构造函数和 explicit 转换运算符：

```cpp
struct A {
	explicit A(int a) {}
};
void f(A a) {}

int a = 1;
f(a); // CE
f(static_cast<A>(a)); // ok，调用explicit构造
```

这可能会导致意外。应该用尽量弱但正合适的方式解决问题，而非过于强大的方式（比如 C 风格转换）(principle of least power)。

但有时隐式转换会不生效（即使完全合适），就是需要显式 static_cast。
比如：在模板函数类型推导中，子类可能需要显式转换为基类：

```cpp
template<class T>
void f(const T& b, const T& d) {}

f(base, derived); // CE
f(base, static_cast<Base&>(derived)); // ok
```

因此我们需要写一个隐式 cast，只做隐式转换会做的事情，虽然写出来它就像是一个显式转换。
这个 cast 不需要做任何事，只需要返回对应类型的原值，因为将参数传入本身就会做隐式转换（如果隐式转不了编译器也会给出错误）（是否需要加引用？）：

```cpp
template<class T>
constexpr T implicit_cast(type_identity_t<T> val) {
    return val;
}
```

[**type_identity**](https://zh.cppreference.com/w/cpp/types/type_identity)可以使一个参数不参与类型推导，它只是和推导完成后的类型 T 相同（允许传其它类型，隐式转换到 T）。
由于没有其它参数供推导，所以这种写法可以要求 implicit_cast 必须写明 T（如`implicit_cast<Base>(d)`）而不能忽略`<T>`走类型推导。
（用有限定标识指定的类型的嵌套名说明符（`::`左侧的所有内容）是*模板 - 不推导语境*，即如果参数类型中有作用域解析运算符`xx::type`，则该参数不会进行推导，比如`type_identity_t`）

> type_identity C++20 起才有，因此可以自己实现：
>
> ```cpp
> template<class T>
> struct type_identity {
>    	using type = T;
> };
> template<class T>
> using type_identity_t = typename type_identity<T>::type;
> ```

实际使用时，还要注意如果 T 可移动构造且 noexcept，则函数可以标记 noexcept。

**pun_cast / bit_cast**

> bit_cast 实现：https://github.com/ClickHouse/ClickHouse/blob/master/base/base/bit_cast.h

由于 *C++ - 严格别名规则*，将一个类型的指针强制转换（如 reinterpret_cast、C cast）到另一个不相关类型的指针是 UB（同一内存地址不能拥有两种类型的视图）。
但有时确实有这种类型双关 (type punning) 的需求。那么如何写一个不是 UB 的强制转换？

C 中能用的一个方法是联合：将两种类型放在一个 union 里（同一内存地址），写入 U 类型值，然后用 V 类型读取该值：

```cpp
template <class U, class V>
V pun_cast(const U& val) {
    union { U u; V v; };
    u = val;
    return v;
}
```

但是在 C++ 中，*union* 只能读取最后一次被写入（已激活）的成员，否则也是 UB（也是因为严格别名）（除非此成员具有标准布局）。

要避免 UB 只能保证 U, V 有不同的地址，因此可通过逐位拷贝：

```cpp
template <class U, class V>
V pun_cast(const U& val) {
    static_assert(sizeof(U) == sizeof(V) &&
                 std::is_trivially_copyable_v<U> &&
                 std::is_trivially_copyable_v<V>);
    V v;
    std::memcpy(std::addressof(v), std::addressof(val), sizeof v);
    return v;
}
```

注意需要 static_assert（或 sfinae (enable_if) 或 concepts）保证类型大小相同，且两个类型可以逐位拷贝（可平凡拷贝）。
但由于 memcpy 不是 constexpr 的，所以该函数不能是 constexpr，因此不能在编译期完成双关转换。

C++20 起，引入了 [bit_cast](https://zh.cppreference.com/w/cpp/numeric/bit_cast)，它类似 memcpy，但是允许在编译时完成转换。

```cpp
template <class U, class V>
constexpr V pun_cast(const U& val) {
    return std::bit_cast<V>(val);
}
```

所以其实也不需要写 pun_cast，直接用即可。

**public_cast**

通过它可以在类外部访问私有或保护的数据成员或函数，不会产生 UB。但这会破坏代码的封装性，影响人对程序的判断（类外可以随意更改私有变量），所以不应被使用。
原理是：在显示实例化和显式特化的声明中使用的名字，不会进行通常的访问权限检查，除非名字位于函数体、默认实参、成员声明等少数场景内。

代码见下，具体见[视频](https://www.youtube.com/watch?v=SmlLdd1Q2V8)。

```cpp
class C {
    int x{9};
} c;
// auto px = &C::x; // 非法
// int x = c.x; // 非法

// M是想访问的成员指针，Secret的名字是一个key
template <class M, class Secret>
struct public_cast {
    static inline M m{};
};

// 在val实例化时，能够将私有的成员指针C::x赋值给m
// 通过一个链式调用，让其在赋值时顺便赋给public_cast，以获取到私有的成员指针
template <auto M, class Secret>
struct access {
    static const inline auto m
        = public_cast<decltype(M), Secret>::m = M;
};

// 访问c.x需要两条语句
template struct access<&C::x, class CxSecret>;
int x = c.*public_cast<int C::*, CxSecret>::m; // 9
```

[其它方法](https://zclll.com/index.php/cpp/266.html)也能实现，但原理是一样的：因为会有导出显式实例化模板的需求，而当该模板实例化涉及私有成员时，就不得不允许忽略访问权限。

**栈展开 (stack unwinding)**

简单来说就是：函数返回或抛出异常时，每个尚未析构的自动存储期对象，会按照和构造相反的顺序进行析构。

当函数抛出异常时，函数会将当前栈内的对象析构并返回 (return)，然后沿着函数调用栈依次向上，不断析构栈对象、返回，直到遇到第一个能捕获当前异常的函数。
这种沿着调用栈不断向上，寻找异常处理块的过程，叫栈展开。

**析构函数抛出异常**

C++ 并不阻止，但析构函数不应该抛出异常，否则可能导致异常无法处理，程序退出；或导致内存泄露。

因为在遇到异常时，会发生如上的栈展开过程，这期间会析构当前栈内对象，直到找到一个能处理异常的函数。
如果在析构栈对象的过程中，析构函数又抛出了一个异常，由于 C++ 无法同时处理两个异常，就会导致程序调用`std::terminate()`结束（准确来说，如果当前有一个异常，只要新的异常能在函数内被立刻处理、不继续抛出就没事）。
此外，如果栈内有一个容器，当该容器进行析构时，会执行每个元素的析构，如果某个元素在析构时抛出了异常，容器的析构还是要继续（因为函数要退出，必须析构栈内的数据），如果又有一个元素抛出异常，也会导致程序崩溃。
所以如果一个类型的析构函数会抛出异常，该类型的容器的析构就是很危险的，连普通的数组也是。

此外，delete 操作符会先调用对象的析构函数，然后调用 operator delete 释放内存。如果析构函数抛出了异常，后续的释放内存就不会执行，导致内存泄露。

所以，应避免在析构函数中抛出异常，如：

1. 在析构函数内就将异常处理掉。
   对于实在无法处理的，可以调用`std::abort()`主动退出，避免程序在一个未知的时刻突然崩溃，减少风险。
2. 将会抛出异常的部分放在析构函数外，手动调用。

> 析构函数、资源释放函数（例如 operator delete，以及功能类似物）和兼容标准的自定义 swap 函数，都应该尽可能保证成功。不抛出异常是成功的要求之一。

**函数返回局部变量的指针**

如果局部变量分配在栈上（如`char s[] = "a";`，注意 s 不是指针），在函数返回时会释放，所以如果返回这种临时局部变量的指针，使用时就会出错。
如果局部变量在堆上（如静态局部变量，或`char *s = "a";`分配到常量区），指针返回后可以使用。

**函数内联**

内联：将被调用函数的函数体的副本，替换到调用位置处；修改代码以体现参数。
优点：消除函数调用开销：参数传递、寄存器保存；将过程间分析转化为过程内分析，便于优化。
缺点：函数体会变大，对指令缓存 (icache) 不友好；生成的二进制文件会变大（代码段变大），占用内存更多。
多数情况下是正向优化。

**代码膨胀**

> https://zhuanlan.zhihu.com/p/686296374

代码膨胀/程序膨胀/二进制膨胀：生成的二进制文件过大，超出预期（正常的大是合理的），导致程序变大、占用内存变多，可能也会导致缓存不命中（无法形成热点）。
导致代码膨胀的原因可能有几点：

- inline。

inline 与内联无关，只是允许有多个定义（内联通常无法控制，不需要考虑）。
按照标准语义，不同翻译单元的 inline 变量或函数是同一个符号，即链接时会合并不同翻译单元的同名 inline 符号，最后只会产生一个，所以不会导致二进制膨胀。

- 常规的隐式实例化。

与 inline 类似，不同翻译单元隐式实例化的相同模板实例化，会在链接时被合并，即重复代码会被去除，所以也不会有额外膨胀。
但是检查、合并模板可能会增加编译时间。*显式实例化*可以减少编译时间。

- 不同类型、但二进制代码相同的隐式实例化。

某些模板满足：即使传入的模板参数类型不同，实例化后的代码有时也是相同的。
比如：对编译器生成汇编来说，char 总是和 signed char 和 unsigned char 中的一个没区别，但是 C++ 中 char 和 (un)signed char 不是同一类型，因此会被视作不同模板，在实例化这三个模板时，会产生两份相同的代码。如果生成的模板被内联，也没有影响；但如果不能内联、且生成的模板较大，就会导致程序膨胀。

gold 链接器会在链接时合并二进制代码相同的符号，但主流的 lld 等不会。但 gold 也只能比较整个函数，无法局部合并（比如两个函数前面都相同但最后一行不同），只能靠程序员修改逻辑实现（将不同的逻辑抽象为另一个函数）。

- *异常*。

Itanium ABI 的异常实现中，在 Happy Path 下不会有额外的开销，但是会带来明显的二进制膨胀：为了避免运行时查找，就需要预先打表？因为异常会传播，所以会产生很多表。MSVC ABI 的异常虽然在 Happy Path 下也有开销，但是膨胀更小。
所以关闭异常可以减少程序大小。

此外，异常会导致函数提前返回，所以如果某个函数可能抛出异常（没有 noexcept 声明，且同一翻译单元内没有定义要调用的函数，或有定义但抛出了异常），且存在已创建的不可平凡析构的栈对象，编译器需要生成析构栈对象的汇编供抛出异常时使用。
通过添加 *noexcept* 声明、将未用到的栈对象定义移到可能抛出异常的语句之后，可能能减少异常处理代码的产生。

**inline**

实际上 [inline](https://zh.cppreference.com/w/cpp/language/inline) 的含义已经从“优先内联”变成了“允许函数和变量重复定义 / 规避 ODR”。不同编译/翻译单元可以有多个相同的 inline 函数实现，最后会只保留一个。因此可以在头文件中直接给出 inline 函数的完整定义，而不必像普通函数一样只写声明、将定义放在.cpp中。这对于 header-only 库开发很有用（多个编译单元可能同时使用某个库）。
inline 声明的函数或变量在每个翻译单元中都要拥有相同的地址、定义（包括必须都是 inline）。

> 首先要明确 include 头文件只是文本替换，因此不同翻译单元都会包含头文件中的定义，当引用同一头文件时就会出现重定义。
> inline 声明的对象是外部链接，连接器会将这些对象标记为弱符号，从而避免重定义冲突。链接器最后只会保留任意一个符号/定义，因此不同翻译单元会使用同一个 inline 对象。
>
> static 声明与匿名 namespace 等价，也可用来允许重复定义、解决编译错误，但与 inline 的原理和目的不同：static 声明的对象是内部链接，其符号不会导出，仅限于当前翻译单元可用，在每个引用该头文件的翻译单元内都会有一个该对象。它们有不同的地址、是多个符号，不同的单元使用的是不同对象（因此导入相同头文件的不同源文件，将使用不同的 static 变量！不能用于全局配置）。
> static inline 与 static 基本等价。实际上重定义的 inline 是拥有外部链接的 inline 函数/变量，因此声明 static 后就不可。
>
> 对于 const 但非 volatile 的非模板变量，如果不声明为 inline、extern 或声明于模块接口单元，则具有内部链接。

inline 并不常用，只是用于模板或 header-only lib，解决多个编译单元包含同名对象时的重复编译问题。在 C++20 有模块后就不需要了。

（C++17 起）constexpr 声明的对象包含 inline。
在类 (class, struct, union) 内定义的成员函数与友元函数是蕴函 inline 的，类外定义不会（包括 .cpp 中的）。
模板函数是 inline 的（因为需要在 .h 定义）。

>inline 函数必须要在 .h 中给出定义，这会增加编译时间，在修改函数时导致更多文件重新编译。（但通常来说影响不大？）
>
>inline 还会用来定义 *内联命名空间*。

>默认的函数是 extern 的，可能被其它编译单元调用，编译器必须生成符号。但如果函数被标记为 inline 或 static，则编译器可能不会生成它的符号（比如：没有对它取地址等），从而更可能内联它。所以 inline 和  static 还是有隐式、不确定的提示内联作用。
>原因：如果某个翻译单元 odr 使用了某个 inline 函数/变量，则当前翻译单元必须有该 inline 函数/变量的定义，否则违反 *ODR*。所以 inline 函数/变量的定义不需要暴露给其它翻译单元，如果其它翻译单元要用，那么它们自己也需要定义。
>static 不能被其它单元调用。
>
>如果想要内联某个函数，需要将函数的定义放在头文件中，以允许编译器在调用时就看到它的实现，这样才能内联（为了避免 ODR 还要加 inline）。
>开启链接时优化 (LTO) 可以在链接时跨编译单元内联，就不需要这样了。
>
>C 的 inline 含义与 C++ 不同，代表的就是强制内联，如 gcc 的`__atrribute__((always_inline))`。（但 always_inline 并不保证一定内联，可能被忽略，会给警告。noinline 和 [clang 的](https://clang.llvm.org/docs/AttributeReference.html#always-inline-force-inline)也是）
>

注意，inline 全局对象在 DLL 中可能并不是唯一的，见 *设计模式 - 单例是唯一的吗*。

C++17 前避免变量违反 ODR 的方式（这和直接 static 有什么不同？）：

```cpp
template<class T>
struct __static_const {
	static constexpr T value{};
};
// 定义
template<class T>
constexpr T __static_const<T>::value;
// A 类型全局变量
constexpr auto const &a = __static_const<A>::value;
```

**匿名命名空间**

*unnamed namespace / anonymous namespace* 与 static 的一种用法类似，用于限制定义仅在当前单元可见，以允许 ODR。
使用它比 static 更好：匿名命名空间的用途更多，可以定义类型，而不只是函数或变量；static 有过多的其它含义；namespace 直观、风格统一。

当函数 f 未声明 static 或不在匿名空间时，就可能在链接时被其它翻译单元使用，即使 f 不在头文件中：如果某个翻译单元内声明了 f 但未定义，则会在链接时查找，就可以找到其它 TU 的非匿名 f 定义。

不应在头文件中使用匿名命名空间，因为它们根本不匿名（include 会进行文本替换）。如果要写 header-only，或不得不在头文件中写某些定义，放在 detail、internal 之类的子命名空间里。可见 *规则 - SF.21*。

**\_\_builtin\_popcount 原理**

`__builtin_popcount()`是一个内建函数，可以理解为一个特殊的函数。编译器看到这个函数之后不会按照普通的函数来处理，而是由编译器自己来决定这个函数应该生成什么代码。之所以要使用内建函数，主要是有的函数只用C代码很难实现或者效率不够高，不同平台的实现方式也可能不一样，就让编译器来实现。交给编译器就可以针对特定的硬件指令集优化，比如popcount函数，在x86平台上编译器就能直接用`POPCNT`这条指令而不是使用C语言位运算做。
其他很多builtin函数原理都一样，是gcc内建的函数，一般没有移植性，使用时要注意。
C++里类似函数为`std::popcount()`。

**__builtin_expect**

`long __builtin_expect (long exp, long c)`。
给编译器提供分支预测信息：exp 是一个 bool 表达式，为实际返回值；c 是表达式的期望取值（0 或 1）。

在 if-else 中，编译器会根据`__builtin_expect`的值，决定哪条分支的汇编代码紧跟在 if 后面，可提高 icache 的命中率。

**size_t**

std::size\_t 是无符号数，表示理论上一个对象的最大大小，常用做容量和数组索引。sizeof 的返回值就是它。
size\_t 在 32 位机器上是 32 位的 unsigned int，在 64 位机器上则是 64 位的 unsigned long (int)，因为理论上一个数组的大小可以超过 2^{32}，虽然并没有人这么做。
使用 size\_t 可以增加程序的可移植性。但要注意无符号数为 0 时 -1 的问题。

ssize\_t 是有符号的 size\_t，即 int 或 long (int)。
intptr\_t 与 ssize\_t 相同，提供了一种可移植且安全的方法定义指针。

**数据模型**

每个实现关于基础类型的大小所做的选择被统称为[数据模型](https://zh.cppreference.com/w/cpp/language/types)。
因此，基础类型的大小是 implementation-defined 的，标准只规定了一部分，比如 int 至少是 16 位的。
但可以确定 5 类标准有符号整型满足：char <= short int <= int <= long int <= long long int。

64 位系统使用的数据模型有三类：LP64, LLP64, ILP64，只是在 int, long 两个整数类型上有差异：
LLP64 指只有 long long 和 指针是64位的，LP64 指 **long** 和 指针是64位的（自然包括更大的 long long），ILP64 指 **int**, long, long long 和指针都是64位的。
所有64位的类 Unix 平台均使用 LP64 数据模型，而64位 Windows 使用 LLP64 数据模型，两者在 long 上有区别。

long (int) 是至少 32 位的整数，由上，在 windows 下一般是 32 位，在 unix 下则是 64 位。
long long (int) 是至少 64 位的整数。

C++20 前标准还允许任意的有符号整数表示（如反码原码），C++20 起才规定必须使用补码表示。

**extern**

见 *OS - extern*。

**字符类型**

> https://zhuanlan.zhihu.com/p/680666214

字符包括7种：char、(un)signed char、char8_t (C++20) 称为 *窄字符类型*；char16_t、char32_t、wchar_t 称为 *宽字符类型*。

> (un)signed char 不属于字符类型，而是属于 无/有符号整数类型。(u)int8_t 就是 (un)signed char 的别名（因此注意流输出 (u)int8_t 时，实际输出的是个字符！）。
> 与整数不同，char 和 (un)signed char 不是同一类型。
> 标准没有规定 char 是否有符号。可通过编译选项`-f(un)signed-char`修改。

标准没有规定宽字符 wchar_t 是多长，只是不短于 char，所以可移植性很差。

char8_t 代表使用 UTF-8 作为执行字符集，char16/32_t 分别代表 UTF-16/32（即 16/32 位 unicode 字符）。

> MSVC 下 wchar_t 可能不是独立类型（即可能是 ushort 的别名），取决于编译选项 /Zc:wchar_t。gcc 下它是独立类型。

C++ 的编码可分为两种：

- 源码字符集：源码文件用什么编码保存。
- 执行字符集：可执行程序内保存的字符串是什么编码。

上述类型影响的都是执行字符集，源码字符集则始终没有规定。
gcc 可通过`-finput-charset=charset`、`-fexec-charset=charset`分别指定。
MSVC 也有`/source-charset:utf-8`、`/execution-charset:utf-8`。

> 普通字符字面量的类型是 char，它的值等于该字符在执行字符集中的表示，而程序使用的执行字符集是实现定义的（只是通常是 UTF-8）。
> 但是，标准保证空字符的值是0，并且数字字符`'0'`之后的每个十进制数字字符的值都比上一个数字字符的值大1（不管是在源码字符集还是执行字符集）。因此虽然`'3'`的值是实现定义，但`'3'-'2'`一定是1。

**整数字面量**

[整数字面量](https://zh.cppreference.com/w/cpp/language/integer_literal)的最小大小就是 int，并且会根据值大小选择最合适的类型，因此不会出现越界（只要在 ull 内）。
通过加 u/U/l/L/ll/LL 后缀可以让它至少有 unsigned/long/long long 修饰。

没有负数字面量。-xxx 实际是对字面量 xxx 调用一元减运算符。

**字符字面量**

[字符字面量](https://zh.cppreference.com/w/cpp/language/character_literal)的表示与[字符串字面量](https://zh.cppreference.com/w/cpp/language/string_literal)类似，包括：

- 'a'：普通字符字面量。类型为 char。
- u8'a'：UTF-8 字符。C++20 前类型为 char，20 起为 char8_t。
- u'猫'：UTF-16 字符。类型为 char16_t。
- U'猫'：UTF-32 字符。类型为 char32_t。
- L'猫'：宽字符。类型为 wchar_t。
- 'abc'：多字符字面量。类型为 int，值实现定义。

除了多字符外，字符串字面量的前缀也类似，分别对应对应类型的数组：const char/char(20 前), char8_t(20 后)/char16_t/char32_t/wchar_t [N]。

> 内建一元算术加/减运算符 会对操作数进行整数提升，因此对于字符 c，+c, -c 的结果类型均为 int。
> 对字符字面量同样生效，+'A' 的类型也是 int。

**字符串字面量**

程序中字符串字面量的生命周期伴随整个程序，不需要也不能去释放它。比如`const char *s = "abc"; delete[] s;`是错的。`const char s[] = "abc";`是栈上对象，也不应该 delete。
只有程序 new 出来的指针才能 delete。
所以如果要将字符串字面量（const char *）传给一个类，类获得指针后要 new 一个空间拷贝过来，不直接用这个指针；如果直接用那不能在析构时 delete。类内保存一个 string 而非 char * 指针更安全，不用考虑析构问题。

注意，通过字符串字面量隐式构造的 string 只是临时量。

> 注意，字符串字面量是一个左值，而其它字面量（字符、数字、bool...）是纯右值。
> 因此`decltype("hello")`是`const char(&)[6]`；而`decltype(u8'A'/1/true)`是不带引用的 char8_t/int/bool。

**成员指针**

[成员指针](https://zh.cppreference.com/w/cpp/language/pointer)包括 *数据成员指针* 和 *函数成员指针*/*成员函数指针*，指向类的某个成员。前者大小为 8B，后者大小为 16B（原因见下）。
使用成员指针时，也必须和该类的实例一起使用。
静态数据和函数成员不与类关联，自然也不需要什么成员指针。

**函数成员指针**语法：`返回值 (类名::* 函数指针名)(参数列表)`，通过`(对象名.*函数指针名)(参数列表)`或`(对象指针->*函数指针名)(参数列表)`调用。
与普通*函数指针*相比，就是在 \* 前多了类名和作用域限定符::。
例：

```cpp
struct X {
	void f() { cout << "f()\n"; }
	void f(int x) { cout << x << '\n'; }
} x;

// #1 p是一个成员函数指针（函数指针比较难看）
void (X::*p)()  = &X::f;
(x.*p)();

// #2 参数p是一个成员函数指针。可以动态决定访问类的哪个字段
void g(void (X::*p)(), X& x) {
	(x.*p)();
    // (x->*p)(); // 如果x是指针
}
g(&X::f, x);

// #3 通过参数类型，可决定选择哪个重载，与普通函数指针一样
void (X::*p2)(int)  = &X::f;
(x.*p2)(1);

// #4 传入bind时，通过类型转换决定所选重载
auto func = std::bind(static_cast<void(X::*)(int)>(&X::f), &x, 3);
func();

// 赋值给 function 时，需要有 (const) ClassName& 参数
Node node{1};
Function<int (Node&, int)> fp = &Node::f; // 通过Node&实例调用（也可以是const Node&）
cout << fp(node, 2) << '\n'; // 1
```

**数据成员指针**语法：`变量类型 类名::* 成员指针名`。
例：

```cpp
struct X {
	int v{1};
} x;

// #1 p是数据成员指针
int X::*p = &X::v;
cout << x.*p << '\n'; // 1
int& t = x.*p;
t = 2;
cout << x.*p << '\n'; // 2

// #2 参数p是数据成员指针
void f(int X::*p, X* x) {
	(x->*p) = 3;
}
f(&X::v, &x);
```

`.*`和`->*`都是[成员访问运算符](https://zh.cppreference.com/w/cpp/language/operator_member_access)，分别表示对象/指针的成员指针。后者可重载。

一般搭配某些函数使用，比如[invoke](https://zh.cppreference.com/w/cpp/utility/functional/invoke)：

```cpp
struct X {
	int v{1};
	void f() {
		cout << "f()\n";
	}
} x;

// 绑定数据成员，则返回引用
int& i = std::invoke(&X::v, &x);
i = 2;
cout << x.v << '\n';

// 绑定函数成员，则直接调用，返回值与调用的函数一致？
std::invoke(&X::f, &x);
```

> 标准没有规定成员指针如何实现，只规定了其行为，因此其实现（可以看[这里](https://zhuanlan.zhihu.com/p/659510753)）是一个 implementation-defined 行为（可能与编译器、平台都有关）。
> 对 gcc 和多数平台，数据成员指针 和 虚函数成员指针 实际是一个偏移量，代表该成员在类中的位置，不像普通指针一样指向实际的内存地址。
> 而 非虚函数成员指针 则是指向函数所在的内存地址（测试方式见[这里](https://zhuanlan.zhihu.com/p/584267190)）。
>
> **为什么成员函数指针大小为 16B？**
> 在调用成员函数时，需要传入当前对象的地址 this 以能访问成员，但这在多继承时有点不一样：设 C 继承了 A, B，当 C 对象调用 A 方法时，A 使用的 this 实际是 C 对象的地址 + A 类子对象在 C 中的偏移；B 使用的 this 同理，实际是 A 使用的 this + sizeof(A)。因此在调用父类方法时，需要给 this 加一个偏移量才可调用。
> 此时 C 的成员函数指针既可能指向 A 的方法，也可能指向 B 的方法，但它们使用的 this 不同，因此为了能区分，只能在成员函数指针中保存实际的 this 相对于当前 this 的偏移量。

指向类 C 的非静态数据成员 m 的成员指针，可以用`&C::m`进行初始化。但在 C 的成员函数里面使用`&C::m`会出现二义性：它既可以代表对 m 取地址`&this->m`，也可以代表成员指针。
因此标准规定，`&C::m`表示成员指针，`&(C::m)`或者`&m`表示对成员 m 取地址。
指向类 C 的非静态函数成员 f 的成员指针，可以用`&C::f`进行初始化。由于不能给非静态成员函数取地址，所以`&(C::f)`和`&f`也都代表成员指针。

基类的成员指针，可以隐式转换为派生类的数据成员指针，对函数、数据都有效（前提是不是虚继承，没有虚继承表；但是 MSVC 例外）。
如：如果`int Base::* bp = &Base::m`，则可`int Derived::* dp = bp;`。

**C 中的 tag**

> https://www.cnblogs.com/sirlipeng/p/4538996.html

C 将 tag (enum, struct, union) 视为二等公民，也就是不那么重要，甚至同名定义与标识符不会冲突。但使用前必须加详细类型说明符，如：使用 Node 结构体类型前要加 struct`struct Node node;`。

**using**

[using](https://zh.cppreference.com/w/cpp/keyword/using) 有如下功能：

- 命名空间的 using 声明：将另一命名空间的成员引入到当前命名空间或块作用域中。
- 类成员的 using 声明：可将基类成员引入到派生类的定义中（可以改变私有或保护变量（或私有或保护继承的变量）的访问级别：在 public 下 using 就会将它作为派生类中的公开成员）。
- 类型别名与别名模板声明：见下 *C++ - 类型别名*。
- 枚举项的 using enum 声明（C++20 起）。

注意 using 不能引入基类的析构函数、不能引入模板的特化。

**using 声明**

将别处定义的名字引入到此 using 声明所出现的声明区中。包含多种情况。

C++17 起，单个 using 语句可以定义多个别名：

```cpp
using std::mutex, std::lock_guard;
```

这也允许 using 进行形参包展开：

```cpp
template<typename... Ts>
struct Overloader : Ts... {
    using Ts::operator()...; // 从每个基类暴露 operator()
};
// C++17 推导指引，20 起不再需要
template <typename... T>
Overloader(T...) -> Overloader<T...>;

auto o = Overloader{ [] (auto const& a) {std::cout << a;},
	[] (float f) {std::cout << std::setprecision(3) << f;} };
```

**类型别名 (alias)**

using 和 typedef 都是对原有类型起别名，不会创建新的类型。
但 using 不仅有 typedef 的各功能，还有其它优势（具体见[这里](https://c.biancheng.net/view/3730.html)和[EMCpp](https://cntransgroup.github.io/EffectiveModernCppChinese/3.MovingToModernCpp/item9.html)）：

- 别名声明可以被模板化，称为别名模板 (alias templates)，不像 typedef 需要被嵌套进一个模板类（但不能偏特化）。
    C++14 的各种 ..._t 就是用 using 定义，这在 C++11 就能实现。

```cpp
template<class T>
using remove_reference_t = typename remove_reference<T>::type;

template<typename T>
using MyAllocList = list<T, MyAlloc<T>>;
// 使用：MyAllocList<T> list;

// typedef只能直接指定具体的类型
typedef unique_ptr<unordered_map<string, string>> UPtrMapSS;
// 或在类内部定义依赖类型
template<typename T>
struct MyAllocList {
    typedef list<T, MyAlloc<T>> type;
};
// 使用：typename MyAllocList<T>::type list;
```

- 不需要使用 typename 来标识 dependent type。
    通过 typedef 定义的、包含模板参数的类型名属于依赖类型？因为它依赖于 T，在使用该类型前需要加 typename（C++20 前）。但用 using 定义的类型不需要。
- 由于后面立即跟随新标识符（类似赋值），所以有时会更清晰易读。

```cpp
// 函数指针类型
typedef void (*func_p)(int, int);
using func_p = void (*)(int, int);
func_p f; // 函数指针定义

// 函数类型
using func_t =  int ();
func_t f; // 函数声明
```

定义函数类型的别名后（注意这不是函数指针），可以通过该别名声明一个对应类型的函数或成员函数，但不能同时给出定义。

**命名空间**

[命名空间 (namespace)](https://zh.cppreference.com/w/cpp/language/namespace) 用于避免命名冲突。

namespace 可定义[命名空间别名](https://zh.cppreference.com/w/cpp/language/namespace_alias)，比如：

```cpp
namespace std {
 namespace views = ranges::views;
}
```

C++17 起，允许简化嵌套命名空间的定义：`namespace A::B::C { ... }`等价于`namespace A { namespace B { namespace C { ... } } }`。

**内联命名空间**

namespace 前可以加 inline，以定义内联命名空间。
TODO

**异常安全 (exception safety)**

> http://exceptionsafecode.com/

[异常安全](https://zh.cppreference.com/w/cpp/language/exceptions)是指程序在发生异常或错误时，是否仍能保持正确工作的状态（这里异常与错误等同）。
通常异常安全可以分为四个等级：

1. 保证不抛出异常 (no except)：此时自然不存在异常带来的错误。
2. 强异常安全保证 (strong guarantee)：如果操作发生异常，则它不会产生任何副作用，系统保持这个操作前的一切状态。
    比如 std::vector 等容器提供强异常安全保证。
3. 基本异常安全保证 (basic guarantee)：即使发生异常，程序也处于合法状态（但原值可能改变），不会发生资源泄露。
4. 无异常安全保证 (no guarantee)：如果发生异常，程序可能不会处于有效的状态。
    比如：发生异常前动态申请了内存或文件、异常处理后未释放，就产生了资源泄露；修改某个对象，改了一半抛出了异常，就产生了值的错误等。

程序中想要保证强异常安全是非常困难的，但如果使用异常，应尽可能做到基本异常安全。RAII 有助于实现这一点。

异常或错误处理 就是在问题发生时，恢复程序的状态、报告问题、可能还要处理泄露的资源（如果 RAII 则不需要）。

> 正常情况下，对象或系统应该满足某个一致性约束，称为*不变式 (invariant)*（在 go 为什么不支持*可重入锁*中也出现过）。比如：vector 对象要保证 data 指向的空间大小为 capacity，元素保存在 data 中。
> 一个操作或函数可能会暂时违反 invariant，并在正常完成时恢复。但是如果在操作的过程中出现了异常或说错误，对象的 invariant 应该怎么样？异常安全描述的就是错误发生后对象的 invariant，即对象是否可用：
>
> 1. 强异常安全：invariant 仍成立，且状态与调用之前完全相同，即没有产生任何效果。对象可继续使用。
> 2. 基本异常安全：invariant 仍成立，但不能知道它具体的状态。因此对象不能再使用，只能恢复成初始状态或销毁。
> 3. 无异常安全：invariant 不再成立。如果不做处理，可能出现资源泄露。

**异常**

C++ 中的[异常](https://zh.cppreference.com/w/cpp/language/exceptions)可以是任意类型（如 throw new int(5)），没有 Exception 等基类限制。

错误检查与处理有两种方式：抛异常；操作返回错误码，使用前检查。
因为异常有额外开销，一般不使用异常，直接用错误码即可。当错误比较罕见、且其它机制不便时，可以用异常。（TODO，看 core guideline）
异常对象和错误码都可以附带一些其它信息，或继承形成层次结构，没有本质区别。
也可以用 *C++ - expected*（C++23）？

> 如果构造函数中存在错误，只能通过异常或传参来报告错误。所以有时会使用两段初始化：构造后再调用 init 等函数初始化。
>
> 早期有[动态异常说明](https://zh.cppreference.com/w/cpp/language/except_spec) (dynamic exception specification) 用来限制函数能够抛出异常的种类（通过动态异常说明`throw(类型列表)`），现在已经废除。它并不强制要求列出所有可能抛出的类型，如果抛出了一个未列出的异常，则会在运行时调用`std::unexpected`来处理该异常。
> 废除的原因：
>
> 1. 它不是强制性的，抛出的类型依然不确定，所以无法避免在堆上分配内存。
> 2. 它要在运行时动态判断抛出的异常是否在列表中，可能带来额外开销。
> 3. C++ 的异常是非检查型异常/运行时异常 (Unchecked Exception/Runtime Exception)，catch 时对异常的类型匹配会通过 RTTI，不取决于该异常说明，所以它并没有什么用。
> 4. 可维护性差：异常说明有传播性，如果底层函数新加了一个异常，就需要在上层全部添加该异常说明直到异常 handler，否则程序会在异常不匹配时直接调用 unexpected，即使上层有能处理该异常的 handler 也会不去处理。
>
> 有一个[提案](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3166r0.html)对原本的异常说明做了改进：强制要求函数只能抛出列出的异常，否则会编译错误；为了避免传播，引入`throw(auto)`允许函数自动计算可能抛出的异常类型。
> 但大概率不会使用。见[这里](https://www.zhihu.com/question/653025897/answer/3475070926)。

`-fno-exceptions`会禁止异常/假设所有函数都不会抛出异常。但这不是标准选项，只是编译器提供的扩展，因此效果可能不同。
gcc 会禁止代码中程序 try、catch、throw 关键字，如果使用会编译失败；但不会影响标准库，如果标准库抛出异常则会无法捕获、直接 terminate。

**异常的开销**

异常不是 zero overhead 的：主流实现中（Itanium ABI、MSVC x64），在 happy path 下（即不会抛出异常的情况下）使用异常与错误码几乎没有性能区别，在各种错误处理机制中性能前列；但在 bad path 下（即异常发生时）异常会比错误码慢很多。
因此当错误出现频率很低、不将异常用于控制流或高频率事件时，可以使用异常，省掉每次对错误码的检查。

但 [MSVC x86 (32位) 是例外](https://www.zhihu.com/question/651439531/answer/3452987714)，它在遇到每个 try 块时都会动态调整异常处理程序，并保存一些状态，所以即使是在 happy path 上也会有额外开销。

**异常的原理/实现**

> 异常的原理：https://zhuanlan.zhihu.com/p/684409834
> 不同实现的异常处理可能不同。
> Itanium ABI 在抛出异常时需要：申请堆内存，存放异常对象；查找对应的 Exception Handler，可能需要频繁比较 RTTI 信息；回溯并释放栈对象，可能需要频繁查找`.eh_frame`段。
>
> 实现异常的考虑：https://zclll.com/index.php/cpp/tr18015exception.html

主流实现中，会在编译期生成一张表，维护可能抛出异常的代码与异常处理程序之间的映射；在运行时发生异常时，会通过 RTTI 和查表选择合适的异常处理程序。因此不发生异常时没有额外开销。

当发生异常时，开销主要有三方面：

1. RTTI：将抛出的异常类型与 catch 中的类型进行匹配。因为允许多态异常（父类 catch 可以处理子类异常）且异常继承层级通常很深，所以需要 RTTI。
2. 潜在的动态内存分配：不能确定抛出的异常类型，所以只能在堆上分配。
3. 访问映射表时的 cache 不命中。

因为异常很少发生，所以 3. cache 不命中难以避免，但 1.2 可以通过 *herbception* 异常实现方案优化，即要求抛出一个固定类型 error 对象。

**error_code**

[std::error_code](https://zh.cppreference.com/w/cpp/error/error_code) 是一种依赖于平台的错误码实现，它存储一个来自 os 或其它接口的 int 错误码值，和一个指向 [error_category](https://zh.cppreference.com/w/cpp/error/error_category) 对象的指针。
错误码是一个普通的整数，error_category（称为 domain）给出了错误码与错误原因的映射，并可以进一步定义不同 domain 之间的错误码是否等价 (operator ==) 以及如何在不同 domain 之间转换错误码。
默认提供的 error_category 可能是依赖平台的。

当用户需要自定义新的 error_code 时，只需要自定义错误码，添加一个 error_category 作为 domain，在内部实现从错误码到错误消息的转换，选择性地实现跨 domain 比较错误码和转换错误码功能。
在返回错误码时，需要用错误码和对应的 domain 对象构建一个 error_code 对象，并在之后使用 bool 检查它。

```cpp
#include <system_error>

constexpr int MY_ERR_SUCCESS = 0;
constexpr int MY_ERR_1 = 1;
constexpr int MY_ERR_2 = 2;
	
class my_category : public std::error_category {
public:
	static const my_category& singleton() noexcept { // 使用单例
		static const my_category cat{};
		return cat;
	}

	const char* name() const noexcept override { return "my category"; } // 错误类别名称

	std::string message(int condition) const override { // 指定错误码的解释性字符串
		switch (condition) {
			case MY_ERR_SUCCESS: return "Success";
			case MY_ERR_1: return "error code 1";
			case MY_ERR_2: return "error code 2";
			default: return "unknown error code";
		}
	}
	
private:
	my_category() noexcept = default;
};	// class my_category

std::error_code foo() {
	if (!x) {
		return std::error_code{ MY_ERR_1, my_category::singleton() };
	}
	if (!y) {
		return std::error_code{ MY_ERR_2, my_category::singleton() };
	}
	return std::error_code{ MY_ERR_SUCCESS, my_category::singleton() };
}

int main() {
	auto ec = foo();
	if (ec) {
		std::cerr << "Error: " << ec.value() << ": " << ec.message() << "\n";
		return 1;
	}
}
```

**herbception**

> https://www.zhihu.com/question/581896340/answer/2873474245

herbception 是[某提案](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1028r3.pdf) 提出的一种异常实现方式，提出将原本的可抛出任意异常类型，替换为只能按值抛出 std::error 类型的异常对象。
error 就是一个与 error_code 类似的对象，包含错误码和一个 domain。

与目前的异常相比，它不需要动态内存分配（异常是大小确定的 error 对象）和 RTTI（只需要比较内部错误码）。

**函数 try 块**

[function try block](https://zh.cppreference.com/w/cpp/language/function-try-block) 是一种函数体，它把整个函数体变成了一个 try catch 块。

```cpp
struct S {
    string m;
 
    S(const string& str, int idx)
    try : m(str, idx) { // 如果是构造函数，try 后可选初始化列表
        cout << "构造完成，m = " << m << '\n';
    }
    catch (const exception& e) {
        cout << "失败：" << e.what() << '\n';
    } // 此处构造函数可能会 throw
};
```

主要目的是应对从构造函数中的成员初始化器列表抛出的异常，进行记录并重抛、或修改异常对象并重抛、或抛出一个不同的异常、或终止程序。析构函数或常规函数很少用到。

**noexcept**

[noexcept](https://zh.cppreference.com/w/cpp/keyword/noexcept) 有两种含义：

- 说明符：`noexcept`或`noexcept(表达式)`（前者等价于 noexcept(true)）。
    如果一个函数没有 noexcept 说明，或是其 noexcept 表达式可能求值为 false，就可能抛出异常。
- 表达式：`noexcept(表达式)`。
    可用于编译时检查，如果表达式不会抛出任何异常，则返回 true。表达式是不求值操作数，可用于模板。

函数在不加任何说明符时，可以抛出任何异常。如果加了 noexcept，则（在表达式成立时）不能在运行时抛出任何异常，否则程序会直接终止（调 terminate）（noexcept 不是编译时检查：编译器只会检查当前函数内是否有异常，不会管调用的其它函数是否抛异常）。

noexcept 的意义：

- 给 noexcept 运算符提供信息。
    比如 vector 等有强异常安全保证的 STL 容器，在进行扩容等移动元素的操作时，如果移动构造函数不是 noexcept，会使用复制构造（除非复制构造不可使用。此时无法保证强异常安全，因为移动后难以恢复原状态；并且将其它元素移动回去的时候，还可能二次抛异常）。这种情况下移动构造不加 noexcept 等于白写（原理见[这里](https://zhuanlan.zhihu.com/p/222167649)。可以测试）。
    强异常安全指如果一个操作发生异常，它也不会产生任何副作用，系统保持这个操作前的一切状态。容器提供强异常安全保证。
- 在没有加 noexcept 声明，且同一翻译单元内没有定义要调用的函数，且存在已创建的不可平凡析构的栈对象时，需要假定该函数会抛出异常、能够中途返回，因此会生成调用栈对象析构函数的汇编供抛出异常时使用。声明为 noexcept 可以不必生成这部分代码。例子见[这里](https://www.zhihu.com/question/496351156)。

但是：

- 由于 noexcept 不是编译检查，而是在运行时直接终止，所以过早给复杂的代码加 noexcept 可能不合适：noexcept 一旦添加，去掉就会很难。
    比如：设 B 是 noexcept，A 调用 B，如果 A 本身不抛异常，由于 B 不抛异常，所以可能也给 A 加 noexcept；如果 B 修改后去掉了 noexcept，但不知道 A 的引用、不修改 A，就可能导致程序直接终止。
- 虽然 noexcept 函数的调用方可以少产生一些代码，但当函数定义可见时，没有 noexcept 一般也能识别；noexcept 还可能要求函数加上`try...catch`逻辑，导致额外代码或阻止优化。所以其带来的优化很有限。

因此一般情况下，**只需要给移动构造、移动赋值、swap 添加 noexcept 声明**（swap 可能会被用作移动）。
leaf function（不会调用其它函数的函数，比如：获取类成员变量、简单计算）也可以加。
对其它情况，确定的情况可以加，不加也没事，不会带来多少优化，不需要太在意。

> 如果没有 noexcept 声明，析构函数会自动 noexcept（如果需要，要用 noexcept(false) 声明其会抛出异常）。
> 默认生成的移动构造是 noexcept 的。
>
> （C++17 起）与返回类型相似，异常说明是函数类型的一部分，但不是函数签名的一部分，因此只有异常说明不同的函数不能重载。

**不求值操作数**

以下操作数是[*不求值操作数*](https://zh.cppreference.com/w/cpp/language/expressions)，它们不会被求值：

- typeid 的操作数（且不是多态类类型的泛左值）
- sizeof、noexcept、decltype 的操作数。
- concept、requires 子句、requires 表达式中的约束表达式。

除了不求值操作数表达式和其子表达式外，其它表达式都*潜在求值*。

**作用域**

[作用域](https://zh.cppreference.com/w/cpp/language/scope)有多种：

- 每个程序都有一个*全局作用域*，包含整个程序。
- if、switch、循环、异常处理等语句会引入一个包含该语句的*块作用域*。函数体（包括 lambda）也会引入块作用域。
- 每个命名空间定义都会引入一个*命名空间作用域*。在命名空间外进行命名空间内对象的定义，也属于该作用域内。
- 每个类的声明会引入一个*类作用域*。在类外进行类内对象的定义，也属于该作用域内。
- 每个枚举的声明会引入一个*枚举作用域*。
- 每个形参声明都会引入包含该形参的*函数形参作用域*，它从形参声明的位置开始，在函数的末尾结束。作用就是供后续的形参声明和函数体使用该形参。
- 每个模板类型的模板形参会引入一个*模板形参作用域*。

extern "C" 的 {} 不会引入作用域。

**extern "C" / 语言链接**

> https://zhuanlan.zhihu.com/p/123269132

所有函数 和 具有外部链接（即能被其它翻译单元使用）的变量和函数，具有语言链接的性质。语言链接是函数或变量类型的一部分。
具有某种语言链接，意思是它满足与某种语言编写的模块进行链接的所有要求（即它可以与这种语言编写的模块进行链接。要求包括调用约定、命名重整等，见 *基础 - ABI, name mangling*）。这使得不同语言编写的翻译单元可以互相链接。

[extern](https://zh.cppreference.com/w/cpp/language/language_linkage) 后可使用字符串字面量声明语言链接。标准包括两种语言链接："C++"（默认）、"C"。
后面可以加大括号，来声明一系列函数。

因此，extern "C" 表示该函数或变量 满足要与 C 程序进行链接的所有要求，它可以与 C 编写的模块进行链接。
因此 C 单元可以调用 C++ 定义的 extern "C" 函数/变量，或链接这些 C++ 库。

> 最基本的要求为：不会进行 name mangling（但不同编译器生成的结果仍然可能不同）。因此这样的函数也无法重载（否则 C 也没法用）。
> 如：`extern "C" void func(int, int)`，C 会将函数名编译为`_func`，C++ 可能会编译为`_Z4funcii`。
>
> C 没有 namespace，所以编译产生的符号也不会带 namespace，所以不同 namespace 声明的同名 extern "C" 变量实际上是同一个变量。

通过 extern "C"，可以让 C 直接 include C++ 程序所使用的头文件，避免再写一遍。
但要注意 C 中没有 extern 的用法，只在 cpp 里有，因此这种头文件的接口函数要定义为：

```cpp
#ifdef __cplusplus
extern "C" int f(int);
#else
int f(int);
#endif

// -- 或 --
#ifdef __cplusplus
extern "C" {
#endif

int f(int); // ...

#ifdef __cplusplus
}
#endif
```

注意，直接包含在语言链接中的声明（即不包含在 { } 内），被视为它含有*存储类说明符*中的 extern，以此作为声明的名字的链接以及决定它是否是定义。
使用 extern 并且没有初始化器的声明不是定义。

```cpp
// 均为静态存储期
extern "C" int x; // 声明不定义。外部链接
// 与 extern "C" { extern int x; } 等价

extern "C" int x = 0; // 声明并定义。外部链接
// 与 extern "C" { extern int x = 0; } 等价

extern "C" { int x; } // 声明并定义。无链接（该花括号不会建立作用域）
```

**do while (0)**

`do ... while (false)`有两个好处：类似简单的函数，可通过 break 跳出代码块，代替 goto；在宏定义中包含代码，可以在后面安全地加分号。

`[]{...}()`是它的一个替代，并且能像函数一样返回值。只是没法直接 return 跳出当前函数。

**伪析构函数**

类型 T [*可析构 (Destructible)*](https://zh.cppreference.com/w/cpp/named_req/Destructible)，指类型 T 的表达式 u 满足`u.~T()`合法，且会回收 u 所拥有的资源、不抛出异常。

为了在模板中使用方便、不用检查类型 T 是否有析构函数，所有标量类型都满足可析构，但数组类型和引用类型不满足。
因此在模板中使用`x.~T()`对于 int 等标量类型是合法的，尽管 int 没有析构函数，且直接调用`x.~int()`并不合法。

```cpp
template <typename T>
void f(T* p) {
    p->~T();
}
int i = 1;
f(&i); // ok
// i.~int(); // error

template<typename T>
concept is_destructible = requires(T v) { v.~T(); };

struct X {};

cout << is_destructible<X> << '\n'; // true
cout << is_destructible<int> << '\n'; // true
```

[对于`E.~T`](https://zh.cppreference.com/w/cpp/language/operator_member_access)，当 E 是标量类型、T 是与 E 表达式同类型的类型名或 decltype 时，其只能用做函数调用运算符的左操作数（即`func(args...)`的 func），所构成的函数调用表达式称为 *伪析构函数调用 (pseudo destructor call)*。求值 E 后结束它的结果对象的生存期（对于非类类型，在销毁该对象时（包括通过伪析构函数调用销毁）其生命周期结束）。
这是唯一使 operator. 的左操作数是非类类型的情况。

**alignas**

[alignas](https://zh.cppreference.com/w/cpp/language/alignas)可以修饰类、非位域数据成员和变量，指定该类型的实例或该对象有额外的对齐要求。（修饰类时，影响的是类对象，而非类内成员）
一个类的实际对齐，是该类所有成员中对齐要求的最大值：max(max(各成员类型的基本对齐)，各成员的 alignas 最大值)。可通过[alignof](https://zh.cppreference.com/w/cpp/language/alignof)查询。

内存对齐的原因见 *基础 - 计组 - 内存对齐*。

- 对齐值是一个 size_t 整数，且为 2 的幂，也可以是一个类型名。如果 alignas 后的值非 2 的幂，则程序非良构（可能 CE）。
- alignas(0) 合法，会被忽略（但还是可能 CE）。
- 如果某个 alignas 声明的对齐值，比没有该声明时的对齐值还小，则程序非良构。即 alignas 要求的值要大于等于类型原有的对齐。
    （如果想要对齐值小于原对齐，则应使用 *pragma - #pragma pack*）

注意，只有栈对象保证其起始地址位于对齐边界处，直接使用 new/malloc 分配的不保证。
此外，传入函数实参的对象也不会对齐。想要对齐，需要传递指针或引用。

> 使用 [new](https://zh.cppreference.com/w/cpp/language/new) 分配时，有默认的对齐边界`__STDCPP_DEFAULT_NEW_ALIGNMENT__`，如果分配的对象对齐值不超过该值，自然是对齐的，否则不保证。
> 要想保证对象对齐，需要用 new 的重载`void* operator new(std::size_t, std::align_val_t);`
> [operator delete](https://zh.cppreference.com/w/cpp/memory/new/operator_delete)也有同样的重载。
>
> C++17 起，如果对齐超过默认对齐边界，new 会自动调用重载版本，将对象的对齐值作为`align_val_t`的实参。
>
> 容器的内存申请默认通过`std::allocator`，也不会特意进行对齐。想要保证需要自己指定分配器，比如：[Eigen::aligned_allocator](https://eigen.tuxfamily.org/dox/classEigen_1_1aligned__allocator.html)。

alignas 也可展开形参包。有多个 alignas 修饰的对象会取最大的对齐值。

```cpp
template<class... T>
struct A {
    alignas(T...) unsigned char buffer[8];
};
```

**decltype**

> https://zh.cppreference.com/w/cpp/language/decltype
>
> **总结：**decltype 对变量（无括号的标识符表达式）推导其原本的类型（不会 decay。当有括号时视其为表达式）；对其它表达式，亡值推导右值引用，左值推导左值引用，纯右值推导值类型。
> decltype(auto) 是对推导式的 decltype 的简写，实际就是 decltype(expr)。
> auto 对实际类型为 T 的变量，推导得到 decay<T>（不带引用、cv）。
> auto&& 是万能引用，对左值得到左值引用，对右值得到右值引用。
>
> ```cpp
> // 推导 x 的类型，为 T
> cout << is_same_v<decltype(A{}.x), int> << '\n';
> cout << is_same_v<decltype(node.x), int> << '\n';
> 
> // 推导该表达式的类型，由于是亡值为 T&&
> cout << is_same_v<decltype((A{}.x)), int&&> << '\n';
> // 推导该表达式的类型，由于是左值为 T&
> cout << is_same_v<decltype((node.x)), int&> << '\n';
> 
> // auto&& 对左值得到左值引用
> auto&& v1 = node.x;
> cout << is_same_v<decltype(v1), int&> << '\n';
> // auto&& 对右值（纯右值和亡值）得到右值引用
> auto&& v2 = Node{}.x;
> cout << is_same_v<decltype(v2), int&&> << '\n';
> ```

`decltype(表达式)`的返回值为：

- 如果实参是**没有括号的**标识符表达式或类成员访问表达式，那结果为以表达式命名的实体的类型。如果该表达式命名的实体不存在，或指向一组重载函数，则程序非良构。
- 否则（实参有括号，或不对应任何标识符）设表达式的类型为 T，
    - 如果表达式值类别是亡值，则为 T&&。
    - 如果表达式值类别是左值，则为 T&。
    - 如果表达式值类别是纯右值，则为 T。

所以，`decltype((e))`（两个括号）与`decltype(e)`的结果可能不同：如果 e 是带有括号的对象的名字，那么它会被当做普通的表达式，去推导其形成的表达式的类型，而非变量本身的类型 T：

- 如果 e 是标识符表达式（左值），则无括号时为 T，有括号时为 T&。
- 如果 e 是右值对象的成员表达式（亡值，如`Node{}.x`），则无括号时为 T，有括号时为 T&&。

在模板中，常与 *模板 - declval* 一起使用。

**decltype(auto)**

[decltype(auto)](https://zh.cppreference.com/w/cpp/language/auto) 与 auto 都是占位类型说明符，可从变量的初始化表达式/函数的 return 语句推导其类型。
与 auto 的区别为：

- auto 使用模板实参推导的规则，可以使用 const、& 这样的修饰符（会参与类型推导）。
    返回的类型一定是对象类型（无引用）。auto &/&& 一定返回对象的引用类型。
- decltype(auto) 可能返回 T 也可能返回 T&/&&，取决于 decltype(expr) 的结果（expr 是初始化或 return 语句中的表达式）。

比如：`auto c = s.at(0);`和`decltype(s.at(0)) c = s.at(0);`类似，前者总是不带引用的，后者取决于`s.at()`所以带引用。

注意，如果表达式 expr 中有括号，则 decltype(auto) 按照规则可能导致结果不同！

```cpp
// 类似，decltype(auto) v = t; 与 v = (t) 也可能不同。
decltype(auto) f1(Node& t){
    return t.x;
}
decltype(auto) f2(Node& t){
    return (t.x); // decltype(auto) 实际为 decltype((t.x))
}
decltype(auto) f3(const Node& t){
    return (t.x);
}
// 推导变量类型
cout << is_same_v<decltype(f1(node)), int> << '\n';
// 推导表达式类型，左值返回 T&
cout << is_same_v<decltype(f2(node)), int&> << '\n';
// 即使传右值，函数内 t 也是 const 左值，得到 const 引用
cout << is_same_v<decltype(f3(Node{})), const int&> << '\n';
```

**auto**

[auto](https://zh.cppreference.com/w/cpp/keyword/auto) 可用于多种场景。

- 作为函数参数类型时，对于普通函数将生成*简写函数模板*（C++20 起）。对于 lambda 将生成*泛型 lambda*（C++14 起）。

- 作为占位类型说明符推导类型时，与[*模板实参推导*](https://zh.cppreference.com/w/cpp/language/template_argument_deduction#.E5.85.B6.E4.BB.96.E8.AF.AD.E5.A2.83)方式相同。
  
    比如：`const auto& x = ...`得到的类型与`template <class T> void f(const T&)`、`f(...)`得到的 T 类型相同。除了万能引用，**auto 和 T 本身不会附加引用**。

> 当 auto 不带引用时：对 T 的数组及其引用，auto 会得到 T\*；对函数，得到函数指针；否则得到 remove_cvref_t<T>（不会附加 cv 与 &）。
> 当 auto 带引用时，使用它引用的类型；此外当 auto 是转发引用时，如果表达式是左值，则得到左值引用。
>
> 简单来说，推断对象类型时（不需要引用）用 auto；推断引用类型时用 auto&&（auto&& 跟 T&& 一样也是万能引用，因为规则相同：左值得到左值引用，右值得到右值引用。如果不修改可以用 const auto&）。
> 当无法确定带不带引用时（常见于模板），可以用 decltype(auto)。注意可能返回引用，不要出现悬垂引用。
>
> auto 会强制代码做初始化，并强制变量类型与初始化的返回值一致，所以也可以多用。

**如何用一个类型表示不同类型**

比如允许一个类型同时可表示 bool, int, double。
如果不同类型间可能同时存在，那么用结构体或 tuple 可以同时包含上面的几种类型（称为 product type）。
如果同一时刻只会使用一种类型（称为 sum type），上面的方案会浪费空间，可以：

- std::any：any 会 new 一个对应类型的指针保存，然后记录对象的一些类型信息，以便正常调用对象的函数。
- union：C 中的方案，多个类型共用一块内存，大小取决于里面最大的类型。与 any 不同的是它可以把数据存在栈里（只要是栈对象），减少 new 的开销。
    但是 C++ 中 [union](https://zh.cppreference.com/w/cpp/language/union) 很难用，如果联合体的某个成员是拥有用户定义的构造函数和析构函数的类，那么切换其活跃成员通常需要显式析构函数和 placement new。很容易 UB。
- std::variant：类似 union，但 variant 可以在切换活跃成员时，自动管理对象的生命周期（主要是调用构造函数和析构函数？），而 union 需要自己管理。
    但使用起来也不太方便，具体见：https://zhuanlan.zhihu.com/p/645810896

**union** / **联合体**

C++ 中的 [union](https://zh.cppreference.com/w/cpp/language/union) 使用与 C 不同，有很多问题：

- 只允许读取最后写入的那个联合成员，直接访问其它的联合成员是 UB。
    原因就是 *严格别名规则*：不允许不同类型的指针指向同一片内存。（也可能是因为原对象没有被销毁，新对象直接复用存储）
- 在切换对象时，无法调用旧对象的析构函数。因此不应放入有非平凡析构函数的东西。
- 无法知道当前 union 持有的值的类型。
- 不能作为基类。

std::variant 是更现代的 union，见 *variant*。

union 是一种特殊的类，也可以定义成员函数（包括构造和析构），但不能定义虚函数；不能有基类且不能用作基类；不能拥有引用类型的非静态数据成员。

> 可以利用 union 跳过对象的析构。
>
> ```cpp
> template <class T>
> union Forget{
>     T value;
>     ~Forget() {}
> };
> struct A{
>    ~A(){
>       cout<<"~A\n";
>    }
> };
> 
> auto f = Forget<A>{A{}}; // 不会执行A的析构
> // f.value.~A(); // 需要手动调用析构, 否则资源泄露
> ```

**union-like class**

[*联合体式的类*](https://zh.cppreference.com/w/cpp/language/union) (*union-like class*) 是一个联合体，或是一个至少拥有一个匿名联合体成员的类。
如果它是前者，则称它的非匿名联合体的非静态数据成员为它的*变体成员* (*variant member*)。
如果它是后者，则称类的匿名联合体成员中的非静态数据成员为它的变体成员。

联合体式的类可以实现与 std::variant 一样的效果。

**结构化绑定 (structured binding)**

> https://zh.cppreference.com/w/cpp/language/structured_binding

C++17 及以后，可用 auto 同时声明多个不同类型的变量，并从一个复杂对象得到赋值。
对象会被解包成多个变量，其类型和顺序与对象中的成员对应。

- 可以绑定三种类型：数组、[tuple-like](https://zh.cppreference.com/w/cpp/utility/tuple/tuple-like) 类型、类（会绑定到该类的非静态成员，它们必须都是 public 的，数量也要与标识符数量一致；静态成员不会被绑定）。
    绑定数组时，如果不加引用，会产生额外的数组拷贝？
- 在 auto 前加 const，则定义出来的变量类型会有 const；在 auto 后加 &，则会拿到引用。
- C++20 前，lambda 表达式不能捕获结构化绑定定义的变量。
    结构化绑定的变量也不会被视作隐式可移动实体，return 时默认不会用 NRVO。它和普通变量有些区别？

例：

```cpp
struct Node {
    int x;
    std::string y;
};
const auto &[num, s] = Node{1, "s"};
```

**弃值表达式**

[弃值表达式 (discarded-value expression)](https://zh.cppreference.com/w/cpp/language/expressions)是那些出现只是为了实施它的副作用的表达式，其计算的值会被丢弃。
包括：任何表达式语句的表达式本身、内建逗号左边的实参、到 void 的类型转换表达式的实参。
当它不存在副作用时，往往会被优化掉。

在丢弃弃值表达式的结果时，如果它不是到 void 的转换表达式，且调用了声明 [[nodiscard]] 的函数（还有其它规则），则会警告。

**decay**

[decay](https://zh.cppreference.com/w/cpp/types/decay)<T> 的结果与将 T 传递到函数实参时对 T 进行的转换一样？
会对 T 进行：数组到指针转换（将“T 的数组”类型的左右值转为“指向 T 的指针”类型的纯右值）、函数到指针转换（函数类型的左值转为指向该函数的指针的纯右值）、去除引用和 cv（为什么？）。

在[N2609](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2006/n2069.html)引入，是为了解决 make_pair 传参的问题。

```cpp
template <class T1, class T2> 
pair<T1, T2> make_pair(T1 x, T2 y) { 
    return pair<T1,T2>(x, y); 
}
```

在有 decay 前，make_pair 只能使用值传递。如果改为使用`const T1& x`引用传递，`pair<string, int> p = make_pair("a", 0)`会编译不过，因为 T1 会被推导为 char[2]，而 pair 不能使用数组作为模板参数，因为它不能默认初始化或复制初始化。
传值需要拷贝，效率很低，但通过 decay 将 pair 的模板参数改为 const char\*，就可以编译了，也就是：

```cpp
template <class T1, class T2> 
pair< decay_t<T1>, decay_t<T2> > 
make_pair(T1&& x, T2&& y) { 
    return pair< decay_t<T1>, 
                 decay_t<T2> >(forward<T1>(x), forward<T2>(y)); 
}
```

**内建逻辑运算符**

&& 和 || 都是短路求值：保证从左向右求值；如果求值第一个操作数后就可以确定表达式的结果，就不再求值第二个操作数。

重载的 && 和 || 没有短路性质，因为重载后是一个函数调用（`t1 || t2`实际上是`t1.operator ||(t2)`），在调用函数前必须对对象 t1 和实参 t2 进行求值。

**在 std 中添加声明**

> https://zh.cppreference.com/w/cpp/language/extending_std

在命名空间 std 中添加任何声明或定义都是 UB，除了以下情况（具体条件略）：

- 添加模板特化。比如：添加 hash 的特化`std::hash<MyType>`。
    这不需要展开 namespace std 完成，不推荐在`namespace std {...}`内编写，容易导致 UB。
- 显式实例化模板。

> 通常不需要为自定义的类特化 std::swap，只需要在与类相同的命名空间中定义 swap 即可。或者在类内定义 swap 友元函数，不对外使用（见 [Swappable](https://zh.cppreference.com/w/cpp/named_req/Swappable)）。
> 在标准库交换元素时（如 sort）会使用不带限定的 swap，所以能通过 ADL 找到正确的 swap（见类型特征[值可交换](https://zh.cppreference.com/w/cpp/named_req/ValueSwappable)）。
> C++20 前，在 std 内特化 swap 反而会使标准库找不到它？因为标准库不直接使用 std::swap，并且 ADL 不会查找 std 中的特化（命名空间 std 不是程序定义类型所关联的空间）（但实测可以）。
>
> 因为 std::swap 是模板，所以如果要特化它，需要以偏特化的格式：`template <> void swap(A& a, A& b)  {...}`。








---

## end







