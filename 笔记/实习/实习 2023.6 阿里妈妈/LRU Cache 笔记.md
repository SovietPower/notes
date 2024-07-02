# LRU Cache 笔记

Tags: 实习

---

**总结**

Rocksdb LRU Cache

- 引用计数、分段加锁。
- 允许为数据设置优先级。这与 Rocksdb 的数据特性有关（一个 SSTable 包含三种块：data block, index block, filter block）。
- 可以根据数据访问次数自动调整它的优先级。

Rocksdb Clock Cache

- 开放寻址，特殊的探测方式。
- cache 策略为第二次机会算法。所有内存块会放到开放寻址使用的数组中，组织成一个环。每个未被引用的、可驱逐的内存块会记录一个 counter。cache 会维护一个指针，在需要驱逐内存块的时候环形遍历这个数组，每遍历到一个内存块，检查它的 counter 是否为0，如果是就驱逐，如果不是就减1 继续遍历。
    所以 counter 就表现了一个数据块的优先级，counter 更大的、也就是优先级更大的内存块，它肯定会被 counter 更小、优先级更小的内存块晚释放，因为它要被遍历很多次才能被释放。
    counter 的初始值，取决于这个内存块的引用计数变为0之前，也就是放到环形数组之前，它被引用了多少次。一个之前被引用3次的内存块，放入数组后的 counter 就是3，所以就自然实现了一个 访问越多、优先级越高的机制。
- 指针遍历时可以多线程并行，每个线程取到指针后+4，释放指针，检查前面的4个。
- 直接做出修改来代替自旋锁， 然后看修改操作（如 fetch_add）的返回值，决定是不是真的能修改，如果不能再改回去。但有些时候并不需要回滚修改。
- 缺点是优先级的要求不够硬性，LRU 总是可以保证一部分高优先级块不会被低优先级块淘汰，但在 Clockcache 中可以。
    在负载因子很高时，如果可驱逐的内存块很少，指针遍历就会浪费大量 CPU。所以 shard 应该小一些。









## LevelDB LRU cache

### 特点
**引用计数**

因为 cache 容量有限，所以缓存满的时候，每次访问都可能要驱逐一个已有的数据。
驱逐的对象肯定不能是正在被使用的数据，所以 cache 的每个节点都要维护一个引用计数。根据这个计数，每个节点处于两种状态之一：

1. refCount = 0，即数据不被任何线程使用，保存在 LRU List 中，可以被淘汰。
LRU 链表会按最后一次使用时间排序，淘汰时每次淘汰尾部的。
2. refCount > 0，即数据被至少一个线程使用，保存在 In-use List 中，不可被淘汰。
In-use 链表是无序的（其实这个链表本身也没有意义）。

当新数据被读入时，refCount = 1，会被放入 In-use 链表。
当数据被最后使用的线程释放时，refCount 减为 0，会从 In-use 链表中移出，放入 LRU 链表，可以被淘汰。
> 代码实现的不同：
> 关于上面一点有个例外：
> 1. 用户可以调 erase 来从缓存中删除一个数据。如果数据当前在使用，会标记 in-cache = 0。等待 refCount 变为 0 后，直接从 In-use 链表中淘汰，不放入 LRU。
> 2. 同一个 key 对应的键值对可以被 insert 多次。insert 一个重复的 key，不能 overwrite 旧的 value（否则原来的指针会失效），所以它会 erase 旧的 key，并放入新的 key。所以旧的键值对在 refCount 变为 0 后也直接淘汰，不放入 LRU。
> 
> 因此在代码中，未被 erase 的数据可以看做有一个来自 cache 的引用，所以数据被放入 LRU 链表的条件是 refCount = 1 而非 0。被淘汰后，计数会变为 0 从而被 free 释放。
> 所以数据其实有三种状态，见 RocksDB 描述。

**分段**

为了线程安全，cache 每个操作前都加锁；通过分片减少锁冲突。 

### 其它
**总结**

1. 代码精简。同时简单实现了一个哈希表，直接用 LRUHandle 里的`LRUHandle* next_hash`字段实现链式哈希，不需要多存一个 struct HashNode，不需要外部支持。
2. 引用计数。
3. 分段加锁。

