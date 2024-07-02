# Folly ConcurrentHashMap 与 AtomicHashMap
Tags: 实习 2022.7 华为

------------

## ConcurrentHashMap

folly 的 ConcurrentHashMap 是一个并发安全的哈希表，允许 wait-free 的读操作(?)；会将数据分段，对每个段的写操作需要加锁。
ConcurrentHashMap 效率很高，但是依然比无锁的 atomic maps (AtomicUnorderedMap, AtomicHashMap) 慢。
如果哈希表容量不可预估，或包含大量`erase`操作，AtomicHashMap 就不合适了，ConcurrentHashMap 要更好。

ConcurrentHashMap 分为$2^k$段（默认为$256$），每段包含若干个桶（称为一个`BucketTable`）。


### **并发哈希的主要问题**
folly 使用 Hazard Pointer 保护 被删除 但还在使用的点不被回收。但允许访问被删除的点会导致以下问题：
设 $...\to a\to b\to c$是桶中的一条链：
1. 线程1 执行`find`且正枚举到$a$。
2. 线程2 执行`erase`删除$a$。由于1 持有$a$，所以$a$不会被回收，仍合法。
3. 线程3 执行`erase`删除$b$。没有人引用$b$，所以回收$b$。
4. 线程1 继续进行`find`，从$a$枚举到$b$（$a$被删除所以`next`不能更新），此时访问$b$就会出错。

为此，folly 允许待回收的对象`hazptr_obj`有相关父节点/子节点。当所有父节点被回收完时，对象才可被回收。
上述情况中，$a$是$b$的父节点，会保证$a$被回收前$b$一定仍可访问。但线程1 不能看到线程2、3 的并发更改，会在旧的链上进行查询。

> 这种对象为`hazptr_obj_linked`类，有两个`count`记录它外部对它的链接数，只有`count`为0 时才可被回收。每当一个对象被回收时，减少其子对象的`count`。

> 无锁哈希论文中的解决方式是：当通过$a$访问到$b$后，先用 HP 保护$b$，然后检查$a$是否被删除或$a$的`next`是否发生改变：`if (a.<mark, next> != <0, b>)`，如果是则$b$不合法，`goto try_again`。
> 这样线程能看到更近的更新，但一次操作可能需要多次重试。

由于插入、删除、扩容都是加锁的，除 HP 外与普通哈希表几乎相同，所以其它一般的读写不会出问题。

### **扩容**
每次对一个满的段进行两倍扩容：分配两倍个新桶，然后将所有键值对拷贝到新桶。
迁移每个桶时，会复用桶末尾最长的那条 仍在同一个新桶的链：直接移动其 head，不拷贝。
```cpp
// Set longest last run in new bucket, incrementing the refcount.
lastrun->acquire_link(); // defined in hazptr_obj_base_linked
newbuckets->buckets_[lastidx]().store(lastrun, std::memory_order_relaxed);
```

### **iterator**
使用 iterator 可保证访问到的对象一定合法（但不一定最新）：iterator 内有三个 Hazard Pointer，分别用来 保护它在使用的`BucketTable`（避免扩容后桶被回收）、保护当前对象、临时使用。
因此扩容后 iterator 也不会失效。

迭代通过依次枚举每个桶实现。如果哈希表内比较稀疏，效率可能会较低（一般的哈希表只会枚举已有元素组成的链表）。

### **问题**
不太懂 既然复用了末尾的一条链，说明拷贝代价更大，那为什么不复用所有的链？毕竟中间与末尾的链相比，只是尾部不为空。
可能是只保留末尾的，依然能有较好的空间连续性？

### **总结**
ConcurrentHashMap 的实现以简单为主，没使用复杂的无锁算法，而是在链式哈希的基础上加了 锁、带计数的 HazardPointer 来实现 并发安全、不会访问无效指针。



---

## Folly AtomicHashMap

### **ThreadCachedInt**

在线程本地缓存中保存变量

- 线程可使用`IntCache`缓存自己对共享变量的更新。只有本地更新量到达指定值，或手动调用`sharedVar.readFull()`时，线程的更新才会被同步到共享变量。
- 线程修改本地缓存不需要原子操作或锁，所以效率很高。但变量的值会很不精确，获取精确的值需要更大开销（读取每个线程的缓存）。


### **AtomicHashArray**

线程安全的无锁哈希表，不能扩容。

- 通过 CAS 设置元素状态，获取资源，实现无锁（将一个空位置 CAS 成非空，允许只有自己修改；将一个非空位置 CAS 为删除）。
- 使用简单的开放寻址，局部性好。
- 因为只有 CAS，没有锁等机制，不能安全的删除元素。
  所以`erase`的元素不会被真正删除，依旧占据空间，只是通过 CAS 标记为删除。
- 只支持`int32_t`或`int64_t`类型的`key`。
- 因为使用了`ThreadCachedInt`，元素数量不能实时更新，表内元素的比例会超过`maxLoadFactor`，可能影响效率。
- 没有`update`操作，只能通过 iterator 直接修改值，需自行保证正确性。


### **AtomicHashMap**

线程安全的无锁哈希表，可通过分配更多的哈希表扩容。

- 效率高，空间利用率高，但与初始容量相关，需要：预先知道大概需要多少空间，`erase`操作不多。
- 每次扩容需要分配一个`AtomicHashArray`，所有（不能提前返回的）操作均需多访问一个哈希表。也即效率随扩容次数线性降低。
- 最大扩容的空间有限，与初始容量相关。
- 其它特性与`AtomicHashArray`相同。

`AtomicHashMap`由1个主哈希表 (primary map) 和扩容新建的最多16个次哈希表 (secondary map) 组成，都称为`subMap`。每个`subMap`都是一个`AtomicHashArray`。

### **初始化**
创建指定大小的主哈希表`subMaps[0]`。

### **查询/插入/删除**
枚举所有`subMap`，在每个`AtomicHashArray`中进行无锁的开放寻址。

### **扩容**
锁住一个新的`subMap`，初始化它。

### **迭代器**
因为不存在数据迁移，所以迭代器不会失效。

### **总结**
类似 ConcurrentHashMap，AtomicHashMap 也以简单、安全为主：使用线性探测；创建新哈希表实现扩容；不真正删除对象保证指针有效；通过自旋锁占据一个槽 实现并发安全。
算法简单使代码易于实现，bug 更少，但保证了 大部分时间/多数场景下 依旧有很高的效率。
简单也允许代码在其它方面复杂，如多个模板参数、类型检查、线程本地缓存。





