# 语言：C++ 杂

---

[TOC]

---

> https://github.com/cpp-best-practices/cppbestpractices



---

## 可参考的实现

> ClickHouse：https://github.com/ClickHouse/ClickHouse/tree/master/base
>
> Boost：https://github.com/boostorg/boost/tree/master/libs

**编译期获取数组大小**

```cpp
// https://github.com/ClickHouse/ClickHouse/blob/master/base/base/arraySize.h
template <typename T, std::size_t N>
constexpr size_t arraySize(const T (&)[N]) noexcept { return N; }
```

**简易线程池**

```cpp
class ThreadPool {
 public:
    ThreadPool(size_t numThreads);
    ~ThreadPool();

    void enqueueTask(std::function<void()> task);

 private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;

    std::mutex queueMutex;
    std::condition_variable condition;
    bool stop;

    void workerThread(int thread_id);
};

ThreadPool::ThreadPool(size_t numThreads) : stop(false) {
  for (size_t i = 0; i < numThreads; ++i) {
    workers.emplace_back(&ThreadPool::workerThread, this, i);
  }
}

ThreadPool::~ThreadPool() {
  {
    std::unique_lock<std::mutex> lock(queueMutex);
    stop = true;
  }
  condition.notify_all();
  for (std::thread &worker : workers) {
    worker.join();
  }
}

void ThreadPool::enqueueTask(std::function<void()> task) {
  {
    std::unique_lock<std::mutex> lock(queueMutex);
    tasks.push(std::move(task));
  }
  condition.notify_one();
}

void ThreadPool::workerThread(int thread_id) {
  while (true) {
    std::function<void()> task;
    {
      std::unique_lock<std::mutex> lock(queueMutex);
      condition.wait(lock, [this] { return stop || !tasks.empty(); });
      if (stop && tasks.empty()) {
        return;
      }
      task = std::move(tasks.front());
      tasks.pop();
    }
    task();
  }
}
```

**实现 defer**

TODO
或者叫 scope_exit（rust）。

```cpp
class Defer {
public:
    explicit Defer(std::function<void()> f) : cleanupFunction(f) {}
    ~Defer() { cleanupFunction(); }
private:
    std::function<void()> cleanupFunction;
};

// 使用模板、不存 function 可以减少开销
// 缺点是创建大量实例化会使程序膨胀（比如单测中多次使用）
template <typename F> // 最好限制一下 is_invocable 避免大量编译错误
class Defer {
public:
	Defer(F&& f) : cleanup(std::forward<F>(f)) {}
	~Defer() { cleanup(); }
private:
	F cleanup;
};

// 封装，使其像 go 的 defer {...} 写法，不用每次创建 lambda
#define defer Defer __defer##__LINE__ = [&]()
// 不过最后要加分号
defer { delete p; };
```

或是直接用一个智能指针（但有额外开销）：

```cpp
// shared_ptr 即使传入 nullptr 也会调 deleter
// 当传入的不是 nullptr 时，注意进行 delete
std::shared_ptr<void> release_on_return(nullptr, [&](auto) { // 需要 auto，调用时会传一个参数（保有的指针）
    // ...
});

// （unique_ptr 的开销相对更小，但使用麻烦）
// 如果 deleter 不是函数，unique_ptr 需要将 deleter 类型作为模板参数
// 赋值 nullptr 时不会调用 deleter，所以需要赋值一个新指针。但注意要在 deleter 中释放 new 的对象不然也会泄露
auto f = [&](int* p) {
    delete p;
    // ...
};
std::unique_ptr<int, decltype(f)> release_on_return(new int, f);
```

**简易 benchmark** / **计时**

> 来自 https://zh.cppreference.com/w/cpp/algorithm/reduce
> https://zh.cppreference.com/w/cpp/container/set/emplace
> 其它可参考：https://zh.cppreference.com/w/cpp/language/attributes/likely
>
> 可以像 cppref likely 的示例代码一样用 `volatile int result` 作为函数结果来保证有副作用。

