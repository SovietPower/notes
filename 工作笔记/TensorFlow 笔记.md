# TensorFlow 笔记

---
[TOC]

---





---

## 基础



**tf.Variable**

> https://www.tensorflow.org/guide/variable?hl=zh-cn



**tf.variable_scope**



reuse 有三种选择：

1. True：在该作用域中只能获取已经存在的变量，不能创建新变量。如果尝试获取一个不存在的变量则报错。应用于 sub-scopes。
2. None：该作用域中只能创建新变量，不能获取已经存在的变量。如果尝试获取一个已经存在的变量则报错。
3. tf.AUTO_REUSE / tf.compat.v1.AUTO_REUSE：如果变量已存在则获取它，如果变量不存在则创建它。



**tf.get_variable**









---
## 算子
> https://www.tensorflow.org/api_docs/python/tf
> 1.15：https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/

**concat**

连接若干个 tensor。tensor 之间除了 axis 之外的维的大小必须相同。
不会使 rank 改变，只会增加 axis 维的大小。

```python
tf.concat(
    values, axis, # 0-D tensor
    name='concat'
)
```

**equal**

逐元素比较两个张量，返回与输入张量相同的 bool 张量（代表每个元素是否完全相同）。
结合 reduce_all 可以比较两个张量是否完全相同：

```python
print(tf.equal(t1, t2))
print(tf.reduce_all(tf.equal(t1, t2))) # 结果也是一个 tensor
```

如果是浮点数，需要自己实现以近似比较两个张量是否相同？

**expand_dims**

在 axis 维度插入大小为 1 的新维度。支持负下标。

```python
tf.expand_dims(
    input, axis, # 标量，即一次只能扩张一维
    name=None
)

# 例
image = tf.zeros([10,10,3])
tf.expand_dims(image, axis=1).shape.as_list() #[10, 1, 10, 3]
```


**fill**


```python
tf.fill(
    dims, value, name=None, layout=None
)
```

**gather**

基于索引提取张量中特定切片或元素。输出结果的每一维由 axis 维的 indices 中的每一维指定（不一定是从小到大）。

```python
tf.gather(
    params, # 要提取的张量
    indices, # 要提取的索引，可以为负数索引
    axis=0, # 要提取的维度
    batch_dims=0, # 指定前多少个维度作为批处理维度？
    name=None
)
```

`gather(x, [a1, a2, ...], axis)` 等价于切片 `x[:, :, ..., [a1, a2, ...], :, ...]`（如果有这种语法；因此当 indices 是标量时 gather 会像 StridedSlice 一样降维），axis 维就是`indices`，除了 axis 外的维都是`:`。

indices 可以是一个 rank>1 的张量，此时会升维。
是否升维取决于 rank(indices)。

例：

```python
x = tf.constant([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
result = tf.gather(x, [1, 2], axis=1) # 等价于 [-2, -1]，注意结果顺序与 indices 一致
print(result)  # 输出: [[2, 3], [5, 6], [8, 9]] (3, 2)
# 等价于
result = tensor[:, 1:3]

# 升维
print(tf.gather(x, [[1, 2], [2, 1]], axis=1))
# 输出：[[[2 3], [3 2]], [[5 6], [6 5]], [[8 9], [9 8]]] (3, 2, 2)

# 降维
print(tf.gather(x, 1, axis=1))
# 输出：tf.Tensor([2 5 8], shape=(3,), dtype=int32)
# 不降维
print(tf.gather(x, [1], axis=1))
# 输出：tf.Tensor([[2], [5], [8]], shape=(3, 1), dtype=int32)

o = o[:, :, 1] # 第 2 维取第 1 部分
# 等价于
o = tf.gather(o, indices=[1], axis=2)

o = o[:1] # 第 0 维取第 0 部分
# 等价于
o = tf.gather(o, indices=[0], aixs=0)
```

似乎 indices 为 1 和 [1] 的效果不同：后者会添加一维，像`[1, 2]`一样，前者不会。
但测试是有时会，有时不会？
indices 中的值好像也不能是负数？

**matmul**

`tf.matmul(a, b)`等价于`a @ b`，会进行矩乘。
矩阵 A (seq..., n, m) 和矩阵 B (seq'..., m', p) 必须满足 seq = seq' 且 m = m'，结果矩阵的 shape 为 (seq..., n, p)。
~~前面 seq... 的部分可以广播。~~ a, b 需要有相同的 type 和 rank（虽然测试时 rank 不同的 (a, b, c) 和 (c, d) 也会广播...）。

$output[..., i, j] = \sum_k (a[..., i, k]\times b[..., k, j]), \forall\ i, j$ 

**multiply**

