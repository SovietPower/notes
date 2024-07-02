# 语言：C++ STL 库函数

Tags: 笔记

---

[TOC]

---

STL (standard template libaray) 属于标准库的一部分。
包括六大部分：容器、分配器、算法、迭代器、仿函数、适配器。

> 标准库实现：
> GCC libstdc++：https://github.com/gcc-mirror/gcc/tree/master/libstdc%2B%2B-v3/include/std
> Clang libc++：https://github.com/llvm/llvm-project/tree/main/libcxx
> MSVC STL：https://github.com/microsoft/STL/tree/main/stl
>
> 通过`-stdlib=libc++`选项来指定使用不同的标准库。

> C 运行时库实现：
> glibc 源码：https://elixir.bootlin.com/glibc/glibc-2.39/source/
>
> C 运行时除了提供 C 标准库的实现外，还负责程序的初始化和清理。它负责调用main函数，并管理程序的启动和终止过程，包括执行一些必要的初始化和清理工作。对于大多数在操作系统上的软件来说，链接它是必须的。



## STL - 工具库

**variant**

> variant 和 visit 也能实现运行时多态，只是表达能力比继承弱（仅限于声明的几种类型）。因为是直接用值而非指针实现的多态，所以也叫值语义多态 (value polymorphism)。
> 理论上 visit 是可以内联的，只需要把整个函数体嵌入。如果有 switch 实现，则也不需要查表和访问函数指针。

