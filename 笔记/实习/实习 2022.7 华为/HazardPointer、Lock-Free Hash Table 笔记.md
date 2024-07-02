# HazardPointer、Lock-Free Hash Table 笔记
Tags: 实习 2022.7 华为

------------
[TOC]

------------

## 内存管理

**无锁**<br>
称一个共享对象是无锁的（或非阻塞的，lock-free/nonblocking），当且仅当：在一个线程对该对象进行有限次操作的过程中，总会有至少另一个线程在这个对象上 离完成工作更进一步。即共享不会导致阻塞。<br>
与使用锁相比，无锁不会遇到死锁问题，且有更好的性能与鲁棒性，不管线程被怎么延迟。而锁会导致线程阻塞，进入内核态。

> 无等待(wait-free)是一个更强的条件，它表示所有线程最终都能执行成功，不管其它线程做了什么。
> CAS类的调用就不是wait-free的，因为wait-free的原语都不能包含内部循环，而CAS原语使用时通常包含在`while true`的循环内部。<br>
> 无锁(lock-free)仅意味着系统中总存在某个线程能够得以继续执行（虽然没锁，但某个线程的执行情况也受其它线程的影响）。<br>
> 无阻塞并发(obstruction-freedom)指在任何时间点，一个孤立运行线程的每一个操作可以在有限步之内结束。只要没有竞争，线程就可以持续运行。一旦共享数据被修改，obstruction-free 要求中止已经完成的部分操作，并进行回滚。它在不出现冲突性操作的情况下提供单线程式的执行进度保证。<br>
> （Obstruction-freedom is the weakest natural non-blocking progress guarantee. An algorithm is obstruction-free if at any point, a single thread executed in isolation (i.e., with all obstructing threads suspended) for a bounded number of steps will complete its operation.）
> 或者可能可以说，无阻塞中一个线程的失败或挂起不会引起其它线程的失败或挂起。
> 阻塞并发(blocking algorithms)是并发级别最低的同步算法，它一般需要产生阻塞。可以简单认为基于锁的实现是blocking的算法。

> 重新描述下：
> **阻塞**指一个线程进入临界区后，其它线程就必须在临界区外等待，也就是阻塞，直到临界区没有线程后，才可进入。但是持有锁的进程也可能被阻塞，导致所有进程饿死（死锁）。
> **无阻塞**类似乐观锁（但可能有锁），所有线程都可以进入临界区，然后一直尝试获取最新数据并计算，如果在提交前发现数据被更改，则会回滚重新进行。调用也可以立即返回，不会等待。
> **无锁**保证无论何时，至少有一个线程在工作（能够在有限时间内取得进展）。但它可能一直占用共享资源，导致有线程饿死。
> **无等待**不仅要求无锁，即任意时刻至少有一个线程在工作，还要求所有使用共享资源的线程都能在有限时间内完成操作。所以所有线程都会在有限时间内结束，没有线程会饿死。
> 后三种都是非阻塞的。
>
> 无锁的典型例子就是CAS循环。无阻塞应该类似，不过可以用锁。SMR是无等待的，但是why？
> 找不到更多例子。
>
> 还有一种更强的无等待：集居数无关无等待(Wait-Free-Population-Oblivious, WFPO)，不仅要无等待，还要性能与当前活动线程数无关。
> 一般的无等待的开销与线程数有关，一定范围内（很小）线程数的增加可提高效率，但后续增加不会，反而会使每个线程平均执行时间增加（总是在争取共享资源不工作）。
> 但对于WFPO算法，可以通过无限制的增加线程数来提高总体工作效率（线性增加）。
>
> 要求越强的算法越难实现，代价越大，但**可能**带来更高的收益。
> 但事实上没有多少无锁或无等待的算法，一篇文章说也没有完全WFPO的算法或数据结构。

在有锁的情况下，很容易保证线程不会访问一个被另一个线程删除（但还没被复用或重新分配）的对象。<br>
但这在无锁情况下很难，每个线程都可以在任意时刻任意次访问一个对象。如果一个线程$A$在对象$x$被删除前获取了对$x$的引用，则要么$x$变成了一个无效指针，要么$x$被其它线程复用，指向了其它对象，导致$A$对$x$的修改产生问题。$x$还可能被os回收，对$x$的访问将会导致内存访问错误。