```cpp
// 简单：
using Time = std::chrono::milliseconds;
auto start = std::chrono::system_clock::now();
// do sth
auto ms = std::chrono::duration_cast<Time>(std::chrono::system_clock::now() - start);
cout << ms.count() << '\n';

//
std::cout.imbue(std::locale("en_US.UTF-8"));
std::cout << std::fixed << std::setprecision(1);
auto eval = [](auto fun)
{
    const auto t1 = std::chrono::high_resolution_clock::now();
    const auto [name, result] = fun();
    const auto t2 = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double, std::milli> ms = t2 - t1;
    std::cout << std::setw(28) << std::left << name << "sum: "
        << result << "\t time: " << ms.count() << " ms\n";
};
{
    const std::vector<double> v(100'000'007, 0.1);

    eval([&v]{ return std::pair{"std::accumulate (double)",
                                std::accumulate(v.cbegin(), v.cend(), 0.0)}; } );
    eval([&v]{ return std::pair{"std::reduce (seq, double)",
                                std::reduce(SEQ v.cbegin(), v.cend())}; } );
    eval([&v]{ return std::pair{"std::reduce (par, double)",
                                std::reduce(PAR v.cbegin(), v.cend())}; } ); // 可并行
}
```

或：

```cpp
void time_it(std::function<int()> set_test, std::string what = "")
{
    const auto start = std::chrono::system_clock::now();
    const auto the_size = set_test();
    const auto stop = std::chrono::system_clock::now();
    const std::chrono::duration<double, std::milli> time = stop - start;
    if (what.empty() && the_size)
        std::cout << std::fixed << std::setprecision(2)
                  << time << " for " << what << '\n';
}
```

C：

```c
#include <time.h>
#define BILLION 1000000000L
#define SIZE 1000000

{
    uint64_t diff;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (size_t i = 0; i < SIZE; i++) {
        sqrt(sequence[i]);
        __asm__ __volatile__("" : : : "memory");
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    diff = BILLION * (end.tv_sec - start.tv_sec) + end.tv_nsec -
        start.tv_nsec;
    printf(" sqrt, %llu\n", (long long unsigned int)diff);
}
```

**重载 new 简单实现内存泄露检测**

> TODO
> https://www.zhihu.com/question/29859828/answer/1798470821
>
> https://zh.cppreference.com/w/cpp/memory/new/operator_new
>
> 可以统计哪些地方是内存分配频繁，哪些地方存在大内存消耗，哪些内存长时间未释放。
> 但最好不这么做。

```cpp
void* operator new(std::size_t size, const char* file, int line);
void* operator new[](std::size_t size, const char* file, int line);

#define new new (__FILE__, __LINE__)
```

给内存分配/释放加日志：

```cpp
inline atomic_bool trace = false;

void* operator new(std::size_t sz) {
    if (trace) {
        bool old = trace.exchange(false);
        {
            auto stack = boost::stacktrace::stacktrace();
            std::printf("global new called: %zu bytes\n", sz);
            cout << stack << endl;
        }
        trace.store(old);
    }
    if (sz == 0) ++sz;
    if (void* ptr = std::malloc(sz)) return ptr;

    throw std::bad_alloc{};  // [new.delete.single]/3
}

void operator delete(void* ptr, size_t size) noexcept { // 注意 new(size_t) 对应 delete(void*, size_t)
    if (trace) {
        bool old = trace.exchange(false);
        {
            auto stack = boost::stacktrace::stacktrace();
            std::printf("global delete called: at %p\n", ptr);
            cout << stack << endl;
        }
        trace.store(old);
    }
    std::free(ptr);
}
```

**封装 allocator 监控内存使用**