**问题**

1. 每次硬盘访问都需要保存一个 Handle，在不使用时必须调 cache.release(handle) 来减少引用计数。
不安全的替代方案是，类似 DelayQueue，只保证返回的内存块指针在 10s 内一定有效。这样不需要引用计数和 handle 处理。而且因为 LRU 本身就按使用时间有序，也不需要额外的 DelayQueue。
2. 在 cache 已满且所有数据块都在使用的情况下，cache 会找不到能移出的数据块。
所以如果不严格要求，cache 可能使用比预设容量更大的内存。





---

## RocksDB LRU cache
### 特点
基于 LevelDB 做的，不同点在于：

**去掉了 in-use list**

没有本质区别，节点/数据还是有三种状态：

```cpp
1. Referenced externally AND in hash table.
   In that case the entry is *not* in the LRU list
   (refs >= 1 && in_cache == true)
2. Not referenced externally AND in hash table.
   In that case the entry is in the LRU list and can be freed.
   (refs == 0 && in_cache == true)
3. Referenced externally AND not in hash table.
   In that case the entry is not in the LRU list and not in hash table.
   The entry must be freed if refs becomes 0 in this state.
   (refs >= 1 && in_cache == false)
```

**优先级**

RocksDB 里的数据分为各种块，主要有三种：

1. 数据块 data block 存放实际数据，会按序存放多个键值对。
2. 索引块 index block，保存每个 data block 中最大的 key，用来根据查询的 key 快速确定对应的 data block。
3. filter block，包含一个布隆过滤器，用来提高读效率、减少不必要的磁盘读。

data block 是始终放在 cache 里的。通常情况下，index 和 filter block 放在堆里，由 os 管理。如果想更好地控制内存，也可把这两种块与数据块一起放在 block cache 里。
由于每次操作一个 key，都需要 1. 通过 index block 确定它在的 data block；2. 通过 filter block 检查它是否真的在 data block；3. 存在时访问 data block 取出。所以显然 index 和 filter block 的使用率要远高于 data block；而且这两种块比较大，从磁盘读的代价高，所以留在 cache 中有更大的收益，所以我们不想让 data block 随意把它们逐出缓存。
因此用户可以指定 index, filter block 可以有更高优先级 (high)，更不容易被移出缓存。

此外 RocksDB 将大 Value 的键值对称为 blob。每个 blob 内只有一个键值对，而 data block 通常包含多个键值对，所以 blob 放在 cache 中的价值比 data blocks 还要低，它的优先级是 bottom。
所以 RocksDB 的 LRU 链表概念上分成了三部分，每一部分的链表头由不同指针指向：