`tf.multiply(a, b)`等价于`a * b`，会进行逐元素的向量相乘（而非矩乘）。
可以进行广播调整操作数的大小。

**tensordot**

`tf.tensordot(a, b, axes=1)`等价于`tf.reduce_sum(tf.multiply(a, b))` (TBC)，会计算内积（点积）。

**reduce_sum**

沿指定维求和。结果会消除指定维，其它维大小不变。

```python
tf.math.reduce_sum(
    input_tensor, axis=None, # 如果为 None，reduce 所有维，即结果为标量
    keepdims=None, # 是否将 reduce 的维度保留（大小为 1），默认 False
    name=None, reduction_indices=None,
    keep_dims=None
)
```


**sequence_mask**

生成一个 [shape(lengths), maxlen] 的张量：将 lengths 中的每个元素 v 扩充成大小为 maxlen、且前 v 个元素为 true、后 maxlen - v 个元素为 false 的张量（即使 maxlen 为 1 也会新增加一维）。

```python
tf.sequence_mask(
    lengths, # 所有元素要小于等于 maxlen
    maxlen=None, # 默认为 lengths 中的最大值
    dtype=tf.dtypes.bool,
    name=None
)

# 例
tf.sequence_mask([1, 3, 2], 5)  # [[True, False, False, False, False],
                                #  [True, True, True, False, False],
                                #  [True, True, False, False, False]]

tf.sequence_mask([[1, 3],[2,0]])  # [[[True, False, False],
                                  #   [True, True, True]],
                                  #  [[True, True, False],
                                  #   [False, False, False]]]
```

**shape** **get_shape** 和 **tf.shape(ts)**

ts.shape 与 ts.get_shape() 等价，返回一个 TensorShape 对象，表示张量的静态形状 (Static Shape)。这种形状在编译时确定，不依赖于运行时的实际数据。
返回类型: TensorShape 对象，可以通过 .as_list() 方法转换为 Python 列表（例：`x.get_shape().as_list()[1:-1]`）。
它不是 tensor，而是类似一个 list，`ts.shape[axis]`的结果是一个整数而非 tensor（例：`x.shape[-1]`）。
适用范围: 用于编译期（构建图阶段）的形状推断和检查。只能获取静态形状信息，对于动态大小的张量（例如 batch size 可以变化），它会包含未知的维度（值为 None）。

ts.get_shape() 适用于 TensorFlow 1.x 和 2.x；tf.shape 是 TensorFlow 2.x 中的推荐方式，效果一样。

tf.shape(ts) 返回一个表示张量动态形状的张量 (Dynamic Shape)。这个形状在运行时计算，适用于未知维度或动态变化的形状。
返回类型: 一个整数类型的 TensorFlow 张量，包含每个维度的大小。
它是 tensor，`tf.shape(ts)[axis]`的结果也是一个 shape 为 () 的 tensor（不能直接用于 split 的分割参数，可以先 .numpy().tolist() 再取 [axis]）。
适用范围：可以在运行时获取张量的实际形状，用于需要在运行时确定形状的操作，例如处理输入数据的动态 batch size 或在图计算中需要动态调整形状的场景。

> as_list 只适用于 TensorShape 静态形状获取 list，tf.shape(x) 获取的动态 tensor 必须拷贝到 numpy 数组才能 tolist 转为 list。
> tf.shape(x) 有 _shape_as_list() 这样的私有方法可以做到相同功能，但不推荐使用。


**slice**

从指定位置开始，切片指定大小的张量。
如果 size 的元素为 -1，则选取余下的所有元素。

```python
tf.slice(
    input_, begin, size, name=None
)

# 例
t = tf.constant([[[1, 1, 1], [2, 2, 2]], # [3, 2, 3]
                 [[3, 3, 3], [4, 4, 4]],
                 [[5, 5, 5], [6, 6, 6]]])
tf.slice(t, [1, 0, 0], [1, 1, 3])  # [[[3, 3, 3]]]
tf.slice(t, [1, 0, 0], [1, 2, 3])  # [[[3, 3, 3],
                                   #   [4, 4, 4]]]
tf.slice(t, [1, 0, 0], [2, 1, -1])  # [[[3, 3, 3]],
                                   #  [[5, 5, 5]]]
```

**stack**

将 N 个 shape 相同的 tensor 在指定维上拼接成一个 +1 维的 tensor（会插入一个对应的维度使 rank + 1）。

如：N 个 (a, b, c) 的 tensor 在 axis=0 进行 stack 结果 shape 为 (N, a, b, c)；在 axis=1 进行 stack shape 为 (a, N, b, c)。

**strided_slice**

 StridedSlice 是步长可以不是 1 且功能更多的 Slice 扩展。