[cppref](https://zh.cppreference.com/w/cpp/named_req/Allocator)：

```cpp
template<class T>
struct Mallocator
{
    typedef T value_type;

    Mallocator() = default;
    template<class U>
    constexpr Mallocator(const Mallocator <U>&) noexcept {}

    [[nodiscard]] T* allocate(std::size_t n)
    {
        // if (n > std::numeric_limits<std::size_t>::max() / sizeof(T))
        //    throw std::bad_array_new_length();

        if (auto p = static_cast<T*>(std::malloc(n * sizeof(T))))
        {
            report(p, n);
            return p;
        }

        throw std::bad_alloc();
    }
    void deallocate(T* p, std::size_t n) noexcept
    {
        report(p, n, 0);
        std::free(p);
    }
private:
    void report(T* p, std::size_t n, bool alloc = true) const
    {
        std::cout << "在 " << std::hex << std::showbase
                  << reinterpret_cast<void*>(p) << std::dec
                  << (alloc ? " 分配 " : " 解分配 ")
                  << sizeof(T) * n << " 个字节\n";
    }
};
```

可参考：

```cpp
#include <memory>
#include <iostream>
#include <unordered_map>

// 自定义分配器
template <typename T>
class TrackedAllocator
{
public:
    using value_type = T;

    TrackedAllocator() : allocatedMemorySize(0) {}

    template <typename U>
    TrackedAllocator(const TrackedAllocator<U>& other) noexcept {
		allocatedMemorySize = other.getAllocatedMemorySize();
	}

    T* allocate(std::size_t n)
    {
        std::size_t allocationSize = n * sizeof(T);
        std::cout << "Allocating " << allocationSize << " bytes." << std::endl;
        allocatedMemorySize += allocationSize;
        return static_cast<T*>(::operator new(n * sizeof(T)));
    }

    void deallocate(T* p, std::size_t n)
    {
        std::size_t deallocationSize = n * sizeof(T);
        std::cout << "Deallocating " << deallocationSize << " bytes." << std::endl;
        allocatedMemorySize -= deallocationSize;
        ::operator delete(p);
    }

    std::size_t getAllocatedMemorySize() const
    {
        return allocatedMemorySize;
    }

    template <typename U>
    struct rebind
    {
        using other = TrackedAllocator<U>;
    };

private:
    std::size_t allocatedMemorySize;
};

// 为std::unordered_map指定自定义分配器
template <typename Key, typename Value>
using TrackedMap = std::unordered_map<Key, Value, std::hash<Key>, std::equal_to<Key>,
                                      TrackedAllocator<std::pair<const Key, Value>>>;

int main()
{
    // 创建使用自定义分配器的std::unordered_map
    TrackedMap<int, std::string> map;

    // 添加一些元素
    map[1] = "One";
    map[2] = "Two";
    map[3] = "Three";
    map[5] = "123";

    // 获取已分配的内存大小
    std::size_t allocatedMemorySize = sizeof(map) + map.get_allocator().getAllocatedMemorySize();
    std::cout << "Allocated memory size: " << allocatedMemorySize << " bytes." << std::endl;
}
```

**swap / swap 的实现与使用**

通常会先`using std::swap;`，使用时`swap(a, b);`。
这样在自定义了 a, b 的 swap 时，会优先使用自定义的；在没有定义时，使用 std 的。尤其适合模板（未知类型）的情况。见 *C++ - 无限定的名字查找*。

实现 TODO

**operator = 简单实现**

有时通过复用拷贝构造，可以简化拷贝赋值逻辑：

```cpp
A& A::opeartor =(const A& o) {
    this->swap(A(o));
    return *this;
}
```

copy and swap（复制并交换）只需类实现了 swap。虽然会多一次 swap 逻辑和析构，但是是强异常安全和自赋值安全的。
可见：https://zh.cppreference.com/w/cpp/language/operators

**string_view**

https://github.com/apache/doris/blob/master/be/src/vec/common/string_ref.h

**获取当前文件所在路径**

```cpp
#include <source_location> // C++20
constexpr std::string_view FileDir() {
    std::source_location loc = std::source_location::current();
    std::string_view path = loc.file_name(); // 直接 __FILE__ 也可
    return path.substr(0, path.find_last_of("/\\"));
}
constexpr auto name = FileDir();
cout << name << '\n';
```

**执行、打印并返回结果**

```cpp
#define EXEC_AND_PRINT(...) \
	[]() { \
        int result = (__VA_ARGS__); \
        printf("%s = %d, at %s:%d\n", #__VA_ARGS__, result, __FILE__, __LINE__); \
        return result; \
    }()
```

**多个变量的 maybe_unused**

```cpp
[](...) {} (a, b, c);
```

**字符串根据指定分隔符切分 / Split**

```cpp
// 需保证参数 s 的生命期不短于返回值。
vector<string_view> Split(string_view s, char sep) {
	vector<string_view> ret;
	size_t last = 0;
	for (size_t i = 0; i < s.size(); ++i) {
		if (s[i] == sep) {
			if (last < i) {
				ret.emplace_back(s.data() + last, i - last);
			}
			last = i + 1;
		}
	}
	if (last < s.size()) {
		ret.emplace_back(s.data() + last, s.size() - last);
	}
	return ret;
}
```

**mt19937 状态保存**

https://stackoverflow.com/questions/18361050/saving-random-number-generator-state-in-c11





## 一些代码

**accumulate**

注意，泛型中 T 可能没有 operator +=，所以应使用 operator = 和 +；`a = a + b;`可以写为`a = std::move(a) + b;`。

```cpp
template <class InputIt, class T>
T accumulate(InputIt first, InputIt last, T init) {
    for (; first != last; ++first)
        init = std::move(init) + *first;
    return init;
}
```

**获取随机数**

`mt19937{ random_device{}() }`。

**二进制输出整数**

直接用 bitset。

```cpp
cout << std::bitset<32>(x); // 其它流输出方式均可
```

**利用 true_type/false_type 类型进行重载**

其实与写 if constexpr 一样，但可用于旧版本。

```cpp
void f(void* p, std::true_type) {
	cout << "is int: " << *reinterpret_cast<int*>(p) << '\n';
}
void f(void* p, std::false_type) {
	cout << "is not int\n";
}
template <class T>
void g(T x) {
	f(&x, std::is_same<T, int>());
}
g(1);
g(1.);
```

**在容器中插入元素**

```cpp
// #1
container.resize(...);
std::copy(
    std::move_iterator(newElems.begin()),
	std::move_iterator(newElems.end()),
	std::next(container.begin(), insertPos)
);

// #2
container.insert(
	container.cend(),
    std::move_iterator(newElems.begin()),
	std::move_iterator(newElems.end())
);
```

**在容器中移除元素**

```cpp
std::erase(std::remove_if(begin, end, cond), end)
std::erase_if
```

**自定义 std::hash**

```cpp
// namespace std { // 不需要包括在 namespace std 中，这也容易导致 UB
template<>
struct std::hash<vector<float>> {
	std::size_t operator()(const std::vector<float>& vec) const noexcept {
		std::size_t seed = vec.size();
		for(auto f : vec) {
			uint32_t x = reinterpret_cast<uint32_t&>(f);
			x = ((x >> 16) ^ x) * 0x45d9f3b;
			x = ((x >> 16) ^ x) * 0x45d9f3b;
			x = (x >> 16) ^ x;
			seed ^= x + 0x9e3779b9 + (seed << 6) + (seed >> 2);
		}
		return seed;
	}
};
// } // namespace std

// 使用
auto val = std::hash<vector<float>>{}(vec);
```

注意，只能在 std 中添加模板特化，否则是 UB。具体见 *C++ - 在 std 中添加声明*。

**间接排序**

指根据 data 的大小排序下标数组，不改变 data 本身。用于对象较大的情况时，可减少交换操作。

```cpp
std::vector<int> p(n);
std::iota(p.begin(), p.end(), 0);
std::sort(p.begin(), p.end(), [&](const auto& i,const auto& j) {
    return data[i] < data[j];
});
```

排序通常有局部性，但间接排序不会改变数据位置，因此局部性很差，相邻两次比较的对象可能在内存中离得很远，很容易 cache miss。因此构造 {i, data[i]} 结构体一起排，有时候可能更快（除非对象太大）。
不过如果要排的数据本身不是值（比如指针）、本身也不会有局部性，就无所谓了。

**将 a<=>b 的结果转为 1、0、-1**

`(x>0)-(x<0)`能实现大于0返回1、小于0返回-1。
但为什么不用条件判断？

```cpp
template <typename T>
int sign(T val) {
    return (val > T(0)) - (val < T(0));
}
```

**thread RAII**

`std::unique_ptr<std::thread> t;`就不需要在析构时释放 thread 了。
但如果要在析构时做处理（比如调`t.join()`），则还是要保存`thread*`、手动释放`delete t`。通常没必要存 thread*，thread 也不大。


### 字符串

**EndsWith**

```cpp
auto endsWith = [&](const std::string& str, const std::string& suffix) {
    if (suffix.size() > str.size()) {
        return false;
    }
    return str.substr(str.size() - suffix.size()) == suffix;
};
```




**字符串转数字**

> https://zhuanlan.zhihu.com/p/618928075

总结：用 stoi 系列；如果有 C++17 用 from_chars；stringstream 可以方便转换包含多个数字的字符串。

- atoi、atol、atoll：很早的 C 函数，直接传递 const char*。
    如果结果不能用对应类型表示则是 UB，即没有边界检查；当不能转换时直接返回0，不方便错误检查。
- strtol、strtoll：C 的函数，传递 const char*，可以指定结束位置和数的进制。
    如果结果不能用对应类型表示则设置 errno；当不能转换时直接返回0，不方便错误检查。
- sscanf：C 的函数，因为缓冲区溢出和类型安全的问题很少用。
- stringstream：可以直接用 operator >> 将数据输入到变量。通用但效率低。
- stoi、stol、stoll、stoul、stof 等（常用）：传递 const string&，可以指定数的进制，可转换浮点。实际是调用 strtol。
    如果结果不能用对应类型表示则设置 errno；当不能转换时抛出异常。
- from_chars（C++17 起）：传递一对 const char* first, last，可以指定数的进制，可转换浮点。高效。
    通过参数返回结果。返回类型为 from_chars_result，包含一个指针和一个错误码。
    可以接收 string_view（stoi 只接收 string，因此传递 string\_view 时会拷贝创建一个 string）。
- spanstream（C++23 起）：与 stringstream 类似，但效率高一点。

**字符串转大写**

```cpp
// 1
for (auto& c: s) c = toupper(c);
// 2
std::transform(s.begin(), s.end(), s.begin(), [](char c) { return std::toupper(c); });
// 或
std::transform(s.begin(), s.end(), s.begin(), ::toupper);
// 注意这里不能用 std::toupper，只能用 C 的全局的 toupper，不知道为什么
// 如果 C 用宏实现 toupper 就会出错
```

**在字符串中使用中文字符**

```cpp
// wchar_t、wstring 可以以 unicode 字符为单元存储数据，便于遍历
// 但必须使用单独的一套函数，与 char、string 不同
const wchar_t* s = L"山东省省委书记省abc"; // 带L前缀的是宽字符(串)字面量

int count = 0, len = std::wcslen(s);
for (int i = 0; i < len; ++i) {
    count += (s[i] == L'省');
}
std::cout << count << '\n';

// 或者直接将中文存入 char 数组，然后使用子串比较进行字符检查
// 中文的各字节会被拆分成多个字节保存。但显然可能出错
const char* s = "山东省省委书记省abc";
const char *tmp = s;

int count = 0;
while ((tmp = std::strstr(tmp, "省")) != nullptr) {
    std::cout << tmp << '\n';
    ++tmp;
	++count;
}
std::cout << count << '\n';
```



### 输入输出

**endl**

[endl](https://zh.cppreference.com/w/cpp/io/manip/endl) 输出换行符到任何 basic_ostream 类型并进行 flush。会影响输出性能。

> 多数实现中，标准输出 stdout（不包含文件输出）是行缓冲的，即写入'\n'也会导致 flush，除非执行过[`std::ios::sync_with_stdio(false)`](https://zh.cppreference.com/w/cpp/io/ios_base/sync_with_stdio)。
>
> 可以输出 std::flush 来 flush 不需要换行的输出。

**ostream**

```cpp
// 为某个类重载 <<
std::ostream& operator<<(std::ostream& os, const A& p) {
    os << p.x << ", ";
    return os;
}
// 通过迭代器的方式使用 << 输出
copy_if(begin(a), end(a),
	std::ostream_iterator<A>(std::cout, "; "),
	[](const Product& p){
		return !p.name_.starts_with("none");
	});
// 输出5个随机值
std::mt19937 rng; // 默认构造，使用固定的种子
generate_n(std::ostream_iterator<std::mt19937::result_type>(cout, ' '), 5, std::ref(rng));
```

**iostream**

iostream 内部包含输入位置和输出位置两个指针，在每次输入/输出时更新。类似文件读写，也可以通过 seek, tell 读写指针位置。
stringstream 的输入是将它保存的字符串的内容输入到其它对象中，输出是将其它对象中的内容输出到它保存的字符串里。

**ostringstream**

ostringstream 以流输出的格式，将变量或字符串保存。
可通过 .str() 取出保存的字符串，用 cout、ofstream 等输出，或赋值给其它字符串。
可以在构造时赋值一个字符串。后续输出的内容会覆盖或追加已保存的字符串（取决于设置的模式，默认覆盖）。

```cpp
class LogMessageFatal {
 public:
	LogMessageFatal(const char* file, int line) {
		log_stream_ << "\n[FATAL] "
					<< "[" << get_time() << "] "
					<< file << ":" << line << ": ";
	}
	~LogMessageFatal() noexcept(false) {
		LOG(ERROR) << log_stream_.str();
		throw PSError(log_stream_.str());
	}
	std::ostringstream &stream() { return log_stream_; } // 需要将日志保存，因此不能直接先输出

 private:
	std::ostringstream log_stream_; // 需要将输出保存作为 PSError 信息

	DISABLE_COPY_AND_ASSIGN(LogMessageFatal);
};
```

**istringstream**

istringstream 以流输入的格式，将保存的字符串输入到变量中。

```cpp
ifstream input(filename);
string line, buf;
while (getline(input, line)) {
    istringstream in(line);
    int label;
    in >> label; // 从字符串 line 中读入一个整数

    in >> buf; // 然后读入一个字符串
    cout << label << ": " << buf << '\n';
}
```

**ifstream**

ifstream 以流输入的格式，将从文件中读取的字符串输入到变量中。
如果文件不存在或打开失败，则 is_open 为 false。
虽然有 close 接口但不需要手动调用，能正确析构即可。

```cpp
ifstream input(model);
CHECK(input.is_open()) << "Old model doesn't exist in path: " << model;

input >> num_feature;
for (size_t i = 0; i < num_feature; ++i) {
    input >> weight[i];
}
```

**ofstream**

ofstream 以流输出的格式，将变量或字符串输出到文件中。

```cpp
std::ofstream fout(filename);
fout << total_iteration_ << '\n';
fout << weight_.size() << '\n';
for (auto w: weight_) {
    fout << w << ' ';
}
fout << '\n';
```



### 算法应用







**uninitialized_copy**

见：https://zh.cppreference.com/w/cpp/memory/uninitialized_copy





### 迭代器应用

**back_inserter**

```cpp
vector<int> v{1, 2, 3};
fill_n(back_inserter(v), 3, -1);

generate_n(
    back_insert_iterator<std::vector<int>>(v), // back_inserter(v),
    10,
    [n = 0]() mutable { return ++n; }
);

vector<int> v{1, 2, 3, 4, 5};
deque<int> d;
copy(v.begin(), v.end(), front_inserter(d));
```

**move_iterator**

```cpp
string concat = accumulate(move_iterator(v.begin()), move_iterator(v.end()), string());

list<string> s{"1", "2", "3"};
vector<string> v1(s.begin(), s.end()); // 复制
vector<string> v2(make_move_iterator(s.begin()), make_move_iterator(s.end())); // 移动
```





---

## 模板使用

**形参包示例**

```cpp
template<class... Ts>
struct A {
    // 通过`sizeof...`获取变长参数包中的参数数量
	size_t nSize = sizeof...(Ts);

    // 调用函数并连接，也可以是加减等二元运算符
    // 这类更推荐 std::conjunction？
	static_assert(std::is_copy_constructible_v<Ts> && ...);
};

// 包展开的捕获；包展开的简写函数模板
static auto in = [&vals...](auto&& k, auto&&... args)-> bool {
    // 连接 bool 表达式
	return ((args == k) || ...);
};
// 等价于4个 if 的或
if(in(x,'x','X','e','E')) {
    // ...
}

// 多继承
template<class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };
// 显式推导指引（C++20 起不需要）
template<class... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

// 依次转发
template<typename... Args>
void f(Args... args) {
    g(forward<Args>(args)...);
}

// concept 修饰的任意个参数
void f(std::same_as<int> auto... args);
```

**sort**

```cpp
template <typename T>
struct Less {
	bool operator()(const T& a, const T& b) const { return a < b; }
};

template <typename T, typename Func = Less<std::remove_pointer_t<T>>> // less需要传入T指向的对象
void Sort(T st, T ed, Func less = Func()) { // T是指针或迭代器
    for (T i = st; i != ed; ++i) {
		T mi = i;
		for (T j = i; j != ed; ++j) {
			if (less(*j, *mi)) mi = j;
		}
		auto tmp = *i;
		*i = *mi;
		*mi = tmp;
    }
}
```







---

## 优化/找 bug

见 *most vexing parse*。

**三五零法则**

如果需要析构释放资源，就应该定义或禁用拷贝/移动函数。

```cpp
struct C {
    C(int x = 0) {
        p = new int{x};
    }
    ~C() {
        delete p;
    }
    int* p;
};
C c;
c = C(2);
cout << *c.p;
```

**const char\* 隐式转换为 string**

见 *C++ - 引用初始化*。

```cpp
auto kRun = "run"; // const char*
// const auto kRun = "run"; // const char* const，注意这个 const 是 top layer

void Report(const std::string& s, int value) {}
void ReportRunTime(int value) {
  Report(kRun, value); // 每次调用都会拷贝一个 string。如果是 string_view 倒能省掉拷贝
}
// 更直观：string 不能直接绑定引用到 const char*，显然要构造并拷贝一个
const string &rs = "run";
```

**条件运算符**

见 *Quiz - 319*。

```cpp
double Get() {return 1.;}
int64 key = 221795837984284688ll;
int64 x = i == 0 ? key : Get();
```

**排序**

```cpp
void addExtrapolationPoint(vector<pair<double,double>>& vec, double& delta) {
  const auto& last_point = vec.back();
  vec.emplace_back();
  vec.back().first = last_point.first + 1.0;
  vec.back().second = last_point.second + delta;
}
void swapTwoPoints(pair<double,double>& a, pair<double,double>& b) {
  static pair<double,double> tmp = a;
  a = b;
  b = tmp;
  return;
}
int main() {
  vector<pair<double,double>> input_vector = getInputVector();
  for (int i = 0; i < input_vector.size(); i++) {
    for (int j = 0; j < i; j++) {
      if (input_vector[j].first > input_vector[j+1].first) {
        swapTwoPoints(input_vector[j], input_vector[j+1]);
      }
    }
  }
}
```

问题及建议：

- 取 back 前必须判断 vector 是否为空，空容器上调用 back 是 UB。
- vector emplace_back 触发扩容时，迭代器会全部失效。
- static 变量只在第一次执行时初始化，所以`static auto tmp = a;`只会执行一次！初始化和赋值要分开。而且其实没必要用 static？
- 基本/小的类型作为参数 double 没必要传引用或 const 引用，就 8B，引用本身可能也要 8B；而且传引用会导致访存，传值可能直接存在寄存器里。
- 这里没必要自己实现 swap。用 std::swap 也更清晰。
- 同理，没必要自己写 sort，还是冒泡。
- `pair<double,double>`最好定义一个别名。用的多的话最好定义一个类，first、second 很不直观。
    tuple 类似，`std::get<0>(tuple)`非常不方便。
- 循环变量最好用 size_t。
- 函数名用 add 不准确，应该是 append ...。

**move**

```cpp
{
    vector<Node> v;
    // 获取v...

    // 拷贝
    for (const auto &i: v)
        ans.add(i);
    // 更好的版本（后续不再使用v）
    for (auto &i: v)
        ans.add(std::move(i));
}
```

**注意模板中的常量类型**

```cpp
std::vector<int> v;
// 初始化v...
int64_t sum = std::accumulate(v.begin(), v.end(), 0);
```

问题：[accumulate](https://zh.cppreference.com/w/cpp/algorithm/accumulate)是一个模板函数，其返回值取决于传入的初始值 init 的类型。
因此使用 0 会返回 int，使用 0ll 才会返回 int64_t。

```cpp
template<class InputIt, class T>
constexpr // C++20 起
T accumulate(InputIt first, InputIt last, T init)
{
    for (; first != last; ++first)
        init = std::move(init) + *first; // C++20 起有 std::move
    	// 表达式求值后，init就会被赋新值，所以move了也没事
    return init;
}
```

此外，用[reduce](https://zh.cppreference.com/w/cpp/algorithm/reduce)求和可能效率更高，因为允许并行。

**使用 {} 初始化**

在定义变量时，可能会由于笔误或歧义的语法解析规则 (most vexing parse)，导致写成了函数声明，而非变量定义。
所以构造函数应使用`{}`而非`()`。

```cpp
using less = bool (*)(const Node&, const Node&);
set<Node, less> st(less); // 应该传递函数指针，这里传了函数类型，变成了函数声明
```

**实参形参的类型不匹配 / const string& 还是 const char\***

如果实参形参的类型不匹配，则在传入时会隐式构造、生成临时对象（常见于 (const) char* 与 string），将它赋给引用成员显然是错的（不管形参是不是引用，实际的参数都是临时对象）。
实参的生命周期将仅限于函数内，且会发生额外的构造和拷贝。

```cpp
struct Node {
	Node(const string& s): s(s) {}
	const string& s;
} n {"abc"}; // 生成并引用了临时的 string

void f(const string& s) {}
f("abc"); // const char* 转为 string
```

使用 const char* 做形参，可以避免产生临时变量、便于使用 C 函数。
使用 string 做形参，获取长度方便（char* 需要从头遍历直到找到 \0 才能确定长度，或者自己带长度）、使用方便（如果此时不修改，更推荐 string_view）。

**修改 string.data**

（具体见 *STL - string*）string 要能支持转为 const char*，标准规定通过 c_str、data 返回的指针指向的字符串，其末尾一定要有空终止字符。通常情况下，为了避免拷贝、O(1) 直接完成转换，string 的实现仍然会在字符串的最后添加 \0（本质还是 Unix/C 字符串要以 \0 结尾带来的问题）。也因此，访问和修改 data[size] 通常不会导致写非法内存（但依然不建议使用，看实现）。

```cpp
string s(3, 'a'); // size, capacity 都是 3，但底层 buffer 实际是 4B
s.data[3] = 'b';
cout << s << '\n'; // aaa
cout << s.data() << '\n'; // aaab
```

**指针**

下面这种写法通常一个使用 unique\_ptr、一个使用 raw ptr。如果有需要也可以一个 shared\_ptr，一个 weak\_ptr？

```cpp
struct A { B* b; }
struct B { A* a; }
```





---

## 未定义行为

**向 memcpy 传递空指针**

**如果 memcpy 的两个参数 src, dest 为空指针或无效指针，则是 UB**，即使传递的字节数 count 为0。
因此标准允许编译器认为 src 和 dest 不可能是空指针，在 memcpy 的调用方和被调用方（即函数本身）进行优化。

```cpp
// 当前环境中，gcc 和 clang 会进行空指针比较
// count 为常量0时，编译器可能直接不进行拷贝
int f1(void* dest, const void* src) {
	memcpy(dest, src, 0);
	if (dest == nullptr) { // 判 dest 还是 src 没有影响
		return 1;
	}
	return 2;
}
// clang 会进行空指针比较，gcc 不会，直接返回2
// count 为常量时，编译器可能不调用 memcpy，而是自己生成拷贝逻辑，比如 rep movsq
int f2(void* dest, const void* src) {
	memcpy(dest, src, 1024);
	if (dest == nullptr) {
		return 1;
	}
	return 2;
}
// clang 会进行空指针比较，gcc 不会，直接返回2
int f3(void* dest, const void* src, size_t cnt) {
	memcpy(dest, src, cnt);
	if (dest == nullptr) {
		return 1;
	}
	return 2;
}
```

gcc 有个 attribute 叫 *nonnull*，它可以说明函数，声明某个参数一定不是空指针，memcpy 的参数就相当于有该属性。

**使用 memcpy 拷贝大小为 0 的 vector data 是 UB**：当 vector 的 size 为0时，[data()](https://zh.cppreference.com/w/cpp/container/vector/data) 可能会也可能不会返回空指针，所以此时使用 memcpy 拷贝 vector 的底层数组时可能是 UB：

```cpp
vector<int> v(0);
char c[10] = {0};
memcpy(c, v.data(), v.size() * sizeof(int));
// -fsanitize=undefined: runtime error: null pointer passed as argument 2, which is declared to never be null
```

使用 std::copy 可以避免这个问题，在数据范围为0时它不会拷贝。

**使用未初始化的标量类型**

```cpp
int f(int x) {
    int a;
    if(x)
        a = 42;
    return a;
}
```

编译器可以假定不存在 使用未初始化（实际为默认初始化）的标量类型 a（包括算术类型、指针、枚举、nullptr_t）这一 UB，因此可认为分支始终为 true，以使 a 得到赋值、没有发生 UB。
因此编译器可将函数优化为：`int f(int) { return 42; }`。

















---

## end