一般的解决方式有三类：
1. 使用 IBM Tag（在写入位置的同时递增标签值）来阻止被随意回收。但需要`double-width instructions`（一次操作两个连续字的原子指令，如[`double-width compare-and-swap (DWCAS)`](https://en.wikipedia.org/wiki/Double_compare-and-swap)），64位处理器并不支持（32位通常支持，因为可以用来支持64位指令，但64位不需要去支持128位指令）。
2. 使用无锁引用计数，但很低效，且需要使用`unavailable strong multiaddress atomic primitives`来允许内存复用。
3. 使用`aggregate reference counters`，或每个线程都维护一个时间戳。但如果没有特定调度器支持，这两个方法也会阻塞，即一个线程的延迟或崩溃会 阻止`aggregate reference counter`降为0 或 阻止对象的时间戳更新，从而导致大量的对象在被删除后不会被真正删除（称为`retired nodes`），即大量的内存不能被复用。


------------
## Hazard Pointer (Safe Memory Reclamation)
> [Hazard Pointers: Safe Memory Reclamation for Lock-Free Objects](https://www.tsingfun.com/uploadfile/2022/0224/Hazard%20Pointers.pdf) （[链接2](https://citeseerx.ist.psu.edu/pdf/94746e049d8322489c0d3f9acfa732df67ae787a)）<br>
> （正确性证明只看了部分，性能测试基本没有看）<br>
> 其它：<br>
> https://sf-zhou.github.io/programming/hazard_pointer.html <br>
> 一个简单翻译：
> https://www.cnblogs.com/cobbliu/articles/8370734.html
>
> C++26：https://lancern.xyz/2023/07/05/hazard-pointers/

>[folly/Hazptr.h](https://github.com/facebook/folly/blob/main/folly/synchronization/Hazptr.h)：
>
>/// Hazard pointers is a safe reclamation method. It protects objects
>/// from being reclaimed while being accessed by one or more threads, but
>/// allows objects to be removed concurrently while being accessed.
>///
>/// What is a Hazard Pointer?
>/// A hazard pointer is a single-writer multi-reader pointer that can
>/// be owned by at most one thread at a time. To protect an object A
>/// from being reclaimed while in use, a thread X sets one of its
>/// owned hazard pointers, P, to the address of A. If P is set to &A
>/// before A is removed (i.e., it becomes unreachable) then A will not be
>/// reclaimed as long as P continues to hold the value &A.
>///
>/// Why use hazard pointers?
>/// - Speed and scalability.
>/// - Can be used while blocking.
>///
>/// When not to use hazard pointers?
>/// - When thread local data is not supported efficiently.
>///
>/// Alternative Safe Reclamation Methods
>/// - Locking (exclusive or shared):
>///   o Pros: simple to reason about.
>///   o Cons: serialization, high reader overhead, high contention, deadlock.
>///   o When to use: When speed and contention are not critical, and
>///     when deadlock avoidance is simple.
>/// - Reference counting (atomic shared_ptr):
>///   o Pros: automatic reclamation, thread-anonymous, independent of
>///     support for thread local data, immune to deadlock.
>///   o Cons: high reader (and writer) overhead, high reader (and
>///     writer) contention.
>///   o When to use: When thread local support is lacking and deadlock
>///     can be a problem, or automatic reclamation is needed.
>/// - Read-copy-update (RCU):
>///   o Pros: simple, fast, scalable.
>///   o Cons: sensitive to blocking
>///   o When to use: When speed and scalability are important and
>///     objects do not need to be protected while blocking.
>///
>/// Hazard Pointers vs RCU
>/// - The differences between hazard pointers and RCU boil down to
>///   that hazard pointers protect specific objects, whereas RCU
>///   sections protect all protectable objects.
>/// - Both have comparably low overheads for protection (i.e. reading
>///   or traversal) in the order of low nanoseconds.
>/// - Both support effectively perfect scalability of object
>///   protection by read-only operations (barring other factors).
>/// - Both rely on thread local data for performance.
>/// - Hazard pointers can protect objects while blocking
>///   indefinitely. Hazard pointers only prevent the reclamation of
>///   the objects they are protecting.
>/// - RCU sections do not allow indefinite blocking, because RCU
>///   prevents the reclamation of all protectable objects, which
>///   otherwise would lead to deadlock and/or running out of memory.
>/// - Hazard pointers can support end-to-end lock-free operations,
>///   including updates (provided lock-free allocator), regardless of
>///   thread delays and scheduling constraints.
>/// - RCU can support wait-free read operations, but reclamation of
>///   unbounded objects can be delayed for as long as a single thread
>///   is delayed.
>/// - The number of unreclaimed objects is bounded when protected by
>///   hazard pointers, but is unbounded when protected by RCU.
>/// - RCU is simpler to use than hazard pointers (except for the
>///   blocking and deadlock issues mentioned above). Hazard pointers
>///   need to identify protected objects, whereas RCU does not need to
>///   because it protects all protectable objects.
>/// - Both can protect linked structures. Hazard pointers needs
>///   additional link counting with low or moderate overhead for
>///   update operations, and no overhead for readers. RCU protects
>///   linked structures automatically, because it implicitly protects
>///   all protectable objects.
>///
>/// Differences from the Standard Proposal
>/// - The latest standard proposal is in wg21.link/p1121. The
>///   substance of the proposal was frozen around October 2017, but
>///   there were subsequent API changes based on committee feadback.
>/// - The main differences are:
>///   o This library uses an extra atomic template parameter for
>///     testing and debugging.
>///   o This library does not support a custom polymorphic allocator
>///     (C++17) parameter for the hazptr_domain constructor, until
>///     such support becomes widely available.
>///   o hazptr_array and hazptr_local are not part of the standard
>///     proposal.
>///   o Link counting support and protection of linked structures is
>///     not part of the current standard proposal.
>///   o The standard proposal does not include cohorts and the
>///     associated synchronous reclamation capabilities.

### 介绍

SMR 可以对无锁对象进行内存复用，且 SMR 高效，保证一个要删除的节点 到 真正被删除（可以回收）所需的时间平均/均摊下来是一个常量。所以删除但不能被回收的对象数量 始终不会超过一个上界。<br>
SMR 也不需要`double-width or strong multiaddress`的原子指令，只有单字的读和写。<br>
SMR 不会有线程等待并饿死（非阻塞且wait-free），线程总会是活跃的，不需要休眠和唤醒。<br>
SMR 允许内存被os回收，不需要内核或调度器提供特定支持。

> SMR 的性能依赖于平台上线程本地存储（TLS）的性能。单纯使用 CAS 更新全局的对象链表和退休列表的性能太低，可以使用 TLS 做为缓冲层，这样大部分时间都是更新本线程的数据。这部分可以参考 Folly 中的`ThreadLocalPtr`。

以下来自 folly `Hazptr.h`：
```
/// Hazard pointers is a safe reclamation method. It protects objects
/// from being reclaimed while being accessed by one or more threads, but
/// allows objects to be removed concurrently while being accessed.
///
/// What is a Hazard Pointer?
/// -------------------------
/// A hazard pointer is a single-writer multi-reader pointer that can
/// be owned by at most one thread at a time. To protect an object A
/// from being reclaimed while in use, a thread X sets one of its
/// owned hazard pointers, P, to the address of A. If P is set to &A
/// before A is removed (i.e., it becomes unreachable) then A will not be
/// reclaimed as long as P continues to hold the value &A.
///
/// Why use hazard pointers?
/// ------------------------
/// - Speed and scalability.
/// - Can be used while blocking.
///
/// When not to use hazard pointers?
/// --------------------------------
/// - When thread local data is not supported efficiently.
///
```

### 定义
**计算模型**
假设所有线程通过共享内存通信，共享对象存储在一系列共享的内存位置处。<br>
线程不能注意到其它线程是活跃的、被延迟的、还是被销毁的。

**原子原语**
除了原子读和原子写，还需要其它对共享对象进行操作的 原子原语：

**Compare and Swap(CAS):**<br>

```
CAS(addr; exp; new)
{
	if (*addr != exp)
		return false;
	*addr <- new;
	return true;
}
```

常见的用法是，exp就是addr的旧值，new是addr的新值，当addr与旧值相等时，将其改为新值。
这种用法是ABA的一个原因，见下ABA Problem。

**TAS(test and set)**<br>
当给定地址处的值为false时，将其设为true。返回其原本的值。<br>
即：
$$TAS(addr) \equiv \neg CAS(addr, false, true)$$

**the pair LL/SC(load-linked/store-conditional):**<br>
LL：返回给定地址处的值。<br>
SC：若自从上次该线程读取该地址（调用LL）到现在，没有任何线程写过该地址，则将该地址处的值赋一个新值，返回true；否则写失败，返回false。

**validete(VL)**<br>
返回自从上次该线程调用该地址的LL到现在，是否有任何线程写过该地址。

出于实际架构原因，没有任何支持LL/SC的架构支持VL和上述真正意义上的LL/SC。<br>
现在的架构都不允许嵌套或穿插使用LL/SC，且只支持弱化/受限制的LL/SC：只要对某地址进行过访问（不只是写，包括读），该地址的SC就会失败（但不会经常发生？）。

使用受限制的(restricted)LL/SC，可以这样实现CAS：<br>
```
while true
{
	if LL(addr) != exp return false;
	if SC(addr, new) return true;
}
```

大多数架构要么支持一个字的CAS，要么支持一个字的受限制LL/SC。<br>
如前所说，只有大部分32位处理器支持双字上的CAS或LL/SC，64位不支持。

**DCAS**
DCAS 是比 CAS 更强的原子指令或操作，表示原子地执行如下语句：
```
DCAS(addr1; exp1; new1; addr2; exp2; new2)
{
	if (*addr1 != exp1 || *addr2 != exp2)
		return false;
	*addr1 <- new1;
	*addr2 <- new2;
	return true;
}
```

### ABA Problem
> https://en.wikipedia.org/wiki/ABA_problem

在多线程环境中，某个地址可能被一个线程连续重复读取两次，只要第一次读取的值和第二次读取的值一样，那么这个线程就会认为这个变量在两次读取时间间隔内没有发生任何变化。
在单线程环境下，这是正确的，在多线程环境下则不对。

线程1首先读出某个共享对象的值为A，然后因为某个原因挂起（网络延迟，时间片分配，中断等）；然后线程2将该对象的值改为B，然后再改为A（也可能由线程3进行）；线程1继续执行，读取对象的值发现仍为A，所以认为该对象没有被修改过（依据值没有发生改变）。
这显然不对，线程1会认为什么都没发生，忽略线程2在两次修改间做的任何事情。

产生ABA有3个必需条件（所以可能比较少见，产生ABA也不是CAS的问题）：

1. 程序以内存处的值是否变化，作为该变量是否发生变化的唯一依据。
2. 重复读取的变量会被多线程共享，且存在“值回退”的可能（值变化后有可能因为某个操作复归原值）。
3. 在多次读取间隔中，开发者没有采取有效的同步手段，比如上锁。

> ABA 问题的例子：
> 常常这么使用CAS操作：读取某个位置的值old，它一般是一个对象的指针，利用该指针指向对象的信息执行某些操作、计算出一个新值new，如果那个位置的值依然是old，则认为这个位置的值没有变过，依然指向原对象，将其赋为new。
> ~~但即使这个位置的对象没变，它的信息也可能发生更改？~~（但这好像不重要？）
> 如果这个位置是一个对象的地址，在对象被释放后，这个地址可能被分配给新的对象；如果新的对象在线程阻塞过程中，又被调整到这个位置，会导致这个位置保存的指针没变，但对象变了。
>
> 常见的单向链表实现栈的例子：
>
> ````
> pop()
> {
>         do{
>               ptr = top;            // ptr = top = NodeA
>               next_ptr = top->next; // next_ptr = NodeX
>         } while(CAS(top, ptr, next_ptr) != true);
>         return ptr; // pop 后通常会释放该节点内存
> }
> ````
>
> 如果在获取`next_ptr`后，线程挂起；其它线程弹出该栈顶，释放内存，然后push了一个内存地址刚好与`ptr`相同的新对象。在线程恢复后，CAS的`*top==ptr`依然返回true。
>
> 但是如果ptr的对象没有释放，且其它线程之后又把ptr放入了栈，也会有比较成立？这时就没有内存复用的问题了，不知道算不算ABA问题？（比较依据不合理）

> 所以一个说法是（有争议），问题出在不正确的内存复用上，旧对象的地址被阻塞线程引用，不能被回收复用。
> 解决方法：用`DCAS`（同时判断一个递增的时间戳或序列号，消除值回退的可能）；对对象引用计数，避免错误的回收；用Hazard Pointer保护该指针。
> （但 [DCAS 不是解决 ABA 的一劳永逸的方案(Silver Bullet)](http://people.csail.mit.edu/shanir/publications/DCAS.pdf)？）
>
> 用GC（自动垃圾回收），而非手动释放内存，通常可避免该问题。
> （但论文说，GC不能完全解决ABA问题，没看懂）
>
> 也有的说法是，CAS本身就不该这么用，与内存复用无关：CAS可以实现自旋锁，但别的线程却可以解开（结束）这个锁，锁保护不了临界区的资源不被修改。

> 关于ABA有另一种说法：有些业务可能不需要关心中间过程，只要前后值一样就行。但有些业务要求变量在中间过程不能被修改。
> 但找不到合理的例子，基本有方法轻松解决。
>
> 一个例子（这个例子我认为不对，争论也很多）：
> 银行系统用CAS指令控制金额变化。
> A有100元，想给B转100元，于是在1号ATM进行转账操作。在1号ATM读取到余额为100后、执行CAS(余额, 100, 0)之前，由于网络问题卡住。
> A于是去2号ATM进行同样操作，然后操作成功。这时C给A转账100，操作成功，所以A的余额仍为100。
> 之后1号ATM恢复正常，然后CAS(余额, 100, 0)又执行成功，又进行了一次转账。
>
> 但有些问题：
> ATM应该明确告诉用户，在问题被修复后是否会继续操作，让用户知道应该等待结果，如果重试可能会多次转账。也可以出问题就结束，让用户重试。
> 这个转账是一个独立的事务，不只修改，读取旧值和修改的过程，都应该原子完成。但这种情况下，1号ATM事务延迟会导致2号也无法完成？

ABA 问题是必须要被解决的。<br>
GC 通常能阻止这个问题发生（但不是一定）。<br>
SMR 阻止 ABA 发生的能力与 GC 一样强，即如果某个无锁算法在 GC 下是 ABA-safe 的（不会发生 ABA），则使用 SMR、不使用 GC 也是 ABA-safe 的。

### 算法整体过程
冒险指针（Hazard Pointer, HP）是一个`single-writer multi-reader`的指针，保护线程正在使用的共享变量不被其它线程回收，同时允许不被任何线程使用的变量被自动释放。

线程共享的主要结构是一个 冒险指针记录的链表（the list of hazard pointer (HP) records）。冒险指针记录（以下记作 HPRec）是链表的一个元素，包含$K$个冒险指针（以下记作 HP）和链表使用的`next`。<br>
每个正在使用共享变量的线程都拥有一个 HPRec，通过链表动态分配。设这样的线程有$N$个，每个线程有$K$个 HP，则 HP 的数量为$H=NK$个。$K$为线程会同时使用的共享变量个数，一般不会很大，比如只有2个。<br>
每个线程拥有私有变量`rlist`（`retired node list`，保存`retired`但还没`deleted`的对象）和`rcount`（`rlist`的对象数量）。<br>
每次（逻辑）删除一个节点，线程就将其放入自己的`rlist`。当`rcount >= R`时，线程执行`Scan`。
`Scan`通过两次扫描，将`rlist`中与所有线程的任何 HP 都不相等的`retired node`彻底删除（回收）。<br>
`Scan`第一次扫描`HPRec`链表，将所有 HP 的值存入临时哈希表`plist`。第二次扫描`rlist`，检查每个`retired node`，如果没在`plist`中出现，就回收；否则仍留在`rlist`中。<br>
$R$要取$R=H+\Omega(H)$（大于等于H，足够多），才能保证每个`retired node`（被逻辑删除但没实际删除的对象，不可被复用）~~不被删除的时间（空间被浪费的时间）~~被删除所需的时间（包括Scan与回收，Scan是O(H)的），平均情况下均摊下来是个常量（大概是这么翻译，原文：`in order to achieve a constant expected amortized processing time per retired node`）。<br>

> 这里看起来可能出问题：因为`Scan`不是原子的，会不会某个`retired node` `x`在第一次扫描中不等于某个 HP，但第二次扫描前被赋给某个 HP？<br>
> 论文 3.4 Lemma1 就给了证明，保证了：如果在`x`被`retire`后的某一时刻，没有任何 HP 指向`x`，则之后也不会再有 HP 去指向`x`。
> 也就是被逻辑删除(retire)的节点，在释放前一定不会再被使用，所以不会被赋给某个线程或HP。

`Scan`可根据情况调整：`plist`使用哈希，复杂度有时可能不可保证，可以换平衡树，保证$O(\log p)$的插入、查询；或者第一次扫描完后可以给`plist`排序，在查询时二分。

------------
SMR 是 wait-free 的。平均情况下每次花费$O(R)$的时间（使用平衡树则为$O(R\log p)$），就可回收$\theta(R)$个`retired nodes`。<br>
SMR 只需要单字原子指令，保证了未被回收的`retired nodes`不会超过$NR$个（即使有线程延迟或崩溃）。

### 算法扩展
`HPRec`使用链表，可方便地动态分配：在`HPRec`中加一个`active`字段，当有线程需要使用 HP、要获取 HPRec 时，选择一个`active`为false的`HPRec`（可以使用 TAS 指令）（如果没有则新建）；线程结束或不需要 HP 时，将`active`设为false。<br>
此外，当一个线程结束时，其`rlist`可能不为空。将`active`设为false，可允许其它线程替它回收它的`rlist`：线程在`Scan`完后，执行`HelpScan`，扫描是否有`active`为false的`HPRec`，如果有，则将其`rlist`中的对象全插到自己的`rlist`中，然后可以清空那个`rlist`。


------------
## Lock-Free List
> [High Performance Dynamic Lock-Free Hash Tables and List-Based Sets](https://citeseerx.ist.psu.edu/pdf/fb47306b9007a2a901f7214e2a9b2005f20ed4b7)

### 介绍
该算法（指上面论文中的，下同）是第一个基于 CAS 和无锁链表、与简单高效的无锁内存管理方法兼容的 无锁哈希。它只需要 CAS 或 restricted LL/SC，但效率比（当时）其它无锁算法要高许多。

算法实现了一个有序的无锁链表，然后在哈希数组的每个位置上保存一个该链表，用链式哈希。<br>
因为本质只是修改了链表，哈希算法没变，所以想扩容只能进行迁移。

该无锁链表是线性一致的（linearizable），即所有操作在进行到某一点（linearization point）时，可视作已被原子的完成。

### 算法整体过程

链表主要使用结构`NodeType`，分别记录：该节点的数据；该对象是否已被（逻辑）删除（但未回收）；指向`next`的指针；Tag（递增的序列号）。

```
structure NodeType {
	Key: KeyType;
	<Mark,Next,Tag> : <boolean, *NodeType, TagType>;
}
// 链表头部，即哈希数组直接指向的
structure MarkPtrType {
	<Mark,Next,Tag> : <boolean, *NodeType, TagType>;
}
// 哈希数组
MarkPtrType *T[M];
```

无锁算法的一般问题有：

- 访问一个已被回收的节点导致出错（访问无效内存）
- 删除/回收一个正在使用的节点导致出错
- ABA 问题
- 仅使用 CAS/restricted LL/SC 完成

该算法的解决方式分别是（**算法核心**）：

- 每次使用一个节点的数据前，会检查它是否被删除（`mark`是否为1），如果不是，则继续遍历；如果是，去 CAS 更新 pre 节点（`CAS(prev, <0,cur,ptag>, <0,next,ptag+1>)`）尝试真正删除并回收，如果 CAS 成功则继续，如果失败了要try again（pre 的`tag`发生了改变，则连链表结构变化，或该节点已被其它线程删除）。
  可以发现，当`mark`为1时，我们不会访问当前节点的数据，所以即使当前节点被回收，也不会访问无效内存（`mark`值是之前节点存在时就赋的）。
- （应该是通过tag保证，可用HP）
  会通过`mark`位标记节点是否删除，~~`Delete`并不会立刻回收节点。所以可避免回收正在使用的点。~~
  程序可以访问一个被删除但未被回收的节点，且当前线程会尝试去回收它，如果发现已回收则try again（某个节点只会被一个线程回收）。
- 每次更新节点时，CAS 检查其`tag`，若被修改，则节点发生了改变，try again；否则 CAS 修改其`tag`。
- `mark`只需要一位，可使用`next`的一位记录，所以`mark, next`只需要一个字；使用 Hazard Pointer 作为内存管理方式，可避免 ABA 问题和删除正在使用的节点，从而可不使用`tag`。所以所有的原子操作只需操作一个字，CAS 即可解决。

实际的实现中，可以用 HP 保存节点指针，不用`tag`字段，使操作能用 CAS 完成（也能避免 ABA）。
每个线程只需要使用3个HP，就可保证所有正在访问的节点不被回收。

所有共享数据（链表元素）的更改都要通过 CAS 完成。

该算法是线性一致的，也就是对（所有情况/返回结果的）所有操作，存在一个线性化点，在线性化点前，操作未执行；线性化点后，操作执行成功，对所有线程可见。
证明要涉及很多情况（不怎么记得了）。


------------
## Split-Ordered Lists

> [Split-Ordered Lists: Lock-Free Extensible Hash Tables](https://ldhulipala.github.io/readings/split_ordered_lists.pdf)

### 介绍
该算法基于上述 Michael 提出的有序无锁链表，但可进行均摊$O(1)$复杂度的2倍扩容。

### 算法整体过程
一般的扩容是将旧节点插入到新桶指针指向的位置，而该算法将新桶指针插入到旧的节点链表中：<br>
所有节点（regular nodes）和桶指针（作为dummy nodes）通过一个有序无锁链表连接，顺序为按节点的 split-ordering key 从小到大排序。<br>
排序后，常规节点往前遇到的第一个桶指针，即为它所在的桶。

常规节点的 split-ordering key 定义为 将原本 key 的二进制表示翻转后或`1`的值（也即先或`0x8000..`再翻转）；桶指针节点的 split-ordering key 定义为 将桶的编号`0,1,2,..`的二进制表示翻转后的值。<br>
翻转后的最低位 1 用来区分常规节点与桶指针。<br>

```cpp
so_key_t so_regularkey(key_t key) {
	return REVERSE(key OR 0x8000..);
}
so_key_t so_dummykey(key_t key) {
	return REVERSE(key);
}
```

桶的数量总是2的$k$次幂($k\in Z$)。<br>
易知在桶$x$中的所有节点，都满足：其 so key 的高$k$位与$x$的 so key 的高$k$位相同（或者说原本 key 的低$k$位相同）。

**扩容**<br>
设当前容量为$2^k$，要扩为$2^{k+1}$。<br>
对于在桶$x\ (0\leq x\lt 2^k)$中的每个节点（高$k$位相同），根据 so key 的第$k+1$位为0还是1 将其划分到两个桶：桶$x$和桶$x+2^k$。<br>
此时只需要插入一个值为$x+2^k$的桶指针节点到对应位置，即可完成划分。<br>
易知所有桶仍满足 so key 的高$k+1$位相同。

哈希表的扩容就是增加桶的数量、减少每个桶中的元素数量。

**初始化桶**<br>
在扩容时，并不立刻进行加入$2^k$个新桶节点。<br>
因为节点通过`key % count_of_buckets`决定在哪个桶，所以只需在要访问新桶时初始化新桶（发现该桶为 null，遍历它的 parent 桶在对应位置加入新桶节点），分摊扩容时的复杂度。<br>
这样令`count_of_buckets *= 2`（原子的），扩容就完成了。

但这样在初始化新桶时，该新桶上一层的桶可能也未被初始化。此时需先递归初始化上一层的桶。（称每次扩容新建的桶为下一层的桶）

定义$a\lt b$为$a$的 key 小于$b$（桶的 key 即为桶编号），$a\prec b$为$a$的 so key 小于 $b$。<br>
定义一个桶$x$的 parent 为$y$，当且仅当$y$为$x$上一层的桶，且$y$是上一层桶中满足$y\prec x$的 so 序最大的桶。<br>
易知$x$的 parent 为$x$的 so key 去掉最低位的 1。即`x^lowbit(x)`（这种结构本身就和树状数组一致）。或者是$x$的桶编号去掉最高位的 1。<br>
所以有：

$$\forall k, (k\text{ is bucket}\land k\prec x)\to (k=parent\ \lor\ k\prec parent) \\ parent\lt x \\ parent \prec x$$

为保证能初始化所有所需的桶，且不发生重复/循环初始化，每次初始化$x$时，检查$x$的 parent 是否已被初始化，如果没，递归初始化 parent。<br>
该操作的复杂度可能达到$O(\log buckets)$。但只要哈希或 key 随机，很难发生这种情况。

此外在初始化时，另一个线程可能刚好完成初始化。<br>
因为初始化就是插入一个 dummy node，插入也是原子的，所以如果插入时发现已有该节点，直接返回即可（以及 free 刚刚分配的节点）。

**插入**<br>
用`key % count_of_buckets`获得桶编号，检查桶是否为空（为空则初始化），调用链表插入 插入新的节点即可。<br>
如果发现节点已插入，要 free 新的节点。<br>
如果需要扩容（`nodes / buckets > load_factor`），CAS 设置`buckets *= 2`即可。

**删除/查询**<br>
获得桶编号，检查桶是否为空，调用链表删除/查询。<br>

### 更现实的扩容
上面的扩容中，假设了可直接在`bucket`数组后进行成倍扩容，所以可直接通过`T[bucket]`访问该桶。但现实中很难分配这样连续的空间。<br>
实际的扩容为：每次分配数个`bucket`数组（每个为一段空间）。使用 ST (Segment Table) 找到某个桶所在的数组（段）。

例：
```cpp
typedef MarkPtrType[SEGMENT_SIZE] segment_t;
segment_t ST[ ];

MarkPtrType *get_bucket(uint bucket) {
	segment = bucket / SEGMENT_SIZE;
	if (ST[segment] == NULL)
		return UNINITIALIZED;
	return &ST[segment][bucket % SEGMENT_SIZE];
}

MarkPtrType *set_bucket(uint bucket, NodeType *head) {
	segment = bucket / SEGMENT_SIZE;
	if (ST[segment] == NULL) {
		new_segment = new segment_t;
		new_segment[0..SEGMENT_SIZE-1] = UNINITIALIZED;
		if (!CAS(&ST[segment], NULL, new_segment))
			free(new_segment);
	}
	ST[segment][bucket % SEGMENT_SIZE] = head;
}
```

多次扩容后（或最开始就这样分配），ST 会类似一个多级页表，每次操作都需$O(\log n)$的时间通过各级 ST 表找到最底层的桶表，再找到桶地址。<br>
但实际上，4 层的 ST 表就可覆盖 64 位机器的所有内存空间，所以这个层数是无需考虑的。


------------
## HazardPointer 实现
> https://github.com/bhhbazinga/HazardPointer <br>
> 主要分析上面这个的实现

### 目标
实现一个`HazardPointer`类。<br>
当创建 HP 或给它赋一个指针后，要确保该指针不会被回收；当执行删除一个 HP 指向的指针对象时，不能立刻回收，而是要定期（如当未回收指针数大于$R$时）回收 不被任何 HP 指向的 指针。<br>
当 HP 析构时，也执行上述的删除指针对象；该全局内存回收器析构时，等待，直到回收完所有对象。<br>

### 实现
**HazardPointer**<br>
只供外部直接使用的 HP。主要包含以下字段/函数：

`HazardPointer(Reclaimer* reclaimer, void* ptr)`：构造函数。要指定线程使用的（全局的）内存回收器，以及指向的对象。

`~HazardPointer()`：析构函数。调用`UnMark()`。

`UnMark()`：告诉回收器该指针对象被删除，即调用`reclaimer->UnMarkHazard(index)`。<br>
由于 HP 赋值时不会调用`UnMark()`，所以给 HP 赋新值前要手动调用`UnMark()`。

`index`：所有的 HP 使用`vector`管理，通过`index`可快速访问该 HP。

**Reclaimer**<br>
`Reclaimer`为线程本地的内存回收器，但共享全局的`global_hp_list_`。包含以下字段/函数/结构：

**分配/创建 HP**<br>
`InternalHazardPointer`：`Reclaimer`内部使用的 HP，为一个链表节点，维护`ptr`（保存的指针）、`next`、`flag`（是否正在被使用，为false则可被复用）。

`hp_list_`：线程本地的所有`InternalHazardPointer`，用来管理、分配 HP。

`global_hp_list_`：全局（所有线程）的所有`InternalHazardPointer`（包含`flag=false`、等待其它线程复用的 HP），用来快速遍历所有 HP。

`HPIndex MarkHazard(void* ptr)`：创建指向 ptr 的 HP。首先在`hp_list_`中找是否有未被使用的 HP（指向null），没有则用`TryAcquireHazardPointer()`获取一个新的 HP。

`HPIndex TryAcquireHazardPointer()`：创建一个新的 HP。首先在`global_hp_list_`中找是否有`flag`为false的 HP，没有则新建 HP，加入到`hp_list_`和`global_hp_list_`中。

> 这里`flag`的意义和论文中不太一样。<br>
> 论文中的`flag/active`是 HPRec 记录的，用于在线程退出时，允许其它线程获取、帮助释放它目前不能释放的 HP（`HelpScan`），线程无需等待所有 HP 被释放。<br>
> 而此处 HP 的`flag`只是单纯能复用其它线程结束后不用的 HP 结构，而不能帮助其它线程释放 HP（没实现`HelpScan`），所以感觉意义不大？

**更新 HP**<br>
在创建 HP，即调用`MarkHazard()`时，会返回`HPIndex`帮助外部 HP 快速获取它对应的内部的 HP。

`void* GetHazardPtr(HPIndex index)`：获取`HPIndex`对应的 HP，即`hp_list_[index]->ptr.load(std::memory_order_relaxed)`。

`void UnMarkHazard(HPIndex index)`：删除该 HP 对某指针的引用，也表示该 HP 不再被使用。只需将`hp_list_[index]->ptr`设为null。

**回收**<br>
`ReclaimNode`：保存一个被逻辑删除、等待被回收的指针。保存`ptr`（被删除的指针）、`next`、`delete_func`（真正被删除/被回收时的回调函数）。<br>
`ReclaimPool`：`ReclaimNode`的对象池。

`std::unordered_map<void*, ReclaimNode*> reclaim_map_`：保存所有`ReclaimNode`，用于遍历。<br>
~~事实上也用一个链表即可，没有用到`map`的功能~~ 用`map`可避免里面有太多重复指针。

`void ReclaimLater(void* const ptr, std::function<void(void*)>&& func)`：逻辑删除一个指针；当该指针不被任何 HP 引用时，回收它（实际为调用该`func`）。<br>
函数创建一个`ReclaimNode`，加入到`reclaim_map_`中。

`void ReclaimNoHazardPointer()`：检查一次 是否有可回收的节点并回收。<br>
首先遍历`global_hp_list_`，将 HP 的引用保存到`std::unordered_set<void*>`中。然后遍历`reclaim_map_`，若某元素不在 set 中，回收。<br>
只有在满足条件$\frac{\text{待回收节点数}}{\text{当前 HP 数量}}\geq 4$（`reclaim_map_.size() < kCoefficient * global_hp_list_.get_size()`）时，才会进行检查回收。

**析构**<br>
`bool Hazard(void* const ptr)`：判断一个指针是否被某个 HP 引用。遍历`global_hp_list_`即可。

`~Reclaimer()`：析构。线程退出时，析构自己的`Reclaimer`。<br>
函数将自己`hp_list_`中的所有 HP 的 flag 设为false，即允许其它线程复用；然后扫描`reclaim_map_`，依次删除所有待回收节点（如果此时不能删除，需等待）：<br>
```cpp
for (auto it = reclaim_map_.begin(); it != reclaim_map_.end();) {
	// Wait until pointer is no hazard
	while (Hazard(it->first)) {
		std::this_thread::yield();
	}

	ReclaimNode* node = it->second;
	node->delete_func(node->ptr);
	delete node;
	it = reclaim_map_.erase(it);
}
```

> 如上所说，没有用论文提到的`HelpScan`，线程退出时必须等待它的所有对象不被任何线程引用，然后亲自回收它们。


------------
## Lock-Free Hash Table 实现
> https://github.com/bhhbazinga/LockFreeHashTable <br>
> 主要分析上面这个的实现

### 介绍
实现同 Split-Ordered Lists，使用上面的有序无锁链表和 HazardPointer，允许无锁进行增删改查和均摊常数复杂度的2倍扩容。

### 实现
**Reclaimer**<br>
`class TableReclaimer : public Reclaimer`：保存一个`Reclaimer`单例，即当前线程本地使用的`Reclaimer`，用于定义和回收 HazardPointer。

**最大容量及LoadFactor**<br>
```cpp
// The maximum bucket size equals to kSegmentSize^kMaxLevel. Here the
// maximum bucket size is 64^4. If the load factor is 0.5, the maximum number of
// items that Hash Table contains is 64^4 * 0.5 = 2^23. You can adjust the
// following two values according to your memory size.
const int kMaxLevel = 4;
const int kSegmentSize = 64;
const size_t kMaxBucketSize = pow(kSegmentSize, kMaxLevel);

const float kLoadFactor = 0.5;
```

**LockFreeHashTable**<br>
`LockFreeHashTable()`：构造函数，初始化：<br>
`power_of_2_ = 1`：扩容了多少次，即$2^{\text{powerOf2}}$为表的最大容量。<br>
`size_ = 0`：当前表中的元素个数。<br>
`hash_func_ = std::hash<K>()`：将`key`映射到桶的哈希函数。<br>

新建第0个桶和`DummyNode* head`。`head`既是桶0的起始节点，也是所有节点/整个大链表的起始节点。

Segment Table 一共有`kMaxLevel`层，字段`segments[kSegmentSize]`保存最顶层的段。<br>
段最初都是未初始化/未分配的。找到第0个桶需要新建每一层的`segments[0]`，在最底层的`segments[0]`新建一个桶：
```cpp
LockFreeHashTable() : power_of_2_(1), size_(0), hash_func_(Hash()) {
	// Initialize first bucket
	int level = 1;
	Segment* segments = segments_;	// Point to current segment.
	while (++level < kMaxLevel) {
		Segment* sub_segments = NewSegments(level);
		segments[0].data.store(sub_segments, std::memory_order_release);
		segments = sub_segments;
	}

	Bucket* buckets = NewBuckets();
	segments[0].data.store(buckets, std::memory_order_release);

	DummyNode* head = new DummyNode(0);
	buckets[0].store(head, std::memory_order_release);
	head_ = head;
}
```

`~LockFreeHashTable()`：析构。通过`head`遍历所有节点，全部删除。

`Segment* NewSegments(int level)`：分配并简单初始化一个新段，包含`kSegmentSize`个子段或buckets。<br>
`Bucket* NewBuckets()`：分配并简单初始化一个新Buckets，包含`kSegmentSize`个桶。<br>
```cpp
Segment* NewSegments(int level) {
	Segment* segments = new Segment[kSegmentSize];
	for (int i = 0; i < kSegmentSize; ++i) {
		segments[i].level = level;
		segments[i].data.store(nullptr, std::memory_order_release);
	}
	return segments;
}

Bucket* NewBuckets() {
	Bucket* buckets = new Bucket[kSegmentSize];
	for (int i = 0; i < kSegmentSize; ++i) {
		buckets[i].store(nullptr, std::memory_order_release);
	}
	return buckets;
}
```

`DummyNode* GetBucketHeadByIndex(BucketIndex bucket_index)`：根据桶编号，获得桶的指针`head`。<br>
从最顶层的`segments`逐级找。注意遇到 null 时表示该桶不存在。<br>
```cpp
template <typename K, typename V, typename Hash>
typename LockFreeHashTable<K, V, Hash>::DummyNode*
LockFreeHashTable<K, V, Hash>::GetBucketHeadByIndex(BucketIndex bucket_index) {
	int level = 1;
	const Segment* segments = segments_;
	while (++level < kMaxLevel) {
		segments =
				segments[(bucket_index / static_cast<SegmentIndex>(pow(kSegmentSize, kMaxLevel - level + 1))) % kSegmentSize]
						.get_sub_segments();
		if (nullptr == segments) return nullptr;
	}

	Bucket* buckets =
			segments[(bucket_index / kSegmentSize) % kSegmentSize].get_sub_buckets();
	if (nullptr == buckets) return nullptr;

	Bucket& bucket = buckets[bucket_index % kSegmentSize];
	return bucket.load(std::memory_order_consume);
}
```

`DummyNode* GetBucketHeadByHash(HashKey hash)`：由 key 的哈希值获取桶。即调用`GetBucketHeadByIndex(hash & (bucket_size() - 1))`。<br>
因为几乎所有获取桶的操作都是通过`GetBucketHeadByHash`，所以在`GetBucketHeadByHash`里检查桶是否被初始化：<br>
```cpp
DummyNode* GetBucketHeadByHash(HashKey hash) {
	BucketIndex bucket_index = (hash & (bucket_size() - 1));
	DummyNode* head = GetBucketHeadByIndex(bucket_index);
	if (nullptr == head) {
		head = InitializeBucket(bucket_index);
	}
	return head;
}
```

**初始化桶**<br>
`BucketIndex GetBucketParent(BucketIndex bucket_index)`：获取桶的 parent。结果可以用`index ^ lowbit(index)`，也可以用`__builtin_clzl(index)`得到。

`DummyNode* InitializeBucket(BucketIndex bucket_index)`：初始化一个桶。<br>
首先通过`GetBucketParent()`获取 parent，检查其是否被初始化，没有则先进行递归。<br>
然后找到桶，这与`GetBucketHeadByIndex()`步骤相同，但在遇到 null 时要进行初始化（`NewSegments`、`NewBuckets`或`NewDummyNode`）。<br>
注意如果初始化失败（另一个线程此时完成了初始化），要回收当前分配的空间，使用已初始化的。

**查询**<br>
`bool SearchNode(DummyNode* head, Node* search_node, Node** prev_ptr, Node** cur_ptr, HazardPointer& prev_hp, HazardPointer& cur_hp)`：查找桶`head`中第一个大于等于`search_node`的节点位置和前驱。<br>
与无锁链表论文中的实现基本相同。<br>
要注意：

- 遍历到的节点要存为 HP：`cur_hp = HazardPointer(&reclaimer, cur)`。
- 给 HP 赋值前，先调用`UnMark()`。
- 删除节点要使用`reclaimer.ReclaimLater(cur, OnDeleteNode)`。
- 由于用了指针的一位作为删除标记`mark`，获取指针时要注意忽略该位，如：`cur = get_unmarked_reference(next)`。
- 由于上一条中`cur`已忽略了`mark`位，所以判断当前节点是否被删除，可使用`next`的`mark`位即`is_marked_reference(cur->get_next())`。
- 交换 HP 要使用`std::move`。
- 因为 HP 每次赋值，都要获取、分配新的 HP，所以不懂两个 HP 通过参数传入的意义？

**插入/修改节点**<br>
`bool InsertRegularNode(DummyNode* head, RegularNode* new_node)`：插入节点。当该 key 对应的节点已存在时，更新 value。<br>
实现与论文相同（除了论文不会更新 value）。<br>
若插入成功，检查是否需扩容：$\frac{2^{\text{power}}}{size}\geq kLoadFactor$。

`bool InsertDummyNode(DummyNode* head, DummyNode* new_node, DummyNode** real_head)`：插入假节点（桶指针）。当该节点已存在时，将该节点存为`real_head`。<br>
实现与上个函数相同，只是不影响`size`和扩容。

**删除节点**<br>
`bool DeleteNode(DummyNode* head, Node* delete_node)`：删除节点。<br>
实现与论文基本相同。