```python
tf.strided_slice(
    input_,
    begin,
    end,
    strides=None,
    begin_mask=0,
    end_mask=0,
    ellipsis_mask=0,
    new_axis_mask=0,
    shrink_axis_mask=0,
    var=None,
    name=None
)
```

如果 begin_mask 为 5 (101)，则代表 slice 的第 0 维、第 2 维的 begin 是未指定的（如 t[:3, 0:1, :]），end_mask 同理（所以需要每维度都指定具体的值，如 0:3）。
begin_mask 和 end_mask 在某些情况下，比依次设置 begin 为 0 或 end 为 -1 更方便。

new_axis_mask 为 1 的维度代表在该维插入一个大小为 1 的维，与 expand_dims、[None] 一样。

**切片**

切片和 tf.stride_slice 中不使用`:`且大小为 1 的维度会被压缩省略（有点类似 gather？）。
如`q[:,0,0]`的结果形状为`[bs]`而非`[bs,1,1]`。如果要保留形状，可以用`q[:, :1, 0:1]`或`tf.reshape(q[:, 0, 0], [bs, 1, 1])`。
tf.slice 不会。

`tensor[:, :, None]` 会在第三维插入一个大小为 1 的维，不影响前后的维（后面未指定的维会取所有元素，如 `x[:]` 等价于 `x[:, :, :]`）。
假如 tensor shape 为 [2, 3, 4, 5]，`tensor[:, :, None]` 的结果 shape 是 [2, 3, 1, 4, 5]。

**split**

将一个张量按指定维度进行分割。返回一个 tensor 数组（在图中会有多个输出，如 `split_3:5`；如果没有指定`:n`则会使用第一个输出）。
分割后的子张量除了 axis 维由 num_or_size_splits 指定外，其它维与 value 一致。

```python
tf.split(
    value,
    num_or_size_splits, # 如果是整数，代表沿该维均分成多少个子张量；如果是列表，代表沿该维分割的每个子张量大小
    axis=0,
    num=None, # 当 num_or_size_splits 为整数时，如果均分的子张量数量无法推断，则需手动指定
    name='split'
)
```

实现 unstack：

```python
shape = tf.shape(tensor).numpy().tolist()
num_slices = shape[axis]
# 将指定维切分成该维大小份
split_tensors = tf.split(tensor, num_slices, axis=axis)
# 指定维度依然存在，大小为 1，消除掉
reshaped_tensors = [tf.reshape(st, shape[:axis] + shape[axis+1:]) for st in split_tensors]
```

**squeeze**

移除 tensor 中所有大小为 1 的维。
如果指定 axis，则只移除 axis 维，需要保证该维的大小为 1。

```python
tf.squeeze(
    input, axis=None, name=None, squeeze_dims=None
)
```

**unstack**

unstack(x, axis) 结果：依次从 axis 之外的维度选取所有元素，组成最终列表的每个元素。

**where**

condition 也可以被广播。condition、x、y 必须能被广播到相同大小。







---

## 其它算子

**einsum**

> https://zhuanlan.zhihu.com/p/71639781
> https://rogerspy.github.io/2021/09/12/einsum-mhsa/





**tf.layers.dense**

计算 `outputs = activation(inputs * kernel + bias)`。kernel、bias 是 layer 内部创建的一个矩阵。

```python
tf.layers.dense(
    inputs, units, # dimensionality of the output space
    activation=None, use_bias=True, kernel_initializer=None,
    bias_initializer=tf.zeros_initializer(), kernel_regularizer=None,
    bias_regularizer=None, activity_regularizer=None, kernel_constraint=None,
    bias_constraint=None, trainable=True, name=None, reuse=None
)
```








---
## 语法









---

## 其它

**Broadcasting**

> https://numpy.org/doc/stable/user/basics.broadcasting.html

两个数组进行运算时，会逐元素计算，因此通常需要有相同的 shape。
有了广播后的规则为：从末尾维度反向遍历两个数组 shape 的每一维，当且仅当它们的大小相等或其中一个为 1 时，两个维度兼容。
如果某个数组维数更少，则**剩下的左侧的**维度会被视为 1，即总可与其它维兼容。比如：(2, 3) 与 (3,) 兼容，但与 (2,) 不兼容。

只要满足广播条件，多个数组可以被广播到同一大小 (they are broadcastable to the same shape)。
比如：(5, 1), (1, 6), (6,) 可被广播到 (5, 6)（(5,) 不可。

广播可以避免不必要的数据拷贝，提升性能（虽然看起来是标量被拷贝成了向量，但实际不会产生拷贝）；但有时可能会导致内存利用低效，影响计算。










---
## end



