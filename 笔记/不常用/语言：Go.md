# 面试 语言：Go

Tags: 实习


-----
[TOC]


----------
> Effective Go 中文：https://www.kancloud.cn/kancloud/effective/72201
>
> Go 的设计与实现：https://draveness.me/golang/
>
> TODO：
> go 常见面试题：https://learnku.com/articles/62720

## Go

与通常以类型层次与继承为根基的面向对象设计（OOP）语言（如C++、Java）不同，Go 的核心思想就是组合（composition）。Go 进一步解耦了对象与操作，实现了真正的鸭子类型（Duck typing）：一个对象如果能嘎嘎叫那就能当做鸭子，而不是像 C++ 或 Java 那样需要类型系统去保证：一个对象先得是只鸭子，然后才能嘎嘎叫。

go是Google开发的一种静态强类型、编译型、并发型、具有垃圾回收功能的编程语言。

**init()**
> https://blog.csdn.net/bestzy6/article/details/122503275
> https://zhuanlan.zhihu.com/p/163251113https://zhuanlan.zhihu.com/p/163251113

init 标示符不会引入绑定，就像空白标示符('_')（以及main？）表现的一样。所以无法自行引用`init()`。
一般为初始化表达式中不能被计算的那部分赋值一个值（如需要for循环初始数组）。
使用空白标识符`import _ "image/png"`，可以只进行一个包的`init()`，而无需调用这个包的内容（go对包导入的要求严格）。

**byte**

go 通过`byte`和`rune`表示一个字符。字符默认是一个`rune`，即 go 默认为 unicode 字符集、utf-8 编码。
因为 utf-8 是变长的，对于 ASCII 只占用1B，对于中文字符占用3B。

`byte`是`uint8`的别名：`type byte = uint8`。
代表了一个ASCII字符，可通过如下赋值：

```go
ch := 'A' // rune 字符
ch := byte('A') // byte
var ch byte = 65 // uint8
var ch byte = '\x41' // 十六进制（\x+两位数）或八进制（\+三位数）也可，注意用''包括
var ch byte = '\377'
```

**rune**

`rune`是`int32`的别名。
代表了一个 utf-8 字符，用来处理中文等字符。
Unicode 通过`\u+4位十六进制数`或`\U+8位十六进制数`表示，在 go 中也叫做 Unicode code point。

```go
var ch int = '\u0041'
var ch2 int = '\u03B2'
var ch3 int = '\U00101234'
fmt.Printf("%d - %d - %d\n", ch, ch2, ch3) // integer：65 - 946 - 1053236
fmt.Printf("%c - %c - %c\n", ch, ch2, ch3) // character：A - β - r
fmt.Printf("%X - %X - %X\n", ch, ch2, ch3) // UTF-8 bytes：41 - 3B2 - 101234
fmt.Printf("%U - %U - %U", ch, ch2, ch3)   // UTF-8 code point：U+0041 - U+03B2 - U+101234
```

**unsafe.Sizeof(x)**

返回一个变量 x 占用的字节数。注意它不会计算 x 指向的数据的大小，因为它是在编译时就确定的！（所以`Sizeof`可赋给常量）
对切片来说，大小固定为24B（1个uintptr、2个int）；但对数组来说，大小为 元素数量*元素大小（注意数组没有长度）。
注意 go 中的`uint, int`同指针，大小取决于机器类型，即一般为 8B！

**string 底层**
go不使用C中的 使用特定标识符作为字符串结尾。而是在string中保存长度（字节个数，非字符个数）。
直接定义的字符串会分配到只读内存段，不允许被修改，只能重新创建、赋值。旧的对象会被 gc 回收。
对slice赋值，会为slice重新分配内存，拷贝原字符串修改。

一个 string 的大小固定为 16B。

**string 与 []byte**
string是8位字节的集合，通常但不一定代表UTF-8编码的文本。
一个string既可以被拆分为字符，也可以被拆分为字节；前者使用`[]rune`切片表示，后者使用`[]byte`切片表示。
string可以为空，但是不能为nil。string的值是不能改变的。

```
type stringStruct struct {
    str unsafe.Pointer
    len int
}
type slice struct {
    array   unsafe.Pointer
    len     int
    cap     int
}
```
string的`str`在赋值时就是用`*byte`（或`*rune`）赋值的，所以string的底层数组就是[n]byte（或`[]rune`？当要保存utf-8时使用后者？）。
所以string和[]byte的底层只差一个cap（切片有容量），所以它们在内存布局上是可对齐的（对齐到16B，指针和len都在0, 16位置处）。
所以`copy(dst, src []Type)`有一种特例`copy(dst []byte, src string)`（可以将string拷贝到[]byte上，允许这一种类型不同）。

[]byte是可以修改某个字符的。
string不能，只能重新赋值，因为string结构体的str指针指向一个字符串常量的地址，地址里的内容不可被改变，因为是只读的。但这个指针可以指向不同的地址。
所以以下操作的含义是不同的：

```
s := "S1" // 分配存储"S1"的内存空间，s结构体里的str指针指向这块内存
s = "S2"  // 分配存储"S2"的内存空间，s结构体里的str指针转为指向这块内存

b := []byte{1} // 分配存储'1'数组的内存空间，b结构体的array指针指向这个数组。
b = []byte{2}  // 将array的内容改为'2'
```

string的指针指向的内容是不可更改的。每更改一次字符串，要重新分配一次内存，之前分配的空间还需要gc回收，导致string相较于[]byte低效。

此外，用 range 遍历 string 和 []byte 的值时，前者以rune类型（utf-8编码）为单位，后者为byte类型，结果会不同。
但用 for 下标遍历 string 时，则是按照 byte 即 ASCII 码去读取。所以涉及中文字符等 unicode 时，可用 for range。

> string 与 []byte 的使用场景：
> string 可以比较，[]byte 不可，所以 []byte 不可以作为 map 的 key。
> []byte 可以赋值为 nil 用于特殊的语义，string 不可。
> []byte 切片很灵活，可修改下标，且性能更高。

**string 与 []byte 转换**
标准转换：
```
// []byte和string都是独立的，[]byte可修改，不影响string

// string to []byte
s1 := "hello"
b := []byte(s1)

// []byte to string
s2 := string(b)
```

强转换（通过unsafe和reflect）：
```
// []byte和string不是独立的！
// 如果String2Bytes，[]byte不可修改，因为指向的是只读区域
// 如果Bytes2String，[]byte的修改会影响string的结果

func String2Bytes(s string) []byte {
	sh := (*reflect.StringHeader)(unsafe.Pointer(&s))
	bh := reflect.SliceHeader{
		Data: sh.Data,
		Len:  sh.Len,
		Cap:  sh.Len,
	}
	return *(*[]byte)(unsafe.Pointer(&bh))
}

func Bytes2String(b []byte) string {
	return *(*string)(unsafe.Pointer(&b))
}
```
强转换性能优于标准转换（当数据大时差距会更大）。应尽量避免 []byte 和 string 的标准转换。
原因：当转换的数据较大时（超过定义的32），标准转换方式会进行一次分配内存；此外标准转换需进行拷贝。强转换只是指针的赋值。
但是，强转换会带来安全隐患。
string 转为 []byte 后，[]byte 可进行修改，但由于指向的是只读区域，会导致捕获不到的错误。
只有有高性能要求、需要频繁转换、确保不修改数据的场景，才可使用强转换。

**string to []byte 的标准转换**
string 各操作在`src/runtime/string.go`中。
如`b := []byte("123")`。
关键在于**有一个长为`tmpStringBufSize = 32`的`buf *tmpBuf`**，其中`type tmpBuf [tmpStringBufSize]byte`。是结果未逃逸时，会为每个 []byte 分配32B的缓冲（分配在栈上），如果结果足够小就放在缓冲里，就不需要再去堆中分配内存。

1. 判断字符串是否是常量，如果是常量则转换为等容量等长的字节切片。
2. 如果是变量，先判断生成的切片是否发生内存逃逸：
3. 如果逃逸或字符串长度>32，则根据字符串长度计算出实际分配的容量、为其**分配内存**。
4. 如果未逃逸且字符串长度<=32, 则字符切片容量为32，无需再分配内存（使用buf）。
5. 拷贝。

```
// 1.
bs := []byte("abc")
fmt.Println(len(bs), cap(bs)) // 输出: 3 3

// 3.
a := "abc"
bs := []byte(a) // Println(a ...interface{}) 导致bs内存逃逸
fmt.Println(bs, len(bs), cap(bs)) // 输出： [97 98 99] 3 8

a := ""
bs := []byte(a) // Println(a ...interface{}) 导致bs内存逃逸
fmt.Println(bs, len(bs), cap(bs)) // 输出: [] 0 0

// 4.
a := "abc"
bs := []byte(a) // bs不会逃逸
fmt.Println(len(bs), cap(bs)) // 输出: 3 32

a := ""
bs := []byte(a) // bs不会逃逸
fmt.Println(len(bs), cap(bs)) // 输出: 0 32
```

**[]byte to string**
`s := string([]byte{65,66,67})`。
与前者部分类似：

1. 如果[]byte逃逸或其长度>32，则根据[]byte长度计算出实际分配的容量、为字符串的底层数据**分配内存**。
2. 如果[]byte未逃逸且长度<=32, 则无需再分配内存（使用buf）。
3. 拷贝。

**字符串拼接 concat**

同上类似，如果结果未逃逸且足够小，则使用32B的缓存做结果，否则在堆中分配空间。

**强转换**

> 任何类型的指针`*T`都可以转换为 unsafe.Pointer 类型的指针，它可以存储任何变量的地址。同时，unsafe.Pointer 类型的指针也可以转换回普通指针，而且可以不必和之前的类型`*T`相同。另外，unsafe.Pointer类型还可以转换为uintptr类型，该类型保存了指针所指向地址的数值，从而可以使我们对地址进行数值计算。

string和slice在reflect包中，对应的结构体是reflect.StringHeader和reflect.SliceHeader，它们是string和slice的运行时表达。
```
type StringHeader struct {
	Data uintptr
	Len  int
}
type SliceHeader struct {
	Data uintptr
	Len  int
	Cap  int
}
```
只是SilceHeader多了一个int类型的Cap字段，Date和Len字段是一致的。所以它们的内存布局是可对齐的，就可以直接通过unsafe.Pointer进行转换。

**slice**
`make([]int, len[, cap])`定义切片结构，同时分配底层数组（同时初始化为零值），`array unsafe.Pointer`指向底层数组。
`var arr []int`只定义切片结构（nil切片），没有分配底层数组，所以`array=nil, len=cap=0`。
`pArr := new([]int)`与`var`相同（但arr是切片 ），只定义切片结构，没有分配底层数组，所以`array=nil, len=cap=0`。

len以内的元素可读写，超出len范围会panic。
没有底层数组时，访问`arr[0]`也会panic。
使用`arr/*pArr = append(arr/*pArr, 1)`会为其分配底层数组（如果没有）。

切片的长度为实际元素数，容量为 从array指向的底层数组位置开始，到数组结束有多少个元素。
如`arr := [5]int{0, 1, 2, 3, 4}`，`var s []int = arr[1:3]`，`s`的长度为2，容量为4，且 s 只能看到自己对应的区间！

当对一个数组的切片使用append时，若append后切片的cap没变化（即没有超出原数组大小上限），则会修改原数组对应位置的值；否则切片扩容，cap增长，切片会和数组切断关系，拷贝新数组修改，不再共享引用。

> ```go
> a := make([]int, 0, 2)
> b := append(a, 1)
> c := append(a, 2)
> // 此时：a:[] b:[2] c:[2]
> ```
>
> 注意，切片的长度决定了它能看到哪些数据，后面即使有数据也看不到。
> b 通过 append 将切片第 2 个位置设为了 1，c 通过 append 又将切片第 2 个位置设为了 2。

**slice 扩容规则：**

> https://www.bilibili.com/video/BV1hv411x7we?p=2

设需要扩到`C`，当前容量为`cap`：
若`cap*2 < C`，则令`cap = C`。
否则，若`cap < 1024`，则令`cap = cap * 2`；否则不断重复`cap *= 1.25`，直到`cap >= C`（即可能会扩 1.25, 1.56, 1.95 倍，而不是直接 2 倍）。
这样得到增长后的预估容量`cap`。
`cap * 单个元素占用空间`即为新的底层数组需要的内存`B`。但由于内存一般是分成固定规格的（在`class_to_size`中定义），不会分恰好这么多的内存，而是分稍大的一部分`B'`，则`B' / 元素占用空间`即为实际扩容后的容量。
如：单个 String 对象占用空间16B。

**切片值传递和切片指针传递**

值传递同样拷贝切片（如`s2 := s1[:]`），但是只是浅拷贝一个结构体（因为切片内容是指针，没有实际数据），切片的底层数组不会变，依旧会和原切片互相影响。
但当某个切片发生扩容后，两者的底层数组就无关了，就不会受到影响（因为扩容不会使用之前的内存，会新开一个空间全拷贝进去，使得两切片的底层数组地址分开）。
使用`copy(dst, src []Type)`深拷贝一个切片（要求类型相同）。

注意range遍历切片时，会先拷贝一个切片，每遍历一个数据拷贝一个数据，修改遍历的数据不会影响切片（其实遍历什么，过程中都是值拷贝，直接修改不会有影响）。

**defer原理** TODO
> https://www.bilibili.com/video/BV1hv411x7we?p=9

先注册到一个`*_defer`链表，在return前执行。
每个goroutine的运行时信息`runtime.g`都保存了`*_defer`链表的头指针。
新注册的`_defer`会添加到链表头，实现栈的效果。
...