高级别的 block 只有被同级别的 block 挤到后面后，才能被低级别的 block 淘汰。
> [RocksDB - BlobDB](https://github.com/facebook/rocksdb/wiki/BlobDB)
> Blobs 价值低的另一原因：with BlobDB, data blocks containing blob references conceptually form an index structure which has to be consulted before we can read any blob value.
> 没看懂，可能是因为访问 blob 本身代价就大，cache miss 下也相对还好？
>
> blob 也可不放在 block cache 中，而是放在单独的 blob cache。也可用 secondary cache 作为  blob cache。
> 注：图中的箭头实际是 prev，next 与箭头指向相反。链表头 (high_pri_) 的 next 为 dummy node `lru_`。

> [RocksDB - Partitioned Index Filters](https://github.com/facebook/rocksdb/wiki/Partitioned-Index-Filters)
> 默认情况下，RocksDB 的每个 SSTable 都只有一个 index block 和一个 filter block，所以它们的大小可能在 MB 级别，远大于普通的数据块（可能几 KB 到几十 KB）。
> 如果内存足够能将所有 index, filter block 一直留在内存当然很好，但如果内存不够，os 会把它们移出内存，可能导致多次的硬盘读取。如果把它们放入 block cache，就可以控制淘汰策略，同时减少不必要的内存占用。
>但由于它们非常大，留在有限的 cache 就容易导致大量 data block 的 cache miss；不同 index, filter block 之间也会竞争，导致对方淘汰，下次使用时还需要大量磁盘读。所以 cache 中的一大块 index block 的利用率可能并不高。
> 为此，原本大的 index 和 filter 可以划分为多个小块，然后由一个上层的、更小的二级索引来索引它们。这样只有上层的小索引，和实际用到的小块索引，才会被放入 cache。
> 
>优点：
> 
> - 提高 cache 命中率：减小了 cache 中对象大小，能缓存更多对象。
> - 减少 IO：index, filter block 未命中后，只需要从磁盘按需读对应的一小块。
> - 不需要调整 index, filter 的实现：如果不这样，就需要调大 data block 大小来使 index block 相对更小；或牺牲 filter 的准确性、减少 filter 的位数。
> 
>缺点：
> 
>- index, filter 多了一个二级索引，需要多消耗一点点内存（0.1-1%）。
> - 多了一个二级索引块，也会导致更多的磁盘 IO。但其实可以一直留在内存。
> - 空间局部性更差：如果需要频繁、随机读写同一 SSTable，显然原先把整个 SSTable 的 index block 直接读入，要比读一些零散的 block 效率更高。
> 当然这种情况不多，一般只在 L0, L1 发生，所以这两层的 index, filter block 可以不分块。

**热数据标记**

一个已经在缓存内的 data block 再次被查询时，会被标记 isHit。这个 data block 下次放回 LRU list 时，会被视为 high priority 放在链表头。

### 其它
**总结**

1. 数据可以有优先级，以保证热点数据不容易被淘汰。
2. 可以根据查询次数提高数据的优先级。

**问题**

1. 目前来说，优先级应该不需要考虑（内存块间没有明显优先级关系）。
如果场景合适，可以考虑维护命中次数，提高热数据优先级。



---

## RocksDB ClockCache
### 设计和代码
**哈希表**

使用开放寻址，修改操作都是无锁的（不涉及结构修改，只需要原子修改 slot 状态）。
查找一个数据需要两个哈希值，第一个哈希值作为探测的起始位置 base，第二个哈希值 或 1 的结果（保证为奇数）作为每次探测位置的增量 incr。即第 i 次探测位置为$(\text{base} + i*\text{incr})\%\text{tableSize}$。这样冲突的概率会很低。
因为表的大小是 2 的幂，所以从任意起始位置 base 开始每次加一个奇数，一定会在回到 base 前遍历完所有位置。
没有用线性探测，因为每次探测访问的 slot 都占了一个完整的 cacheline，所以局部性带来的好处可能不大。

为了能删除数据，哈希表中的每个位置记录了一个 displacement，表示本来可以放在这里、但由于这已经有数据只能再往后放的数据个数。

查询哈希表时，即使某个位置为空，只要 displacement 不为 0 就要继续向后检查。这样就可以安全删除数据。

**standalone insert**

如果没有要求严格内存限制（ !strict_capacity_limit ），则 cache 要保证插入一定会成功。
在缓存已满（数组已满）的情况下继续插入，会把 handle new 出来放在堆上，最后用 delete 回收。这个 handle 不在哈希表中，所以查询时不能复用，只能继续 new。

为了避免效率降低，哈希表也有一个严格负载因子 kStrictLoadFactor = 0.84，只要超过该值就不能再数组中插入。

与 LRU cache 相同，插入一个已有的 key 不能 overwrite 已有的、相同的 key 存放的 value（会导致原指向它的指针失效）。
所以如果在插入时遇到已有的 key：cache 仍然需要 insert 一个新的 key 32（和新的 value）。但如果插入在已有 32 的后面（记为 32'），可以发现在 32 被从内存中驱逐之前，插入的新 slot 永远不会被访问（因为所有对 32 的查询在前一个 slot 就停止了），所以 ref count 始终为 1，还很可能会在前一个 slot 被释放前就被释放。
所以新插入的、更靠后的 32' 除了浪费一个 slot 外没有任何意义（不会提高查询效率）。
所以这种情况下（插入时遇到已有的 key）新的 32 会作为 standalone 插入，也就是 new 在堆上，不放入 cache；在当前引用释放后就被 delete。
但是新的 key 拥有的新的 value 不会被查询到。

如果在插入遇到已有的 key 之前发现一个空 slot：即使空 slot 位置的 displacement 不为 0，也就是后面可能存在 key 32，应该继续向后检查，Insert 也会在空 slot 位置插入新的 32。
提前插入 32，可以减少后续查询 32 时需要探测的长度，提高效率。
旧的 32 在所有引用都被释放后，最终会被驱逐。
这种情况下，新的 key 和 value 可以被查询到。

**cache 策略**

经典的第二次机会算法，或叫时钟置换算法。
所有内存块组织成一个环。cache 会保存一个指针，每次需要驱逐内存块时，就移动指针，检查指针之前指向的内存块，如果不被引用，就降低它的 reference counter。如果 counter 变为 0 则清空。然后移动指针。
指针会一直遍历，直到释放足够容量的内存块或遍历一圈为止。
所以，一个被引用过 k 次的内存块，会在第 k 次循环遍历时才被释放（实际 k 会对 kMaxCountdown = 3 取 min，即 3 轮后一定会被释放）。
这个环就是开放寻址用的数组，不需要维护额外的结构。

多个线程共用 cache 指针。为了减少争抢，每个线程会检查指针指向位置的连续 4 个内存块，将指针原子加 4。

数据可以设置优先级，低优先级内存块在第一次插入时 counter 是 1，高优先级在第一次插入时 ref counter 是 3，会更难被驱逐。

**状态设计**

BlockCache 是一个无锁 cache。为了减少原子操作数，把三个信息放在了一个 uint64 meta 中：

- 高 3 位表示 slot 状态：slot 有三种状态：
   - empty（000）：该位置没有数据。
   - construction/occupied（100）：该位置被某个线程独享。可能是线程刚刚占下这个空槽、要插入数据；也可能是最后一个释放这个槽，负责清空数据。
   - shared（11x）：该位置可正常被多个线程访问。又分为两种状态：
      - visible（111）：可以被 lookup 查询到。
      - invisible（110）：不可被 lookup 查询，只能由已经持有该引用的线程访问。
调用 Erase 会导致 slot 从可见变为不可见。
- 中间 30 位是 release counter，记录数据一共被释放引用过多少次。
- 低 30 位是 reference counter，记录数据一共被引用过多少次。
所以实际的引用计数是 ref counter - release counter。

cache 策略会使用数据块的历史总引用次数，所以要分别保存 ref 次数和 release 次数，不能只存当前的引用计数。
30 位 counter 溢出问题counter 只有 30 位，虽然同一时刻不会有 2^30 个线程访问一个内存块，但累计的引用次数可能超出 2^30。
counter 是用来设置淘汰所需遍历次数的，最大值是 kMaxCountdown，所以大于 kMaxCountdown 的 counter 值在逻辑上都是一样的。
为了减少原子修改，选择在 release counter >= 2^29 + kMaxCountdown 时，同时给 ref 和 release counter 减去 2^29（fetch_and）。
状态的读取、更新到原子修改这段内容都没加锁，所以存在“线程 A 读取旧的 counter、线程 B 完成 counter 的减少、线程 A 更新 counter 覆盖 B 的修改”的情况。但只要保证 2^29 次操作中至少有一次减少 counter 的操作成功，就不会溢出。

**乐观修改**

所有操作都是无锁的。因为每个更新都要访问 slot 的信息 meta，在状态合适时才能修改，所以会有很多这样的代码：

```cpp
// 只有 slot 状态为 visible，才可以访问
if ((meta.load() >> kStateShift) == kStateVisible) {
	meta.fetch_add(1 << kAcquireCounterShift);
    // ...
}
```
为了减少对 meta 的原子操作，许多场景下会直接做出更改，然后用返回的旧值检查合法性，如果不行再撤销更改：
```cpp
old_meta = meta.fetch_add(1 << kAcquireCounterShift);
if ((meta.load() >> kStateShift) != kStateVisible) {
	meta.fetch_sub(1 << kAcquireCounterShift);
    return;
}
```
比如：Insert 中会先遍历所有 slot，试图找到一个空的 slot 插入，并且可以发现无论旧的状态是什么，insert 操作后 occupied 这一位一定是 1，所以 fetch_or 的乐观操作不需要额外撤销。

### 其它
**总结**

1. 开放寻址。
2. 利用开放寻址中的数组，使用时钟置换算法。
3. 自动根据查询次数，提高数据的优先级（延缓被释放时间）。也可自己设置优先级。
4. 完全无锁，也没有自旋。并发写只需要 1~2 次原子修改，并发读只需要原子 load 和 add，都不涉及链表操作。
驱逐内存块时也可以完全并行。
5. 一些场景直接做出修改来代替自旋锁，先修改再检查；有些修改即使不应该做，也不会影响正确性，不需要再撤销。
6. 并发性能更好，所以可以用更大的 shard（最小 32M）来减少 shard 间读写不平衡的情况。

**问题**

1. 具体比 LRU 好多少不清楚，官方给的测试结果打不开：[http://smalldatum.blogspot.com/2022/10/hyping-hyper-clock-cache-in-rocksdb.html](http://smalldatum.blogspot.com/2022/10/hyping-hyper-clock-cache-in-rocksdb.html)
2. 实现非常麻烦。
3. 优先级的要求不够硬性，LRU 中再多的低优先级块也不能冲掉高优先级块，但在 clock 中可以。
4. 插入一个新的 key, value 有可能不会 overwrite 之前的 value。这在 RocksDB 中是 ok 的。
5. 当负载因子很高时，如果可驱逐的块不多，每次 evict 遍历就会消耗大量 CPU。
所以一个 shard 最好大些，value 小些，让可驱逐的内存块更多。
6. 哈希表不能扩容，要预估好 cache容量。
7. currently for advanced usage only.

> RocksDB 之前使用的是和 levelDB 一样的 ClockCache，去年才改成了现在的 HyperClockCache。
> LevelDB 和 RocksDB 都已经删掉了旧的 ClockCache，因为 '_ClockCache is known to have bugs that could lead to crash or corruption, so should not be used until fixed._'



---

## 其它
**是否预读**
> Linux：
> [Linux中的Page Cache [二]](https://zhuanlan.zhihu.com/p/71217136)：
> 是否采用预读（**readahead**）要看对文件的访问是连续的还是随机的，如果是连续访问，自然会对性能带来提升，如果是随机访问，预读则是既浪费磁盘I/O带宽，又浪费物理内存。
> 那内核怎么能预知进程接下来对文件的访问是不是连续的呢？看起来只有进程主动告知了，可以采用的方法有madvise()和posix_fadvise()，前者主要配合基于文件的mmap映射使用。advise如果是**NORMAL**，那内核会做适量的预读；如果是RANDOM，那内核就不做预读；如果是**SEQUENTIAL**，那内核会做大量的预读。
> 预读的page数被称作预读窗口（有点像TCP里的滑动窗口），其大小直接影响预读的优化效果。进程的advise毕竟只是建议，内核在运行过程中会动态地调节**预读窗口**的大小，如果内核发现一个进程一直使用预读的数据，它就会增加预读窗口，它的目标就是保证在预读窗口中尽可能高的命中率。


**是否支持写**
涉及写回策略和重新压缩。

**是否关闭 page cache**
[rocksdb - Direct IO](https://github.com/facebook/rocksdb/wiki/Direct-IO)

**性能测试**
simulated cache：
[RocksDB系列三：Block Cache](https://www.jianshu.com/p/64ff46550ee5)
[rocksdb -  Simulation Cache](https://github.com/facebook/rocksdb/wiki/Simulation-Cache)
[rocksdb -  Block Cache](https://github.com/facebook/rocksdb/wiki/Block-Cache#simulated-cache)
[Block cache analysis and simulation tools](https://github.com/facebook/rocksdb/wiki/Block-cache-analysis-and-simulation-tools)

**是否支持 Secondary Cache**
[rocksdb -  SecondaryCache (Experimental)](https://github.com/facebook/rocksdb/wiki/SecondaryCache-%28Experimental%29)
[RocksDB Secondary Cache](https://rocksdb.org/blog/2021/05/27/rocksdb-secondary-cache.html)