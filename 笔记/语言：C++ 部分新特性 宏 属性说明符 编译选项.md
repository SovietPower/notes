# 语言：C++ 部分新特性/关键字 属性说明符 日期和时间

Tags: 笔记


-----

[TOC]

---

> C++17的改动：https://isocpp.org/files/papers/p0636r0.html





---

## C++14













---

## C++17

> 具体可见 *Books - C++ - C++17 完全指南*。



**launder**

[std::launder](https://zh.cppreference.com/w/cpp/utility/launder)主要用于两种情况：

- 在新旧对象不可重用存储时，获得指向在同类型既存对象的存储中创建的对象的指针。
    （覆盖对象的存储，创建新对象）

当两个对象 x, y 满足以下所有[存储重用的条件](https://zh.cppreference.com/w/cpp/language/lifetime#.E5.AD.98.E5.82.A8.E7.9A.84.E9.87.8D.E7.94.A8)时：

- y 的存储准确地与 x 所占据的存储位置重叠。
- x, y 类型相同（忽略 cv），且都不是基类子对象。
- x 不是完整的 const 对象。
- x, y 都是完整对象，或分别是 ox, oy 的直接子对象，且 oy 能透明替换 ox。

则 y 能够*透明替换* x：一旦在对象 x 所曾占据的地址上创建了新的对象 y，所有原对象的指针、引用及名字都会自动代表新的对象，而且一旦新对象的生存期开始，它们就可以用于操作这个新对象。
即可以通过 placement new `new(&x) T{...};`重用 x 的存储、构建一个新的对象 y，且原先指代 x 的都会自动指代新对象 y。

否则，即使进行原地构造，旧的指针、引用仍然"指向"旧对象，访问它们是 UB。
只有 launder（清洗）获取这块内存的新的对象的指针，才能以原对象的名字访问新对象。
可以认为为了优化，编译器能够认为原对象的指针始终指向原对象，不会被破坏、变成新对象（比如虚表不会被改变），除非用 launder 阻止优化、重新读内存（不过如果编译器能确保 launder 前后的指针指向同一个对象，也不会重读内存）。
使用 new 返回的指针访问新对象是 ok 的。

> 理论上，指针并不是一个简单表示地址的整数，而是标识一个对象的东西，并不一定要与地址关联。
> 因此，指针不会随意的访问到另一个不相关的对象，即使两个指针指向相同的地址。
> 当对象的生命周期结束后，其指针也会失效，即使后续对象占用原对象的空间，它也不会随意变成新对象的合法指针。

常见的不可重用的例子为：类 T 包含非静态 const 数据成员 或 引用数据成员，则在 x 上创建新的 T 对象，原本 x 的指针、引用都不会重新指向新的对象 。

```cpp
// #1 见 std::launder，基类子对象无法重用

// #2 在包含 const 的对象上重新创建新对象
// 注：C++20 起不需要了，因为新旧 value 满足存储重用（可透明替换），所以 value 会指代新对象
template <typename T>
class Wrapper {
private:
	T value;
public:
	Wrapper(T v): value(std::move(v)) {}
	template<typename... Args>
	void emplace(Args&&... args) {
        // 结束对象的生存期
		value.~T();
        // 原地构造新对象，但使用旧对象的指针
		::new (&value) T(std::forward<Args>(args)...);
	}
	T& get () {
		// return value;
        // 正确方式
        return *std::launder(&value);
        // 也可以拿一个指针成员保存 placement new 的返回结果，但显然很麻烦
	}
};
struct X {
	const int v;
	X(int i) : v(i) {}
	friend std::ostream& operator <<(std::ostream& os, const X& x) {
		return os << x.v;
	}
};

Wrapper<X> x{new X{2}};
x.emplace(5);
cout << *x; // UB

// #3 同上
struct X { const int n; };
union U { X x; float f; };

U u = {{ 1 }};
X *p = new (&u.x) X {2};
cout << u.x.n; // UB
// 正确方式
assert(*std::launder(&u.x.n) == 2);
```

- 如果一个对象通过 placement new 从为该对象提供存储的对象的指针创建，可用 launder 获得指向该对象的指针。
    （在一个对象提供的空间中，创建新的对象；即利用某个对象的存储，创建新对象，然后通过 reinterpret_cast 转换）

C++17 起，若 T 类对象 t 与 U 类对象 u 之间不是[指针可互转换的](https://eel.is/c++draft/basic.compound#4) (pointer-interconvertible)，则通过 placement new 在 &u 位置创建对象 t，或认为 &u 位置有个对象 t，然后通过 &u 或 reinterpret\_cast<T\*>(&u) 访问 t，都是 UB。
必须使用 **launder**( reinterpret\_cast<T\*>(p) )。

两个对象 a, b 是指针可互转换的，当且仅当：

- 它们是同一对象。
- 或 a 是 union，b 是它其中的非静态数据成员。
- 或 a 是标准布局的类对象，b 是 a 的第一个非静态数据成员或任意的基类子对象。
- 或存在对象 c，a 与 c、b 与 c 分别可互转换。

**只有 a, b 指针可互转换，且地址相同，才可直接使用 reinterpret 将指向 a 的指针转为指向 b 的指针。**否则需要 launder。

例：**使用 char 数组为对象提供存储：**

```cpp
alignas(int) unsigned char buffer[sizeof(int)];

// #1
int* p1 = reinterpret_cast<int*>(buffer);
*p1 = 3; // UB
int* p2 = new(buffer) int(0);
*p2 = 3; // ok

// #2
int* p = launder(reinterpret_cast<int*>(buffer));
*p = 3; // （C++20前）UB：no int here

// #3
struct Node { int a, b; };
Node* x = reinterpret_cast<Node*>(std::malloc(sizeof(Node)));
x->a = 10;  // （C++20前）UB: no Foo object here

// #4 隐式创建只能创建一个对象
int* p = launder(reinterpret_cast<int*>(buffer));
*p = 3; // C++20 起 ok
float* pf = launder(reinterpret_cast<float*>(buffer));
*pf = 3f; // UB：no float here
```

#1：C++17 起，由于 (unsigned) char 与 int 对象不是指针可互转换的，因此 #1 直接通过 reinterpret_cast 转换 buffer 再访问是 UB。p1 需要通过 launder 获取，否则仍然指向 buffer 对象（一个 (u)char）而非 int。
或者显式构造，然后用 new 的返回值 p2，就不用 launder buffer 指针了。

#2、#3：C++20 前，两者都是 UB。
注意，==只有对象分配完内存（获得存储）、完成初始化，其生命周期才开始、才认为该对象存在。==但 reinterpret_cast、malloc 并不会初始化对象，因此它们不会开始一个对象的生命周期，导致访问该对象是 UB（见 [生存期](https://zh.cppreference.com/w/cpp/language/lifetime)）。
但由于两种写法（使用 char 做存储构建对象；使用 malloc 分配内存然后强转访问）非常常见，C++20 规定了一组[隐式对象创建](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0593r6.html)(Implicitly Object Creation, IOC) 操作（[链接2](https://zh.cppreference.com/w/cpp/language/object)）：

- 使得一个 unsigned char/byte 数组的生命周期开始的操作，会隐式地创建由这个数组提供存储的对象。
    因此 C++20 起，#2 会隐式地在 buffer 位置创建一个 int。
    注意，这只能自动创建一个对象，如果像 #4 在该位置创建多种对象，就无法自动构造。
- 调用 operator new、std::m/c/realloc 函数等内存分配操作，会隐式地在分配出的存储空间中创建对象。
    包括 placement new。它们会构造对象（并结束原位置对象的生命期？）。
- 调用 memcpy、memmove、bit_cast 这些拷贝对象表示的操作，会隐式地在拷贝目标位置中创建对象。

它们会在相应位置隐式地创建[*隐式生存期类型 (Implicit Lifetime Type)*](https://zh.cppreference.com/w/cpp/named_req/ImplicitLifetimeType) 的对象，避免上面的 UB。

注意，由于不可互转换，#2、#4 仍然需要通过 launder 获得 IOC 创建的新对象。
但是 malloc 不需要，因为它属于一组 产生正确创建的对象的指针 (Producing a Pointer to a Suitable Created Object)，它们会直接产生指向 IOC 创建的对象的指针。

> ## 在已有内存上 placement new 创建对象需要注意：
>
> - 创建的对象不需要 delete，但如果析构函数非平凡，则需手动调用析构函数！如：`p->~vector<int>()`。
>     释放 buffer 时不会调用其存储对象的析构！（只会将其当做 uchar[]）
> - 用于存储的 buffer 需要 delete[]。生存期与内存如何分配释放是无关的，new [] 的对象一定要对应 delete[]。
> - 如果创建的对象 a 被 memcpy 到了另一位置 b（且它们是 *relocatable* 但不是可平凡拷贝），则必须有 a 或 b 之一调用析构函数（因为它们共享资源）。即 a 的存储可以不调用析构就释放，但 b 之后必须调用析构。
>
> C++20 起提供了 [construct_at](https://zh.cppreference.com/w/cpp/memory/construct_at)，它与 placement new 一样，但是是 constexpr 的（能用于常量表达式）。
> （对应的还有 destroy_at，C++20 起是 constexpr 的）

> 由于内存分配不只有 new、malloc，还可能包含大量自定义的 malloc。为了能让这些操作类似 IOC 操作一样创建新对象（并且不需要因为 placement new 结束原对象生命期？），C++23 提出了 [std::start_lifetime_as](https://zh.cppreference.com/w/cpp/memory/start_lifetime_as)（最初叫 std::bless），它允许我们在某位置开始新对象的生命期：
>
> ```cpp
> struct Node { int a, b; };
> Node* x = start_lifetime_as<Node>(myMalloc(sizeof(Node))); // 非标准库的 malloc 无法保证 IOC
> x->a = 10; // ok，这里确实有 Node
> 
> // placement new 虽然也行，但会覆盖原位置的数据，start_lifetime_as 不会
> std::unique_ptr<unsigned char[]> raw_data = myRead();
> Node* d = std::start_lifetime_as<Node>(raw_data.get());
> ```
>
> 它与 bit_cast 很像，但前者是原地创建，后者是在新的位置创建。见 *C++ - pun_cast*。
>
> C++17 前，在数组中 placement new 构造对象会造成存储的重用，使得数组对象生存期结束。
> C++17 起，使用 unsigned char、std::byte 为其它对象提供存储时，不会结束数组的生命周期（没有包括 char）。
> https://www.zhihu.com/question/454829347
>
> launder 也能获取被修改的 const 对象的新值。





---

## C++20

**模块**

> https://www.zhihu.com/question/644295072/answer/3397337831
> https://zhuanlan.zhihu.com/p/373457208



**预置比较**

允许定义 default 的比较运算（default comparisons，具体见[这里](https://zh.cppreference.com/w/cpp/language/default_comparisons)）。

```cpp
// 除了 <=> 外均需返回 bool
bool A::operator <(const A&) const = default;
// ...
auto A::operator <=>(const A&) const = default;

// 可类外定义
friend bool A::operator <(const A&, const A&) const = default;
// 可显式弃置，但意义不大
bool A::operator <(const A&) const = delete;
```

默认的实现中，<, >, <=, >=, <=> 会调用三路比较函数；==, != 会调用相等比较函数。

预置的 <=> 会按照基类（从左到右）、非静态成员（按声明顺序）的顺序依次调用它们的 <=>，直到出现结果不为 0 的情况（即不相等的情况）。返回值类型可以是三种比较类别或 auto（使用所有 <=> 中最强的序关系）。
预置的 == 会按照基类、非静态成员的顺序依次依次调用它们的 ==。返回类型为 bool。
如果有任意一个基类子对象或非静态成员 不存在合适的 <=>/\=\= 重载，则不会预置定义。

在定义 <=> 后，编译器会使用它自动生成 <, >, <=, >=。预置定义的 <=> 也可以。
在定义 == 后，编译器会使用它自动生成 !=。预置定义的 == 也可以。

> 自定义 <=> 不会生成 ==，因为三路比较需要返回序关系，而相等比较只返回是否相等，它们可能是不同的逻辑（比如字典序 == 可以先比较长度，再看是否要遍历；而 <=> 必须进行遍历）。
> 但预置定义 <=> 后，会生成预置定义的 ==。

**三路比较运算符** / **<=>**

[比较运算符](https://zh.cppreference.com/w/cpp/language/operator_comparison)包括 *双路比较*（包含4个关系运算符与2个相等性运算符）与*三路比较*。
传统的双路比较返回 bool，需要两次判断才能确定结果是大于、小于还是等于，在某些情况下可能影响性能（比如字符串比较）；双路比较还需要用户全部给出定义，重复且易错。三路比较可以解决这两个问题。

三路比较的结果是一个序关系 (ordering)，序关系有三种类型：

- [strong_ordering](https://zh.cppreference.com/w/cpp/utility/compare/strong_ordering) (强序)：任意元素间都可比较，且等价蕴函可替换性。
    序关系为等价的两个值是相等、不可区分的（始终满足$a=b\to f(a)=f(b)$，即 a 在任意位置都可替换为相等的 b）。
- weak_ordering (弱序)：任意元素间都可比较，但等价不蕴函可替换性。
    序关系为等价的两个值可能是可区分的（等价的两个值并不一定相等，在某些逻辑下可产生不同结果）。
- partial_ordering (偏序)：两个元素可以不可比较，等价不蕴函可替换性。
    并非任意两个值之间都存在序关系。a < b, a == b 和 a > b 的值可以均为 false，而不是有且仅有一个为 true。

每种类型都有3~4个可用的值。
三种类型的限制由强到弱。限制更强的关系可以隐式转换为更弱的关系，反之则不能隐式或显式转换。
标准涉及的类型中，只有浮点的比较是 partial_ordering（NaN 不可比，且 +0.0 与 -0.0 等价但不相等，因为符号不同），其余为 strong_ordering。

> 有理数是弱序，比如：1/2 与 2/4 等价但可区分。
> 
>比较运算符应该带 const，否则 const 对象无法比较。
> 自行实现比较运算符时，如果实现有问题（非严格弱序？比如产生 a < b 且 b < a），程序可能会崩溃？

**获取三路运算符的结果**

`auto o {v <=> 0}`，有三种方式使用 o：

- 与对应类型的值用相等性比较。比如：`o == strong_ordering::less`。
- 使用 <compare> 提供的函数 is_eq、is_neq、is_lt、is_gt、is_lteq、is_gteq，它们接受一个比较类型，返回 bool。比如：`is_lt(o)`。
- 与 0 比较：`a <=> b`在 a > b 时 > 0，在 a < b 时 < 0，在 a 与 b 相等或等价时等于 0。比如：`o < 0`。

**功能特性测试**

[功能特性测试](https://zh.cppreference.com/w/cpp/feature_test) (feature test) 提供了一组宏，是一个检测特定功能特性是否存在的一种简单、可移植的方式。

- 测试编译器是否支持某**属性说明符** (attribute)，格式均为：`__has_cpp_attribute(attribute_name)`。
    如果支持某属性，则该宏会被定义成 "该属性被添加到工作草案中时的年份和月份的整数字面量" 或 0（实现定义）。
- 测试编译器是否支持某**语言功能特性**，不同特性有不同名称（见文档）。
    如果支持，宏会被定义成 "功能特性被包含到工作草案时的年份与月份的整数字面量"。
- 测试编译器是否支持某**标准库功能特性**，与上语言功能特性类似。
    需要包含头文件 <version> 或对应头文件，才可能有该宏的定义。

**允许为 range for 添加初始化语句**

range for 的对象称为范围表达式。
如果范围表达式是返回临时量的表达式，则其生命期会被延续到循环结束；但范围表达式中的其它临时量，其生存期在 C++23 前不会被延长，因此下面是 UB：

```cpp
// 注意 f() 需要返回值，如果返回悬垂引用那也没办法
// f() 返回值的生存期会被延续，但 .items() 不会
for (auto& x : f().items()) { /* use x.. */ }
```

这就可以通过初始化语句解决：

```cpp
for (T thing = f(); auto& x: thing.items()) { /* ... */ }
```

C++23 起，如果临时量会在范围表达式末尾销毁，则会被延长到循环结束。

**contains**

为相关容器添加成员函数 contains，不用再写 find != end 了。

**引入 char8_t**

char8_t 是更明确的 char 类型，对应 C++11 就有的 char16/32_t。见 *C++ - 基础 - 字符类型*。
u8'a' 是一个 UTF-8 字符，类型为 char8_t。

**starts_with**

为 string 引入了 starts_with 和 ends_with 成员函数，更方便判断前后缀。

**更安全的比较**

在比较有符号数和无符号数时，非常容易出错。
C++20 在 utility 下引入了一系列比较函数，可以在数学意义上比较数字。

```cpp
long longVal = -100;
size_t sizeVal = 100;
cout << boolalpha << (longVal < sizeVal); // false
cout << std::cmp_less(longVal, sizeVal);  // true
```







---

## C++23

**start_lifetime_as**

见 *特性 - 17 - launder*。

**unreachable**

[unreachable](https://zh.cppreference.com/w/cpp/utility/unreachable) 是 C++23 引入的函数。
被调用时会触发 UB，用来向编译器说明该语句不可能会执行，以优化掉不可能的分支或条件。类似某些编译器的扩展`__builtin_unreachable`。

**显式对象形参** / **显式 this**

> TODO
> https://zh.cppreference.com/w/cpp/language/function#.E6.98.BE.E5.BC.8F.E5.AF.B9.E8.B1.A1.E5.BD.A2.E5.8F.82

因为非静态成员函数遵循 thiscall *调用约定*，所以调用时必须通过 this 指针用 operator -> 调用，不能像普通函数一样将对象指针传递到参数列表调用，所以使用时可能要进行包装：

```cpp
struct X {
    void f(int);
};
using Func = void(*)(X*, int);
Func f = [](A* self, int x) { self->f(x); };

f(p, 1);
```

C++23 的显式对象形参可以明确 this 的传入方式，

```cpp
struct X {
	// 这里的 this 只是个标记作用，为了和旧语法区分开来
	void f(this X self, int x); // pass by value
	void g(this X& self, int x); // pass by reference
};
```

在 C++23 前，不存在合法的获取一个成员函数地址的方式，只能获取成员函数指针。C++23 起，被显式 this 标记的函数也可以直接获取函数地址，和普通函数一样。

```cpp
auto f = &X::f; // type of f is void(*)(X, int)
auto g = &X::g; // type of g is void(*)(X*, int)
```

**static operator ()**

某些类型只是用做无状态的函数对象，即除了`operator ()`外不包含任何成员，比如 std::hash、各种谓词。
因为 operator () 是非静态成员函数，所以调用它时仍然需要传递一个无用的 this 指针。
C++23 允许定义将 operator () 定义为静态成员函数，无需传递 this。它的使用方式不变，还是要传递一个无用的类对象，这与其它静态函数不同？

```cpp
template <class T>
struct hash {
    size_t operator ()(const T& t) const;
};

// C++23
template <class T>
struct hash {
    static size_t operator ()(const T& t);
};
// 使用方式不变
hash<int> h;
cout << h(1);
```









---

## 宏

> https://zh.cppreference.com/w/cpp/preprocessor

宏定义是不受 namespace 影响的，因为是预处理阶段就进行的文本替换。
即在 namespace A 下定义的宏 B，使用时直接用 B，不能用 A::B（会对 B 进行替换）。

宏没有类型的概念，只有不同的符号。因为宏替换在编译前完成，所以编译器看不到宏替换的过程，无法针对报错。

可以通过 -E 仅执行预处理，查看预处理后的代码。
-P 与 -E 一起使用，要求在执行预处理步骤时，删除所有的行号和前导 # 符号，使预处理结果更简洁。

**文本替换宏**

> https://zh.cppreference.com/w/cpp/preprocessor/replace
> 包括预定义宏，如：`__cplusplus`、`__FILE__`、`__LINE__`。
>
> 应用：https://zhuanlan.zhihu.com/p/152354031

文本替换宏有两类：

- 对象式宏：#define 标识符 替换列表
- 函数式宏：#define 标识符(形参, ...﻿) 替换列表
    在遇到左括号时，会向右直到找到匹配的右括号，作为整个宏。

替换列表、形参、... 均可省略。形参可以为空，且以逗号分隔。
宏中的所有空白字符会被忽略。

特殊功能的宏名通常以`PP_`为前缀，代表 pre-processor。

在展开宏时，如果遇到当前宏的符号，则不会继续展开，避免无限展开。因此宏不支持递归/重入。但可以通过某些方式实现。

**在宏形参中使用非分隔逗号**

一个形参内部不能出现逗号，否则会被视为多个形参（比如：`f(vector<int, int>)`会有两个形参）。
解决方法有两个：1. 如果某个类型内部有逗号，为其创建不含逗号的别名再传递给宏；2. 用括号对封装参数，并在最终展开时才移除括号（避免逗号被作为形参分隔符处理），这种括号对称为元组？

```cpp
// 2.
#define REMOVE_PARENS(T) REMOVE_PARENS_IMPL T
#define REMOVE_PARENS_IMPL(...) __VA_ARGS__

#define FOO(A, B) int foo(A x, B y)
#define FOO2(A, B) FOO(REMOVE_PARENS(A), REMOVE_PARENS(B))

using Pair = pair<int, int>；
FOO(bool, Pair) // ok，无多余逗号
FOO2((bool), (pair<int, int>)) // ok，展开为 int foo(bool x, pair<int, int> y)
```

上述代码中，元组封装`REMOVE_PARENS(T)`会展开为`REMOVE_PARENS_IMPL T`，如果 T 包含一个括号，则会成为宏`REMOVE_PARENS_IMPL(...)`，从而在最终才展开其内部内容`pair<int, int>`。

**可变实参 / VA_ARGS**

宏中的`...`称为可变实参，可以接收 至少1个（C++20 前）/ 任意个（C++20 起）实参，使用`__VA_ARGS__`访问。

**VA_OPT**

`__VA_OPT__(sth)`可以出现在宏替换列表内，当 VA_ARGS 非空时，它会被替换为 sth（可以为空）；当 VA_ARGS 为空时，它为空、不会展开成任何内容。
与 VA_ARGS 一起使用，可以避免 VA_ARGS 为空时有多余逗号等问题：

```cpp
#define p(fmt, ...) printf(fmt, __VA_ARGS__)
p("p: %d, %lf, %s\n", 1, 2.5, "abc"); // ok
p("p"); // error：fmt 后有一个逗号，但逗号后没有内容

// 在 VA_ARGS 为空时忽略逗号
#define p(fmt, ...) printf(fmt __VA_OPT__(,) __VA_ARGS__)
p("p"); // ok
```

某些编译器提供扩展：允许 ## 在逗号后及`__VA_ARGS__`前出现，## 在 VA_ARGS 非空时不做任何事，但在 VA_ARGS 为空时移除逗号，也能实现上述功能（但通常 ## 不应拼接空内容）：

```cpp
#define p(fmt, ...) printf(fmt, ##__VA_ARGS__)
p("p"); // ok
```

**# 与 ## 运算符**

#：获取字面量，将实参转换为其原本的字符串。常用于输出表达式名。
会对实参进行字符串化：移除所有前导和尾随空白符，并将文本中间的空白符序列缩减为单个空格；如果实参内本身有 " 和 \，则会为其转义生成`\"`和`\\`。

```cpp
#define PRINT(x) printf("print: " #x " is %d.\n", (x))
PRINT(x);
PRINT(3 * 2);
```

##：拼接记号，将替换后的两个记号连接成一个记号，可以组成更长的标识符、组成数字、组成复合运算符。
拼接非法符号是 UB，包括空符号？

```cpp
#define XNAME(n) x ## n
int XNAME(4) = 4; // x4
```

如果一个宏用于 # 或 ##，那么它不会被继续展开：

```cpp
#define FOO(N) foo_## N
#define BAR() bar

FOO(bar)    // -> foo_bar
FOO(BAR())  // -> foo_BAR()，BAR() 不会展开
```

但通过将其作为另一个函数式宏的参数，在该宏内再用 #/##，就可以先被展开：

```cpp
#define CONCAT(A, B) CONCAT_IMPL(A, B)
#define CONCAT_IMPL(A, B) A##B // 需要吗

#define FOO(N) CONCAT(foo_, N)
#define BAR() bar

FOO(bar)    // -> foo_bar
FOO(BAR())  // -> foo_bar
```

**函数式宏的展开规则**为：

1. 进入宏函数前，所有宏参数先进行一次预扫描，完全展开未用于 #/## 的所有参数。
2. 展开宏函数时，用预扫描展开后的参数替换展开目标里的同名符号。
3. 展开宏函数后，对替换后的文本进行二次扫描，继续展开结果里出现的宏。

在第一步和第二步之前（即预扫描前后），实参个数必须与宏定义匹配。

上述代码将`foo_## N`换成了`CONCAT(foo_, N)`，因此会先展开参数 N，再进行拼接。

可以定义一些宏用做符号，这样能控制符号展开的时机，或选择展开哪个符号。

```cpp
#define COMMA() ,
#define LPAREN() (
#define RPAREN() )
#define EMPTY()
```

**条件选择**

```cpp
// 接收规定好的整数，返回0或1
#define BOOL(N) CONCAT(BOOL_, N)
#define BOOL_0 0
#define BOOL_1 1
#define BOOL_2 1
// ...

#define IF(PRED, THEN, ELSE) CONCAT(IF_, BOOL(PRED))(THEN, ELSE)
#define IF_1(THEN, ELSE) THEN
#define IF_0(THEN, ELSE) ELSE
```

IF 会根据条件转换为 IF_1 或 IF_0，再展开成对应参数。

因为展开规则，IF 宏中的所有参数会在进行替换前先被展开，这可能不符合预期：

```cpp
// 如果条件为真，则展开为逗号，否则展开为空
#define COMMA_IF(N) IF(N, COMMA(), EMPTY())
COMMA_IF(1)  // -> IF(1, , , ) (too many arguments after prescan)
```

这可以通过惰性求值避免：让宏先返回对应宏的名字（无括号），再在后面附近括号和参数实现延迟调用：

```cpp
#define COMMA_IF(N) IF(N, COMMA, EMPTY)() // 先展开成 COMMA 或 EMPTY，再变为 COMMA() 或 EMPTY()，再展开

COMMA_IF(0)  // 空
COMMA_IF(1)  // -> ,
COMMA_IF(2)  // -> ,

// 如果条件为真，则用 () 包裹 N，否则用 []（可以换为任意符号）包裹 N
#define SURROUND(N) IF(N, LPAREN, [ EMPTY)() \
                    N \
                    IF(N, RPAREN, ] EMPTY)()

SURROUND(0)  // -> [0]
SURROUND(1)  // -> (1)
SURROUND(2)  // -> (2)
```









---

## 属性说明符

> https://zh.cppreference.com/w/cpp/language/attributes （缺失的部分见 en）
>
> gcc：https://gcc.gnu.org/onlinedocs/gcc/Attribute-Syntax.html#Attribute-Syntax
> 常见的类型说明符：https://gcc.gnu.org/onlinedocs/gcc/Common-Type-Attributes.html
> 常见的函数说明符：https://gcc.gnu.org/onlinedocs/gcc/Common-Function-Attributes.html
> 常见的变量说明符：https://gcc.gnu.org/onlinedocs/gcc/Common-Variable-Attributes.html
>
> clang：https://clang.llvm.org/docs/AttributeReference.html

属性为各种由实现定义的语言扩展。
以下如无标注，均为 gcc 语法。

标准定义了几种属性：noreturn、deprecated、deprecated("reason")、nodiscard、maybe_unused、likely、unlikely 等。

> 许多属性是用来辅助编译器进行优化。但如果编译器能够看到函数的定义，就没必要使用某些属性；当函数来自其它翻译单元且没有 LTO 时，需要这些属性。

**gcc 属性语法**

gcc 有两种声明属性的方式 (*attribute specifier*)：

- 标准的 C++ 语法：`[[Attribute]]`。
    对于 gcc 的、标准没有定义的属性，属性名前需要加 gnu::，如：`[[gnu::unused]]`。
- 较老的 GNU 扩展语法：`__attribute__((Attribute))`。
    这种似乎只能在声明中出现，不能在定义中使用？

Attribute 可以为空，或是任意个逗号分隔的属性名称（可以通过括号带参数）。
可以同时使用多个属性说明符，只需用空格分隔。
属性名称的前后可以加`__`，避免可能和已有的宏冲突，比如：`__attribute__((noreturn))`和`__attribute__((__noreturn__))`都可。

例：
函数说明符：

```cpp
// 标准语法：
// 属性既可以在整个声明之前出现，也可以直接跟在被声明实体的名字之后
[[gnu::always_inline]] [[gnu::const]] [[nodiscard]]
inline int f(); // 多个属性说明符
 
[[gnu::always_inline, gnu::const, nodiscard]]
inline int f(); // 一个属性说明符，包含多个属性
 
// C++17，将命名空间 gnu 应用到后面的所有属性
[[using gnu : const, always_inline]] [[nodiscard]]
inline int f [[gnu::always_inline]] (); // 一个属性可以出现多次

// 扩展语法：
// 此时，属性只能出现在声明中，可以在前面，也可在最后？
__attribute__((always_inline, const))
inline int f();

inline int f() __attribute__((always_inline, const));
```

类型说明符：

```cpp
// 需要紧跟在 struct 后
struct [[gnu::packed]] D2 {
    char a;
    int b;
};
// 同上
enum __attribute__ ((__packed__)) E {
    A,
    B,
    C,
};
```

**always_inline**

强制内联声明为 inline 的函数（如果没声明 inline 则无效）。
如果函数被间接调用，则不保证 inline。

clang 的`[[clang::always_inline]]`可以说明表达式，要求编译器**尝试**内联该表达式涉及的所有调用。
该说明不是强制性的，只是允许编译器无视优化等级尝试内联。

**noreturn**

（标准支持）函数可以标记为 [noreturn](https://zh.cppreference.com/w/cpp/language/attributes/noreturn)（一类[属性说明符](https://zh.cppreference.com/w/cpp/language/attributes)），表示不会返回（此时再 return，或既没有调用非 noreturn 的函数、也不 throw 导致函数执行完毕，将是 UB）。
在一个非 void 函数调用该函数时，后面也可以不写返回语句（因为编译器知道即使有也不会被执行），否则会有 warning。

比如[exit](https://en.cppreference.com/w/cpp/utility/program/exit)：`[[noreturn]] void exit( int exit_code )`。

**pure**

> C++ 将纯函数的性质称为 [*保持相等性* (equality-preserving)](https://zh.cppreference.com/w/cpp/concepts)，将纯函数的约束定为 *regular_invocable*。

[[[gnu::pure](https://gcc.gnu.org/onlinedocs/gcc/Common-Function-Attributes.html#index-pure-function-attribute)]] 声明一个函数是纯函数：不会产生副作用，即不会对程序的状态产生可观测的影响。除了返回值供使用外，不会有任何影响。
这允许编译器在状态未发生变化的情况下，将参数相同的多次函数调用优化成一次（*公共子表达式消除*，CSE，Common Subexpression Elimination）；或在不需要其返回值的情况下， 直接不调用函数。

比如：`[[gnu::pure]] int hash(int* p)`，编译器可以在 p 和 p 指向的内容（即对 hash 函数有关的状态）均未发生变化时，返回之前得到的结果。在调用 hash 之间修改 p 指向的内容也是安全的，只是会放弃该优化。
即使 p 不是 const，hash 也不能修改 p 指向的内容。

pure 函数允许读取非 volatile 的对象并计算返回值。这些对象会被计入影响其状态的因素，并且在对象被修改时，不会使用优化。

常用于 跨编译单元的函数调用/引用外部函数 的情况：由于函数定义不可见，编译器不能判断它是否是纯函数，不能执行这种优化。但当定义可见时，编译器可以自行优化甚至内联。

```cpp
extern int g1(int);
[[gnu::pure]] extern int g2(int);

// 使用 g1 时，将会始终调用 g1，然后再判断，因为 g1 可能有副作用
// 使用 g2 时，则只会在 *p!=1 时调用 g2
int f1(int* p) {
	int res = g1(1);
    return *p == 1 ? 0 : res;
}
```

**const**

gnu::const 是比 pure 更严格的限制，它说明函数不会产生副作用，之后返回值，且返回的值不会受程序的任何状态所影响。
这允许编译器直接将参数相同的多次函数调用优化成一次。

比如：返回 x*x 的`[[gnu::const]] int sqaure(int x)`。

const 禁止函数读取会影响其返回值的对象。但如果对象不会导致返回值变化（比如非 volatile 的 const），则可以读取。
因此 const 与 pure 不同且不兼容，同时声明 const 与 pure 是错的。
const 函数的参数不应是指针或引用，它不会考虑它们指向的内容是否发生修改。
const 函数不应调用非 const 函数。

**aligned**

设置类型的最小对齐值。

```cpp
typedef __attribute__((aligned(1))) int packed_int;
// using packed_int = [[gnu::aligned(1)]] int; // 都可
struct D3 { // 5B
    char a;
    packed_int b;
};
```

**packed**

修饰结构体、类、联合时，要求内部成员紧密放置，以使用尽量小的内存（要求成员均 1 字节对齐 (aligned(1))，或叫不进行对齐）。
修饰 enum 时，使用最小、最合适的类型做底层类型（1字节能存 256 个）（与选项`-fshort-enums`等效）。

修饰类 A 时，不会间接影响内部类 B：只是 A 的各成员间紧密排列，不管 B 内部。

> 注意，为了安全 gcc 不允许将引用绑定到某个未对齐的成员上（比如 packed field）：
> 不是所有平台和架构都支持字节可寻址（地址空间以字节为单位）。在这些平台访问非对齐成员时，编译器能通过结构体的信息（pack）和移位等操作，正确进行读写。但如果将成员绑定到普通引用，就丢失了 pack 信息，编译器会直接访问成员地址（可能并不支持），可能导致崩溃，或发生 trap 影响性能。
>
> 虽然可以定义 1 字节对齐的类型以保留对齐信息 `typedef __attribute__((aligned(1))) int packed_int;`，但在 mangle 时不会考虑对齐，重载或模板中 packed_int 都会被当做 int，导致错误。

**nonnull**

nonnull 是函数说明符，用来指定函数的部分指针参数绝不会是空指针，以允许对函数调用者和该函数本身进行优化。

标准规定 memcpy 的两个指针参数不能为空，相当于有该说明。



**no_unique_address**

[no_unique_address]() 在用来实现空基类优化的效果。（C++20 起）

https://www.cppstories.com/2021/no-unique-address/

**likely**

[likely/unlikely](https://zh.cppreference.com/w/cpp/language/attributes/likely) 修饰声明语句外的语句和 switch 的标号 (case)，告诉编译器该执行路径比不包含该说明的执行路径更可能/更不可能发生。（C++20 起）

主要修饰 if 和 for？

```cpp
constexpr long long fact(long long n) noexcept
{
    if (n > 1) [[likely]]
        return n * fact(n - 1);
    else [[unlikely]]
        return 1;
}
constexpr double cos(double x) noexcept
{
    constexpr long long precision{16LL};
    double y{};
    for (auto n{0LL}; n < precision; n += 2LL) [[likely]]
        y += pow(x, n) / (n & 2LL ? -fact(n) : fact(n));
    return y;
}
```

**assume**

[assume(expr)](https://zh.cppreference.com/w/cpp/language/attributes/assume) 告诉编译器在该位置，该表达式的求值一定为 true，以便进行优化。如果 expr 可能为 false，那么是 UB。（C++23 起）
编译器可以根据前面或后面的任何相关的 assume 假设，来优化某条语句。
某些编译器有类似的扩展，比如：clang `__builtin_assume`、MSVC `__assume`。

等价于 C++23 引入的`unreachable()`函数或扩展`__builtin_unreachable()`：

```cpp
if (expr) {
	// ...
} else { 
	__builtin_unreachable();
}
```

应用：

- 在进行复杂运算时，可以说明变量非负，优化汇编。
- 在让编译器生成 SIMD 时，可以说明数组长度为2的倍数，来避免额外的处理。







---

## pragma

**#pragma**

> gcc 支持的：https://gcc.gnu.org/onlinedocs/gcc/Pragmas.html

[pragma](https://zh.cppreference.com/w/cpp/preprocessor/impl) 控制编译器执行实现定义的行为。

标准不要求编译器支持任何该指令。当指令不被当前编译器支持时，会被忽略。

**#pragma once**

[once](https://en.wikipedia.org/wiki/Pragma_once) 可避免一个头文件被编译多次。

与符合标准的 #ifndef、#define、#endif（include guard）相比：

- once 不是标准的，只是受大多数现代编译器支持，某些情况可能不兼容，此时也不会导致 CE。
    两种方法可以同时用：在 #ifndef 前加 #pragma once。这样即使编译器不支持也不会影响正确性。
- 宏定义方式每次都要读取头文件，才能判断是否重复；还要扫描整个文件直到 #endif（但现代编译器可能识别 #ifndef 并避免这点，并不会影响效率）。
    once 直接根据文件系统检查重复，可能提升编译效率。
- 宏定义方式可能出现命名冲突。
    once 没有该问题。但由于是根据文件路径检查，如果某个头文件在项目中出现多次，也会编译多次（但很好发现该错误。但如果依赖关系复杂、引用库的数量多可能很难？）。

总的来说不用在意用哪个。最好是一起用。

**#pragma pack**

[pack](https://zh.cppreference.com/w/cpp/preprocessor/impl)（具体见 gcc、msvc 等文档）控制类或 union 的对齐值。
注意，它将会影响后面的所有代码，所以使用完后需要 #pragma pack() 恢复原对齐。

设定的对齐不能大于类型原有的对齐，而标准的 *C++ - alignas* 不能小于原有的对齐。
#pragma pack(1) 与 *属性说明符 - aligned(1)、packed* 类似，要求成员紧密放置，以使用尽量小的内存（1字节对齐），见 *packed*。



**#pragma warning**

用于 MSVC（`#if defined(_MSC_VER)`），`#pragma warning(disable:xxxx)`可以关闭编译器警告 Cxxxx。
比如：disable: 4127 可以关闭警告 warning C4127: xxx。

可在使用第三方库无法处理警告时使用。



---

## 编译选项

>gcc：https://gcc.gnu.org/onlinedocs/gcc/Option-Index.html
>https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html
>clang：https://clang.llvm.org/docs/CommandGuide/clang.html
>https://releases.llvm.org/16.0.0/tools/clang/docs/UsersManual.html
>MSVC：https://learn.microsoft.com/zh-CN/cpp/build/reference/compiler-options?view=msvc-170





**clang 的优化等级**

![img](https://cdn.jsdelivr.net/gh/Apricity-qvq/ImageHostForTypora//img/v2-8f24a9b3796b52cbd14ac7a04be4e1ef_r.jpg)

**-fdump-lang**

输出特定信息。
格式：`-fdump-lang-switch`。switch 有4种，可分别查看不同信息：

- all：`-fdump-lang-all`，输出所有信息。
- class：输出类的布局和虚表内容。
- module：输出模块信息。
- raw：输出原始内部树数据？





