**panic原理** TODO
> https://www.bilibili.com/video/BV1hv411x7we?p=11



**类型系统**
> https://www.bilibili.com/video/BV1hv411x7we?p=12

go的类型分为内置类型和自定义类型（通过`type`定义）。
不能给内置类型和接口定义方法（接口是无效的方法接收者）。

每种类型都有它的全局唯一的类型描述信息，称为类型元数据。
每个类型元数据都记录的信息（也即header）放在`runtime._type`结构体中，如类型名称、类型大小、对齐边界、是否为自定义类型等。
每个类型除了一个`_type`实例外，还可存储类型的额外描述信息（如果需要）。如`slice`的元数据`_type`后定义了`elem *_type`，表示其存储的元素的类型元数据。
如果是自定义类型，则额外描述信息后还有`uncommontype`结构体，保存了：该类型所在的包路径`pkgpath`、该类型关联的方法数目`mcount`、该类型的方法数组地址相对该结构体的偏移量`moff`等。
再后面就是方法元数据数组。

如：`type myslice []string`定义的`myslice`，其类型元数据为：`_type`类型的`slicetype`和`uncommontype`。`uncommontype`结构体的地址加上`moff`，即为`myslice`的方法元数据数组。

```go
type _type struct {
    size uintptr
    hash uint32 // 快速比较类型是否相同
    align uint8
    fieldalign uint8
    kind uint8
    ...
}
type uncommontype {
    pkgpath nameOff
    mcount uint16 // 方法数
    moff uint32 // 方法元数据数组的偏移量（相对uncommontype）
    ...
}
// 例：slice 的元信息
type slicetype struct {
    typ _type
    elem *_type
}
```

`type MyType1 = int32`：给类型取别名，两种类型会关联到同一种类型元数据，为同一种类型。如`rune`与`int32`。
`type MyType2 int32`：基于已有类型创建新类型。新类型会有自己的类型元数据。

**接口**

> https://www.bilibili.com/video/BV1hv411x7we?p=13
>
> 接口有一个别名是`any`，即`any`与`interface{}`可以互换。
> 注意，接口会隐藏类型信息，会使代码不直观，不容易判断变量的作用；还会影响 Go 作为静态类型语言（变量的类型在编译时就确定）的优势。
> 所以除非确实是任意类型，最好不要用 any 偷懒。

接口包含了一个类似C中`void*`的数据指针，所以保存的是地址而不是数据。
因此，空接口类型的参数只能接收一个地址（否则获取不到原数据的地址），如果要把a作为空接口类型的参数，则需使用`&a`，但一般参数要求值拷贝，即无论怎样修改参数，都不能对a进行修改，所以也不应使用`&a`。
实际上，在编译阶段，会创建一个临时变量作为a的拷贝a'，使用`&a'`做参数。
不过这些都是编译器做的，一般只需要写`a`就可以了，如`fmt.Println(a)`。

所有参数为空接口的情况，都需传递拷贝变量的地址。
但如果要修改参数，则需显示传入`&a`，不使用拷贝。否则函数需要修改参数、将参数逃逸到堆时，也是修改的拷贝变量，不会作用到原变量。（见反射，可能需要`v := reflect.ValueOf(&a)`）

空接口可接收任意类型数据。
空接口赋值前`_type data`均为nil，赋值后指向相应的元数据与数据。
```
type eface struct { // 空接口 runtime.eface
    _type   *_type // 指向接收的动态类型元数据
    data    unsafe.Pointer // 指向该接口的动态值
}
```

非空接口为有方法列表的接口类。赋值给该接口的变量，必须要实现该接口定义的所有方法。
同样，赋值前`tab data`均为nil，赋值后`data`指向数据，`tab`指向一个`itab`。

```
type iface struct { // 非空接口 runtime.iface
    tab *itab
    data unsafe.Pointer // 指向接口的动态值
}
```
接口的方法列表和动态类型信息存储在itab：
```
type itab struct {
    inter   *interfacetype // 非空接口自己的类型元数据
    _type   *_type // 接口类型的动态类型元数据
    hash    uint32 // 动态类型元数据中的hash值，用来快速比较类型是否相等
    _       [4]byte
    fun     [1]uintptr // 当前类型实现的 接口要求的方法数组地址（会被调用）
}
type interfacetype struct { // 非空接口的类型元数据
    typ     _type
    pkgpath name
    mhdr    []imethod // 接口要求的方法数组（不会被调用）
}
```
`itab`的`inter`为接口的类型元数据。
`_type`为动态的数据类型。
`fun`会从指向类型的方法列表中，拷贝接口类型要求的那些方法的地址，避免再次到类型元数据中读取。

因为一旦接口类型`inter`和动态类型`_type`都确定，则`itab`确定。所以`itab`结构体是可复用的。
go会将`itab`缓存，以接口类型`inter`和动态类型`_type`的两个类型哈希值异或作为key，以`*itab`作为value，构造哈希表。
不能成功实现接口的类型在类型断言时也会被缓存，`itab`中的`fun`会被设为0，即`fun[0]=0`。见下类型断言。

**类型断言**
空接口、非空接口被称为抽象类型，其它类型称为具体类型。
类型断言：`res, ok := a.(b)`，判断接口类型数据a的动态类型是否为具体类型b或实现了非空接口b的方法。
若判断成功，ok为true，res.data为a指向的动态值（若b为非空接口，则res也为非空接口，tab指向的itab与b相同）；否则ok为false，res为b类型的零值。
类型断言作用在抽象类型（空接口、非空接口）`a`上，断言的目标类型`b`是具体类型或非空接口类型。

**空接口.(具体类型)** 判断空接口的动态类型是否为某具体类型。
判断空接口的`_type`是否指向具体类型元数据即可。每种类型的类型元数据都是全局唯一的。

**非空接口.(具体类型)** 判断非空接口的动态类型是否为某具体类型。
检查接口的`tab`是否指向 以`<接口类型, 具体类型>`作为key的itab。（如果用这个类型定义了非空接口，则itab肯定在缓存里）

**空接口.(非空接口)** 判断空接口的动态类型是否可作为（实现了）某非空接口。
先去itab缓存中检查 是否有`<非空接口, 空接口的动态类型>`作为key的itab。
若没有，检查 空接口的动态类型 的方法列表，看是否有非空接口要求的所有方法，然后将结果添加到itab缓存中（若有，则itab的fun为方法地址列表，若没有，则itab的fun设为`fun[0]=0`）
若有，检查itab的`fun[0]`是否为`0`，不是则成功，否则失败。

**非空接口.(非空接口)** 判断非空接口的动态类型是否可作为（实现了）某非空接口。
同上，先去itab缓存中检查 是否有`<非空接口, 非空接口的动态类型>`作为key的itab。后续步骤也相同。

类型断言也有 switch 格式，通过`x.(type)`使用：

```go
func checkType(args ...interface{}) {  
    for _, arg := range args {  
        switch arg.(type) {  
            case int:  
                fmt.Println(arg, "is an int value.")  
            case string:  
                fmt.Println(arg, "is a string value.")  
            case int64:  
                fmt.Println(arg, "is an int64 value.")  
            default:  
                fmt.Println(arg, "is an unknown type.")  
        }  
    }  
}
```

**make 和 new 的区别**

new(T) 分配空间，并用T类型的零值填充，返回其起始地址，即一个\*T类型的值。
make 只能创建 slice、map 和 channel，并且返回一个有初始值(非零)的T类型，而不是\*T。本质来讲，导致这三个类型有所不同的原因是，指向数据结构的引用在使用前必须被初始化。make初始化了内部的数据结构，填充适当的值，初始化后的（非零）值。
如对于切片来说，`var p *[]int = new(int)`，`p`为一个指向切片`ptr=nil, len=0, cap=0`起始地址的指针；`var v []int = make([]int, 0)`，`p`为一个切片`ptr!=nil, len=0, cap=0`。

概括：**new 返回指针，分配空间但只是用零值填充；make 返回数据，分配空间并初始化，只用于 slice、map、channel**，因为它们只是一个指针，直接声明的话并不会初始化底层的结构。
map, chan 不初始化时不能使用，但 slice 可以，因为 append 时会自动分配（但也不能做任何引用，相当于容量为0）。

> Go 保证分配的内存是用零值初始化的（与C不同，不是随机值）。
> 堆内存是由`runtime.mallocgc()`分配的，这个函数有一个`needzero`参数，当用户使用时该参数为 true，因此会额外进行初始化。

**Go 的 nil**

nil 是一个 Type 类型的变量（`var nil Type`），但编译器会对其进行特殊处理。Type 类型就是 int（`type int Type`）。
nil 适用于 指针、函数、interface、map、slice、channel 这 6 种类型。不能将 nil 与这 6 种类型外的类型比较或赋值，否则在编译时就出错。
nil 的比较与赋值与普通变量不同，应该是编译器会对 nil 做特殊的处理。

- slice：当与 nil 比较时，只比较 slice 的指针是否为 nil，不管 cap 和 len。赋值为 nil 时，将整个结构（指针 data, cap, len）清0。
- map/chan：只有一个指向 imap/hchan 的指针，所以与 nil 比较和赋值都与指针一样。赋为 nil 后，原 map/chan 可以被 GC 回收。
- 函数：本身也是一个 8B 的指针，同上。
- 接口：分为 eface 和 iface，都是分别有两个指针 tab/_type 和 data。与 nil 比较时用第一个指针，赋值时整个结构清0。

总结：**对于这几类结构，与 nil 比较时 都是用第一个字段的指针比较；赋值为 nil 时，将整个结构清空。**

**接口 与 nil 比较**

注意 接口与 nil 比较时看的是第一个字段，也就是类型元数据，**只要这个接口有具体类型，即使这个类型的值是 nil，接口也会被判为非 nil**。
例：定义函数`func f() A { return nil }`，返回具体类型`A`，但值是 nil。
定义`var v interface{}`，`v = f()`，`v == nil`的判断将失败，因为接口 v 有具体类型。
所以，不要写`接口 = 具体类型(nil)`逻辑的代码。如果是 nil 就直接赋给接口，不要经过具体类型的转换。对于上面的函数，不如直接返回接口。

**反射**

> https://www.bilibili.com/video/BV1hv411x7we?p=15

在Go中，如果想在一个包里引用另外一个包里的标识符（类型、变量、常量等）时，必须先将被引用的标识符导出，即将要导出的标识符的首字母大写，引用者就可以访问这些标识符了。

`runtime`包中定义了各种类型的元数据类型（`_type, uncommontype, interfacetype, eface, iface, slicetype`等），但这些类型都是未导出的，所以`reflect`包中定义了相同的一套类型方便使用（可能名称不同，如`rtype`表示`_type`）。
所以**反射就是把类型元数据暴露给用户使用**。

**reflect.Type**
是一个非空接口，实现了获取该类型的常用信息的方法：对齐边界Align、获取第i个方法Method(int)、类型名称Name、包路径PkgPath、判断是否实现某接口、是否可和某类型比较、是否可转换为某类型等。
这个就是反射类型对象。

**reflect.Kind**
Kind 是在`src/reflect/type.go`中定义的若干基础类型，包括各种基本类型（`Int, Int8...`）、数组`Array`、接口`Iterface`、映射`Map`、指针`Ptr`、字符串`String`、结构体`Struct`。
即 Kind 把各种类型进行了更高层次的划分。
对于`type A sturct {}; var a A`，a 的类型是 A，但 a 的 Kind 就是`Struct`。

通过`Type.Kind()`获取一个类型的基础类型。

**func reflect.TypeOf(i interfrace{}) reflect.Type**
获取`reflect.Type`：将接口 i 的动态类型转为反射类型 Type。
编译阶段，会拷贝参数，使用副本的地址作为参数，避免修改原数据（同时满足空接口需传递地址的要求）。

函数`runtime.eface`类型的`i`（通过`unsafe.Pointer`）转为`*reflect.emptyInterface`类型，然后取值赋给变量`eface`，然后返回`toType(eface.typ)`。
```
type emptyInterface struct {
    typ     *rtype
    word    unsafe.Pointer
}
func TypeOf(i interface{}) Type {
	eface := *(*emptyInterface)(unsafe.Pointer(&i))
	return toType(eface.typ)
}
```
`toType`将`*rtype`类型的`eface.typ`包装为`reflect.Type`（一个非空接口）：
`tab *itab`指向的itab为：非空接口类型元数据为`reflect.Type`，动态类型元数据为`eface.typ`的类型即`*rtype`，方法列表就是`*rtype`实现的`Type`方法（`*rtype`实现了`Type`接口）。
`data unsafe.Pointer`就指向`eface.typ`（该非空接口指向的是一个`*rtype`）。

所以`TypeOf(x)`返回的就是上述的`Type`非空接口：data为x的类型元数据(`eface.typ`，`*rtype`类型，等同于`_type`)，itab为`Type`接口和`*rtype`类型的信息。

**func reflect.ValueOf(i interfrace{}) reflect.Value**
获取`reflect.Value`：将接口 i 的动态类型转为反射类型 Value。

```go
type Value struct {
    typ *rtype  // 反射变量的类型元数据指针，为i的类型元数据
    ptr unsafe.Pointer  // 数据指针，指向i
    flag        // 反射值的描述信息（用位图表示），如是否为指针、是否为方法、是否只读
}
func ValueOf(i interface{}) Value {
    if i == nil {
        return Value{}
    }
    escapes(i)
    return unpackEface(i)
}
// 直接将 x 赋给一个全局变量，来让它逃逸？
func escapes(x interface{}) {
	if dummy.b {
		dummy.x = x
	}
}
```

`ValueOf`会显式地将参数`i`逃逸到堆上（`escapes(i)`）。
如果想使用`Value`修改原数据，必须使用原数据的地址作为`ValueOf`参数，而不是副本的地址（同时满足空接口需传递地址的要求），否则会panic（更改的只是一个不可寻址的副本）。所以我们反射的应该是 a 的指针，而不是 a。
此时反射的是a的指针，其`Value.typ`是`&(*_type)`。要修改原数据a，需使用`Value.Elem().SetString()`（对字符串）：`Value.Elem()`将`Value.ptr`指向的变量a包装成`Value`返回，此时`Value.typ`是`&(_type)`，即将a的指针转为a。

**反射的应用**

反射可以将 接口类型 转为 反射类型；可以将 反射类型 转为 接口类型。
再通过类型断言，可以将 接口类型 转为合适的类型。

Go 的反射效率较低，涉及到内存分配以及后续的GC，实现中有很多 for 枚举。

**uintptr**
https://blog.csdn.net/hello_ufo/article/details/86713947
https://blog.csdn.net/cbmljs/article/details/82983639

**unsafe.Pointer**
https://www.jianshu.com/p/7c8e395b2981
https://zhuanlan.zhihu.com/p/137060307
TODO

可以简单地将两个内存结构一致的类型的实例，进行类型转换。需要保证转换后的类型大小不大于转换前的类型（不会访问非法位置），且具有相同的内存布局。

为了安全，Go 限制指针不能像 C 一样执行各种运算，指针的类型也不能直接转换。
但有时候有这种需求，就可以用 unsafe.Pointer 实现：

- 任意类型的指针和 unsafe.Pointer 可以互相转换。

- unsafe.Pointer 与 uintptr 可以相互转换。

- uintptr 可以进行加减操作，从而实现指针的运算。

**堆与栈**
栈内存从上往下增长，分配空间有限，是连续的，分配效率高，会自动回收。
堆内存从下往上增长，分配空间大（取决于虚拟内存空间），不连续，有碎片，分配效率低，需要注意回收（或进行gc）。

**堆内存管理**

> https://www.bilibili.com/video/BV1hv411x7we?p=30

BiBOP(Big Bag of Pages)，即pintos中的实现，包含三个层次：arena、span、page。
内存划分为多个相同大小的arena，arena被划分为不同规格的span，每个span按照规格大小划分为若干等大的内存块，放入该span的空闲链表中。
内存块的大小是规定好的若干种，包含一组连续的page。每次使用找到大小最合适的块。
这样可以减少内存碎片，便于分配和管理。

Go 中 arena 的大小为64MB，包含8192页，每个页8KB。规定了67种块大小，最小的块为8B，最大的块为32KB。>32KB的另外定义。

具体的堆内存管理结构：`mheap`管理整个堆内存，`heapArena`对应一个arena，`mspan`对应一个span。
`mheap`中包含一个全局的`mspan`管理中心`mheap.central`，包含136个`mcentral`，便于分配各种规格的span。
每个`mcentral`管理一种规格的`mspan`：规定的67种大小和大块共68种，再根据是否需要GC (scannable, noscan) 分成136种。

为了减少冲突，每个 P 都有一个本地缓存`p.mcache`，从这里取可以不加锁。
`mcache`的`alloc`数组有136个`*mspan`，用于 P 在本地获取堆内存块。如果`mcache`中没有或者用完了，就去`mcentral`中获取一个放到这里，把用过的放回去。
还有专门用于分配小于16B、noscan类型的`tiny`数组。

**栈内存管理**

> https://www.bilibili.com/video/BV1hv411x7we?p=32

因为 goroutine 的存在，Go 自己实现了内存管理，会为每个 goroutine 分配栈空间，这个栈空间也是在程序的堆空间申请的（程序最初创建的 g0 例外，是在 os 提供的栈空间中）。
Go 会预估函数所需的栈空间，进行预分配，而不是在函数使用时逐步扩张。当要使用的空间超过预分配的时，会将当前整个函数栈迁移到新的更大的栈空间位置，避免与其它goroutine的栈空间冲突。

Go 将堆内存划分为若干 arena，每个 arena 划分为不同规格的 span，每个 span 按照规格大小划分为等大的内存块。
span 不仅用做堆内存，还用做栈内存。堆的 span 是`mSpanInUse`状态，栈的 span 是`mSpanManual`状态。

为了提高栈分配的效率，Go 有全局栈缓存，包括两个用于栈分配的全局对象。
stackpool 用于分配小于 32KB 的栈，包含几种规格的 mspan 链表。比如在 Linux 下，stackpool 中有 2K, 4K, 8K, 16K 四种规格的 mspan 链表。
stackLarge 用于分配大于等于 32KB 的栈，它是一个数组，第 n 个元素指向大小为 2^n 个页面，也就是 8*2^nKB 的 mspan 链表。所以它前4个元素指向的是大小为 8K, 16K, 32K, 64K 的 mspan 链表，不过前面两个小的 mspan 链表实际总是空的。

类似堆内存，每个 P 也有本地栈缓存`stackcache [n]stackfreelist`。在 Linux 下，也是有 2K, 4K, 8K, 16K 四种规格的空闲 mspan 链表。
分配栈内存时，对于小于 32KB 的栈空间，先从本地缓存中取，如果没有，就去全局的栈缓存 stackpool 的对应链表中取出一部分(16KB) 放到本地缓存中，继续从本地分配。
如果 stackpool 的对应链表也为空，就从堆内存中分配一个 span (32KB) 划分为对应大小，放到 stackpool 中。
但有时不能使用本地缓存（比如：关闭 stackcache 时，当前 M 没有绑定的 P，GC 过程中），就直接从 stackpool 分配。

对于大于等于 32KB 的栈空间，计算它需要的页数n，以$\log_2n$为下标去 stackLarge 的对应链表找。如果没有，就直接从堆内存中获取一个拥有这些页的 span。

**Go 协程栈的扩缩容**

编译器会在函数的头部插入检测代码，检查当前的栈空间是否够用，如果不够，就先进行`morestack`分配，再执行函数。

栈增长过程：将协程状态设为`_Gcopystack`，调用`copystack()`，分配当前栈大小两倍的栈空间，拷贝过来数据，释放旧栈空间，将协程恢复为`_Grunning`。

空间过大的栈也会收缩：GC 在`scanstack`中，如果发现可以安全的收缩栈，就进行栈收缩；否则设置栈收缩标识`g.preemptShrink = true`，在协程检测到抢占标识`stackPreempt`时（见下 *G 的让出*），会在主动让出 CPU 前，检查栈收缩标识，如果为 true 则进行收缩。
栈收缩可以减少协程对栈空间的浪费。栈最少只会收缩到 2KB。

释放的栈空间 可能回到 P 的本地栈缓存，可能回到全局栈缓存，也可能还给堆内存。
小于32KB 的栈空间，先放到本地栈缓存中；如果本地缓存不可用，或者该队列总大小超过了32KB，就把一部分放回到全局缓存 stackpool 中，只保留16KB；返回到 stackpool 后，如果它所属的 mspan 的所有内存块都被释放了，就把这个 mspan 归还给堆内存。
大于等于32KB 的栈空间，如果当前处于 GC 清理阶段（`gcphase == _GCoff`），就直接释放到堆内存，否则放到 stackLarge。

> 栈增长代码有三种：
>
> 1. 栈帧大小 小于等于 _StackSmall 时，若栈指针 SP 超过（小于等于）栈边界 stackguard0 就扩容。
> 2. 栈帧大小 大于 _StackSmall 但小于等于 _StackBig 时，若`SP - stackguard0 <= framesize - _StackSmall`（距离栈边界有足够小距离），就扩容。
> 3. 栈帧大小 大于 _StackBig 时，与情况 2 基本相同，只是多判断了 如果`stackguard0 == stackPreempt`则也扩容。
>
> stackPreempt 与协程调度有关，见下 *G 的调度*。

**协程的回收**

常规协程在运行结束后，会被放到调度器的空闲 G 队列`sched.gFree`中。
空闲队列中的协程有两种：一种有协程栈（sched.gFree.stack），一种没有协程栈（sched.gFree.noStack）。
创建协程时，会先检查空闲队列有没有协程，且优先使用有栈的协程。

协程结束时都是有栈的，如果它的栈没有增长过（还是2KB），就把它放到有协程栈的空闲队列里；如果栈增长过，就把它的栈释放，放到没有栈的空闲队列里。
有栈的空闲协程的栈，也会在 GC 时被释放掉，然后进入没有栈的等待队列（减少内存占用）。

**程序的启动过程**

> https://cloud.tencent.com/developer/article/1917068

可执行文件被加载到内存后，会创建主线程 m0 和第一个协程 g0，然后进行一系列检查和初始化（这是最早的程序入口，跟机器平台有关，如win的是`src/runtime/rt0_windows_amd64.s`），然后创建 main goroutine 执行`runtime.main`，再进行一部分初始化后才会调用我们定义的`main.main`。

实际的程序入口`rt0_平台_指令集.s`都会调用`rt0_go`，包含各种初始化：如`runtime.check`进行类型检查，`runtime.args`将os传递的 argc, argv 赋值给进程的全局变量，`runtime.osinit`获取 CPU 核数和系统的页大小，`runtime.schedinit`初始化内存分配器、调度器、GC 等组件。
然后调用`runtime.newproc`创建主协程，将其放到 P 的本地队列（当前执行的是 g0），作为 m0 下一个执行的 G。
然后调用`runtime.mstart`，这是每个 M 的入口函数，会初始化 m0 并执行`schedule()`（寻找调度 G，执行 G，再寻找 G...）。

> `runtime.check`在`runtime1.go`中，再次检查了各个基本类型的大小和操作（如CAS, atomic）是否符合预期。
> `runtime.mstart`在`proc.go #1328`，是每个 M 的入口点，进行线程初始化，最后调用`schedule()`进入调度循环。
> `runtime.schedule`在`proc.go #3291`，寻找一个待执行的 G，然后调用`execute`执行。
> `runtime.execute(gp *g, inheritTime bool)`在`proc.go #2670`，将 gp 调度到当前 M 上执行。
> 这些函数都是永不返回`never return`的。M 在执行完一个 G 后应该会重复调用`schedule`，但不会返回来，直到程序结束直接退出。

