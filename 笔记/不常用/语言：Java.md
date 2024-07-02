# 面试 语言：Java

Tags: 实习


-----

[TOC]

-----

## Java





**基本类型及包装类**

基本类型 (primitive type) 简单，操作效率高（但可能也没高多少？），但并不是很常用。
包装类型 (wrapper class) 便于使用，还提供了各类函数。

- 基本类型直接比较（会自动隐式转换）。
  同种封装类型的比较需要使用 equals（使用 == 将会判断对象的地址是否相同，而非值），不同封装类型必须转换为同种类型才能比较和赋值（类似 go 的强类型），封装类与对应基本类型的比较和赋值会自动拆箱、获取数值。
- 包装类对象会分配在堆上（需要用 new 创建，只在栈上保存引用），会涉及 GC，而局部的基本类型会分配在栈上。
- 包装类对象在传递时，是传引用，而不是传值。
- 包装类的默认值为 null，且可以接收一个空值（但可能也会导致 bug）；而基本类型的默认值是 0 或 false，不能接收空参数，所以不适合用于数据库字段。
- 一个包装类对象至少需要 8B，此外还需要一个 4B 或 8B 的引用；而基本类型一般很小，如 int 就是 4B。

除浮点外的包装类，都有一个缓存：

```
boolean：true, false 
char：0~127 
byte/short/int/long：-128~127 
// float 和 double没有缓存
```

值在上述范围内的包装类对象，会直接使用常量区中的缓存对象；否则每次使用，都会在堆中 new 一个新对象。
对于缓存的包装类对象，使用 == 比较也会返回 true。

**包装类的效率**

包装类对象是一个 final 类，无法修改内部值，在运算时，需要拆箱（通过引用获取堆上的对象）再装箱（包装数值在堆上使用 new）创建一个新对象赋值（如`a += 1;`）；而基本类型的运算则非常简单。
对包装类进行频繁运算时，会占用更多内存、触发更多 GC（产生更多内存碎片），影响效率。

除非下面几种迫不得已的情况，应避免使用包装类：字段值可能为 null（数据库字段），用于集合（java 集合内只是存储了对象的引用，无法存储单纯的数值），用于匹配 Object 类型的参数等。

如果不需要赋值给新的包装类，应选择返回基本类型的函数（而非返回包装类）。
比如：`sum += String.parseInt(s)`比`sum += String.valueOf(s)`要高效，后者会生成一个包装类然后释放。



**线程池的7个参数，怎么使用**

**线程池拒绝策略**





---

## Spring

TODO：
https://www.nowcoder.com/feed/main/detail/3fe47f17208c4c43827bf86601f75a6f?sourceSSR=users



---

## 代码相关

**流 stream**

将容器转换为流，可以做很多实用操作：

- `map(func)`：对每个元素，调用某个函数 func，并替换为函数的返回值。函数一般为`Class::getxxx`，或一个 lambda 函数，都以每个元素为参数。
- `filter(v -> v...)`：过滤掉不符合条件的元素。
- `collect(Collectors.toList())`：变为 list。
- `collect(Collectors.groupingBy(...))`：按某个元素分组，具体见下。
- `collect(Collectors.toMap(User::getId, Function.identity()))`：生成一个 map，key 为 id，value 为对象本身。

**Collectors.groupingBy**

> https://blog.csdn.net/u014231523/article/details/102535902

按某个字段进行分组，包含很多功能。
会返回 Map，key 为元素的类型，value 取决于 groupBy 的参数：第一个为分类依据（与 map 类似，是以每个元素为参数的函数）；第二个可选，为分类后的统计方式（默认放入一个 list，如果是 summingInt 则传入一个以元素为参数、返回 int 的统计函数）。

```java
// 将元素分组
Map<Integer, List<User>> userGroup =
	users.Stream().collect(Collectors.groupingBy(User::getUserId));

// 根据元素构造key，然后再按key分组
Map<String, List<User>> userGroup =
	users.Stream().collect(Collectors.groupingBy(user -> user.getName() + "_" + user.getAge()));

// 根据元素构造key，然后再按key分组
Map<Boolean, List<User>> userGroup =
	users.Stream().collect(Collectors.groupingBy(user -> {
		return user.getAge() < 18;
	}));

// 分组后求和
Map<Integer, List<User>> userGroup =
	users.Stream().collect(Collectors.groupingBy(User::getUserId, Collectors.summingInt(User::getNum));

// 分组后计数
Map<Integer, Long> userGroup =
	users.Stream().collect(Collectors.groupingBy(User::getUserId, Collectors.counting());

// counting 实际是 reducing(0L, e -> 1L, Long::sum)，所以可据此写一个返回 Integer 的 counting
Map<Integer, Integer> userGroup =
	users.Stream().collect(Collectors.groupingBy(User::getUserId,
                                                 Collectors.reducing(0, e -> 1, Integer::sum));
```









