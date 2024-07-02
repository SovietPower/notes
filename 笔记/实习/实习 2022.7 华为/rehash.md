# rehash

Tags: 实习 2022.7 华为

-----


## redis
> https://blog.csdn.net/Oooo_mumuxi/article/details/105903889

**rehash过程**
首先给`ht[1]`分配空间，然后逐步将原哈希表`ht[0]`迁移到`ht[1]`：

- **active rehashing**
`server.c`中的`serverCron()`周期性被调用，执行各类需要异步处理的事。
每次调用`serverCron()`时，进行一次`incrementallyRehash()`，花费约 1ms 执行一部分迁移（迁移100个桶或遍历了1000个空桶后结束）
- **lazy rehashing**
哈希表执行基本的增删改查（`dictAddRaw`、`dictGenericDelete`、`dictFind`、`dictGetRandomKey`、`dictGetSomeKeys`）时，调用`_dictRehashStep()`进行少量扩容（迁移1个桶或遍历了10个空桶后结束）。

迁移完成后，释放`ht[0]`，将`ht[1]`赋给`ht[0]`。

rehash 可以扩容也可缩容。