`runtime.main`也即 main goroutine 会先进行一部分初始化（如创建监控线程 sysmon，初始化包），然后才调用 `main.main`。
在`main.main`返回时，会调用`exit()`结束进程。

> GMP 模型中有一个全局变量 g0，就是主协程对应的`runtime.g`结构。与其它协程不同，它的协程栈就是在主线程栈上分配的（所以栈空间非常大，不需要扩容），而其它的是在os提供的堆上分配的。（注意这个主协程是程序最初就创建的，不是之后创建的 main goroutine。正是它创建了后者）
> 全局变量 m0 是主线程对应的`runtime.m`。
> m0 和 g0 是互相关联的。最初在 m0 上执行的协程就是 g0，然后 g0 会创建 main goroutine。
> 在初始化时，会进行调度器初始化`schedinit`，会按照`GOMAXPROCS`创建一定数量的 P，保存在`allp`中，并将第一个 P `allp[0]`与 m0 关联。
>
> m0 是第一个线程，在程序初始化后就与其它线程一样了。
> 每个线程都有自己的栈，所以都有自己的类似 g0 的协程（使用线程栈，处理系统调用和调度）。

协程是通过`newproc`函数创建的。执行`go func()`会被转为`newproc`。
`newproc`会给协程构造一个栈帧，并使协程结束时调用`goexit()`，进行资源回收（可能放回空闲 G 队列，可能释放）。

**GMP模型**

> 对于原生支持协程的语言，系统调用都是被编译器包装过的，调用 read 等系统调用会先走到这个语言提前写好的汇编里，而不是直接发起系统调用。因此语言本身的 runtime 能感知到是否会发生阻塞，从而可在陷入阻塞时让 CPU 回到调度器、调度下一个协程。
>
> 非原生支持协程的语言，需要提前调用一个 patch 函数来自动包装所有系统调用。

GMP 是 Go 协程调度器的调度模型（协程是比线程更小的单位）。
协程 G 携带任务；P 分配、调度 G；线程 M 不是在执行 G，就是在寻找可执行的 G（如果活跃）。
定义协程的结构是`runtime.g`，工作线程的结构是`runtime.m`，本地的协程调度器的结构是`runtime.p`，全局调度器`sched`的结构是`runtime.schedt`。
M 不完全是线程，只有工作、没阻塞的线程会绑定到线程。
（P 代表 Processer 调度器，M 代表 Machine）

GMP 的全局变量除了上述的 g0, m0 外，还有：`allgs`记录所有的 G；`allm`记录所有的 M；`allp`记录所有的 P。

最初 Go 的调度模型中只有 G 和 M。所有 G 位于一个全局队列中，M 每次从全局队列中取出一个待执行的 G 执行。
但该过程需要加锁解锁，多个 M 获取 G 会导致频繁加锁和等待，影响并发性能。
为此 Go 定义了 P。P 包含一个本地的 G 数组`runq [256]guintptr`。只要把 M 关联到一个 P，M 就可以去 P 的本地队列直接取出 G，不用每次都加锁去全局队列取。

除了各个 P 的本地队列，调度器还有一个全局的 G 队列，保存在`sched`的`runq`中（`sched`还记录了各个空闲M和P的信息）。
如果 P 的本地队列已满，新的待执行的 G 就会进入全局队列。
M 会先从关联的 P 的本地队列中取 G；如果没有，就去全局队列中取出一些 G；如果全局队列也没有，则去其它 M 的 P 上取出一些 G。