[std::variant](https://zh.cppreference.com/w/cpp/utility/variant) 是类型安全的联合体（可称为变化体），能在类型切换时调用构造与析构函数，并在使用时检查类型是否匹配（包含类型信息）。
与联合体的行为类似：如果保存某个类型 T 的值，那么 T 的对象表示会在 variant 自身的对象表示中直接分配。
不能分配额外的动态内存，不能保存引用、数组、void。

variant 解决了 union 的缺点：

- 无法判断 union 对象当前持有值的类型（只能通过程序逻辑保证）。
- 难以存储非平凡类型（需要实现构造函数）。
- 不能作为基类。

当 get 访问不匹配的类型时，会抛出异常 bad_variant_access，所以需要确保类型正确。（访问不存在的类型时，可直接在编译期检查）
也可以使用 [holds_alternative](https://zh.cppreference.com/w/cpp/utility/variant/holds_alternative) 或 [get_if](https://zh.cppreference.com/w/cpp/utility/variant/get_if) 安全地访问，它们在类型不匹配时分别返回 false 或空指针。

```cpp
if (auto pval = std::get_if<int>(&v)) {
    cout << *pval << '\n';
} else if (std::holds_alternative<long>(v)) {
    cout << std::get<long>(v) << '\n';
} else {
    puts("not int/long");
}
```

参考实现见 *Codes - C++ - variant*。

注意，variant 允许隐式转换，如：赋值 int 时，优先匹配 int，如果 variant 没有 int 类型则匹配 long，但无法匹配 float、double、char、short。

**visit**

variant 的类型是运行时确定的，因此存在其类型无法确定的情况。虽然能通过 if else 依次检查其所有类型（通过 holds_alternative 或 get_if），但这很繁琐。
[std::visit](https://zh.cppreference.com/w/cpp/utility/variant/visit) 提供了获取其实际类型并执行的简单方式。它接收一个可调用对象 f 和若干个 variant，将 variant 的当前值依次转换为 f 的参数，然后调用 f，返回 f 的返回值。即它能够自动获取当前 variant 内的类型，并传给对应参数类型的 f。
f 称为 visitor（观览者），需要是能接收 variant 所有选项的可调用对象（好像只能是泛型 lambda 和仿函数？），且返回类型都要相同。

使用方式有三种：一是写所有类型都能执行的语句；二是先获取参数（即 variant 当前值）的类型，然后用 constexpr if 和 is_same 根据类型，执行不同语句；三是为可调用对象定义不同参数类型的重载，以便自动匹配（应该最好用）。

```cpp
variant<int, string> v = 1;

// #1 variant 的所有类型必须都能执行下列语句
std::visit([](auto&& arg) { // 需要使用万能引用 auto&&（会生成有 operator ()(T&&) 的泛型 lambda）
    cout << arg << '\n';
}, v);

// #2
std::visit([](auto&& arg) {
    using T = decay_t<decltype(arg)>;
    if constexpr (is_same_v<T, int>) // constexpr if 在编译期判断，从而能根据条件生成不同代码，避免 CE
        cout << "int: " << arg / 2 << '\n';
    else if constexpr (is_same_v<T, std::string>)
        cout << "string: " << std::quoted(arg) << '\n';
    else 
        static_assert(false, "观览器无法穷尽类型！");
}, v);

// #3
template<class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };
template<class... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

std::visit(overloaded{
    [](int arg) { cout << "int: " << arg / 2 << '\n'; },
    [](const std::string& arg) { cout << std::quoted(arg) << '\n'; },
}, v); // 这些重载需要有相同的返回类型
```

实现方式（见 *Codes - C++ - variant*）：
可调用对象 f 的类型在编译时就要确定，但 visit 能让 f 在运行时接收不同类型的参数、返回不同类型的值。
它的实现与 *variant* 中根据类型调用对应的 Destroy 函数类似：设 variant 有 n 种类型，则在编译时创建 n 个 f 的不同实例化函数，对应不同的参数类型，然后将它们的指针保存在数组中，visit 时直接使用 variant.index 访问数组调用。

创建不同实例化函数时，同样使用形参包展开：`static constexpr VisitorT visitorFuncs[] = { visitImpl<F, Variant, ids>... };`。

> 这只适用于接收一个 variant 的情况。当有多个 variant 时，就需要定义 size1 \* size2 \* ... 个函数，并用一个多维表保存它们的指针。
> 也可以在 visit 实现内部写 switch，根据 index 调用不同函数，避免保存和访问函数指针数组。
>
> 这个函数指针数组与虚函数类似，与该类绑定。因此调用代价也与虚函数类似？

**any**

[std::any](https://zh.cppreference.com/w/cpp/utility/any)是一个可以接收任意类型的类型安全的容器。



> 一般来说，C++是一门类型绑定和类型安全的语言。值对象被声明为确定的类型，这个类型定义了所有可能
> 的操作、也定义了对象的行为。而且，对象不能改变自身的类型。
> std::any是一种在保证类型安全的基础上还能改变自身类型的值类型。也就是说，它可以持有任意类型的
> 值，并且它知道自己当前持有的值是什么类型的。当声明一个这种类型的对象时不需要指明所有可能的类型。
> 实现的关键在于std::any对象同时包含了值和值的类型。因为内含的值可以有任意的大小，所以可能会在
> 堆上分配内存。然而，实现应该尽量避免为小类型的值例如int在堆上分配内存。
> 对于一个std::any对象，如果你赋值为一个字符串，它将会分配内存并拷贝字符串，并存储记录当前的值
> 是一个字符串。之后，可以使用运行时检查来判断当前的值的类型。为了将当前的值转换为真实的类型，必须
> 要使用any_cast<>。
> 和std::optional<>、std::variant<>一样，std::any对象有值语义。也就是说，拷贝被实现为深拷贝，
> 会创建一个在自己的内存中持有当前值的独立对象。因为可能会使用堆内存，所以拷贝std::any的开销一般
> 都很大。更推荐以引用传递对象，或者move值。std::any支持部分move语义。

用虚函数实现 any 可见 *Codes - C++ - any*，与 *function* 类似。
不过虚函数需要运行时寻址，而且指针+虚表指针就要 16B，并不是很高效。在对象较小时，可以放在栈上，避免动态分配。

**optional**

> https://www.bilibili.com/video/BV1xa4y1z7jJ/
>
> 在编程时，我们经常会遇到可能会返回/传递/使用一个确定类型对象的场景。也就是说，这个对象可能有一个
> 确定类型的值也可能没有任何值。因此，我们需要一种方法来模拟类似指针的语义：指针可以通过nullptr来
> 表示没有值。解决方法是定义该对象的同时再定义一个附加的bool类型的值作为标志来表示该对象是否有值。
> std::optional<>提供了一种类型安全的方式来实现这种对象。
> 可选对象所需的内存等于内含对象的大小加上一个bool类型的大小。因此，可选对象一般比内含对象大一
> 个字节（可能还要加上内存对齐的空间开销）。可选对象不需要分配堆内存，并且对齐方式和内含对象相同。
> 然而，可选对象并不是简单的等价于附加了bool标志的内含对象。例如，在没有值的情况下，将不会调用内
> 含对象的构造函数（通过这种方式，没有默认构造函数的内含类型也可以处于有效的默认状态）。
> 和std::variant<>、std::any一样，可选对象有值语义。也就是说，拷贝操作会被实现为深拷贝：将创
> 建一个新的独立对象，新对象在自己的内存空间内拥有原对象的标记和内含值（如果有的话）的拷贝。拷贝一
> 个无内含值的std::optional<>的开销很小，但拷贝有内含值的std::optional<>的开销约等于拷贝内含值
> 的开销。另外，std::optional<>对象也支持move语义。

[std::optional](https://zh.cppreference.com/w/cpp/utility/optional) 存储一个可选值，即既可以存在也可以不存在的值。

使用起来类似一个指针，通过 bool 判断是否含值，通过 operator */-> 来访问。

**expected**

TODO

https://zh.cppreference.com/w/cpp/utility/expected

**tuple**

[tuple (元组)](https://zh.cppreference.com/w/cpp/utility/tuple) 可以把一组类型任意的元素组合到一起，且元素的数量不限。
是一个不包含任何结构、快速简单的容器，可用于函数返回多个返回值。

用`std::make_tuple()`、列表初始化（`{1, "abc", 2.0}`）、构造函数（`tuple<int, double> t(1, 1.0)`）都可以构造 tuple 对象。
用`std::get<index>()`来根据下标获取 tuple 对象的某个元素。注意 index 必须为 constexpr，在写代码时确定，所以 tuple 无法循环遍历。

通过`std::tuple_size<decltype(t)>::value`获取元素数量，`std::tuple_element<index, decltype(t)>::type`获取元素类型（可用于声明变量）。
如果两个 tuple 元素数量相同、各元素类型各比较，则可比较。

> 为什么不能写 tuple[1]？
> 函数参数不会被当成编译期常量，不能用于编译期或做模板参数。还要保证传入的不是变量。

[std::tie]() 可用于解包 tuple。

```cpp
std::tie(a, b, c) = tp; // 绑定三个元素
// 如果要忽略绑定某些值，可以用 std::ignore
std::tie(std::ignore, std::ignore, c) = tp;
// std::tuple_cat 可以连接多个 tuple 和 pair
auto tp2 = std::tuple_cat(tp, std::make_pair("Foo", "bar"), tp, std::tie(n));
```

C++17 [结构化绑定](https://zh.cppreference.com/w/cpp/language/structured_binding)可以使用`const auto& [a, b, c]`绑定数组、元组、类成员。见 *C++ - 结构化绑定*。

> tuple 可以使用模板形参包：
>
> ```cpp
> template <typename... Ts>
> struct A {
> 	// Ts... members; // CE
> 	tuple<Ts...> members;
> };
> ```
>
> 除此之外，tuple 就没有什么唯一特别的功能了。
> 提案 [p3115r0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3115r0.pdf) 描述的特性会使 tuple 失去这唯一特别的功能。

**reference_wrapper**

[std::reference_wrapper](https://zh.cppreference.com/w/cpp/utility/functional/reference_wrapper) 模板类可以将 T 类型对象或函数的引用包装成对象。这种对象可复制、可存储于容器，并且能隐式转换成指向原对象或函数的 T& 引用。

可通过 get 和 operator & 获取原对象的引用；可通过 operator () 调用存储的函数。
实际上就是存储了一个指针。

reference_wrapper 常用于为 bind 和 thread 按引用传递对象。也可以在无法存储引用的容器中（比如 vector，要求元素可复制）存储对象的引用。

```cpp
list<int> l(10);
iota(l.begin(), l.end(), -4);
// 不能在 list 上用 shuffle（要求随机访问），但能在 vector 上使用
vector<reference_wrapper<int>> v(l.begin(), l.end());
ranges::shuffle(v, mt19937{random_device{}()});
```

**ref**

[std::ref<T>](https://zh.cppreference.com/w/cpp/utility/functional/ref) 函数用来生成 reference_wrapper<T>。
std::cref<T> 用来生成带 const 的 reference_wrapper<const T>。

```cpp
template <class T>
constexpr reference_wrapper<T> ref(T& val) noexcept {
    return reference_wrapper<T>(val);
}
// 不接收右值
template <class T>
void ref(const T&&) = delete;

// 对 reference_wrapper 使用 ref 时，复制一个 reference_wrapper
template <class T>
constexpr reference_wrapper<T> ref(reference_wrapper<T> val) noexcept {
    return val;
}
```

**byte**

[std::byte](https://zh.cppreference.com/w/cpp/types/byte) 

> 通过std::byte，C++17引入了一个类型来代表内存的最小单位：字节。std::byte本质上代表一个字节的
> 值，但并不能进行数字或字符的操作，也不对每一位进行解释。对于不需要数字计算和字符序列的场景，这样
> 会更加类型安全。
> 然而，注意std::byte实现的大小和unsigned char一样，这意味着它并不保证是8位，可能会更多。

**destroy_at**

[std::destroy_at](http://zh.cppreference.com/w/cpp/memory/destroy_at) 销毁指定位置的对象：对于非数组类型，调用析构函数；对于数组类型，C++20 前非良构，C++20 起按顺序析构每个元素。（C++17 起）

**destroy**

[std::destroy](https://zh.cppreference.com/w/cpp/memory/destroy) 销毁指定范围中的对象，即对每个元素调用`destroy_at(addressof(*p))`。（C++17 起）

destroy_n 类似，从某一位置开始销毁 n 个元素。

**construct_at**

[std::construct_at](https://zh.cppreference.com/w/cpp/memory/construct_at) 在指定地址创建 T 对象，通过实参 args... 初始化。（C++20 起）

**uninitialized_copy**

> copy 是复制到已初始化内存，要使用 operator =（当类型是*可平凡复制赋值*时，可使用 memmove）；uninitialized_copy 是复制到未初始化内存，要使用拷贝构造（当类型是*可平凡复制构造*时，可使用 memmove）。

[std::uninitialized_copy](https://zh.cppreference.com/w/cpp/memory/uninitialized_copy) 将指定范围的元素复制到从另一位置开始的未初始化内存。

等价于：

```cpp
for (; first != last; ++d_first, (void) ++first)
    ::new (static_cast<void*>(address_of(*d_first)))
        typename iterator_traits<NoThrowForwardIt>::value_type(*first);
// 实际的实现还会 catch(...) 并析构已构造元素
```

uninitialized_copy_n 类似，从某一位置开始复制 n 个元素到从另一位置开始的未初始化内存。

**uninitialized_fill**

[std::uninitialized_fill](https://zh.cppreference.com/w/cpp/memory/uninitialized_fill) 将 value 复制到指定范围的未初始化内存。

uninitialized_fill_n 类似，将 value 复制到从某一位置开始的 n 个元素的未初始化内存。

**uninitialized_move**

[std::uninitialized_move](https://zh.cppreference.com/w/cpp/memory/uninitialized_move) 将指定范围的元素移动到从另一位置开始的未初始化内存。（C++17 起）
如果抛出异常，则已移动的元素不会被恢复，会处在移动后未指定的状态。

uninitialized_move_n 类似，从某一位置开始移动 n 个元素到从另一位置开始的未初始化内存。

**uninitialized_default_construct**

[std::uninitialized_default_construct](https://zh.cppreference.com/w/cpp/memory/uninitialized_default_construct) 将指定范围的未初始化内存进行默认初始化构造。（C++17 起）

等价于：

```cpp
for (; first != last; ++first)
    ::new (static_cast<void*>(addressof(*first)))
        typename iterator_traits<ForwardIt>::value_type;
```

uninitialized_default_construct 类似，将某一位置开始的 n 个位置进行默认初始化构造。

**uninitialized_value_construct**

[std::uninitialized_value_construct](https://zh.cppreference.com/w/cpp/memory/uninitialized_value_construct) 将指定范围的未初始化内存进行值初始化构造。（C++17 起）

uninitialized_value_construct 类似，将某一位置开始的 n 个位置进行值初始化构造。



**分配器** / **Allocator**

> allocator 中的类型 T 实际上是多余的，最初是希望 allocator 在分配后也负责构造对象，所以传入 T，实际并不常用，都是容器自己构造和析构。
> 如果要自己设计分配器，只需要在构造时传入内存大小和对齐即可，不需要带类型。

[allocator](https://zh.cppreference.com/w/cpp/memory/allocator)



```cpp
allocator<std::string> alloc;
string* p = alloc.allocate(sz);

uninitialized_fill(p, p + sz, "a");
for (string* i = p; i != p + sz; ++i) {
    cout << *i << '\n';
    i->~basic_string<char>(); // 不能 ~string()
}
alloc.deallocate(p, sz);
```





**allocator_traits**

通过对 allocator_traits 进行特化，用户可以用任何类型作为 allocator。









-----

## STL - 容器库

> 标准中，basic_string 不是容器，但行为与容器非常相似。为方便起见，将其称为*伪容器* (pseudo container)。

**使用 STL 时要注意的问题**

vector 提供了`.at(pos)`，可以代替`[]`获取元素。at 会检查下标是否合法，非法的话将抛出异常`std::out_of_range`。
为了提高性能，对于 [] 程序并不会去检查边界，可能会导致 UB。

`.size()`的类型是无符号的，如果 size 为0，使用 size() -1，则结果是无符号最大值。
所以在循环中，不要写`i <= size-1`。
此外，int 在与无符号数比较时，也会被转为无符号。所以负数在与无符号相比时，会被转换为一个大值！所以最好使用无符号数（如 size\_t）作为下标。

遍历容器时，尽量使用`const auto& v: container`，而不是自己说明类型（如：`const int& v: vec`，这个例子还比较简单）。
因为自己写的类型可能写错，比如 map 的类型是`typedef pair<const Key, T> value_type;`，如`pair<const std::string, int>`，如果写成了`pair<std::string, int>`，对每个元素都会发生一次拷贝。

判断为空时，使用`empty()`而非`size() == 0`。虽然 C++11 保证了 size 也是 O(1) 的，但应使用语义更明确、简洁的函数。

对容器进行 swap 是 O(1) 的（只交换指针）。但例外是 std::array，swap 将交换每个元素的值，所以为 O(n)。
所以，当 swap array 后，原来 array 上的迭代器还依然指向原来的元素，但是值变了；swap 非 array 的容器后，原来容器上的迭代器将指向对方容器上的元素，但指向的元素的值不变（array 和 vector 的区别好像就是可以直接交换）。

**insert 与 emplace**

使用 map/unordered_map 时，如果想在一个元素没有的情况下才插入，需要先 find，确定没有再 insert。这需要两次查询。
map 的 emplace 能够在元素不存在时才进行插入，并返回`pair<iterator, bool>`，只需要一次。例：`auto [iter, insert_ok] = m.emplace("key", 0);`。
而且 emplace 可以原地构造，在给出构造参数的情况下可避免一次移动。

但是即使元素存在，emplace 也可能会进行构造对象。try_emplace 会在元素不存在时不进行构造，所以更适合检查并插入。
但 try_emplace 的参数里的表达式不可避免要执行和求值，比如：函数表达式会被调用。

> 注意，使用 insert 插入非 const& 的 value_type 时 (pair<const Key, T>)，可能会比插入带 const& 的 value_type 开销更大。
> 对于 value\_type，(unordered\_)map 有三个重载：`insert(const value_type&)`、`insert(value_type&&)`、`template <class T> insert(T&& value)`。前两个是 ok 的，问题出在第三个，即 value_type 既不是 const& 也不是 && 的情况。
> 第三个 insert 会调用`emplace(forward<T>(value))`。由于 1. 即使元素存在，emplace 也会先通过 value 构造新节点，然后再比较新节点的 key 是否已出现过；2. value 既不是 const& 也不是 &&，所以要拷贝到新节点。所以它总会发生一次拷贝。
>
> 前两个 insert 可以先用参数中的 key 比较，再决定是否构造新节点，所以如果 key 已存在，不会出现额外拷贝。
> 根本原因还是第三个 insert 允许任意类型 T，只需要 T 可转为 value_type，为了便于实现直接可以用 emplace 的语义完成。但其实如果 T 就是 value_type，或 T 的第一个参数就是 key，那么本可以避免插入。
> 具体还是看实现，应该问题不大。如果要改可以用 as_const 产生一个 const&。

**可移动赋值 [(MoveAssignable)](https://zh.cppreference.com/w/cpp/named_req/MoveAssignable)**

如果 T 满足可移动赋值，则对于 T 类型的可修改左值表达式(T&) t，或 T 类型的右值表达式(T&&) rv，语句`t = rv`返回 t 且可实现赋值。
很多 STL 模板的类型 T，都需满足可移动赋值。

该类型至少要满足两个条件之一：

1. 实现了接收值或`const Type&`的复制赋值运算符，该参数也可绑定右值的实参。
2. 实现了移动赋值函数。

可移动构造类似，对应构造函数。

**clear**

容器的`clear()`都是 O(n) 的，因为要调用每个元素的析构函数。
不过，如果容器是连续存储的（如 vector），且元素的析构函数是平凡的（如 POD 类型），可以在常量时间内完成 clear。
（trivially-destructible types：析构函数是默认的，即什么都不需要干，使用该空间前初始化即可）
调用后 capacity 不变，不会释放已有的内存。

**释放内存**

对于包含 reserve、capacity 的容器，`clear()`不会释放容器的内存，以便复用供之后使用。
对于 vector，clear 后它的 capacity 是不变的。但可以使用`shrink_to_fit()`，或`std::vector<int>().swap(v)`。后者是定义了个临时 vector，在退出作用域（这里由于是右值所以会立刻释放）时析构、自动释放内部元素。

对于其它容器，只能在 clear 前，遍历所有元素自己去 delete 它？
map、set、list、deque 等不需要 reserve 与 capacity，因此 clear 就会直接释放内存（除非是用户定制的 Allocator？）。

> 注意，容器释放内存是指把它使用的内存还给 allocator，并不保证它被还给内存（这是 allocator 的事），所以可能观测不到。
> std::allocator 使用 malloc，malloc 在分配大内存时使用 mmap，因此直接创建大 vector 后释放内存，可能会通过 munmap，其返还的内存就能被观察到。

**容器内元素的生命周期**

容器在析构，或执行 erase, clear 等函数时，会执行内部元素析构函数，释放对象。

注意，如果容器内部存储的是指针，容器不会释放指针指向的对象。如果需要，在 erase 或 clear 前必须自己 delete 掉，否则一样会内存泄露。

**vector 迭代器**

迭代器失效规则：https://zh.cppreference.com/w/cpp/container

1. 当执行 erase 时，指向删除节点及之后的全部迭代器将失效。
    erase 可以删除节点，也可以删除区间，都是用迭代器指定。erase 将返回删除前的下一个位置。
    所以在迭代中有 erase 时，应使用`it = erase(it)`，而不是`++it`。
2. 在 push_back 后，end 操作返回的迭代器肯定失效。
3. 在 push_back 后，若容量发生改变，则需要重新加载整个容器，所有的迭代器都会失效。
4. 在 push_back 后，如果空间未重新分配，指向插入位置之前的元素的迭代器仍然有效，但指向插入位置之后的元素的迭代器全部失效。
5. shrink\_to\_fit 后都会失效。

**容器迭代器的有效性**

对于节点式容器(map, list, set)元素的删除，插入操作会导致指向该元素的迭代器失效，其他元素迭代器不受影响。

**常量迭代器**

`cbegin()`与`cend()`返回一个`const_iterator`（`const_cast<const C&>(a).begin()`），而普通的`begin()`与`end()`返回的是`iterator`。`crbegin()`、`crend()`同理。
const\_iterator 不能更改对应的元素。
对于 const 修饰的 vector，只能调用 cbegin()（只能使用 const 迭代器），不能调用 begin()。

**线程安全**

大部分 STL 都是不保证线程安全的。
即使一写多读，也容易出问题，比如：vector 的 push\_back 和 unordered\_map 的 resize 会导致元素迁移，旧的指针失效。

对于 vector，可以预先 resize n 个元素，当数组使用，以避免扩容导致的问题。

> vector 的 reserve 只是保证 vector 有容纳 n 个对象的空间，而 resize 会构造 n 个对象，并且将容量重新调整到 n。
> reserve 只在容量小于 n 时进行扩容；而 resize 在容量小于 n 时 append n-cap 个元素，在容量大于 n 时 erase 末尾的 cap-n 个元素。
> [resize](https://zh.cppreference.com/w/cpp/container/vector/resize) 后面 append 的元素只会调用默认构造初始化。可以传入一个 value 表示 append value 的副本。
> 当 resize 的大小比容量小时，会调整长度，但多余的空间只有在 shrink_to_fit 后才会被释放。
> 但是 shrink_to_fit 也不保证会进行回收和内存重分配？
>
> vector 中会维护三个迭代器：first（容器的起始位置）、last（最后一个元素的结束位置）、end（容器的结束位置）。

**vector 实现**

vector 有4个必须的成员：begin、end/size、capacity、allocator。
allocator 可以是自定义的分配器，但通常是 std::allocator，就是一个对 operator new 和 operator delete 的简单包装的空类，通常不需要空间。但由于空类的大小为1和内存对齐，直接包含上述4个成员的 vector 大小一般为 32B。

通过继承包含 allocator 的 vector_base 或者直接私有继承 allocator，可以利用 *空基类优化* 将 vector 的大小减少到 24B。
[MSVC STL](https://github.com/microsoft/STL/blob/main/stl/inc/vector#L429)的实现中通过 [_Compressed_pair](https://github.com/microsoft/STL/blob/main/stl/inc/xmemory#L1486) 一起保存 allocator 和另一个成员，允许 allocator 被空基类优化。
C++20 引入的属性 no_unique_address 也可以允许成员子对象潜在重叠，即允许空基类成员不占空间。

```cpp
template <class A, class B, bool = std::is_empty_v<A> && !std::is_final_v<A>>
struct CompressedPair: A {
	B valB;
};

template <class A, class B>
struct CompressedPair<A, B, false> {
	A valA;
	B valB;
};

template <class T, class Allocator = std::allocator<T>>
class Vector1 { // normal
    T* begin, end;
    size_t capacity;
    Allocator alloc;
};

template <class T, class Allocator = std::allocator<T>>
class Vector2: Allocator { // 继承 Allocator
    T* begin, end;
    size_t capacity;
};

template <class T, class Allocator = std::allocator<T>>
class Vector3 { // 使用继承了 Allocator 的成员
    T* begin, end;
	CompressedPair<Allocator, size_t> cap_alloc;
};

template <class T, class Allocator = std::allocator<T>>
class Vector4 { // 属性
    T* begin, end;
    size_t capacity;
    [[no_unique_address]] Allocator alloc;
};

struct MyAllocator final {
	size_t n;
};

cout << sizeof(Vector1<int>) << '\n'; // 32
cout << sizeof(Vector2<int>) << '\n'; // 24
cout << sizeof(Vector3<int>) << '\n'; // 24
cout << sizeof(Vector3<int, MyAllocator>) << '\n'; // 32
cout << sizeof(Vector4<int>) << '\n'; // 24
```

> https://www.zhihu.com/question/21514513

对象构造包含两部分：分配内存、在内存上构造对象。对于 vector 需要分配元素空间、然后构造各个位置上的对象。
定义类 vector_base 负责内存的分配与释放，vector 专注于对象的构造与析构，可以解耦两个过程、更清楚。它们分别只需要处理各自的异常情况，便于实现强异常安全。

**vector::data**

虽然能获取 vector 的底层数组并访问修改，但是对 >= size 的位置的修改将不可见；且使用 resize 或 push_back 会在对应位置构造新对象，因此越界的数组修改是无意义的。

**vector::reserve**

reserve 预留空间，但只是分配存储，不会在 index >= size 的位置上构建对象（resize 会，因此有带初始值的重载）。

当需求容量大于当前容量时，reserve 会分配恰好能满足大小的空间，而不是分配略大的或 2 倍的空间。
因此，注意不要在循环中不断触发 reserve！非指数扩容，将导致每次 O(n) 的扩容复杂度！
比如：

```cpp
void addPoints(const vector<Node> &val) {
    points.reserve(points.size() + val.size());
    for (const auto &p: val) {
        points.push_back(p);
    }
}
while (getTwoPoints(val)) {
    addPoints(val);
}
```

批量添加的接口和每次 reserve 都没问题，但外部循环使用该接口时，就会出问题。
因此：

- 通用、常用的接口最好不要每次 reserve，直接 insert 指数增长也不错。

```cpp
v.insert(
	v.cend(),
    std::move_iterator(newElems.begin()),
	std::move_iterator(newElems.end())
);
```

- 或仿照 rust，提供 reserve 和 reserve_exact 两个接口，前者可能分配更大的内存块，避免复杂度上升。
- 或直接使用 resize 和 copy，它也会使用指数增长。

**vector 的扩容**

> https://zh.cppreference.com/w/cpp/container/vector/resize
>
> 面试说的时候多说点，比如：
>
> - 如果 T 满足可移动插入（可从一个该类型的右值构造到未初始化的空间），则 resize 可以选择移动构造避免拷贝。
> - 如果 T 的移动构造没有加 noexcept，则会优先选择复制构造来保证强异常安全，导致移动白写；大量复制还会导致效率降低与内存增长。
> - 如果抛出异常，则该函数不产生任何效果（强异常安全）。
> - 如果 T 满足可移动插入、但没有 noexcept 的移动构造，且不满足可复制插入，则会选择可能抛出异常的移动构造，并且属于未指定行为。
>
> push_back 和其触发的扩容同理。
> 强异常安全保证要求 vector 在申请空间或拷贝元素中出现异常时，恢复到操作前的状态，由用户处理异常。如果是在调用移动构造的过程中出现异常，恢复状态会很难（原对象和容器的状态已经被破坏），因此只有在移动构造是 noexcept 时，才选择移动而非拷贝。

扩容策略（扩容因子）与编译器相关，mingw 中的 gcc 每次扩容2倍，visual studio 中的编译器每次扩容 1.5 倍。是一个扩容次数（即效率）和可能浪费的空间之间的折中。
理论上来说，1.5 倍扩容更好，因为能够复用之前释放的空间（能够提高页表缓存的命中率？或不需要分配新的页）。而 2 倍扩容中每次申请空间，都恰好不能复用之前释放的空间。
但实际中不只有 vector 需要申请内存，很难保证之前分配的是连续的、且没有其它对象使用，所以不一定有用（但内存管理可能会合并已释放的空间）。

> 因为需要先分配再释放，所以扩容倍数在 (1, 1.618) 之间才能够实现复用（就是斐波那契数列）。
>
> Linux 用 伙伴系统 (buddy system) 管理内存。就是将内存按 2 的幂大小划分成不同规格的内存块，同一规格的用链表管理。
> 所以在申请 2 的幂大小的内存块时，是刚好可以分配的，可能效率也不低。

vector 的扩容拷贝，对于 POD 类型，会调用 std::copy（能够直接使用 memmove？）；对于非 POD 类型，会遍历每个对象，调用构造函数进行拷贝或移动。

扩容可以使用移动构造，但必须满足：类拥有不会抛出异常的移动构造函数（使得源码中的`__move_if_noexcept_cond`为 false，才能使用`move_iterator`）。

> 这种容器内部的复制行为 是不能出现异常的，所以只有标记了`noexcept`，才能使用移动构造函数。
> 大多数情况下，移动构造函数都应该用`noexcept`声明。
>
> [move\_iterator](https://zh.cppreference.com/w/cpp/iterator/move_iterator) 在通过迭代器构造时，会使用 move 移动另一个迭代器的所有权，从而移动指向的资源。

**vector 扩容为什么不像 realloc 一样，先检查后面有没有足够空间能直接使用？**

> https://www.zhihu.com/question/384869006
>
> C++ 标准库容器的动态内存分配是由分配器（Allocator）类处理的。所以分配器提供什么接口，标准库容器的内存操作才能用什么。
> 从 C++98 至今标准库的分配器要求都缺少原位扩张/收缩的接口，所以 vector/basic_string 也用不了。实际上有 N3495 、P0401 、 P0894 等零星提案建议增加分配器的接口，以支持这些功能，但是这些提案都没有通过。 
>
> 为什么不能直接用 realloc？
>
> 1. realloc 只能处理 m/c/realloc 分配的内存，虽然默认分配器确实使用 malloc 分配内存但并不能做这种假设，所以不能直接使用 realloc。
> 2. 因为 realloc 在无法分配时会调用 free 和 memcpy 拷贝，所以对象必须是可平凡拷贝的，但 vector 没有这种保证。

**关联容器**

关联容器：对所有元素的检索都是通过元素的 key 进行的，而非元素的内存地址。
如：map, set。

**vector<bool>**

> https://zh.cppreference.com/w/cpp/container/vector_bool
> std::vector（对于 bool 以外的 T）满足容器、知分配器容器、序列容器、连续容器(C++17 起)及可逆容器的要求。
>
> vector<bool> 的读写效率可能略低？但节省了空间、提高了 cache 命中率。
> 它没有容器的特性，无法使用某些 STL 算法和迭代器，所以在用`vector<T>`时一定要考虑 T 是否可能为 bool（可以 enable_if 拒绝 bool）。
> 比如：`T *p = &v[0];`将编译失败，因为 reference 将返回 proxy 类，而非 T&；`auto b = v[0]`与`T b = v[0]`或`bool b = v[0]`不同。
> 此外，对不同元素的读写不再是线程安全的（读写只能以字节为单位），因此不能像普通 vector 一样，并行执行 vector 元素的修改。

`vector<bool>`虽然是 vector 的 bool 特化，但并不是标准的 STL 容器，不支持 STL 的许多功能。
而且里面的元素不是一个个 bool（1字节），而是一个个 bit 或 proxy object，在用`auto v = vec[i]`时很容易出错。

一个 bool 本身是占1字节的。为了减少空间占用，`vector<bool>`将其中的每1个字节看做8个bool，与 bitset 类似。
对于正常的 STL 容器，调用`operator[]`会返回对应元素的引用 T&。但字节是寻址的基本单位，我们没法获取一个位的地址，所以`vector<bool>`调用`operator[]`会返回一个 proxy reference（代理引用）而非 bool&（所以无法赋给一个 bool\* ）。这不是一个真正的引用，而是一个`std::vector<bool>::reference`类型的返回值。它是一个临时的右值，我们无法对它取地址。

使用 auto 将`operator[]`的结果赋值给变量 x 时，x 也将是代理引用，修改 x 将修改容器内的值。这与其它 vector 是不同的（x 将是一个拷贝值）。
如果容器被销毁，x 将变成悬挂指针，再使用是不安全的。

```cpp
vector<bool> vb = {false, false, false};
bool c = vb[0]; // 包含proxy reference到bool的隐式转换
c = true; // 不影响容器
auto d = vb[1]; // 对于非bool类型的vector<T>，auto将返回T而不是引用
d = true; // 影响容器元素
bool *p = &vb[0]; // error:[]返回值并非bool&
```

之所以定义它，是为了减少内存消耗，而 bitset 无法在运行时改变容器大小。
但由于它的特殊性，在模板编程中可能比较危险（vector<T>，但 T = bool）。如果不在意空间，用 vector<char> 或 deque<bool> 作为替代可能更好（后者与 vector 类似，但不会压缩。deque 的随机访问也是 O(1) 的）。

**push_back 与 emplace_back**

emplace_back 功能上可以替代 push_back，但它们的语义有点不同：push_back 侧重对已有对象的复制或临时对象的移动，emplace_back 侧重直接在容器对应位置构造新对象。
如果是直接调构造函数，则可以用 emplace_back；如果是要利用已有对象构造，则用 push_back（虽然 emplace 有同样的功能）。

- 即使实现了移动构造，push_back 也要在容器外先创建一个对象，然后再 move 过去、释放旧对象（如`strVec.push_back("123")`）；而 emplace_back 直接在对应位置进行构造，不需要 move，可能会有一点提升（当对象很小还是 POD 时，拷贝和移动也很快）。
- emplace_back 可读性相对差（不能明确表达放入一个对象），也不太安全。使用时需要明确操作的 vector 的类型，否则可能写错。所以通常还是选择 push_back。
    如：对于`vector<vector<int>> vec;`，`vec.push_back(10)`与`vec.emplace_back(10)`是不同的。如果想在某个数组后添加一个10，那么必须指定下标，如果不指定，用 push_back 会CE，但 emplace_back 会正常运行且不对（实际是在后面建了个大小为10的 vector），所以 push_back 更好些（写错了也能更快发现错误）。
    具体见：https://abseil.io/tips/112
- push_back 是传已构造好的对象，IDE 可以直接帮你判断传的对象对不对，但 emplace_back 如果传错了，只有编译时才能知道。具体见：https://www.zhihu.com/question/387522517
- emplace_back 的构造可以忽略 explicit 限制。

```cpp
std::vector<A> v;
v.reserve(10);

v.push_back(A{1}); // 构造 A{1}，然后移动
v.emplace_back(1); // 原地构造
v.emplace_back(A{1}); // 也可以直接传入对象，同样是构造 A{1}，然后移动
```

**array**

与 C 数组的区别：

- 数组在作为参数传递时会退化为指针，丢失类型和大小信息，但 array 不会。
- 支持赋值操作，支持同类型数组的比较操作。

**forward\_list**

单向链表。与 list 相比，不能双向迭代，但更省空间。
没有 rbegin(), rend()。insert() 改为了 insert_after()，插入时需要指定迭代器，emplace, erase 同理。

没有维护 size，所以无法获得内部元素数量。
max\_size() 会返回容器大小的理论极限，即`std::distance(begin(), end())`。通常很大，没什么意义？

**deque**

deque 使用多个固定尺寸数组来保存元素，所以内部元素不是连续的，但仍可以保证 O(1) 的随机访问（但需要进行两次指针解引用，比 vector 多一次）。
deque 会按需自动扩展或收缩。扩展 deque 比扩展 vector 要高效，因为不需要移动元素，只需分配一个新的小数组。**所以如果要大量在两端插入/移除元素，deque 会比 vector 高效很多。**
但是，deque 有较大的最小内存开销，因为一次要分配一整个小数组。小数组的大小可能为元素大小的 8 或 16 倍。
deque 的遍历好像也不太高效？

类似 vector，可进行  shrink\_to\_fit()。

**容器适配器**

为底层的顺序容器提供不同接口，可利用底层容器实现新的功能。
包括：stack, queue, priority_queue, flat_set/map/multiset/multimap。

**queue**

queue 是一个专为 FIFO 设计的容器适配器。
容器适配器指它本身只是一个封装层，必须依赖指定的底层容器才能实现具体功能（但要求底层容器实现了特定接口）。
默认容器为 deque，可通过模板指定：`template <class T, class Container = deque<T> > class queue;`。
queue 可以接收任何一个支持下列接口的容器作为底层容器：empty(); size(); front(); back(); push_back(); pop_front()。

priority_queue 也只是一个容器适配器，需要指定底层容器才能实例化。默认为 vector<T>。
底层容器必须支持随机访问和以下接口：empty(); size(); front(); push_back(); pop_back()。

stack 也是，默认为 deque。

**proxy class**

代理类，指“它的所有对象都是为了其它对象而存在的，就像对象的代理人”。
见：
https://www.cnblogs.com/reasno/p/4858490.html
https://blog.csdn.net/weixin_28712713/article/details/82316047

**string**

> string 本身是与 \0 无关的，输出时也不会因此停止（会将 \0 直接输出）。
> 但是，string 要能支持转为 const char*，标准规定通过 [c_str](https://zh.cppreference.com/w/cpp/string/basic_string/c_str)、data 返回的指针指向的字符串，其末尾一定要有空终止字符。通常情况下，为了避免拷贝、直接完成转换，string 的实现仍然会在字符串的最后添加 \0（本质还是 Unix/C 字符串要以 \0 结尾带来的问题）。
> size、capacity 不会计入补充的 \0（因为这也不是标准规定的。因此 SSO 优化后的容量是15 而非16），因此 string 实际保存的字符数是 capacity + 1。
> 当 size < capacity 时，size ~ capacity-1 部分的字符都会被初始化为 \0。
>
> 对于 [operator []](https://zh.cppreference.com/w/cpp/string/basic_string/operator_at) 和 at，标准规定在 pos == size 时，结果返回到拥有值 CharT() 的字符（空字符）的引用（当然不应修改）。pos > size 时才是 ub。
>
> 注意，在将 const char* 赋给 string 时，会以 \0 为终止符（后面的不会被赋值）。只有使用 string 字面量、或使用 string(const char*, size_t len) 指定赋值长度时，才会忽略终止符。
> 比如：`string a("\012")`的结果是大小为0的空串，在定义时指定长度`string a("\012", 3)`的结果才正确（指定的长度不能超过传入的字符串字符数，包括\0）。
> （注：有时字符串中的`\012`会被识别成一个字符？导致它不是一个 \0。原因未解决）
>
> ```cpp
> using std::literals::operator""s;
> cout << string("a\0a"s) << '\n'; // aa
> cout << string("a\0a") << '\n'; // a
> ```

> **capacity**
>
> string 的容量可以比 size 更大，这样后面赋值新的、不超过容量的字符串时，就不需要重新分配内存。
> 分配器分配了大内存、先赋值大串再赋值小串、SSO 优化都能导致容量大于大小。

> 标准库的 string 没有统一编码、不处理编码（没有编码的概念，但可能很难，因为编码和带来的问题也复杂），需要自行处理编码问题。
>
> GCC 的 libstdc++ 的 string 实现中，在 SSO 优化的情况下使用了自引用，因此不是 relocatable 的，无法应用 relocate 优化（见 *其它 - relocatable*；问题见[这里](https://www.zhihu.com/question/643989678)）。
>
> 其实现的 string 结构为：
>
> ```cpp
> struct string {
> union {
>   char buffer[16];
>   size_t capacity;
> } m_storage;
> size_t m_size;
> char* m_data;
> };
> ```
>
> 当 size 小于 16 时，使用 buffer 做存储（所以字符串的大小为 32，最小容量是 15）。
> 但这样有个问题：每次访问数据时，都要判断 size 来决定用 data 还是 buffer。为了减小这个开销，libstdc++ 在 size 小于 16 时让 data 直接指向 buffer，这样任何情况都可以直接使用 data，无需判断。
> 但自引用会导致其无法进行 relocate。
> 此外，当 string 作为局部变量分配在栈上、且 size 小于 16 时，data 会指向自动存储期的内存（栈内存），导致 string 此时不是 constexpr 的（只有静态存储期对象的指针或地址才是编译期常量，见 *C++ - 编译期取地址*）。

**string 的其它实现方式**

> COW：https://www.cnblogs.com/promise6522/archive/2012/03/22/2412686.html

常见的 string 拷贝方式即为全部拷贝，称为 eager copy。
另一种方式为 copy on write (COW) 或 lazy copy，在两个 string 对象进行拷贝时不分配新内存，只在发生修改时进行拷贝。
COW 减少了不必要的资源分配，减少了分配和资源带来的延迟（但如果要写，只是把这部分工作延后了，可能反而影响性能）。

通过下面的代码可以判断 std::string 是否使用了 COW：

```cpp
std::string a = "A medium-sized string to avoid SSO";
std::string b = a;
// a.data() == b.data() true // C++11 中，data() 与 c_str() 是相同的

b.append('A');
// a.data() == b.data() false
```

COW 只发生在两个 string 对象进行拷贝构造和赋值上，如果使用 (const) char\*（如 s.data()）赋值还是会发生拷贝，因为 string 无法确定和控制 char\* 所指对象的生命周期。
所以通过`std::string b = a.data();`可以避免 COW。
但是 COW 由于以下缺点，C++11 起禁止 string 使用 COW，并且没有多少库会用到：

- std::string 本身不是线程安全的，但在两个线程内使用不同的 string 必须是线程安全的（C++ 标准要求，如果库的组件要瞒着用户在多个对象间共享内存，则必须自己保证线程安全）。

    COW 的 string 共享了数据，所以要保证线程安全。COW 是通过用一个`atomic<size_t>`做引用计数来保证的。
    拷贝或创建一个字符串时，将计数器原子加一；如果要修改一个字符串，首先将计数器原子减一，然后分配和拷贝一个新的字符串。如果发现计数器为0，还会释放原字符串。
    但频繁的原子操作可能会影响性能。

- 当使用 string 的非 const 函数返回引用时（如 operator[], at()），由于无法确定之后是否修改该引用，string 必须进行拷贝。
    所以访问`str[0]`就会发生字符串拷贝，即使不做出任何修改；甚至访问迭代器`begin(), end()`也要进行拷贝，因为迭代器是可以修改字符串的。

    除非根据只读还是非只读，对字符串的访问方式进行严格区分（比如`cbegin()`，或像`vector<bool>`中的`[]`返回一个代理引用 proxy），否则无意义的拷贝还是非常容易发生。

> folly 只是字符串长度较大时，才使用 COW（最常见的还是小串）。
>
> 在使用 lazy copy 对象的 operator[] 时，类无法确定使用 operator[] 的语句是否会做出修改。为此可以返回一个 proxy class，代理类保存了父对象的引用，在使用 operator = 时再进行拷贝。
>
> 上面的方式叫做 lazy evaluation？
> lazy evaluation：惰性计算，不仅包含 lazy copy，还要将一个表达式的值的计算尽可能拖延，直到这个表达式真正被使用的时候。
> 典型的例子是 python 中的 generator，只在每次使用时 yield 生成新的元素。
> 另一个概念是 lazy fetch，如果一个对象 a 有很多大对象，并且它们需要从硬盘或数据库中读取，那么我们在创建 a 时不需要将 a 的所有对象进行初始化，而是只初始化需要的子对象。可以将不用的对象值替换为空指针，在使用时获取。

**SSO**

SSO（small string optimization，也可以叫 SOO (small object optimization)）一般用于短字符串，就是将较小的字符串直接存在 string 对象里，而不是存在堆然后用指针保存。能够少一次指针访问，并且对于局部创建的字符串，SSO 会把字符串直接放到栈里。
由于栈空间大小限制，以及 string 数组的需求（大对象的数组太慢），只适合很小的字符串。

> [ddb](https://github.com/duckdb/duckdb/blob/main/src/include/duckdb/common/types/string_type.hpp) 的 SSO 实现为：对于长度不超过12的字符串，用4B存储长度，8B存储字符；对于长度超过12的字符串，用4B存储长度，4B存储字符串的前4个字符，8B存储字符串指针。
> 这种保存4字符前缀的 SSO 可以优化字符串的比较：很多情况下，前4字符就足够比较两个字符串，可以减少一次间接访存。
> 此外，可以直接将前8B（长度和前4字符）作为一个 uint64_t 读取比较，减少一次比较。
>
> <img src="https://cdn.jsdelivr.net/gh/Apricity-qvq/ImageHostForTypora//img/image-20240529235710534.png" alt="image-20240529235710534" style="zoom:67%;" />
>
> 实现只需要 union 两个 struct 即可。
>
> ```cpp
> union {
>  struct {
>      uint32_t length;
>      char prefix[4];
>      char *ptr;
>  } pointer;
>  struct {
>      uint32_t length;
>      char inlined[12];
>  } inlined;
> } value;
> ```

**FBString**

> https://zhuanlan.zhihu.com/p/348614098

是 folly 库实现的 string。
会根据字符串的长度决定是否使用 COW：将字符串按 24、256 分成三类：长度 <24 （大小 <24B）的为 small string，长度在 [24, 255] 的为 medium string，长度大于等于 256 的为 large string。

字符串的主要存储结构是一个 union：

```cpp
union {
    uint8_t bytes_[sizeof(MediumLarge)];          // For accessing the last byte.
    Char small_[sizeof(MediumLarge) / sizeof(Char)];
    MediumLarge ml_; // 大小为24B
};
struct MediumLarge {
    Char* data_;
    size_t size_;
    size_t capacity_;
};
```

small string 使用 SSO，即直接使用 small_ 字段（对象本身）存储字符串。如果是局部对象会用对象本身的栈空间。
medium 和 large string 使用 MediumLarge 结构存储字符串的指针，字符串被分配到堆上。
不同的是，medium 使用 eager copy，即拷贝时直接复制；large string 使用 COW，还有一个 RefCounted 对象进行引用计数。

FB 对 COW 也有改进，会将 operator[] 和迭代器 begin() 分成 const 和 non-const 版本，使用`const char &c = str[0]`会调用 const 修饰的函数。
非 const 的访问会调用非 const 的 begin()，会调用`mutableData()`，将计数器减一、拷贝一个新的字符串；而 const 的 begin() 直接获取`data()`，不会拷贝。

```cpp
iterator begin() { return store_.mutableData(); }
const_iterator begin() const { return store_.data(); }
const_iterator cbegin() const { return begin(); }
// end, rbegin, rend 同理。rend 是一个 reverse_iterator(begin())

const_reference operator[](size_type pos) const { return *(begin() + pos); }
reference operator[](size_type pos) { return *(begin() + pos); }

const_reference at(size_type n) const {
    enforce<std::out_of_range>(n < size(), "");
    return (*this)[n];
}
reference at(size_type n) {
    enforce<std::out_of_range>(n < size(), "");
    return (*this)[n];
}
```

**使用 string 要注意的问题**

- string 是一个字节流，下标访问得到的是一个字节 (一个 char)，而非完整的 Unicode 字符。所以如果存汉字，不能用下标取。只是输出到流还是能拼接成完整字符。
    可以看看 wstring（但好像也不好用）。注意编码问题，ide、文件、cmd 的编码格式要一致。
- string 用 substr 取一个子串，都会拷贝一个新串，即使并不会发生修改。
- 不要使用 std::string 定义常量，还会导致分配堆内存（常量应该可以避免这点）。
    可以使用`constexpr char s[] = "const string";`，但在使用时要写成`const char*`？取长度是 O(n) 的，需要传递长度参数。
    也可使用 string\_view：`constexpr std::string_view s = "const";`或`constexpr auto s = "const"sv;`。与 char 数组相比获取长度是 O(1) 的，也有很多常用方法。
- 析构函数非平凡。因为全局对象销毁顺序难以预测，所以存在生命周期结束后被访问的风险（如 std::string 被其他全局对象引用）。
- 将 string 的底层数组传给 const char\* 时，要用`c_str()`而不是`data()`！后者不保证 \0 结尾（只是通常实现上是）。
- 通过`c_str()`或`data()`获得的指针，不应被传给任何非 const 指针；不能通过其进行写入；不应在其上调用非 const 成员函数。（但实际上修改是 ok 的，只要原 string 不是 const 对象？文档要求不能改，是因为早期没有规定 string 的实现，如果是 COW 修改就是不合法的）
    （C++17 后可以，因为提供了非 const 版本的 .data() 重载）

**string_view**

> 注意，如果形参为 const string&，传递的实参为 const char\*，则会构造一个临时 string；如果形参为 const char\*，则传递 string 只能用 s.c_str 作为实参。使用 string_view 作为形参，就可以随意传递 string 或 const char\*、不用担心构造临时对象、在堆上分配内存（如果没被 SSO 优化）的开销。
>
> 它不以 \0 结尾，也没有`.c_str()`，所以不会在构造或使用时拷贝字符串，但无法用于 C 字符串接口。

[std::string\_view](https://zh.cppreference.com/w/cpp/string/basic_string_view) 在 C++ 17 引入。是一个字符串的视图，不能修改字符串，不会控制字符串的生命周期。所以构造 string\_view 并不会发生字符串的拷贝，但程序员要保证它指向的对象始终合法（只要它还存活）。
string\_view 只包含一个指向数据的指针和长度，是非常轻量的。

提供了`.data()`，返回指针字段；但没提供`.c_str()`，因为它与 C 风格字符串的语义不同（不依赖结束符、只是一个子串/切片）：

- string 和 char 数组，都使用空字符 (NUL) 作为字符串的结束标志；而 string\_view 使用长度，对字符串内的空字符并不关心（还会输出）。
    所以 string\_view 没有要求必须以空字符结束（可能有也可能没有），在使用`data()`时要小心，比如：直接输出 string\_view 是正确的，但获取`sv.data()`再进行流输出，可能是错的（因为类型是 const char*）。
- string\_view 可能通过截取一个字符串的子串产生，用长度字段指定结束位置。
    所以输出`sv.data()`的结果，可能比输出 sv 的结果更长，且不符合预期。

此外，通过默认构造得到的空 string_view 的`data()`会返回空指针，因此使用`data()`和`operator []`前应该先用`size()`获取长度或检查`data()`的返回值。

C++17 的命名空间`std::literals`中重载了[""sv 运算符](https://zh.cppreference.com/w/cpp/string/basic_string_view/operator%22%22sv)，用于定义 string_view 字面量。
也允许通过 ""s 定义 string 字面量（"abc" 在转换前是一个const char*，不能直接 operator+，但 "abc"s 就是一个 string）

```cpp
using namespace std::literals;

std::string_view s("abc"sv);
std::string add = "abc" + "123"; // error: invalid operands of types 'const char [4]' and 'const char [4]' to binary 'operator+'
std::string add = "abc" + std::string("123"); // 可能ok，会进行类型转换
std::string add = "abc"s + "123"s; // ok
```

**使用 string_view 要注意的问题**

- 不要将临时字符串赋值给 string_view（或者不要将返回值赋给 string\_view）。

对于返回字符串的函数`string f()`，使用它初始化一个 string 或 const string& 都是安全的（后者会延长其生存期），但用它初始化 string\_view 是错误的：它既不拷贝也不延长其生存期。

- 当返回类型是 string_view 时，不要返回 string（只可返回传入的安全的 string\_view 实参，或者尽量不要返回 string\_view）。

函数无法保证返回的 string\_view 是否引用了临时或将要销毁的 string。此时应返回 string 或 const string&（并使用 string 接收；前者还可以使用 const string&/string&& 接收）。

```cpp
string_view f(const string& s) {
	return s;
}
auto sv = f("abc");
cout << sv; // 引用的字符串已销毁
```

- 不要在调用链中使用 string_view 来初始化 string，即不要在那些会把参数传递给 string 的 API 中使用 string\_view。
    - 不要用 string\_view 形参来初始化 string 成员（将无法移动）。
    - 不要将 string 做为 string\_view 调用链的终点（会发生拷贝，使用 view 没有意义）。即如果后面要赋值给 string，那在前面使用 string\_view 没什么意义。

如果一个调用链的中途或最后需要 string，使用 string_view 可能适得其反：

```cpp
struct Person {
	string name;
	Person(string_view n): name{n} {} // bad
    // Person(string n): name{move(n)} {} // good，应使用 copy then move
};
Person a{"A"}; // ok 传递字符串字面量
string s = "B"
Person b{s}; // ok 传递 string 左值
Person c{move(s)}; // 无效移动：通过 string_view 初始化 name 时，依然需要拷贝，不会发生移动
```

- 涉及 string_view 时，函数模板应该使用 auto 作为返回类型，而不是 T 本身；不要将返回泛型类型 T 的函数模板的返回值赋给 auto。

```cpp
// ok，返回 string
string operator+ (string_view sv1, string_view sv2) {
	return string(sv1) + string(sv2);
}
// error：传入 string_view 时返回类型也是 string_view
// 如果是 auto concat(...) 就没有问题
template<typename T>
T concat (const T& x, const T& y) {
	return x + y;
}

string_view hi = "hi";
auto s = concat(hi, hi); // s 是 string_view。如果是 string s = concat(...); 就没有问题
cout << s << '\n'; // error
```

- string_view 后没有 \0。

C 的 atoi 等函数需要以 \0 作为结束符，因此虽然 string 勉强能用 atoi，但 string_view 不能用，需要用 [from_chars](https://zh.cppreference.com/w/cpp/utility/from_chars)（stoi 只接收 const string&，传递 string_view 将发生拷贝）。

```cpp
int i;
string_view sv = "213";
auto result = std::from_chars(sv.data(), sv.data() + sv.size(), i);
if (result.ec == std::errc::invalid_argument) {
	cout << "Could not convert.";
} else {
	cout << i << '\n';
}
```

**格式化输出容器**

通用的格式化输出函数是流，输出到 sstream 就是字符串，输出到 ostream 就是打印。
现在可以用 format 库，见：https://www.zhihu.com/question/586364098

**std::allocator / 内存管理**

TODO

一些旧的 STL 里的 std::allocator 实现了二级内存池，但随着 malloc 的改进，这基本不需要了，std::allocator 都只是 operator new 或者 malloc 的一层封装。

> 在使用基于节点的容器（如 map）插入、删除大量节点后，节点的内存可能不会立刻释放。
> 具体见：https://www.zhihu.com/question/483406906
>
> 这是 malloc 的实现导致的，对于小内存块，它会缓存一个 small bin 链表，也就是用户态的一个内存池。但是即使这个链表特别长，也很难触发合并将它们合并成大块内存 或将其释放，导致程序依旧持有大量内存。
> 而 vector 这类持有连续大块内存的容器，析构后内存往往会被真正释放（但如果它比较短，也可能被缓存）。
> 见 *C++ - 库函数 - malloc*。

**range-based for loop / range for**

[range for](https://zh.cppreference.com/w/cpp/language/range-for) 是比传统 for 可读性更好的版本，实际是个语法糖。
语法为`for (范围变量声明: 范围表达式 ) 循环语句`。C++20 支持初始化语句（见 *新特性 - C++20*）；C++17 允许结构化绑定。

range for 某个 A 类型的容器 a，实际就是迭代器 for：

```cpp
for (auto v: a) ...
// 等价于
for (auto it = a.begin(); it != a.end(); ++it)
    auto v = *it; ...
```

所以只要类实现 begin, end 方法，且它们返回的类型可自增、可比较、可解引用，就能用 range for：

```cpp
struct Array {
	Array(std::initializer_list<int> l) {
		size = l.size();
		data = new int[size]();
		std::copy(l.begin(), l.end(), data);
	}
	~Array() {
		delete[] data;
	}
	// 自定义拷贝构造与赋值
	
	int* begin() { // 迭代器类型为int*，可自增、可解引用。也可自定义类
		return data;
	}
	int* end() {
		return data + size;
	}
	
	int *data;
	size_t size;
};

Array a = {1, 2, 3};
for (auto v: a)
    printf("%d ", v);
```

range for 也可遍历 C 数组，但不能是指向数组的指针。因为 begin 有对 C 数组的特化。
注意如果不加引用，则每次迭代都需要一次拷贝构造。

**span**

TODO

https://godbolt.org/z/j11aKGYnh





---

## STL - 算法库

> range 算法示例：https://www.cppstories.com/2022/ranges-alg-part-one/
>
> 算法库中，默认使用 operator < (C++20 前)/std::less{} (C++20 起) 进行大小比较，使用 operator == 进行等价比较。





**accumulate**

[accumulate](https://zh.cppreference.com/w/cpp/algorithm/accumulate)
注意 accumulate 是一个模板函数，其返回值取决于传入的初始值 init 的类型。
因此使用 0 会返回 int，使用 0ll 才会返回 int64_t，容易出错。

```cpp
template<class InputIt, class T>
constexpr // C++20 起
T accumulate(InputIt first, InputIt last, T init)
{
    for (; first != last; ++first)
        init = std::move(init) + *first; // C++20 起有 std::move
    	// 表达式求值后，init就会被赋新值，所以move了也没事
    	// 不要求 T 重载 operator +=，所以使用该写法
    return init;
}
```

也可用来拼接字符串。

**binary_search**

[binary_search](https://zh.cppreference.com/w/cpp/algorithm/binary_search) 在已划分范围内判断是否有等于 value（`!bool(*iter < value) && !bool(value < *iter)`，或`!bool(comp(*iter, value)) && !bool(comp(value, *iter))`）的元素。返回 bool。
如果序列未划分，则是 UB。

**includes**

[includes](https://zh.cppreference.com/w/cpp/algorithm/includes) 判断一个有序范围是否是另一个有序范围的子序列（非区间，不要求连续）。

**lower_bound**

[lower_bound](https://zh.cppreference.com/w/cpp/algorithm/lower_bound) 在已划分范围内查找第一个不先序于 value 的元素。返回其迭代器，不存在则返回 last。

**reduce**

[reduce](https://zh.cppreference.com/w/cpp/algorithm/reduce)

用 reduce 求和可能比 accumulate 效率更高，因为它允许并行，在语义上就能表达“我不在乎顺序”。
在明确不需要顺序规约时，用 reduce 比 accumulate 更好，语义也更明确。
比如：

- double 因为精度问题不满足结合律，accumulate 就不能主动破坏顺序去并行，但 reduce 可以。
    但在 fast math 或 Ofast（包含前者）编译选项下 accumulate 也可以？但这个等级太高了。
- lambda 很可能不是纯函数，因此编译器要假设其结果可能随执行次数而有所不同，从而 accumulate 不能对它做并行优化。

**all_of** **any_of** **none_of**

[all_of](https://zh.cppreference.com/w/cpp/algorithm/all_any_none_of) 等检查范围中的元素是否都/是否存在一个/是否都不满足谓词。

**copy**

[copy](https://zh.cppreference.com/w/cpp/algorithm/copy) 将指定范围的元素复制到从某迭代器开始的另一范围。

copy 的第一个重载允许输入范围与输出范围重叠，但 output_iter 不能位于 [first, last) 中（可以位于 first 左边），因为 copy 从左到右进行。
对于 copy 的其它重载和 copy_if，如果两个范围重叠，则是 UB。

*copy_backward* 与 copy 类似，但是是逆序复制，并且 output_iter 指向输出位置的末尾（不含它）。所以 output_iter 不能位于 (first, last] 中（可以位于 first 及 first 左边）。
当复制范围重叠时，如果复制到输入范围左侧（目标范围的起始位置在 first 左侧），则使用 copy；如果复制到输入范围右侧（目标范围的结束位置在 last 及 last 右侧），则适合用 copy_backward。

reverse_copy 与 copy 类似，但是复制的结果会逆序排列。如果范围重叠，则是 UB。

**std::copy 与 memcpy**

尽可能使用 copy，因为：

- memcpy 只能用于 POD 或可平凡复制类型，copy 更灵活、支持指针和各类迭代器。
- copy 效率可能更高：copy 会根据类型决定实现，所以效率不会比 memcpy 差；此外 memcpy 的参数是 void\*，编译器无法利用参数类型做可能的优化，而 copy 可以。

copy 的实现中，包含一个主模板和两个特化：

- 对于 const char\*, const wchar\_t\* 的特化：使用 memmove。
- 主模板：如果迭代器是指针类型，且指向可平凡复制赋值类型（copy 复制到已初始化内存是 operator =），使用 memmove；否则根据迭代器是 RandomAccessIterator（包括不满足前述条件的指针）还是 InputIterator 使用不同实现：

```cpp
template <class InputIterator, class OutputIterator>
InputIterator __copy(InputIterator first, InputIterator last, OutputIterator result, std::input_iterator_tag) {
    for(; first != last; ++first, ++result) {
        *result = *first;
    }
    return result;
}
template <class RandomAccessIterator, class OutputIterator>
OutputIterator __copy(RandomAccessIterator first, RandomAccessIterator last,
                        OutputIterator result, std::random_access_iterator_tag) {
    __copy_d(first, last, result);
}
// 对于随机访问迭代器，计算要拷贝的次数 n 作为循环条件，避免每次进行迭代器比较
template <class RandomAccessIterator, class OutputIterator>
OutputIterator __copy_d(RandomAccessIterator first, RandomAccessIterator last, OutputIterator result) {
    typedef typename std::iterator_traits<RandomAccessIterator>::difference_type Distance;
    for (Distance n = last - first; n > 0; --n, ++first, ++result) {
        *result = *first;
    }
    return result;
}
```

> *strcpy* 与它们不同：strcpy(dst, src) 不能指定长度，会在遇到 \0 后停止复制（可能需要先找到 \0 再调用 memcpy，也可能逐个复制）。但类似地，两个字符串不可重叠。

**memcpy**

[std::memcpy(dst, src, count)](https://zh.cppreference.com/w/cpp/string/byte/memcpy) 从 src 复制 count 字节到 dst。会将对象视作 unsigned char 数组进行复制。
如果 src 与 dst 对象重叠、潜在重叠、不可平凡复制或 src/dst 无效或为空指针（即使 count 为0），则为 UB。即 src, dst 不可能互为别名。

> 当 vector 存储 POD 时，会使用 memmove 优化扩容时的移动。
> 虽然扩容时两个指针肯定不会重叠，但标准库不会使用 memcpy、只会使用 memmove（但编译器有时能够优化为 memcpy）。
>
> **使用 memcpy 拷贝大小为 0 的 vector data 是 UB**：当 vector 的 size 为0时，data() 可能会也可能不会返回空指针，所以此时使用 memcpy 拷贝 vector 的底层数组时可能是 UB：
>
> ```cpp
> vector<int> v(0);
> char c[10] = {0};
> memcpy(c, v.data(), v.size() * sizeof(int));
> // -fsanitize=undefined: runtime error: null pointer passed as argument 2, which is declared to never be null
> ```
>
> copy 没有该问题，此时它不会拷贝。
>
> 理论上是最快的内存复制。

**memmove**

[std::memmove(dst, src, count)](https://zh.cppreference.com/w/cpp/string/byte/memmove) 从 src 复制 count 字节到 dst。会将对象视作 unsigned char 数组进行复制。
与 memcpy 类似，但是允许对象重叠，会检测并在重叠时改变拷贝方式（可能略微影响效率）；src 与 dst 可能互为别名。
如果 src 与 dst 对象潜在重叠、不可平凡复制或 src/dst 无效或为空指针（即使 count 为0），则为 UB。

当不能确定是否重叠时，使用 memmove。
注意它是复制不是移动！

**count**

[count, count_if](https://zh.cppreference.com/w/cpp/algorithm/count) 统计范围内等于 value 或满足指定谓词的元素数量。

**equal**

[equal](https://zh.cppreference.com/w/cpp/algorithm/equal) 检查两个范围是否完全相等。

**fill**

[fill](https://zh.cppreference.com/w/cpp/algorithm/fill) 将给定的 value 赋值给范围中的每个元素。
不要求 value 的类型与迭代器的 value_type 相同，只需要`*it = value`合法即可（即有对应的 operator =）。

**find**

[find, find\_if, find\_if\_not](https://zh.cppreference.com/w/cpp/algorithm/find) 返回范围内第一个等于 value/满足/不满足指定谓词的元素的迭代器。如果不存在则返回 last。

**find_first_of**

[find\_first\_of](https://zh.cppreference.com/w/cpp/algorithm/find_first_of) 查找范围内等于另一个范围中任意元素的首个元素的迭代器。可以用二元谓词进行比较。
find_end 与此类似，但查找最后一个符合条件的元素。

**for_each**

[for_each](https://zh.cppreference.com/w/cpp/algorithm/for_each) 将范围内每个迭代器解引用的结果应用到给定的函数对象，忽略函数对象的返回值。

```cpp
auto out = [](const A& v) { cout << v.name << ' '; };
// 反向输出
for_each(rbegin(a), rend(a), out);

// ranges version
ranges::for_each(a | views::reverse, out);

// 并行版本（ranges 没有）
for_each(execution::par, begin(a), end(a), /*...*/);
```

**generate**

[generate](https://zh.cppreference.com/w/cpp/algorithm/generate) 将调用给定函数对象的结果赋值给范围中的每个元素。与 fill 类似，但每次赋值都会调用函数获取 value。

可以实现与 iota 一样的效果：

```cpp
generate(begin(a), end(a), [v = 0]() mutable { return v++; });
```

**iota**

[iota](https://zh.cppreference.com/w/cpp/algorithm/iota) 以 value, value+1, value+2, ... 填充指定范围。更方便、语义更明确。

比如：`iota(p.begin(), p.end(), 0);`。

**min_element** **max_element**

[min/max_element](https://zh.cppreference.com/w/cpp/algorithm/max_element) 返回范围中最小/最大的第一个元素的迭代器。可以使用谓词比较大小关系。

**mismatch**

[mismatch](https://zh.cppreference.com/w/cpp/algorithm/mismatch) 返回两个范围中首个不相等或不满足二元谓词的元素的一对迭代器。

```cpp
string s1 = "hello abc";
string s2 = "hello cde";
auto [first, second] = mismatch(begin(s1), end(s1), begin(s2));
{
    const auto pos = distance(begin(s1), first);
    cout << "mismatch at pos " << pos << '\n';
}

// ranges version
// 结果为 ranges::in_in_result<I1, I2>，也可以用一样的结构化绑定 auto [f, s] = ...
auto res = ranges::mismatch(s1, s2);
{
    const auto pos = distance(begin(s1), res.in1);
    cout << "ranges::mismatch at pos " << pos << '\n';        
}
```

**partition**

[partition](https://zh.cppreference.com/w/cpp/algorithm/partition) 将范围内的元素分为连续的两组：将满足谓词 p 的元素排列到前面，将不满足的元素排列到后面。返回不满足 p 的第一个元素的迭代器。

**remove**

> 标准库判断是否等于 value 时，都通过 operator == 判断，因此必须有对应的 == 重载。
> ranges 版本可以设置投影，可将类对象映射到其成员，就不需要为类设置 == 重载。

[remove, remove_if](https://zh.cppreference.com/w/cpp/algorithm/remove) 移除范围内等于 value 或满足谓词的元素，并返回移除后范围的尾迭代器（即第一个满足条件的元素位置）。
不会真的移除元素，只会将满足条件的元素移动到尾部（类似 unique），然后返回第一个满足条件被“移除”的元素的位置。
这与容器的 remove 成员函数不同，后者会移除元素。

ranges::remove 会返回移除了的元素的子 range，包括所有满足条件的元素，其 r.begin() 与 std::remove 的返回值相同。

调用 remove 后通常会调用容器的 erase 成员函数来实际移除元素。这种调用称为 erase-remove。
C++20 为各容器引入的 [*std::erase*, erase_if](https://zh.cppreference.com/w/cpp/container/vector/erase2) 可以达到相同效果（它只有接收各容器的重载）。

```cpp
// standard version
arr.erase(std::remove_if(arr.begin(), arr.end(), check), arr.end());

// ranges version
arr.erase(ranges::remove_if(arr, check).begin(), arr.end());

// C++20 version 
std::erase_if(arr, check); // 返回移除的元素数量
```

**replace**

[replace, replace_if](https://zh.cppreference.com/w/cpp/algorithm/replace) 以 new_value 替换范围内等于 value 或满足谓词的元素。

**reverse**

[reverse](https://zh.cppreference.com/w/cpp/algorithm/reverse) 反转范围中的元素。通过在每对元素上应用 iter_swap 实现。

**rotate**

[rotate(first, mid, last)](https://zh.cppreference.com/w/cpp/algorithm/rotate) 将元素左移：将 mid 位置的元素移动到 first，并以此类推；原本 [first, mid) 范围的元素被移动到 [mid, last) 后。返回之前的 \*first 在左移后的位置，即`std::next(first, std::distance(mid, last))`。

ranges::rotate 返回 subrange {new_first, last}，即 std::rotate 的返回值和一个新的 last。

```cpp
vector<string> a {...};
ostream_iterator<string> out(cout, " ");

// standard version
auto newPos = std::rotate(begin(a), next(begin(a), 3), end(a));
ranges::copy(a, out);
cout << "\n new pos of first: " << distance(begin(a), newPos) << '\n';

// ranges version
auto cppPos = ranges::find(a, "cpp");
if (cppPos != end(a)) {
    // 将元素 cpp 移动到 first 位置
	auto ret = ranges::rotate(a, cppPos); // 返回 subrange
	ranges::copy(a, out);
	cout << "\n new pos of first: " << distance(begin(a), ret.begin()) << '\n';
}
```

**sample**

[sample](https://zh.cppreference.com/w/cpp/algorithm/sample) 从序列中不重复、等概率地选择 n 个元素，写入到指定位置。
如果 output_iter 与序列重叠，则是 UB。

**search**

[search](https://zh.cppreference.com/w/cpp/algorithm/search) 返回范围内等于另一个范围中任意元素的首个元素的迭代器。可以用二元谓词进行比较。
与 find_first_of 类似，但是可以传一个 Searcher 对象自定义搜索方式（TODO：https://www.cppstories.com/2018/08/searchers/）。

search_n 返回范围内连续 n 个位置与目标相同的区间的起始位置迭代器。

**shuffle**

[shuffle](https://zh.cppreference.com/w/cpp/algorithm/random_shuffle) 利用指定的随机数生成器对元素进行重排序。
random_shuffle 通常使用 std::rand 作为随机数来源，C++17 废除。

**sort**

[sort](https://zh.cppreference.com/w/cpp/algorithm/sort) 对指定范围的元素进行非降序排序。可能改变相对顺序。
通常使用 introsort。

其它算法：

- is_sorted 检查指定范围的元素是否已有序。默认使用 operator < (C++20 前)/std::less (C++20 起)，可以指定比较谓词。
- partial_sort 将最小的前 N 个元素放到前 N 个位置，不保证其余元素的顺序（类似 nth_element）。
- stable_sort 排序并保证相对顺序。

```cpp
sort(begin(arr), end(arr), [](const A& a, const A& b)
	{ return a.name < b.name; }
);

// ranges version
ranges::sort(arr, {}, &A::name); // 使用投影直接比较特定成员
auto sorted = ranges::is_sorted(arr, {}, &A::value);
```

**transform**

[transform](https://zh.cppreference.com/w/cpp/algorithm/transform) 在给定范围应用变换，并将结果输出到从 output_it 开始的范围。

可以仅接收一个元素序列，应用一元谓词；也可以接收两个元素序列，应用二元谓词。

```cpp
// 变换 arr 中的元素
ranges::transform(arr, begin(arr), [v = 0](const string &s) mutable {
	return A { s + to_string(v++), 1}; // 接收投影后的 A::name，返回 A 对象
}, &A::name);
```

**unique**

[unique](https://zh.cppreference.com/w/cpp/algorithm/unique) 移除范围中相邻的相同元素，返回移除后序列的尾迭代器。
类似 remove，不会真的移除元素，只会将重复的元素移动到尾部，然后返回第一个被“移除”的元素的位置。

调用 unique 后通常会调用容器的 erase 成员函数来实际移除元素。
可以访问尾部的被“移除”元素，但它们是未指定的（被移动）。







**标准库提供的 range adaptor**

标准库定义了许多常用的 range adaptor，但 C++20 中只有一部分，很多重要功能 23 才有，连接两个 view 的 concat 在 26 才有。

C++20：

- join：展开一个 range 的内部元素，将其变为一维序列。比如`vector<string>{...} | join`的 range 为一个个 char，`vector<vector<char>>`也是如此。
- drop(n)：弃掉一个 view 的前 n 个元素组成 view。
- take(n)：取一个 view 的前 n 个元素组成 view。
- reverse：生成一个 view 的逆序 view。

C++23 或 26：

- zip：
    因为 view 可遍历，所以用 ranges::for_each view 也能达到类似效果？
- to()：通过 view 创建容器。比如：`r | ... | to<vector<string>>();`。
    23 前只能通过遍历结果 range 来创建新容器，比如：
    - `vector<string> vec = {range.begin(), range.end()};`
    - `for (auto&& v: range) vec.pb(v);`
- concat：连接两个 view。
    在 26 前如果要连接两个相同 view，可以`r | cycle | take(2 * size)`。
    或是链接 range v3，然后`#include <range/v3/view/concat.hpp>`。

仅 range v3：

- cycle：重复一个 view 无限次。

**range**

> 总结：
> range 是一对 begin 与 end（代表一系列可迭代的元素），range adaptor closure 是对 range 中元素的修饰（closure 是一元 adaptor 以及多元 adaptor 带实参的类型，如`join`、`take(3)`），被修饰的 range 通常称为 view（使用 view 时 auto 即可，不需要知道它的类型（是一个复杂的 lambda？））。
> range 可以通过 operator | 传递给 closure，生成带有闭包中修饰条件的 view。operator | 可以连接多个 closure，生成包含多个 closure 修饰的 closure（结合律）。
>
> view 通常指带有若干 closure 修饰的 range，它本身仍指向原对象，不拥有任何数据的所有权；如果涉及映射，则会在求值时只访问映射对应的元素；如果涉及修改/变换，则会在求值时产生变换后的右值。
> **通过 | 连接闭包不会修改 range 和原对象**，比如：在闭包的谓词中进行筛选不会影响 range 的 begin 与 end 指向（自然也不会影响所有元素的指向），只是影响访问该 range 时是否遍历某位置；在闭包的谓词中变换元素不会影响原对象，只是在访问该 range 时会拷贝一个对应位置的元素，再应用变换产生右值。
> 即 adaptor 是惰性的：operator | 只会为结果 range 附加若干 adaptor 谓词，只有在访问 range 时，这些 adaptor 才生效，并且不会影响原 range。但这也意味着结果不会被缓存，如果多次访问 view 的同一个元素，将需要多次变换。
>
> 注意，如果不涉及修改（即 closure 中不返回新元素？），则求值时仍产生指代指向元素的左值。
>
> ```cpp
> std::vector<int> vec = {1, 2, 3};
> auto vi = vec | views::filter([](int x) { return x % 2 == 0; });
> //   | std::views::transform([](int x) { return x * x; });
> *vi.begin() = 0; // 如果有 transform，则 vi.begin() 是右值，不可赋值
> print(vec); // vec 被修改
> ```
>
> 访问 range 时，拷贝、变换后产生的元素序列是右值，因此不能使用 auto& 绑定。
> 如果一个 range 引用自局部作用域 A 的对象（不管是直接生成的 range 还是附加 closure 的 range），则在作用域 A 外不能使用该 range，因为引用的对象已析构。
>
> 可参考：
> https://hannes.hauswedell.net/post/2019/11/30/range_intro/

迭代器机制有一个明显的不足：需要使用两个迭代器来表示一组对象，而其它支持迭代器抽象的编程语言通常只需要一个迭代器便可以完整地迭代出所有引用的对象。这会使得代码更加复杂、出错率增加，并且许多通用的集合操作无法以一种相对优雅的方式使用迭代器实现。因此 C++20 引入了 range。

range 库是对迭代器和泛型算法库的扩展，包括立即应用到 range 上的 range 算法，和惰性地应用到 view 上的 range adpator。
range 是对以下内容的抽象：

- [begin, end)：迭代器对。所有接受迭代器对的算法都有接受 range 的重载。
- begin + [0, size)：包含 [begin, begin + size) 的元素序列。
- [begin, 谓词)：在指定位置终止的序列。
- [begin, ...)：无上限序列。

[range](https://zh.cppreference.com/w/cpp/ranges/range) 的核心是一个 concept，满足该约束的所有类型都是一个 range：

```cpp
// 能通过 begin(), end() 获取首尾迭代器的类型都是 range
template <typename R>
concept range = requires(R &r) {
    ranges::begin(r); // 对向前迭代器保持相等性
    ranges::end(r);
};
```

`std::ranges::begin`函数返回一个 range 的首迭代器。对于有成员函数 begin 的类型，它会调用该成员函数。
end 同理，返回尾迭代器。
所有 STL 容器都是 range。

> 除了上述要求外，range 还要求：`ranges::begin(e)`与`ranges::end(e)`都必须有均摊常数的复杂度，且不会更改 e；如果`ranges::begin(e)`不是 input_range（不可重复访问），range 要缓存上次的 begin 结果用于之后的`begin(e)`调用，以保证复杂度（即`ranges::begin(e)`的结果不会变化）。
> 如果修改了缓存的 begin 指向的元素，使其不再满足 view 条件，则是 UB。
>
> 比如：对于 [filter_view](https://zh.cppreference.com/w/cpp/ranges/filter_view)，如果先通过 filter 获取容器的 view，然后修改容器，再次遍历该 filter 可能会访问到不满足过滤条件的元素：
>
> ```cpp
> vector<int> v {1, 2, 3, 4};
> auto view = v | views::filter([](const int& v) { return v % 2 == 0; });
> for (int &i: view) {
> i++;
> }
> print(v); // 1 3 3 5
> 
> for (int &i: view) {
> i++;
> }
> print(v); // 1 4 3 5（UB，3 被修改）
> ```

> 首尾迭代器不需要是相同类型，只需要可通过 operator == 进行比较。尾迭代被称为哨兵 (sentinel)。这种性质非常方便：
>
> - iota 返回一个无界 range，其尾迭代器是一个特殊的迭代器类型，它与任何其它 iterator 通过 operator == 比较的结果都为 false，因此可以做到无边界、不断生成值。
> - 如果要生成一个 C 字符串的 range，可以将首迭代器设为 const char\*，将尾迭代器设为特殊类型，它能与 const char\* p 进行比较，并且仅在 \*p 为 \0 时返回 true。这样就不需要先获取长度。

与迭代器类似，range 和对应的 concept 也分为6类，分别代表其返回的迭代器的类型：input range、output range、forward range、bidirectional range、random access range 和 contiguous range。

> range 和 view 都可以像容器一样直接遍历（会提供 begin 等对应接口，取决于这个 range 的类型）。
>
> vector 本身是一个可输入输出的 range，而 const vector 就是一个 input range。
>
> range 版本的算法是 niebloid，有 concept 约束，所以报错更友好、更适合使用。

例：[一个 map](https://godbolt.org/z/afP614dca)；[Split](https://zhuanlan.zhihu.com/p/474447289)（根据指定字符串切分字符串）。

```cpp
ranges::sort(v); // vector 是 range
ranges::sort(v | views::take(5)); // 只 sort 前5个元素

// 筛选以 c++ 开头的字符串并大写
template <ranges::range InputRange>
auto foo(InputRange r) {
	auto starts_with_cpp = [](const string &s) noexcept { return s.starts_with("c++"); };
	auto transformer = [](string &s) noexcept {
		std::transform(s.begin(), s.end(), s.begin(), [](char c) { return std::toupper(c); });
		return s;
	};
	vector<string> res;
	auto view = r | views::filter(starts_with_cpp) | views::transform(transformer);
	auto iter = std::inserter(res, res.end());
	ranges::for_each(view, [&](auto&& x) { iter = {x.begin(), x.end()}; });
	return res;

	// C++23 可以用 to 直接转换成容器（但 gcc 14 起才支持）
	// return r | views::filter(starts_with_cpp)
	// 		 | views::transform(transformer)
	// 		 | ranges::to<vector<string>>();
}
```

**range adaptor**

[范围适配器对象 (Range Adaptor Object)](https://zh.cppreference.com/w/cpp/named_req/RangeAdaptorObject) 是接收 viewable_range 作为其首个实参并返回一个 view 的*定制点对象*（一个 const 函数对象）。
如果它只接收一个 viewable_range 作为唯一实参，则称为一元 range adaptor object，它同时也是 range adaptor closure。

> 范围适配器是一个重载了 operator ()、满足上述条件的 functor 类，范围适配器对象是这种类的一个对象。对象本身是函数对象、可被调用，但类本身不可调用。
> 对于标准库提供的每个范围适配器对象 a（比如 views::filter），都会提供一个对应的类型 t（比如 ranges::filter_view），前者是后者的实例，`r | a(args)`、`a(r, args)`、`t(r, args)`等价？

当 range adaptor 可以接收多于一个实参时，如果向其传入 range 和其它实参，则它返回一个 view；如果不传入 range、只传递其它实参，则它会生成一个 range adaptor closure。
即对于一个非一元适配器 a，它可以接收 range r 和其它实参**立即**返回 view `a(r, args...);`，也可不接收 range、返回适配器闭包 `a(args...)`，以允许之后通过 | 传递 range 输入（**惰性**）。

例：适配器 filter 有两种调用方式：`filter(r, starts_with_c)`和`filter(starts_with_c)`，前者返回一个直接将 filter 应用到传入的 range 并返回结果 view，后者返回一个 range adaptor，可以在之后用 | 连接其它 range 或闭包作为输入输出`r | filter(...) | ...`，或直接用 opeartor () 传入 range，然后生成最终的 view。

```cpp
// 设 r 是 input range，p 是筛选谓词
// 以下三种调用方式相同
auto fr = filter(r, p);
auto fr = filter(p)(r);
auto fr = r | filter(p);
auto fr = filter_view(r, p); // 不确定
```

能实现上述功能，即满足以下条件的类就是 range adaptor：类重载了 operator ()，且 operator () 有两个重载：第一个重载不接收输入 range 作为参数，返回一个 range adaptor closure；第二个重载接收 range 作为参数，返回输出 range。

> 通过 | 连接时，如果不需要其它实参（一元 adaptor），则 adaptor 对象后不需要带括号和空实参列表（如`r | cycle`），否则需要补全实参（本质上 | 连接的是闭包而不是 adaptor 对象）。但 to 是例外，必须有空括号（如`r | to<string>()`）。
>
> C++ 库通过定制点对象(CPO) 实现了 niebloid，既解决了同时 using 的冲突问题，又借助标签分发的特性解决了兼容问题。
> 如果 std::ranges:: 的函数检测到它应被用于 std:: 函数，则它会把参数转发给 std:: 函数并调用？

**range adaptor closure**

[范围适配器闭包对象 (Range Adaptor Closure Object)](https://zh.cppreference.com/w/cpp/named_req/RangeAdaptorClosureObject) 是可以通过管道运算符 operator | 调用的函数对象。它重载了 operator () 和 operator |，这两个 operator 均是接收输入 range、返回输出 range。
若 C 是适配器闭包，且 R 是 range，则表达式`C(R)`与`R | C`等价，返回 range。

闭包有以下性质：

- 两个闭包对象可以通过 | 连接生成另一个闭包对象。
- 具有结合律，即令闭包对象`C | D`结果为 E，则`D(C(R))`、`R | C | D`、`E(R)`、`R | E`、`R | (C | D)`均等价。

如果类型 T 是以下类型，则它是 range 适配器闭包：

- 一元 range adaptor。
- range adaptor 接收非 range 实参的返回结果的类型。
    可以与上一点结合，即向 range adaptor 传递 range 外的实参后的类型就是闭包。
- 两个闭包对象 operator | 的结果的类型。
- 满足*实现范围适配器闭包对象的要求*的用户自定义类型。

T 实现范围适配器闭包的要求为：T 满足以下所有条件：

- T 是接受一个 range 实参的一元函数对象，即重载了 operator () 且它只接收一个 range。
- T 存在唯一公开基类 range_adaptor_closure<T>。
- T 不是 range。

range_adaptor_closure 在 C++23 引入，即23前除了 ranage adaptor 外，用户无法自定义闭包类型？

**view**

range [view](https://zh.cppreference.com/w/cpp/ranges/view) 是表示可遍历 range 序列的轻量对象。类似 string\_view，它没有该 range 的所有权，仅用来访问 range。

如果类型 R 满足以下所有条件，则它是 view：

- R 是一个 range。
- R 可移动构造、可移动赋值、可 swap（满足 movable）。
- 满足以下条件之一：
    - R 直接或间接继承自 ranges::view_base。
    - R 直接继承自 ranges::view_interface<U> 且 R 没有其它基类，其中 U 为任意一个类型，通常情况下 R 使用 CRTP 直接继承自 ranges::view_interface<R>。

> view_base 是一个空类，它唯一的作用就是标记 view、将 view 和 range 区分开。如果没有任何的标记来区分 view 和 range，那么按照定义，STL 中的所有容器也满足 view 的条件，这与 view 的语义设计不符。
>
> [view_interface<R>](https://zh.cppreference.com/w/cpp/ranges/view_interface) 不同。它会根据类型参数 R（一般为该类本身）的种类（即六种 range 之一），提供不同的实用成员函数。比如：如果 R 是 forward range，view_interface<R> 会提供 empty 成员函数，它检测 view 中是否不包含任何元素；如果 R 是 random access range，view_interface<R> 会提供 operator [] 来按照索引访问 range 中的任意一个元素。
>
> 但 view 可能有比其底层 range 更宽松的约束，比如大部分 view 是 output_range 而非只读的 input_range。

view 复制（如果有）、移动、赋值和析构函数必须是低代价的，不依赖元素数量，使用时可以随意传值、无需传引用。

> [viewable_range](https://zh.cppreference.com/w/cpp/ranges/viewable_range) 指能够通过 views::all 转换成 view 的 range。
>
> range v3 中的 any_view 可以存储任意类型的 view（比如 empty view 与 single_view）到单个容器中（view 的类型擦除）。

**range factories**

range 库提供了一些基础的 range，它们统称为 range factories，包括：空 range（不含任何元素的 range）、只包含一个给定元素的 range、从一个初始值开始不断产生递增的值的 range 以及从一个 input stream 中不断读取特定类型的值的 range。

**投影 proj**

ranges 版本的算法函数可以接收投影。算法会在应用谓词前，先进行投影得到实际操作的元素，再应用谓词。可以用来选择特定对象或成员，或做变换。

```cpp
ranges::copy_if(a,
	std::ostream_iterator<A>(cout, "; "),
	[](const A& a){
		return !a.name.starts_with("N");
	});
// 操作 A::name 而非 a 中的 A 对象
std::ranges::copy_if(a,
	std::ostream_iterator<A>(cout, "; "),
	[](const string& name){
		return !name.starts_with("none");
	},
	&A::name); // 投影
```

**compare**

set、map 等容器，sort 等排序所需的比较谓词，都要满足[比较要求](https://zh.cppreference.com/w/cpp/named_req/Compare)。

“比较要求”要求对象的比较 comp(a, b) 必须是严格弱序的。< 是严格弱序，但 <= 不是。 在 sort 中使用非严格弱序比较可能 RE/coredump。

只要知道严格弱序谓词（< 逻辑），就可以知道 >、==、<=、>= 的实现。 比如：a == b 等价于 !(a < b) && !(b < a)，即 !comp(a, b) && !comp(b, a)。

例：`bool comp(int a, int b) { return a < b; }`是严格弱序的，当 a, b 不同时，!comp(a, b) && !comp(b, a) 的值为 false；相同时，则为 true。 `bool comp(int a, int b) { return a <= b; }`不是严格弱序，无论 a, b 是否相同，!comp(a, b) && !comp(b, a) 的值都为 false，因此即使传入相同的 a, b，也会将它们视作不同。







---

## STL - 迭代器库

> https://zh.cppreference.com/w/cpp/iterator
>
> https://www.zhihu.com/question/550847519/answer/3389388673

迭代器有效地分离了对象的存储和对象的访问。提供迭代器的容器不需要关心上层算法的具体实现，使用迭代器的算法也不需要关心底层对象的存储和组织方式。



> C++ 允许迭代器的复制不是常数时间，但算法没必要传递迭代器引用：算法本身需要使用、读写迭代器，且对相同实参的连续两次调用结果应该是相同的（如果算法不修改）。
> 类似的还有谓词 (predicate)，谓词是无状态、regular_invocable 的，使用时直接拷贝即可。

**老式迭代器**

[*老式迭代器* (Legacy Iterator)](https://zh.cppreference.com/w/cpp/named_req/Iterator) 指可以用来标识和遍历容器中的元素的类型。是迭代器的基础类型。
具体来说，老式迭代器类型 It 需要满足：可复制构造、可复制赋值、可析构，iterator_traits<It>  有 value\_type 等指定成员，且对于 It 类型的左值 r，r 可交换、可解引用、可自增。

> 如果要自定义迭代器，应该满足老式迭代器的要求，即提供以下类型成员：
>
> - value_type：迭代器指向的元素的类型。
> - iterator_category：6种 [iterator_tag](https://zh.cppreference.com/w/cpp/iterator/iterator_tags) 类型之一的别名。
> - difference_type：两个该类型迭代器相减的结果类型。
> - pointer：迭代器指向的元素的指针类型。
> - reference：迭代器指向的元素的引用类型。

**迭代器分类**

根据迭代器所支持的操作，[迭代器](https://zh.cppreference.com/w/cpp/iterator)可以分为6种类别：

> 每个类别是一种要求，一种类型可以满足多个要求，能出现在需要满足该要求的迭代器的地方。比如：指针满足老式随机访问迭代器的要求，因此任何需要老式随机访问迭代器的地方都可以使用指针。
> *老式迭代器*是迭代器的基本要求。
>
> 一个算法可能会根据迭代器的类型有不同实现，算法会根据迭代器的 iterator_category 成员决定使用哪个实现。使用约束更强的迭代器的实现通常效率更高。

- *老式输入迭代器* (Legacy Input Iterator)：能从所指向元素进行读取的老式迭代器。

满足可相等比较。只保证单趟算法的有效性：一旦自增迭代器，那么它之前的值的副本可能失效。

- *老式输出迭代器* (Legacy Output Iterator)：能向所指向元素进行写入的老式迭代器。

对于老式输出迭代器 r，\*r 只能用在赋值表达式的左侧。
通过输出迭代器对同一值进行的赋值只会发生一次：输出迭代器上的算法必须是单趟算法。

- *老式向前迭代器* (Legacy Forward Iterator)：能从所指向元素进行读取的老式迭代器。

类似输入迭代器，但老式前向迭代器可被用于多趟算法。
解引用来自容器的该迭代器会返回容器的 value_type 类型的对象。

- *老式双向迭代器* (Legacy Bidirectional Iterator)：能双向移动（自增与自减）的老式向前迭代器。

- *老式随机访问迭代器* (Legacy Random Access Iterator)：能在常数时间内移动到任何元素的老式双向迭代器。

- *老式连续迭代器* (Legacy Contiguous Iterator) （C++17 起）：所指向的逻辑相邻元素在内存中物理相邻的老式随机访问迭代器。

指向数组元素的指针、`array::iterator`、`basic_string::iterator`等都满足老式随机访问迭代器和老式连续迭代器。

> 除了输出外，其它5种类型是相互包含、由弱到强的。
> 除了输入外，其它4种迭代器类型可以同时满足老式输出迭代器的条件（可写入），此时它是可变的 (mutable)。不可变迭代器称为常迭代器 (const)，解引用后会带 const。
>
> 如果所有满足迭代器类别要求的操作都是 constexpr 函数，那么该迭代器为 *constexpr 迭代器*（C++20 起）。

C++20 引入了基于 concept 的新迭代器系统。为了避免命名冲突，cppref 将上述 C++17 的迭代器命名为老式的（标准不这样称呼）。
新迭代器系统更准确，使用 concept 约束迭代器类型，并引入了移动语义？并且将驼峰命名方式改为了下划线命名（concept 均为下划线命名）。







**迭代器适配器**

类似容器适配器，**迭代器适配器对指定的底层迭代器类型进行包装，提供新的接口，得到一种基于原迭代器、但满足特定条件、有特定用处的新迭代器类型**。

**reverse_iterator**

[reverse_iterator](https://zh.cppreference.com/w/cpp/iterator/reverse_iterator) 是迭代器适配器，反转给定迭代器的前进方向（对返回的迭代器类型自增，效果等于对原迭代器自减；反之同理）。
迭代器必须满足老式双向迭代器。

`rbegin()`就可以通过`reverse_iterator(begin())`实现，`rend()`同理（rbegin、rend 的类型就是 reverse_iterator）。

**make_reverse_iterator**

[std::make_reverse_iterator (Iter it)](https://zh.cppreference.com/w/cpp/iterator/make_reverse_iterator) 用于创建某个迭代器的 reverse_iterator，等价于`reverse_iterator<Iter>(it)`。

与直接自行构造`reverse_iterator(it)`相比，更推荐使用。因为它使用模板实参推导规则推导迭代器类型，并显式传递给 reverse_iterator，而不是由 CTAD 自行推导，它可能出现问题（并且在 C++17 前不能用）。

> CTAD 的问题见[这里](https://quuxplusone.github.io/blog/2022/08/02/reverse-iterator-ctad/)。
> 简单来说，在向模板参数`Iter it`传递 reverse_iterator 类型的对象时，在函数内使用`reverse_iterator(it)`的效果等同于直接使用`it`，因为`Iter`此时的类型就是`reverse_iterator`，`reverse_iterator(it)`会被视为同类型的转换（无意义），而不是使用 it 再生成一个`reverse_iterator`。使用`reverse_iterator<Iter>(it)`或`make_reverse_iterator(it)`都可以避免该问题。

**move_iterator**

[std::move_iterator](https://zh.cppreference.com/w/cpp/iterator/move_iterator) 是迭代器适配器，表现与底层迭代器相同，但在解引用时会将底层迭代器返回的值转为右值。
将该迭代器用作输入迭代器、读取指向的值时，会使用移动进行赋值。

**make_move_iterator**

[std::make_move_iterator](https://zh.cppreference.com/w/cpp/iterator/make_move_iterator) 用于创建某个迭代器的 move\_iterator，通过模板实参推导而不通过 CTAD。

```cpp
string concat = accumulate(move_iterator(v.begin()), move_iterator(v.end()), string());

list<string> s{"1", "2", "3"};
vector<string> v1(s.begin(), s.end()); // 复制
vector<string> v2(make_move_iterator(s.begin()), make_move_iterator(s.end())); // 移动
```

**back_inserter_iterator**

[std::back_inserter_iterator](https://zh.cppreference.com/w/cpp/iterator/back_insert_iterator) 是输出迭代器，每当迭代器被赋值就调用容器的 push_back() 成员函数来追加元素。
自增该迭代器是空操作。

它接收一个容器来创建对应的迭代器，不是一个迭代器适配器。

> *front_insert_iterator*、*front_inserter* 类似，但会调用容器的 push_front。

**back_inserter**

[std::back_inserter](https://zh.cppreference.com/w/cpp/iterator/back_inserter) 用于创建某个容器的 back\_inserter\_iterator，通过模板实参推导而不通过 CTAD。

```cpp
vector<int> v{1, 2, 3};
fill_n(back_inserter(v), 3, -1);

generate_n(
    back_insert_iterator<std::vector<int>>(v), // back_inserter(v),
    10,
    [n = 0]() mutable { return ++n; }
);
```

**流迭代器**





**iterator_traits**

[std::iterator_traits](https://zh.cppreference.com/w/cpp/iterator/iterator_traits) 提供访问迭代器类型各项属性的统一接口。

老式迭代器类型需要定义5个类型成员 (value\_type, iterator\_category, difference\_type, pointer, reference)，所以通常可使用`Iter::value_type`等来获取迭代器指向元素的信息。
但指针也满足老式迭代器的要求，而指针没有这些成员（显然不能写`int*::value_type`）。所以使用迭代器时，不会直接使用类型的`T::value_type`，而是使用`iterator_traits<T>::value_type`。iterator_traits 为 (const) T\* 定义了特化类型。

**iterator**

[std::iterator](https://zh.cppreference.com/w/cpp/iterator/iterator) 是用于简化定义迭代器类型的基类，可以通过它的模板参数简化迭代器中各类型成员的定义。

```cpp
// 一种实现
template<
	class Category,
	class T,
	class Distance = std::ptrdiff_t,
	class Pointer = T*,
	class Reference = T&
> struct iterator {
	using iterator_category = Category;
	using value_type = T;
	using difference_type = Distance;
	using pointer = Pointer;
	using reference = Reference;
};
```

iterator 在 C++17 被弃用（不建议使用），因为：使用它定义类型成员虽然方便，但并不直观；并且如果基类继承的类型成员是待决名，就不能在子类中直接使用（找不到）。

```cpp
struct MyOutputIterator: iterator<std::output_iterator_tag, void, void, void, void> { // 不清晰
	// 推荐写法：
	using iterator_category = std::output_iterator_tag;
    // using ...
};

template <class T>
struct MyIterator: iterator<std::random_access_iterator_tag, T> {
	value_type data; // Error: value_type is not found by name lookup
};
```

**advance**

[std::advance(it, n)](https://zh.cppreference.com/w/cpp/iterator/advance) 返回迭代器 it 自增 n 次的结果。
迭代器必须满足老式输入迭代器。
n 可以为负，此时进行自减 n 次，且迭代器必须满足老式双向迭代器。
复杂度为 O(n)。如果迭代器满足老式随机访问迭代器，则为 O(1)。

**next**

[std::next(it, n = 1)](https://zh.cppreference.com/w/cpp/iterator/next) 与`advance(it, n)`相同，返回迭代器 it 自增 n 次的结果，但 n 默认为 1。

> 虽然表达式`++c.begin()`通常可用，但并不保证，老式输入迭代器不保证可以对右值值类别的迭代器进行自增。
> 而`next(c.begin())`一定可用。
>
> prev 类似，不保证`--c.end()`可行，但`prev(c.end())`一定可行。

**prev**

[std::prev(it, n = 1)](https://zh.cppreference.com/w/cpp/iterator/prev) 与`advance(it, -n)`相同，返回迭代器 it 自减 n 次的结果，但 n 默认为 1。

**distance**

[std::distance](https://zh.cppreference.com/w/cpp/iterator/distance) 计算两个迭代器之间的距离，即从一个迭代器到另一个迭代器需要自增多少次。
迭代器必须满足老式输入迭代器。
复杂度为 O(n)。如果迭代器满足老式随机访问迭代器，则为 O(1)。

对于非老式随机访问迭代器，如果从 first 到 last 不可及则为 UB。
对于老式随机访问迭代器，如果 first 与 last 互不可及则为 UB。如果 first 从 last 可及，结果可能为负。

**projected**

[std::projected](https://zh.cppreference.com/w/cpp/iterator/projected) 通过向迭代器解引用后的对象应用指定谓词？将一种类型投影到另一种类型上。（C++20 起）

```cpp
struct T {
    int val;
    float foo();
};
int f() {}

using Itr = vector<T>::iterator;
using T1 = projected<itr, decltype(&T::val)>::value_type;
using T2 = projected<Itr, decltype(&T::foo)>::value_type;
using T3 = projected<Itr, decltype(+f)>::value_type;
static_assert(same_as<T1,int>);
static_assert(same_as<T2, float>);
static_assert(same_as<T3, int>);
```

**data**

std::data 返回内存块指针：如果参数是类对象 c，则如果有 data 成员函数，返回`c.data()`；如果参数是数组 a，返回`a`；如果参数是 initializer_list l，返回`l.begin()`。









---

## STL - 其它

**cout**

cout 的 operator << 是线程安全的，即多个线程可以同时 cout 输出而不需要加锁，不存在数据竞争，只是可能会乱序；单个 opereator << 是原子的，即使用一个 << 输出长字符串不会被打断。
C++23 引入的 osyncstream 会在析构时一次性写入引用的 cout 流，可避免使用多个 << 会被打断的问题。









---

## 写代码

**写 STL 注意事项**

- 扩容等元素拷贝时，用 move 修饰！
- 如果成员函数不做任何修改，加 const 修饰。同样优先使用 const_iterator 而非 iterator。
- 析构函数加 noexcept 修饰。
- 构造函数一般可加 explicit（看情况）。
- 移动构造最好要加 noexcept！由于容器的强异常安全保证，在移动构造可能抛出异常的情况下，会选择复制构造。
- 有些类应禁用拷贝构造与赋值（同时也会阻止移动的生成），如 lock、lock_guard。
- 比较运算符应该带 const，否则 const 对象无法比较。
    可以用三路运算符。
- 移动可以用 [exchange](https://zh.cppreference.com/w/cpp/utility/exchange) 写，如：`n = std::exchange(other.n, 0);`。这样还是自赋值安全的。
- 其它：
    https://www.zhihu.com/question/53085291

**实现 array**

代码见 *Codes - C++ - array*。

通常实现为：

```cpp
template <class T, size_t N>
struct array {
	T data[N];
	T& operator [](size_t id) {
		return data[id];
	}
};
```

但是，当 array 大小为0时，会创建不符合标准的零长数组。
可以像 MSVC STL 一样，为 array 添加零长的特化，然后重写一遍所有函数：

```cpp
template <class T>
struct array<T, 0> {
	[[noreturn]]
	T& operator [](size_t id) {
		throw std::out_of_range("");
	}
};
```

也可像 libstd 一样，在零长时为内部 data 定义一种特别的非数组类型，对该类型的 operator [] 调用会 trap，转换函数 operator T* 会返回空指针：

```cpp
template <class T, size_t N>
struct array_traits {
	using type = T[N];
};

template <class T>
struct array_traits<T, 0> {
	struct type_impl {
		[[noreturn]]
		T& operator [](size_t id) {
			throw std::out_of_range("");
		}

		operator T*() {
			return nullptr;
		}
	};
	using type = type_impl;
};

template <class T, size_t N>
struct array {
	using data_t = array_traits<T, N>::type;
    data_t data_;

    T& operator [](size_t id) {
        return data_[id];
    }
	T* begin() {
		return static_cast<T*>(data);
	}
	T* end() {
		return static_cast<T*>(data) + N;
	}
};
```

实现 array 的推导指引，即`array a{1, 2, 3}`可以自动推导出`array<int, 3>`。

```cpp
// 使用第一个类型作为 T，并校验所有参数是否类型相同；使用 1+sizeof 获得大小
template<typename T, typename... Args>
array1(T, Args...)
	-> array1<std::enable_if_t<(std::is_same_v<T, Args> && ...), T>,
		1 + sizeof...(Args)>;

array arr {1, 2, 3}; // ok
```

**实现 vector**
见 *Codes - C++ - vector*。
扩容时用 move 移动元素！

注意使用空基类优化 Allocator 的内存！见 *vector 实现*。

**实现 string**
见 *Codes - C++ - string*，和*STL - string 的其它实现方式、SSO*。

**实现 move 相关函数**
见 *Codes - C++ - move*。

**实现 shared\_ptr**
见 *Codes - C++ - shared\_ptr*。

**实现 shared\_ptr 与 weak\_ptr**

https://github.com/tacgomes/smart-pointers/blob/master/weak_ptr.h

**实现 tuple**

> TODO
> https://blog.csdn.net/liuyuan185442111/article/details/123781874
> https://zhuanlan.zhihu.com/p/356954012

注意利用私有继承，继承空基类可以优化。

一个合适的 tuple，对下面的代码应该编译错误：

```cpp
void use_tuple(const ::tuple<float, char> & tuple) {}

int main()
{
	::tuple<int, float, char> t(0, 1.0, 'a');
	use_tuple(t);
}
```







---

## 库函数

**malloc**

当应用程序调用 malloc 时，实际是调用 lib 库的 malloc 实现（这里不是系统调用），它可能会继续调用库实现的 brk/sbrk、mmap 等函数，然后最终调用内核实现的 sys_brk、sys_mmap_pgoff 等（这些是系统调用）。
free 同理。

os 一般是以页为单位管理系统的。可用内存不仅包括实际内存，还包括交换空间（牺牲效率增大内存）。

常见的 malloc 实现中，malloc 会从 os 获取内存页，然后将这些页分成大小不同的块。当用户申请内存时，会找到大小最接近、且不小于指定大小的块给用户。这样可以加快分配、减少系统调用次数。
当需要分配较大内存时，malloc 会直接向 os 请求多个页，将它映射到用户程序的虚拟地址空间中的某个区间（需要系统调用），然后将其返回给用户。在这种情况中，os 分配的页可以是不对应物理内存的页，等用户访问到时再进行映射，所以用户可以 malloc 很大的空间而不会立刻出错。

malloc 能分配的可使用空间的最大大小，取决于：机器位数（可寻址空间）、os 的分配策略（是否在每次分配页时都立刻将页映射到物理内存、确保页可用）、可用内存大小、malloc 算法、程序申请方式等。

**malloc - glibc**

glibc 的内存管理器称为 ptmalloc，它其实是一个内存池，只有在某些情况下，它申请的内存才会调用 sys_trim 返还给 os。因此调用它实现的 free 可能并不会释放内存，可能导致 OOM。









---

## end