P, G 的状态机[见这里](https://juejin.cn/post/7135085217760411661)。

> P 什么时候会创建？
> （见*程序的启动过程*）在程序启动时，有一部分初始化，里面的`schedinit()`会根据`GOMAXPROCS`创建指定数量的 P，保存在`allp`中，并将第一个 P 与 m0 关联。
>
> M 什么时候会创建？
> 当一个新的 G 被创建时（`newproc()`），会检查是否有未关联的 P。如果有，但没有处于自旋状态的 M，就创建或唤醒一个 M。
>
> G 的状态：
> \_Gidle：刚被创建，还未初始化、不可执行。\_Grunnable：待执行。\_Grunning：正在执行。
> \_Gsyscall：正在执行系统调用，会和当前 M 绑定。\_Gwaiting：被阻塞。\_Gdead：空闲状态，没有要执行的代码，可能是刚初始化，也可能是回收后。
> \_Gcopystack：栈正在被拷贝，没有执行代码。\_Gscan：GC 正在扫描栈空间，没有执行代码，可以与其他状态同时存在。
>
> P 的状态：略。
>
> 自旋线程：处于运行状态但没有可执行的 G 的线程，会不断尝试获取 G。数量最多为 GOMAXPROC。如果数量大于 GOMAXPROC 就会进入休眠（因为不需要这么多 M）。
>
> G 的调度策略是什么？
> 创建好的待运行的 G，会被放入当前 P 的就绪队列中，如果满了就放到全局队列（同时取出一半一起放）。
> M 每次取出队首的 G 执行。
> 当一个 G 阻塞后，进入等待队列，恢复后再放入就绪队列。
> 总体类似时间片调度，就是：阻塞、等待时，主动放弃执行；执行太久时，放弃执行。

**G 的创建 / newproc 的过程**

> https://www.bilibili.com/video/BV1hv411x7we/?p=17
> https://juejin.cn/post/7038174578715131912

`newproc(siz int32, fn *funcval)`有两个参数：传递给协程入口函数的参数有多少字节；协程入口函数的指针。
在调用时，传给`fn`的参数也会被放到这些参数后面。

> 栈是从高地址向低地址增长的。一个函数栈依次包括：返回地址，调用者栈基址BP，局部变量，调用函数时的参数。函数参数是从右到左依次放入的，所以第一个参数会在栈顶（最下面）。
> 所以`newproc`中传给`fn`的参数，就是在`siz`上面的`siz`个字节中。

`newproc`会切换到 g0 协程执行`newproc1(fn, argp, siz, gp, pc)`。

> `fn, siz`就是入口函数指针、参数大小。`argp`是`fn`的地址+一个指针的大小，所以就是第一个参数的位置（参数地址）。`gp`是调用`newproc`的协程的指针，即父协程是谁。`pc:=getcallerpc()`是返回地址。
>
> 因为`newproc1`函数被标记为`no-split`，在运行时不会进行栈空间的检查，自然也不会进行扩容。为保证不发生栈溢出，就在 g0 的栈上执行。
> 在简单、不需要什么栈空间的函数中标记`no-split`，可减少检查开销？

`newproc1`的过程：

1. 首先调用`acquirem()`禁止当前 M 被抢占。因为后续会使用当前 P，如果 M 被抢占会导致 P 被关联到其它 M（disable preemption because it can be holding p in a local var）。
2. 获取一个空闲的 G。如果没有就创建，并添加到全局`allgs`中。
   新的 G 的状态为 _Gdead，且已经分配协程栈。
3. 将参数（如果有）拷贝到 G 的协程栈上。
4. 将`goexit()`函数的地址+1 压入协程栈。
5. 将 G 的`g.sched.sp`设为协程栈指针，将`g.sched.pc`设为入口函数地址。
6. 将 G 的状态设为 _Grunnable，表示它可被放入`runq`。
   所以会调用`runqput()`，将 G 放入当前 P 的本地队列 local run queue 中；如果本地队列满了，放到全局队列 global run queue 中（同时也将本地队列中的一半 打乱顺序后 放到全局队列）。
7. 会判断 如果当前有空闲的 P，且没有处于自旋状态的 M（且主协程已经开始执行），即所有线程都在工作（都有 G），就启动或创建一个 M 并将其设为 spinning 状态（它会开始寻找可执行的 G）。
8. 调用`releasem()`允许当前 M 被抢占。

> 函数栈的结构是：(调用者的其它信息...)，调用者传给函数的参数；返回地址，(被调用者的其它信息...)。
> 这正对应于过程的 3 和 4，可看做前半部分是`goexit()`的栈帧，后半部分是`fn()`的栈帧。
> 所以这相当于`goexit()`调用了入口函数，并向它传递了参数。**返回时，自然也是返回到`goexit()`，直接执行协程的回收。**
>
> G 中的`g.sched`用于保存和恢复上下文，其中包括：协程栈指针`sp`，协程当前的PC`pc`。
> **当 G 开始调度执行时，通过`g.sched`恢复现场，就会执行入口函数`fn()`。**
> 所以过程 3,4,5 是为协程伪造了一个调用现场。
>
> 过程 7 为，在一个协程创建后，检查是否有空闲的 P，是否需要新建一个 M。因为只有 G 的创建才会导致需要创建新的 M。

**schedule() 的过程 / G 的调度策略**

> https://www.bilibili.com/video/BV1hv411x7we/?p=18

某个 G 让出 CPU 后，M 要通过 schedule() 决定下个要执行的 G。

1. 检查 M 是否和当前 G 绑定，如果是，阻塞 M，直到这个 G 再次被调度再唤醒 M。
2. 如果没有绑定，如果 GC 在等待执行，就执行 GC。
3. 检查有没有`timer`要执行（检查在 P 上的因`time.Sleep()`阻塞的 G 是否到时）
4. 每进行 61 次调度（`p.schedtick%61 == 0`），就去全局队列中拿出一些 G 放到本地。
   这保证了全局队列中的 G 总会有调度机会，不会饿死。
5. 重复调用`findrunnable()`，直到找到一个 G（这之前会先在本地找，但逻辑类似略过）：
   首先检查是否需要执行 GC；然后在 P 的本地队列中获取。如果没有，就从全局队列中获取一部分；如果还没有，执行`netpoll()`（一个轮询）看看有没有 IO 事件结束、可恢复执行的 G；如果也没有，尝试从其它 P 中获取一些 G (steal)。
6. 判断找到的 G 是否和其它 M 绑定，如果是，还要还回去，重新执行`schedule()`。
7. 否则，执行`execute()`，将 M 和 G 关联，将 G 的状态从 _Grunnable 设为 _Grunning。如果不继承上个协程的时间片，就自增`p.schedtick`（用于判断协程执行时间并切换协程）。
   最后调用`gogo(g.sched)`，从`g.sched`中恢复 G 的上下文。

> 从其它 P 获取 G，减少了 M 的创建和销毁次数。
>
> M 从全局队列获取 G 时，会取$\min\{len(GQ)/GOMAXPROCS + 1, len(GQ/2)\}$个（len(GQ) 为当前全局队列中元素数）。
>
> 处于运行状态但没有可执行的 G 的线程为自旋线程，会去其它线程的本地队列中获取 G。
> 在`schedul()`中，如果当前 M 要去其它 P 的队列获取 G，就把 spinning 标志设置为 true，同时增加处于自旋状态的 M 的数量。获取之后将 spinning 标志改为 false，减少处于自旋状态的 M 的数量。
> 当创建/启动 G 时，如果有空闲 P，且自旋状态的 M 的数量不为0，就不需要创建新的 M。
>
> 从其它 P 获取 G 时，会遍历 allp 中的所有 P，看它是否有 G。如果有，取尾部的一半到当前 P 上，返回。
> 为了保证公平性，遍历 allp 时是用一个随机序列随机访问每个 P，并不是固定的从 allp[0] 开始、每次遍历 i+1。每次遍历时都会用不同的顺序访问 allp。

**go func{}() 后会发生什么**

1. `go func(){}`通过调用`newproc()`创建一个新的 goroutine。
   会将入口函数需要的参数、`newproc()`的参数（入口点、参数大小）依次入栈。
2. `newproc()`调用`newproc1()`。见上*`newproc()`的过程*。
3. 进入 P 或全局队列后，G 等待被 M 调度执行。

**G 执行 time.Sleep 后会发生什么**

协程执行`time.Sleep()`后，状态从 _Grunning 变为 _Gwaiting，进入到对应`timer`结构体中等待。
`timer`中有一个回调函数`f`，会在指定时间后调用该回调函数，将协程状态恢复为 _Grunnable，放回到 runq 中。
每个 P 都有个`timer`堆`p.timers`，堆顶为唤醒时间最早的`timer`。每次 M 执行调度`schedule()`时，都会调用`checkTimers()`检查并执行已经到时间的`timer`。
但这需要有 M 空闲并及时触发调度。为保证所有`timer`按时执行，监控线程 sysmon 也会检查`timer`，在没有 M 空闲时创建新的 M。

监控线程 sysmon 与其它工作线程不同，它不依赖 P，也不由 GMP 模型调度。它会重复执行某些任务，并视情况进行休眠：最初每次休眠 20us，在 50 次即 1ms 后每次执行休眠时间翻倍，最大到 10ms，减少消耗。这个值为 sysmon tick。
在发生抢占后，重置 sysmon tick 为 20us。

因为 IO 等待阻塞的协程，需要进行轮询，由`netpoll()`进行。为减少延迟，监控线程会定期执行`netpoll()`检查是否有恢复的协程：检查 epoll 中已经准备就绪的文件描述符。

> 监控线程 sysmon 的主要工作：
> netpoll：轮询检查是否有从 网络请求 阻塞中恢复的协程。
> forcegc：如果长期没有进行 GC（2min），强制进行 GC。
> retake：抢占长时间执行的 G，解除长期处在系统调用的 M 的 P。
> scavenge heap：释放长时间闲置的内存。

**G 的让出**

协程在执行`time.Sleep()`、等待chan、等待 IO 事件时，会主动让出，进入 _Gwaiting。
**除了因等待让出外，监控线程会通知运行时间过长（超过 10ms）的 G 让出**（这是协程正常运行的情况。对于在进行系统调用的 G，如果超过了一个 sysmon tick 就抢占。sysmon tick 最少为 20us，但每次抢占都会重置，所以应该就是 20us）。

> P 中有一个`schedtick`字段，每当调度新的 G （且没有继承上个 G 的时间片）时，就会自增1。监控线程中也记录了一个`schedtick`，如果这个值与 P 的不相等，说明 P 进行了一次调度，同步更新，并记录`schedwhen`为当前时间；否则说明自`schedwhen`时间起，P 没有发生过调度（或沿用了上个 G 的时间片），根据当前时间和这个时间的差值可判断当前 P 上的 G 是否超时。

怎么通知 G 让出？与栈增长有关。
除了不需要协程栈的函数，Go 会在函数头部插入栈空间检测的代码（见上*协程栈的扩缩容*），其中包含了`stackPreempt`的检查。
当调度器让某个协程让出时，就将其`stackguard0`设为`stackPreempt`，这是一个非常大的值（特殊标识），所以无论什么时候，栈增长判断都会成功，进而在函数执行前跳转到`morestack`。
`morestack`会执行`runtime.newstack()`，会首先检查`stackguard0`是否等于`stackPreempt`，如果是就不增长，而是执行协程调度、让出 CPU。
所以，**设置`stackPreempt`可让协程在下一次进入函数时，主动让出 CPU**。

但这必须涉及栈增长，可能导致一个 G 无限执行。
**Go 1.14 实现了异步抢占**。实现方式与平台有关（也要涉及内核？）。
Unix 中，会向协程的 M 发送 sigPreempt 信号，然后 M 被信号中断，执行`runtime.sighandler`处理信号。当检测到 sigPreempt 后，会在信号处理函数返回时立刻执行一个异步抢占函数。这个函数保存协程上下文（寄存器），调用`schedule()`触发调度，使协程被动让出。

**G 进行系统调用后会发生什么**

G 进行系统调用时，需要切换到 g0 栈（栈空间足够大，也不需要分配栈空间），所以 G 会和当前的 M 绑定，直到系统调用结束。所以 G 的阻塞会导致 M 阻塞。
而 P 是有限的，且包含等待的 G，为保证资源不浪费，长时间处在系统调用的 M 会让出 P，解除它们之间的关联，并记录`m.old = P`。所以 P 可再绑定其它空闲的 M。
当 M 结束系统调用时，会先检查之前的 P `m.old` 是否被占用，没有的话就继续使用，否则就去申请一个 P。如果申请不到，就将当前的 G 放回全局队列，自己进行休眠。

如果 M 被阻塞或执行时间过长，监控线程会解除 M 和 P 的绑定，将 P 和其它自旋或休眠 M 绑定。

**当一个 G 阻塞时，会发生什么**

对于非系统调用的阻塞（如 IO，等待 chan，同上面的`time.Sleep()`后），G 会被设为 \_Gwaiting，进入等待队列，直到事件完成被唤醒；M 寻找新的 G 执行。

**协程池**

协程的创建、销毁、调度都是有开销的（占用内存、增加调度器负担、增加 GC 开销），不能滥用。
如果需要频繁地使用、销毁协程，可以使用协程池，类似线程池，牺牲一些内存，减少创建和 GC 的开销。

实现上，可以创建 n 个协程，重复执行`select`尝试从一个 chan 中取出任务并执行。

**chan 及 chan 的工作原理**

> https://www.bilibili.com/video/BV1hv411x7we?p=29
> https://blog.csdn.net/u010853261/article/details/85231944
> https://www.jianshu.com/p/d841f251d3bc
> （可以看看）https://zhuanlan.zhihu.com/p/261007183

chan 主要有三部分：

1. 如果 chan 有缓冲区，则包含一个循环队列，用两个下标表示读写的位置。根据下标可决定缓冲区是否已满或空。
2. 一个 send 和 recv 队列。对于发送方，如果缓冲区已满且没有协程在接收数据（无缓冲区 chan），则进入发送队列阻塞；对于接收方，如果缓冲区为空且没有协程在发送数据（无缓冲区 chan），则进入接收队列阻塞。
   等待队列是一个 sudog 类型的双向链表。一个 sudog 结构记录了等待的协程、协程在等待哪个 chan，如果是发送方，还会记录要发送的数据。
3. chan 的全局锁。

一个G会保存一部分数据，当数据满时，创建sudog放到sendq中，建立新的G。若recvq不为空，则直接将数据复制到recvq的一个G的数据中。
获取数据时，取出并唤醒sendq的一个G，将其一个元素复制到chan的循环队列中。若sendq为空，将当前G放到recvq中。

通过channel传递消息就是值的拷贝，有缓冲的channel先把发送方G的值拷贝到自己维护的循环队列，再拷贝到接收G，而非缓冲型的则直接从发送栈数据拷贝到接收栈空间。

**select**

通过 select 可实现非阻塞发送或接收。如果不经过阻塞就能操作成功，则执行 case，否则执行 default（可选）。

多路 select 可操作多个 chan。
会通过数组保存所有 case 分支。还有两个同样大的数组，一个用来获取下标的随机排列，以便能用随机的顺序轮询各 case，更公平；另一个数组指定所有 chan 的加锁顺序，因为加锁解锁必须有序，否则会死锁。
多路 select 通过随机顺序轮询，检查是否有 chan 可操作。轮询前会先按特定顺序给所有 chan 加锁，轮询后按顺序释放锁。
如果所有 chan 都不可操作，则将当前协程添加到所有 chan 的等待队列中（根据操作决定是发送队列还是接收队列），然后挂起，直到被唤醒。
被唤醒后，同样先加锁，将协程从各等待队列中删除，然后释放锁。

注意，如果有某个分支的 chan 被关闭，从该 chan 中总会成功读到零值（如果有缓冲区且有数据未读，则读缓冲区数据），所以如果执行该 case 总会判断成功。
`select`不会等待被设为 nil 的 chan 分支。

**mutex 互斥锁**

> https://www.bilibili.com/video/BV1hv411x7we?p=21

```go
type Mutex struct {
    state int32 // 锁，通过原子操作实现
    sema uint32 // 信号量，用于等待队列，可唤醒协程
}
```

state 记录锁的状态，通过 atomic 的 CAS 或原子加实现加锁解锁。
第 1 位表示锁的状态（1：已加锁），第 2 位表示是否已有协程被唤醒（1：已唤醒），第 3 位表示锁的模式（0：正常模式，1：饥饿模式）。其它位表示有多少个等待者在排队（state >> 3 个）。

加锁和解锁都分为了两部分：fast path、slow path，前者只包含少量逻辑，以便进行内联优化；后者是一个函数，逻辑较复杂，见[这里](https://www.bilibili.com/video/BV1hv411x7we/?p=23)。

- 加锁：如果通过一个 CAS 可以直接获得锁，就是 fast path，不涉及太多逻辑。
  否则，进入 slow path。协程会判断是否能自旋，然后开始自旋（执行无意义的操作消磨时间）。
  如果自旋次数到达 4 次，或锁被释放，或锁进入饥饿模式，就结束自旋，尝试通过 CAS 获取锁。如果获取锁失败，重新自旋，也可能会进入等待队列。

  在以下4种情况中，不能直接获得锁的协程不会自旋，而是直接进入等待队列：

  1. 机器为单核，自旋也没意义，因为持有锁的协程没法执行，就没法释放锁。
  2. GOMAXPROCS = 1，即只有一个 P，与单核情况同理。
  3. GOMAXPROCS > 1，但只有一个 P 在运行，同上。
  4. GOMAXPROCS > 1，但当前协程所在 P 的本地队列不为空，则不会自旋浪费 CPU，直接让本地队列中的下一个协程执行。

- 解锁：令 state 减去 mutexLocked 即减去1。
  如果等待队列不为空，即 state 不为0，则进入 slow path，

**锁的两种模式**

- 正常模式：要获得锁的协程会先自旋几次，尝试通过 CAS 获得锁；如果几次自旋后仍不能获得锁，就进入等待队列。
  等待锁的协程会处于等待队列中，按先入先出的顺序获取锁。
  当锁被释放时，队首的协程被唤醒，尝试获得锁。但它不会直接获得锁，而是会和当前正在运行、且尝试获得锁的协程进行竞争。正在运行的协程更有优势，一是因为它们多，二是因为唤醒的协程不一定能立刻进入运行状态。
  所以被唤醒的队首协程，很可能拿不到锁。此时它会被放回队列头部，而不是重新放入尾部。
- 饥饿模式：当一个协程等待锁的时间超过 1ms 后，会将锁的状态切换为饥饿模式。
  饥饿模式下，如果锁被释放，等待队列队首的协程会直接获得锁；正在运行的协程不会尝试获取锁，而且直接进入等待队列。
  如果一个获得锁的协程，等待时间 <1ms，就会将锁的状态切换回正常模式。
  当等待队列为空时，锁也会变为正常模式。

正常模式下，队列中和运行的协程都会争取锁，可以减少挂起、唤醒协程的次数、减少上下文切换。性能更好，但可能导致饥饿。
饥饿模式下，只有队列中的协程能取得锁，能减少协程的最大等待时间。

**可重入锁 (reentrant lock / recursive mutex)**

可重入锁指同一个线程可以多次获取某一个锁。释放锁需要释放同样多次。
可以避免一部分死锁的发生，简化某些场景下的代码（比如：如果没有可重入锁，一个函数 f() 可能要写两份：一份假设已经获取到锁，一份假设没有获取到锁，会进行加锁）。
实现上就是加了个计数，加锁时判断已获取锁的线程 id 与当前线程 id 是否相同。

go 不支持、也不推荐使用可重入锁：
go 的开发者认为：在多线程里，只要各个线程能同时访问一个对象，就应该满足某些约束 (不变式，invariant)。比如线程共享一个链表，如果没有修改、线程能共同访问它们，就需要满足约束：对所有内部节点，`p.next.pre == p`。
一个线程对链表加锁，意味着“此时上述约束仍满足，但我现在可能会打破这个约束”（比如插入节点的中间态）。
而释放锁，意味着“对象的约束仍然满足。如果我之前打破了，那我现在已经恢复了”（其它线程可以安全访问）。
如果一个线程连续加锁两次，在两次加锁之间，线程看可能违反约束，导致第二次加锁时的语义并不正确（需要保证“此时约束仍满足”）。

见[这里](https://groups.google.com/g/golang-nuts/c/XqW1qcuZgKg/m/Ui3nQkeLV80J)和[这里](https://groups.google.com/g/golang-nuts/c/XqW1qcuZgKg/m/tYq8frpidd8J)。
不同的观点是，锁并没有严格要求这种约束语义，应该由代码逻辑决定。
但即使不用可重入锁，也不会导致逻辑很复杂，相比可重入锁可能带来的难以发现的 bug，不使用它还是值得的。

go 中重复加锁会直接死锁 (可检测的 fetal error)。
如果需要这种逻辑，可将一个函数分成 假设已加锁 f() 和 假设没有加锁 f_need_lock() 两个版本，后者会加锁然后调用 f()。

**内存逃逸**

逃逸分析：在编译期间，确定哪些变量应在栈上分配，哪些变量应逃逸到堆中。**编译器**根据代码的特征和生命周期，自动把变量分配到堆或者是栈上面（编译时就确定）。
栈空间的分配效率很高（只需要修改栈指针），且不需要 gc，空间还是连续的。所以编译器进行逃逸分析只让有需要的对象分配到堆上，以减少堆上的内存分配，提高效率。
（对于难以避免但频繁的堆内存申请，可以尝试用对象池）

在`go build`时指定`-gcflags="-m -l"`（-m：内存分析 -l：防止内联优化。可以写最多4个-m，越多代表分析信息越详细）。
常见逃逸的场景（主要有两类：无法确定生命周期或作用域；无法确定大小，或还可能会再申请内存。前者是因为栈上的对象在函数返回时就会销毁，后者是因为栈空间是比较有限的）：

1. 如果函数的局部变量的地址 被作为指针返回，或者在返回的闭包中被引用，或者被某全局变量保存时，该局部变量会放到堆上。即如果编译器不能确保 变量在函数 return 之后不再被引用，编译器就会将变量分配到堆上。
2. 放入指针类型的 channel 中的数据，无法确定什么时候被使用，所以放到堆上。
3. 在切片或map中存放指针，指针指向的元素会逃逸，即使这个切片或map本身是在栈上的。如`[]*string`。
4. 栈空间不足以存放当前对象时，会将对象分配到堆中。比如切片扩容后超出 cap，需要重新分配空间。
5. 在编译期间很难确定变量的具体类型和大小时，会产生逃逸。如无法判断切片长度。

注意，对于 1,2，都强调返回/放入的数据是指针，因为 go 都是值拷贝，不用指针返回/放入的就只是副本，与原值无关。
比如如果直接`ch <- x`， chan 中放入的其实是 x 的值拷贝，逃逸的是 x 的一个拷贝而非 x。但如果`ch <- &x`（存放指针），逃逸的就是 x。

此外，`fmt.Println/Fprintf(x)`等会导致 x 内存逃逸。这和输出的实现有关系，与 interface{} 无关。
似乎是因为 fmt 内的逃逸分析太难了，现在还是这样，见 [#19720](https://github.com/golang/go/issues/19720) 或 [#8618](https://github.com/golang/go/issues/8618)。

例：对于
```go
// escape.go
package main

import "fmt"

func intSeq() func() int {
	i := 0
	return func() int {
		i++
		return i
	}
}
func main() {
	nextInt := intSeq()
	fmt.Println(nextInt())
	fmt.Println(nextInt())
	fmt.Println(nextInt())
}
```
会输出`1 2 3`。执行`go build -gcflags="-m" escape.go`会有`./escape.go:6:2: moved to heap: i`，即编译的时候把`i`变量的内存地址放到了堆(heap)上。
因为当`./escape.go:7:9: func literal escapes to heap`时，函数 intSeq 返回一个闭包，然而这个函数在这时还没执行，因此内存不能回收, 而闭包中的变量 i 本来是 intSeq 函数内声明的一个局部变量，所以随着闭包返回的时候, 自然要从栈内存分配到堆内存上。
此外，由于`Println()`，这个闭包发生了内存逃逸 `./escape.go:14:21: nextInt() escapes to heap`, 因此 i 变成了一个范围更大的一个局部变量（因为被包在nextInt()函数中），因此只要 nextInt 这个变量不被销毁, 那么 i 就一直存在, 相当于无数个 nextInt 专属的 “全局变量”。

**go 的 GC**

> https://www.cnblogs.com/flippedxyy/p/15558742.html（从删除写屏障开始貌似有错）
> https://www.bilibili.com/video/BV1hv411x7we?p=19
> https://zhuanlan.zhihu.com/p/389177621
> https://zhuanlan.zhihu.com/p/82921000

函数的局部变量、参数、返回值均位于函数栈帧中，在函数返回时随栈帧一起销毁。但如果不能在编译阶段确定某个对象的大小，或某对象的生命周期超过了当前函数，则不分配到栈上，而是分配到堆上。
栈上分配的数据在函数结束时销毁，但堆上的数据需要程序主动释放。（**注意垃圾回收的目标是堆上的对象，栈上的不管**）
手动垃圾回收（C, C++）时，过早被释放的数据指针变为悬挂指针（Dangling Pointer），过晚或不释放不使用的数据称为内存泄露。

自动垃圾回收一般都用根节点的“可达性”近似等价于“存活性”（一个有用对象总是能从根节点集合到达）。
但能追踪到不代表一定会用到（一定不是垃圾）。

以下为**追踪式回收**，通过扫描内存识别垃圾对象。根据对内存碎片的处理分为几类。
该类算法在标记时，需要进行STW。只有所有线程停止运行，保证内存中的对象引用关系不变，才可以得到正确的引用关系。（清除时无所谓，因为标记的都是无引用的）

> 另一大类垃圾回收方法，就是引用计数，将数据的可回收性检查分摊到数据的每次操作。
> 容易实现，但代价也高，还要处理循环引用。见下。

**标记清除法：**分为标记和清除两步：标记会从根结点出发遍历所有节点的引用对象，遍历不到的对象就是垃圾，可被回收；清除就是清理可回收对象。
实现简单，但容易产生内存碎片。
内存分配时使用BiBOP（Big Bag Of Pages, 将内存块分为多种规格的大小）：减少内存碎片化，提高内存使用率，但有一定的内存浪费。

**标记整理法：**标记阶段相同。但标记结束后，将非垃圾数据尽可能紧凑地进行移动，减少内部碎片。
但需要大量的扫描和移动（且期间还是 STW，不能使用数据？）。
移动会导致对象所在的内存位置发生变化。
也可以在 GC 时，将常用的对象放在一起，来提高缓存命中率。

**复制回收法：**将堆内存划分为两个相同空间。标记时扫描空间1，将非垃圾数据复制到空间2的合适位置，最后交换空间1、2。
效率更高，避免了内存碎片。但堆内存使用率只有一半。
通常与其它算法（如分代回收）一起使用，在一部分堆内存中使用复制回收。

**分代回收：**基于弱分代假说(Weak Generational Hypothesis)（大部分对象都会在创建不久后死亡，即成为垃圾的概率高；一个对象往往在最初的几次垃圾回收中就被回收），将数据划分为新生代、老年代，老年代将使用更低的垃圾回收频率，也可用不同的回收策略（如新生代复制回收、老年代CMS）
但 go 中没有使用分代？因为分代的收益弥补不了分代的代价？

**标记清除 (mark and sweep)：**

- 暂停程序执行（STW）。
- 从根节点结合出发找出并标记所有可达对象。
- 回收未标记的不可达对象。
- 恢复程序执行（结束STW）。

根集合（Root Set）包含每个运行线程中的直接可见对象（活的），是发现堆内存可达数据的一组起点，一般为bss段、数据段以及协程栈对应的元数据（或全局变量、协程栈、保存了指针的寄存器、静态变量/常量引用的对象？）。

**并发标记清除 (CMS, concurrency mark sweep)：**

- STW，标记根对象。
- 结束STW（这时可与程序并行执行），标记根对象引用的所有对象。
- STW，重新标记在阶段2发生变更的对象。

大大减少了STW时间。但需要并发，还拉长了 GC 的时间。

**三色标记法：**

- 暂停程序的执行（STW）
- 从Root Set开始遍历，把第一次遍历到的对象标记为灰色。
  灰色点为可扩展节点，在扩展完后改为黑色。
- 枚举灰色点，将它变为黑色，把它能遍历到的（非黑色）对象标记为灰色。
- 重复上步，直到不存在灰色节点。
- 回收所有白色对象（即不被任何对象引用）。
- 恢复程序执行（结束STW）。

注：所有新对象都是白色？

上述算法都需要或多或少的STW，会导致程序完全暂停。
但长时间的暂停往往是不可接受的，所以希望能做到**增量式标记**，将 STW 分多次完成、减少每次的暂停时间，即使用户程序能与标记过程并行或交替执行。

**不 STW 或交替 STW 会产生问题的情况：**

1. 一个白色对象被黑色对象引用
2. 且灰色对象到该白色对象的引用路径被删除（黑色对象要想引用一个白色对象，一定有一条黑到灰到白的路径）

只有上述两种情况**同时发生**时，检测不到对白色对象的引用，从而错误回收了该白色对象（将非垃圾数据识别为垃圾）。
强/弱三色不变式保证上述一种情况不会发生，从而避免误回收。
强/弱三色不变式通过建立读写屏障实现。

**强三色不变式**
不允许黑色对象引用白色对象

**弱三色不变式**
允许黑色对象引用白色对象，但必须存在其他灰色对象可到达该白色对象

**写屏障**
对象内存发生修改时，会先判断对象的引用链，进行相应的颜色标注。
两种写屏障均不对栈中的对象使用，仅用在堆中，因为会大幅增加指针更新的代价。函数调用非常频繁，栈空间要求响应速度快。
所以写屏障都需要 STW 去扫描栈，所以不适用于栈特别大的场景：栈越大，STW 扫描时间越长。

**插入写屏障** 保证强三色不变式
每当A对象引用B对象时，将 A 对象标记为灰色（如果A为黑色）。
另一种方式：将B对象标记为灰色（如果B为白色）。

在标记结束时需要STW，再扫描一次所有栈进行标记：若黑色栈对象引用了白色对象，由于栈无屏障，所以该白色对象不会被标记，需在结束时扫描栈保证“不允许黑色对象引用白色对象”。

**删除写屏障** 保证弱三色不变式
删除A对象到B对象的引用时，将B标记为灰色（如果B为白色）。

在标记开始前需要STW，先扫描所有栈进行标记（快照）：若灰色栈对象删除对白色对象的引用，由于栈无屏障，所以该白色对象不会被标记。所以要在开始前扫描栈，把所有白色对象先染灰，保证不管怎样删除，“必须存在灰色对象可到达该白色对象”。
扫描精度低：会导致新的垃圾对象在当前 gc 中不能被删除，只能在下一轮 gc 中被删除。

**混合写屏障(hybrid write barrier)** 保证弱三色不变式
以删除写屏障为基础：删除A对象到B对象的引用时，将B变为灰色（如果B为白色）。
再加上插入写屏障：每当A对象引用B对象时，将B对象标记为灰色（如果B为白色）。

在标记时无需任何STW，会依次或并行扫描每个线程的栈（删除写屏障要求）。扫描单个栈只需阻塞该线程。（扫描时遇到在之前栈中被染黑的，也应将其染灰？）
非同时扫描所有栈可能带来的问题是：设一个堆对象A已被之前的栈染黑，在染下一个栈时，添加引用`A->堆对象B`，删除引用`当前栈的对象->A`。如果栈上有删除写屏障，则A会被染灰，但栈上没有。此时A是黑的，导致B不能被染黑。
加入插入写屏障：在添加引用`A->堆对象B`时，将B染灰即可。

注意，扫描中新创建的所有对象都标记成黑色（而不是白），避免被错删。
由于有删除写屏障和该条原因（？），扫描精度更低。

伪代码即插入和删除同时使用：
```
// 当 slot ptr 均为堆对象时
writePointer(slot, ptr):
    shade(*slot)    // 删除对*slot的引用
    shade(ptr)      // 添加对ptr的引用
    *slot = ptr
```

**读屏障**
会移动数据来避免内存碎片的回收方式，如果要和用户程序交替执行，则需读屏障。
读屏障确保用户程序不会访问到 已经存在新副本的陈旧对象。

读取对象 A 时，如果发现 A 存在新副本，就去读取另一个堆空间中的新副本。

**引用计数式垃圾回收 (reference counting)：**保存并实时更新对象被引用的次数。引用计数为0时，回收。
渐进式，不需要STW。简单，易于实现。
维护引用次数的开销高，不能轻松处理循环引用。

**go 进行 GC 的时机**

阈值：默认内存每扩大一倍触发一次gc
定时：默认每两分钟至少执行一次 GC（sysmon）
手动：手动调用`runtime.GC()`

**操作系统**可能不会立刻回收空闲内存，只是在系统内存紧张时回收，这样无需再分配给程序内存。

**gc的评价标准**

- 安全性（基本要求）：不能回收存活的对象
- 效率：花在gc上的时间，或吞吐率：$1-\frac{gc时间}{程序运行总时间}$
- 暂停时间：STW的时间，业务是否能感知
- 内存开销：gc元数据的开销

**gc的实现** TODO
> https://www.bilibili.com/video/BV1hv411x7we?p=20

go通过对象的类型信息，识别一个变量是指针值（指向一个对象）还是普通数值。

**如何实现STW**
g的运行是依赖p的，所以可以设置p：
1. 设置空闲p的状态为停止。
2. 设置正在运行的g的抢占标志位，等待g主动停止运行。g的主动停止时机是发生系统调用、堵塞操作及函数调用时。

**方法的指针接收者与值接收者**

> https://www.zybuluo.com/SovietPower/note/1828538#%E6%96%B9%E6%B3%95
> https://blog.csdn.net/x356982611/article/details/106544801
> https://blog.csdn.net/why444216978/article/details/110407638

如果只是调用方法，则方法接收者的类型无所谓。只是指针可以修改，且无拷贝代价。

如果是**接口**内的方法，则一个变量能否成为这个接口 与 方法接收者类型相关：

- 如果是值接收者，实体类型的值和指针都可以实现对应的接口；如果是指针接收者，那么只有实体类型的指针能够实现对应的接口。
- 反过来说，类型的值只能实现值接收者的接口；指向类型的指针，既可以实现值接收者的接口，也可以实现指针接收者的接口。

在**类型断言**时，似乎也有区别？

- 当接收者类型为指针时，定义或断言类型任意一个为值时，在编译时就会报错，提示 echo 方法应该是指针类型接收者。
- 当接收者类型为值，定义结构体时也为值，断言类型为指针时，编译不会出问题，但是运行会抛异常。

所以，在实现接口时，应保持接收者定义、结构体定义、断言类型一致。

**函数传指针和传值的区别**
https://www.cnblogs.com/xbblogs/p/11102970.html
严格来说，go只有值传递，但是可以传递指针来实现引用传递的效果，本质上没什么区别，传递值就复制一份值，传递指针就复制一份指针。
指针传递可改变原值，值传递不可。
指针传递传递的是一个地址，而非地址中的数据，传递数据较少，效率较值传递高，一般情况能用指针传递就不用值传递。但指针传递变相延长了目标的生命周期，可能导致它被分配到堆上（即发生内存逃逸），增加垃圾回收的成本。
go中channel，slice，map这三种类型的实现机制类似指针，所以可以直接传递，而不用取地址后传递指针。（注：若函数需改变slice的长度，则仍需要取地址传递指针）

**内存泄漏和内存溢出**
https://www.zhihu.com/question/40560123
内存溢出（Out Of Memory）
内存泄露 （Memory Leak）

**go map 的底层原理**
（动态哈希索引也采用类似方式）
https://www.cnblogs.com/maji233/p/11070853.html
https://www.bilibili.com/video/BV1Sp4y1U7dJ
https://blog.csdn.net/qq_42956653/article/details/121133395
https://zhuanlan.zhihu.com/p/105413496
map为一个指向hmap结构的指针，为链式哈希表（闭合寻址），哈希表中的每个元素是一个bmap（bucket）（链表，或桶）。桶的数目为$2^B$。
map对存储的键值对的key进行hash，哈希值的低8位用来选择bmap（模桶的数量），高8位用来在bmap的链表中找到对应的key。
一个bmap存储了8个键值对（和8个对应key的高8位hash值tophash，便于比对，因为key通常是复杂类型），然后bmap间形成链表（当8个不够存时，通过`overflow *bmap`指向用于扩容的溢出桶的指针）。当哈希表可能的元素过多时（大于$2^4$，即$B\geq 4$），会为每个bmap预分配$2^{B-4}$个溢出桶。
bmap中8个tophash、8个键和8个值分别存储连续，便于一次读取多个tophash（1个tophash为1byte，1个cacheline可以存多个）和键值的内存对齐（eliminate padding）。
与常见拉链法的不同是，哈希表是一个bmap数组（而不是一个值数组）；选择元素用key的哈希值的低8位模$2^B$（而不是用值的哈希值模）；每个bmap可存8个元素（而不是一个），并且有链接到下一个bmap的指针，先通过哈希值的高8位进行快速比对（而不是只通过key值之间的比较）。
**扩容**
负载因子$\text{Load Factor}=\frac{count}{2^B}\gt 6.5$时，**翻倍扩容**，令`B++`。新桶数量为旧桶的两倍，旧桶里的键值对会分流到新桶中的两个桶中（计算存在哪个桶中时，会多考虑一位）。
当负载因子未超标，但是用溢出桶较多（溢出桶数量`noverflow`$\geq 2^{\min(B,15)}$），进行**等量扩容**（`B`不变，实际就是缩容）。分配等量的新桶，并将旧桶迁移到同样编号的新桶中。这种情况一般是删除了较多键值对，重新迁移能使键值对排列更紧凑，减少溢出桶数量。
注意，扩容时并非一次全部迁移。`bmap`中用`oldbuckets`记录旧桶的位置，用`nevacuate`记录旧桶迁移的进度，进行渐进式迁移：每次访问哈希表时，迁移最多两个桶，直到所有旧桶迁移完毕。这样把键值对迁移的时间分摊到了多次哈希表操作，避免了一次性扩容带来的瞬时性能抖动。

翻倍扩容会导致元素顺序变化，等量扩容不会。

**迭代 map**

map的迭代次序不是固定的。
因为map本身是无序的（哈希表），作者希望使用者不依赖它的遍历顺序，所以在每次迭代时会随机一个桶开始遍历。
如果需要一个稳定的遍历次序，可以使用一个切片来保存特定顺序的key，然后依次从map中取出。

**函数传值**
map不同于一般对象（比如自定义的），在函数中传递就是传递一个指针，也不允许再加一个`*`。但一般对象默认是复制传值。

**go 中用 for 遍历多次执行 goroutine会存在什么问题？怎么改进？**

**如果要在每个goroutine中都获取返回值（捕获参数），有哪些方案？**
全局参数，channel，闭包

**gin**
> https://www.bilibili.com/video/BV1kK4y1J74u
> https://www.bilibili.com/video/BV1Hm4y1D7q8
> https://heary.cn/posts/%E4%BB%8E%E6%BA%90%E7%A0%81%E7%90%86%E8%A7%A3Gin%E6%A1%86%E6%9E%B6%E5%8E%9F%E7%90%86/
> gin底层还是net/http，但方便我们添加中间件、路由处理，在性能上针对HTTP Web框架常见的高并发问题进行了优化，如：通过上下文对象的对象池节省连接高并发时内存频繁申请与释放的代价。

洋葱模型

注意与第一个视频不同的是，gin的`Next()`用`for c.index < int8(len(c.handlers))`执行所有handlers，不需要在中间件中调用`Next()`。只需在某些地方`Abort`。
但是如果想（比如要推迟执行某些内容，所以需要在返回前，手动Next），也可以。因为是串行的，在新的Next执行完后`index`会很大，旧的Next会结束。
Abort就是将`index`设为很大的值`abortIndex`。
`index`是`int8`，`abortIndex`是`const abortIndex int8 = math.MaxInt8 / 2`即63，所以最多只能添加63个中间件。

`Use`的接收者实际不是Context，是Engine（包含一个RouterGroup结构体），在`Engine.RouterGroup.Handlers`中添加处理函数。
但是在`Next()`时，还是`Context`保存`index`和`handlers`（在Run之后对请求会生成Context？）。
```go
type RouterGroup struct {
	Handlers HandlersChain // type HandlersChain []HandlerFunc
	basePath string
	engine   *Engine
	root     bool
}
```

`POST, GET`等的接收者是`Engine.RouterGroup`（先使用`Engine.Group("relativePath")`返回一个）。
`Group`创建一个新的路由器组（`r.Group`时传入的就是`Engine`本身），该组的`Handlers`包含父`RouterGroup`的所有Handler和新传入的handlers，`basePath`也是基于父`RouterGroup`再加上新的`relativePath`。
路由器组省去了输入重复前缀和中间件的麻烦（给`r`加中间件也是给所有组加）（请求不在handler中，是单独的路由树，不会复用，路径也不一样）。
```
func (group *RouterGroup) Group(relativePath string, handlers ...HandlerFunc) *RouterGroup {
	return &RouterGroup{
		Handlers: group.combineHandlers(handlers),
		basePath: group.calculateAbsolutePath(relativePath),
		engine:   group.engine,
	}
}
```

`RouterGroup`中保存了创建它时的`basePath`，在生成路由时会添加进去：
```
func (group *RouterGroup) calculateAbsolutePath(relativePath string) string {
	return joinPaths(group.basePath, relativePath)
}
```
`RouterGroup.POST`等创建路由，都是调用`RouterGroup.handle()`函数，但是在`httpMethod`传入相应字符串（`"POST", "GET", "DELETE"`...）：
```
func (group *RouterGroup) handle(httpMethod, relativePath string, handlers HandlersChain) IRoutes {
	absolutePath := group.calculateAbsolutePath(relativePath)
	handlers = group.combineHandlers(handlers)
	group.engine.addRoute(httpMethod, absolutePath, handlers)
	return group.returnObj()
}
```
`RouterGroup.handle()`计算它的路径，在原本的`Engine`中添加该路由。

路由是通过前缀树（Trie）来匹配。

**gin.New()**
`gin.Default()`与`New()`相比，只是使用了两个中间件。
Logger就是日志，Recovery：returns a middleware that recovers from any panics and writes a 500 if there was one。
```
func Default() *Engine {
	debugPrintWARNINGDefault()
	engine := New()
	engine.Use(Logger(), Recovery())
	return engine
}
```

`Recovery()`中间件就是`defer`了一个恢复过程，然后调用`c.Next`。
`defer`的部分就是`if err := recover(); err != nil {..}`。先检查错误是不是连接中断引起的（`brokenPipe`），如果是则Abort。否则调用一个`type RecoveryFunc func(c *Context, err interface{})`的`handle`函数。
如果没定义这个handler，则使用默认的，直接Abort。

```
// AbortWithStatus calls `Abort()` and writes the headers with the specified status code. For example, a failed attempt to authenticate a request could use: context.AbortWithStatus(401).
func defaultHandleRecovery(c *Context, err interface{}) {
	c.AbortWithStatus(http.StatusInternalServerError)
}
```

**for 循环变量的一些问题**

`for i, v := range x`中定义的局部变量`i, v`，只会在最初定义一次，后面的迭代都是直接覆盖`i, v`。
也就是整个循环过程中，`i`或`v`都是同一个变量（这和预期的也一样）。

**对`i`或`v`取地址时：**

```go
var all []*Item
for _, v := range items {
	all = append(all, &v)
}
```

取到的都是循环变量的地址，所以`all`的所有元素都相同，都是`v`的地址。这还可能导致`v`内存逃逸。
有的说可以加一个`v := v`来新声明一个变量：

```go
var all []*Item
for _, v := range items {
	v := v
	all = append(all, &v)
}
```

但由于go只有值复制，新的`v`的地址不同与`items[i]`。正确的方法是用`&items[i]`。

**将`i`或`v`用在闭包函数中时：**

```go
var prints []func()
for _, v := range []int{1,2,3} {
    prints = append(prints, func() { fmt.Println(v) })
}
for _, print := range prints {
    print() // 3 3 3
}
```

闭包函数取到的也是循环变量本身，而非遍历的对象。所以`v`会逃逸，`prints`里全是同一个`v`。

**将`i`或`v`在协程中时：**

````go
wg := sync.WaitGroup{}
var arr []int = []int{1, 2, 3}
for _, v := range arr {
    wg.Add(1)
    go func() {
        fmt.Println(v)
        wg.Done()
    }()
}
wg.Wait() // 3 3 3
````

同样协程中得到的都是同一个变量。这个也会有提示：`loop variable v captured by func literal`。
可以将`v`作为参数传递避免。

**修改map内的元素**

对`map`中值的修改（`map[key]`）只能通过赋新值完成，不能直接修改。这与数组和切片不同。
常见情况是，当`map`的值为结构体时，不能进行`map[key].a = 1`，必须先拷贝一个`tmp = map[key]`，然后修改`tmp.a = 1`，再新赋值`map[key] = tmp`。

但是，当`map`的值为某结构体的指针时，可以进行修改。

```go
// array
a := [...]Item{{1}, {2}, {3}}
a[1].a = 9
fmt.Println(a) // [{1} {9} {3}]

//map
// b := map[int]Item{1: {1}, 2: {2}, 3: {3}}
// b[1].a = 33 // error: cannot assign to struct field b[1].a in map
// fmt.Println(b)

b := map[int]*Item{1: &Item{1}, 2: &Item{2}, 3: &Item{3}}
b[1].a = 9 // ok
fmt.Println(b[1]) // &{9}
```

原因是，数组和切片的元素是可寻址的，即可通过`&arr[i]`找到某元素的地址，从而操作元素的值。
但map的值是不可寻址的，不能通过`&map[key]`找到`value`的地址，获取到的仅仅是一个值，不能操作原本元素。
但如果map保存了指针，`map[key]`就相当于找到了`value`的地址，就可以修改元素。当然这本质上是操作的指针位置而非元素。

> map 中的元素是不可寻址的，因为：
> map 会动态扩容，导致原本的 value 被迁移到新的内存位置，地址发生变化。所以我们允许获取一个 map 元素的值，但不允许获取 map 元素的地址，因为这个地址很可能是无效的。
>
> 关于这个，有一个 [open 的 Issue](https://github.com/golang/go/issues/3117#issuecomment-430632750)，也许在之后可能会改变。

注意，在给`map[int]*int`赋值时，不是赋`&123`，123不是变量没有地址，要先定义一个`x := 1`，然后`map[1] = &x`。

> 有些函数返回值是不可寻址的，必须用一个变量对它进行拷贝，然后再使用变量的地址。
> 例：`type S struct { Time *time.Time }`，`time.Now()`是不可寻址的，`s := S{ Time: &time.Now() }`是错误的。
> 创建 S 必须通过拷贝，如：`s := S{ &[]time.Time{time.Now()}[0] }`，或函数：`func PtrTo[T any](v T) *T { return &v }`、`s := S{ Time: PtrTo(time.Now()) }`。
> 写起来比较麻烦，但目前确实没有更好的方法，见[这里](https://github.com/golang/go/issues/45653)。

**sync.Map 原理**

> https://zhuanlan.zhihu.com/p/115432432

分为两个map：`read`和`dirty`。概括来说，`read`是`dirty`的子集，`dirty`中有`read`没有的一些key。对于共有的key，它们共享value。
读改`read`只需要通过CAS；但读改`dirty`必须加锁（两种情况：读/插入/更新`read`没有的键；更新`expunged`的键，但之后就变为非`expunged`）。

当删除元素时，不会真正删除，而是将其标记为`nil`。
当`dirty`不存在，但出现了新键（`read`没有）时，遍历`read`，创建并拷贝新`dirty`，同时将`read`中的`nil`替换为`expunged`，也不拷贝这部分。
当`dirty`存在，且Load、Delete在`read`中读取不到的次数`missCount`达到当前`dirty`大小时，将`dirty`直接覆盖`read`，清空`missCount`和`dirty`。
`expunged`是一个预定义的指针常量，只要不冲突可以随便设，代码中为：`var expunged = unsafe.Pointer(new(interface{}))`，即一个空接口的地址。

`read`与`dirty`的关系：
创建新的`dirty`时，需要拷贝一份`read`（最初数据和所有的修改一定会包含在`dirty`中，所以要删除`dirty`时，可以直接将`dirty`赋给`read`）。
拷贝规则：
对于`read`中没有被delete的键，拷贝给`dirty`相同的键值。值是值拷贝的`*entry`，但由于是指针，`*entry.p`值相等即指向同一个数据（`p`是value的地址）（准确说`&p`，`p`是一个`unsafe.Pointer`结构体）。所以对于`read`中没有被delete的键，`dirty`与`read`共享值（修改是同步的）。
对于`read`中被delete的键，将其设为`expunged`。`dirty`没有该键。

也就是，在创建`dirty`后：**对于`read`中非`expunged`的键，`dirty`与`read`总是共享值（修改是同步的）。**
`dirty`没有`read`中`expunged`的键，在store时要拷过去（即共享）。

在store一个键key时：

1. 如果`read.m[key] = nil`，则表示创建了`dirty`后删除了该键。
   由于`dirty`包含该键，所以直接改`read.m[key]`即可。可通过CAS直接完成。
2. 如果`read.m[key] = 非nil且非expunged`，则表示创建了`dirty`前没删除该键，或删除了但之后添加了该键（情况3）。
   同1，由于`dirty`包含该键，所以直接改`read.m[key]`即可。可通过CAS直接完成。
3. 如果`read.m[key] = expunged`，则表示创建`dirty`前就删除了该键。
   则`dirty`不包含该键，所以先给`dirty`赋值`m.dirty[key] = read.m[key]`，然后直接改`read.m[key]`。
4. 如果`read`中没有`key`，`dirty`中有，直接更新`dirty`。
5. 如果`read`、`dirty`中都没有`key`，在`dirty`中添加该键值。
   如果此时不存在`dirty`，则执行创建`dirty`。

也就是，在创建`dirty`后：**对于`read`中没有的键，不会再在`read`中出现，所有操作都在`dirty`中进行。**(为`nil`或`expunged`不等于没有)
情况3,4,5 涉及到`dirty`，所以要加锁。

在delete一个键key时：

1. 如果`read`中不存在该键，直接在`dirty`中尝试删除。
2. 如果`read`中存在该键，如果值为`nil`或`expunged`，不用管，否则设为`nil`（`dirty`中的也会被同步设为`nil`）。

根据`read`与`dirty`的关系、store、delete规则，可得出`read`与`dirty`的关系：

1. `read`是`dirty`的子集，创建`dirty`后新出现的键在`read`中不存在，如果是共有的键则值共享。
2. 如果键在`read`中且非`expunged`，则只涉及`read`，不涉及`dirty`，则查询修改都可只通过CAS`read`完成，不需要锁。
3. 否则只要涉及到`dirty`就要加锁（同时为了避免加锁前`read`被改变，依旧要再检查一下`read`）。

继而得到load规则：如果`read`中有则直接读取，否则加锁从`dirty`读取。

**sync.Map 适用场景**：多线程压力大，读多写少，或程序中操作的键值集合变化不大。
理论上，只要不频繁插入新键，就能基本保持只用CAS而不需要锁。

在第一次新建`dirty`时，需要拷贝`read`，可能发生性能抖动。

注意Mutex 一样， sync.Map 也同样不能被复制，因为 atomic.Value 是不能被复制的。

> 设计思路总结：
> 对于map中已有的键（即read有的键值对），可以CAS更新value内部的指针，这只涉及map读，所以可以并发。
> 对于新的键，必须要用map插入，也就是map写，所以要加锁。
>
> 将上面两部分分离，分别用`read`和`dirty`处理，前者不需要锁，很高效。
>
> 当新键过多时，基本都要读`dirty`，所以要将`dirty`再赋给`read`，但这要求`dirty`遍历拷贝`read`来重新创建一个新的（`nil`不可拷贝）。
>
> 具体见 *项目笔记 - go sync.Map 测试*。

**sync.WaitGroup**

> 信号量是 os 提供的，通过`runtime_Semacquire(sema)`休眠当前协程，通过`runtime_Semrelease(sema, false, 0)`唤醒一个因信号量等待的协程。

WaitGroup 包含一个信号量和两个计数器，共 4\*3=12 字节。两个计数器 counter 和 waiter counter 分别保存：通过 Add 加了多少值、当前正在 Wait 的协程数量。

- Add(delta int)：给 counter 加上 delta。
  delta 可能为负，所以加完后会判断 counter 是否为0，如果是，会释放和计数器 waiter counter 等量的信号量，唤醒当前正在 Wait 的所有协程。如果 counter 小于0会 panic。
- Done()：即 Add(-1)。
- Wait()：如果 counter 为0 则直接返回（否则也无法释放），否则通过 CAS 将 waiter counter 加一，然后通过信号量休眠该协程。

可以用来阻塞主线程：首先`wg := sync.WaitGroup{}`，`wg.Add(n)`，然后创建 n 个协程，或在每个协程中`wg.Add(1)`；协程结束时执行`wg.Done()`；主线程创建完协程后执行`wg.Wait()`。
同理，可以阻塞一组因为生产者而等待的消费者。

注意，执行 waiter counter +1 时必须保证 counter 为0（否则不符合逻辑），所以必须通过`CAS(state, <counter, waiter_counter>, <counter, waiter_counter+1>)`实现。
同样，在给 counter + delta 时，必须也是原子加，即`AddUint64`。
为了实现 CAS 和原子加，必须将 counter 和 waiter counter 作为一个64位整体去操作。而64位原子操作要求这个地址必须是8字节对齐的，所以 WaitGroup 会根据自己的起始地址，决定 counter 和 waiter counter 在哪个位置（0字节偏移还是4字节偏移）：

```go
type WaitGroup struct {
    noCopy noCopy
    state1 [3]uint32 // 为什么用数组不用字段？感觉都可以。。
}
// state 即 (counter, waiter_counter)
func (wg *WaitGroup) state() (statep *uint64, semap *uint32) {
    if uintptr(unsafe.Pointer(&wg.state1))%8 == 0 {
        // 如果地址是8字节对齐的，则数组前两个元素做state，后一个元素做信号量
        return (*uint64)(unsafe.Pointer(&wg.state1)), &wg.state1[2]
    } else {
        // 如果地址是4字节对齐的，数组后两个元素做state，第一个元素做信号量
        return (*uint64)(unsafe.Pointer(&wg.state1[1])), &wg.state1[0]
    }
}
```

**使用 map 时要注意什么**

1. 不是并发安全的。写的时候进行其它操作都会 panic。
2. 要初始化（`= make(map[int]int)`或`= map[int]int{}`）。map 结构是一个指向`hmap`的指针，未初始化时为 nil。
   读取未初始化的 map 总会返回零值，但写未初始化的 map 会导致 panic（assignment to entry in nil map）。
   通过`m = nil`直接清空一个 map（需要重新初始化，直接赋值新的也行）。
3. map 的遍历是无序的。
4. map 是一个指针，所以值拷贝的两个 map，还是指向同一个哈希表。
5. map 的元素是不可寻址的，所以如果用结构体做 value，不能直接修改内部的属性，必须重新赋值新的结构体，或使用指针做 value。
6. map 可以是多维的，但注意每一维的 map 都要初始化，如：`myMap := map[int]map[string]string{} myMap[0] = map[string]string{}`。
7. 获取所有 key 可以`keys := reflect.ValueOf(myMap).MapKeys()`，但最好还是先 make len(map) 大小的数组，直接遍历 append？

**使用 append 时要注意什么**

1. 不是并发安全的，多线程 append 要加锁。
2. 拷贝切片时，如果不是深拷贝`copy()`，两个切片还是会共用底层数组。如果 append 后底层数组没有发生扩容，则底层数组不变，修改同步；如果发生扩容，两者的底层数组就独立了。
   一般不会为切片创建多个引用，都要深拷贝。

**使用 channel 时要注意什么**

1. 如果发送的消息数量不等于接收的数量，就会有发送方或接收方阻塞在 chan 上，导致这个 chan 一直被使用，不能被释放。
   正常情况下，如果无人使用，则 chan 会被 GC 释放。所以应与超时机制共同使用。
2. 在如下情况会 panic：重复关闭 chan；向关闭的 chan 中发送；发送时关闭（虽然 chan 还在、不会被 GC，但是 chan 不允许这样）。
   所以应该只由发送方关闭；如果有多个发送方，就需要同步机制保证只由一个关闭、关闭后不再发送。
3. 在一个协程内进行同一个 chan 的读和写可能导致死锁，所以最好要么只写，要么只读。
4. 如果不再使用，chan 要在安全的时候及时关闭，避免后续读的协程一直阻塞。
5. 已经关闭的 chan 总是可以读到东西。如果是有缓冲区的 chan 且缓冲区还有数据，则会读到缓冲区内容（没被 GC），否则读零值（可见 Go chan 源码）。
   所以如果 select 的某个分支有关闭的 chan，总是可以判断成功。
6. 读写未初始化的 chan（即 nil）会阻塞。

go 提供了一些安全使用 chan 的方式：

- 读取关闭的 chan 会返回零值，可以用 chan 的第二个返回值判断读取的 chan 是否关闭（`data, ok := <- ch`）。
- 使用`for range`读取 chan，会在 chan 关闭时退出循环（`for data := range ch`）。
- chan 可以指定方向，`ich chan`或`ich chan int`表示读写都可，`ich chan<- int`表示只能写，可用做发送方，`ich <-chan int`表示只能读，可用做接收方，且不允许调用`close(ich)`。
  如果错误使用，写代码或编译时就能发现错误。

**使用 接口 时要注意什么**

见上 *go - 接口与 nil 比较*。
只要接口有具体类型，即使这个类型的值是 nil，接口也会被判为非 nil。
所以不要写`接口 = 具体类型(nil)`逻辑的代码。

**使用 锁 时要注意什么**

默认的 mutex 是不可重入锁，线程不能重复加锁，否则会死锁（自己加了锁但是又等待解锁）。
同一个锁的 Lock 和 Unlock 一定要配对使用。
（go 不推荐使用可重入锁。见 *go - 可重入锁*）

拷贝的另一个锁和原锁有相同状态（是否锁住），但它们是独立的。
但锁不要随意拷贝，否则容易不注意出问题。
例：

```go
func main() {
    var mu sync.Mutex

    // 第一次加锁放锁
    mu.Lock()
    // 不知道为啥拷出来
    m := mu
    m.Unlock() // 成功，因为拷贝了锁住的状态

    // 第二次加锁放锁 
    mu.Lock() // 死锁，因为 mu 没有释放
    i += 1
    mu.Unlock() 
}
```

注意，**使用结构体方法、或作为参数传递时，如果要修改原对象的状态，必须用指针对象`(o *Obj)`，不能用传值！否则会拷贝对象内的所有字段！**
修改对象的状态，包括修改对象字段、调用会修改对象字段的方法（如 mu.Lock()）。
修改 map 也是，但由于 map 是指针类型，所以没有影响，但规范上也必须传指针。


```go
type Obj struct {
    mu sync.Mutex
}
func (o Obj) Lock()        { o.mu.Lock() } // 注意o是拷贝的Obj！mu自然也是拷贝出来的函数内变量
func (o Obj) Dosomething() {}
func (o Obj) Unlock()      { o.mu.Unlock() }
func main() {
    o := Obj{}

    o.Lock()
    o.Dosomething()
    o.Unlock() // error: unlock 了没有 lock 的锁

    o.Lock()
    o.Dosomething()
    o.Unlock()
}
```

与 mutex 同样必须配对、容易出错的：WaitGroup、Pool、Condition。

```go
// 正确方式：(wg *sync.WaitGroup)
// doSomething(&wg)
func doSomething(wg sync.WaitGroup) {
    defer wg.Done()
}
func main() {
    var wg sync.WaitGroup
    wg.Add(1)
    doSomething(wg)
    wg.Wait() // 死锁，因为wg一直不会执行Done
}
```

虽然上述错误都能过编译，但能用`go vet`检查。这是一个静态诊断器，检查 go 中可通过编译但仍可能存在错误的代码。

**noCopy**

Mutex 理论上不该被拷贝，但编译器不会阻止它被拷贝，只能通过`go vet`检查出来。
之所以能被`go vet`检查，是因为 Mutex 内部定义了一个 noCopy 类型：

```go
type noCopy struct{}
// Lock is a no-op used by -copylocks checker from `go vet`.
func (*noCopy) Lock() {}
func (*noCopy) Unlock() {}
```

如果我们想让自己定义的结构体，也不允许值拷贝，或至少能被`go vet`检查出来，也可以在里面定义一个`noCopy`类型的变量实现。
Mutex 中的 noCopy 不能导出（首字母小写），自定义一个即可。

```go
type noCopySign struct{}
func (*noCopySign) Lock() {}
type A struct {
    // ...
    noCopy noCopySign
}
```

noCopy 结构体的名字是任意的，但必须定义`Lock()`方法。
当对 A 进行值拷贝时，`go vet`能检查出来。引用拷贝自然是允许的。

直接在 A 里包含一个 Mutex 也可以。

**Go 中哪些对象不可比较**

内嵌类型、指针、chan、字符串、数组 都可比较；如果结构体的每个字段都可比较，则结构体可比较。
如果接口的动态类型可比较，则接口可比较。
slice、map、function 只能与 nil 进行比较（规则见上 *go -  Go 的 nil*）。


判断两个函数类型或本身是否相同，要分别用`reflect.TypeOf(f)`和`reflect.DeepEqual(f1, f2)`。

**Go 如何实现面向对象**

封装：结构体实现，可定义字段和方法。通过首字母大小写控制访问权限。

继承：在结构体中包含其他类型的结构体。
这种有两类，一个是匿名结构体字段，一个是有名结构体字段。结构体可以使用匿名结构体所有的字段和方法，即使它们是小写开头的；有名结构体的内容只能通过对象间接使用，所以只能访问大写开头的。
如果两个匿名结构体有相同的字段和方法，则使用时必须指明使用的哪个匿名结构体。
如果包含两个及以上 同一种类型的结构体，则它们不能使用匿名，必须有名字。

```go
type Animal struct {}
type Owner struct {}
type Dog struct {
    Animal // 匿名结构体
    owner Owner // 有名结构体，调用它的方法和属性必须通过owner进行
    name string
}
```

多态：通过接口实现。
当一个结构体实现了接口中的所有方法时，就实现了这个接口，可以写为这个类型。
所以接口可以作为父类，其它结构体可作为类型不同的子类。

**Go 怎么检查内存泄露**

> 短期的内存泄露可能没事，但长期可能导致程序占用过多内存被 os kill 掉。

首先通过 pprof 检查内存的使用情况，可以部分检查内存泄露。
但最主要的，还是要注意内存泄露的场景和相关代码。

Go 虽然有 GC，但也会导致内存泄露或伪内存泄露。
内存泄露一般是协程无法正常退出导致的（程序结束退出不算），比如：写没有缓冲区的 channel 但是没有人接收；写缓冲区已满的 channel 但是没有人接收；等待接收一个 channel 但是没有人发送；select 的控制退出的 channel 没有人发送；读写一个未初始化的 channel。
还可能是因为某些对象的使用不正确，导致不再使用、但一直无法释放，如：定时器`time.Ticker`使用完后必须`Stop()`，不然不会释放。

伪内存泄露，是因为不恰当的引用导致部分内存长时间无法释放。
比如（代码见[这儿](https://blog.csdn.net/qq_42170897/article/details/127771731)）：

1. 截取一个切片 big 得到 small，因为两个切片共享底层数组，所以只要 small 不释放，即使 big 不再使用，整个底层数组也不能被释放。
   通过 copy 一个切片而不是截取可以解决。
2. 截取一个字符串 big 得到 small，同上，只要 small 不释放，big 的其它部分就不能释放。
   也是通过拷贝解决。可以`small = string([]byte(big[:50]))`，但这会产生一个没用的临时副本。
   也可以`small = (" " + big[:50])[1:]`，Go 编译器对该实现做了优化，不会产生临时对象？
   还可以通过`strings.builder`，`sb.WriteString(s1[:50])  small = sb.String()`，底层会通过`unsafe.Pointer`做一个转换。
3. 一般会通过 defer 在函数接收后回收某些对象。但函数的逻辑可能很长，在中间就可以回收对象了，不需要拖到函数返回。
   可以将上面的部分抽象成一个函数，或者用匿名函数。



**Go 如何进行程序性能分析**

> https://www.zhihu.com/tardis/bd/art/371713134
> https://zhuanlan.zhihu.com/p/259689535
> https://studygolang.com/articles/20529

pprof 是一个 go 的程序性能分析工具（profile：画像），提供了对堆内存分配、堆内存使用、CPU 使用、锁、阻塞、线程创建等信息的分析。具体见上链接。
通过对内存的分析，可以一定程度检查内存泄露，但不是完全能查出来，因为它只能给你堆内存的使用情况，使用多、不释放不代表一定泄露。

工具型应用可以通过`runtime/pprof`，在程序执行结束后，将程序数据写入到指定文件中。

gin 框架中可以引用官方提供的`gin-contrib/pprof`包，然后调用`pprof.Register(r)`。
然后访问`http://localhost:8080/debug/pprof/`就可以看到程序的信息（Register 会注册此路由）。

pprof 只是生成了程序数据，通过`go tool`中的`pprof`可分析该数据文件。
对于文件，可`go tool pprof cpuprofile`（命令行交互模式）或`go tool pprof -http=:9091 cpuprofile`（进入web界面）；对于网页，可`go tool pprof http://localhost:8080/debug/pprof/profile`。
以 CPU 或内存使用情况为例，通过`top n`可列出占用最大的 n 个函数。

在交互模式下使用`web`，可生成 svg 格式的函数调用图（火焰图），会通过函数框的大小和颜色 直观地显示函数的占用。







-----

## Go 代码相关题目

**使用两个协程交替输出 0~9 数字**

见 *Codes - Go - 面试 下代码*。

1. 使用一个无缓冲区的 chan，A 发送、然后等待 B 接收，也可实现同步。

   注意，在 一次发送与接收 到 下次发送与接收 之间，只能有一个协程执行任务，否则不能保证顺序（它们会执行相同的循环，但是对每个 i 只有一个协程会操作）。

2. 用两个 chan。双方交替给对方的 chan 发信息。
   最初主线程给 chan1 发信息，让 A 执行；然后 A 给 chan2 发信息，让 B 执行；然后 B 给 chan1 发信息，让 A 执行...

3. 使用一个全局或线程共享变量。不断自旋，检查变量状态、自己是否可更新，可实现同步。

   注意，全局变量是共享的。使用匿名函数时，如果没有将局部变量 x 作为参数传入，x 也是共享的（使用的外部变量）。

**怎么结束协程**

> https://blog.csdn.net/weixin_52690231/article/details/123159765

Go 没有提供从外部终止协程的接口，需要协程主动退出（主线程的 main 结束也会退出）。
可通过 chan 实现。

1. 协程内使用`for v := range ch {...} return`，当 ch 关闭时（close(ch)），循环会结束，可用来退出协程。
2. 协程内使用`for { select {...} ...}`，`select`内可以接收退出管道的信息`case <-quit: return`实现退出。
   注意，当 chan 关闭时，select 会收到零值，所以不需要给 quit 发送数据，直接 close(quit) 也可。
3. 官方提供了 context 包，用于控制协程。context 的 cancel 信号可以终止协程运行。





