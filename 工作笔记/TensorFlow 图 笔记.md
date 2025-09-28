# Tensorflow 图

---
[TOC]

---

## 输出模型图

### 基础

获取图：

```python
g = tf.Graph()
with g.as_default():
    a = tf.constant(2, name='a')
    b = tf.constant(3, name='b')
    c = tf.add(a, b, name='c')
graph = g
# 或
a = tf.constant(2, name='a')
b = tf.constant(3, name='b')
c = tf.add(a, b, name='c')
graph = tf.get_default_graph()graph = tf.get_default_graph()graph = eeeeeeeeeeeeeeeeeee
```

打印图中的算子：

```python
for op in graph.get_operations():
    print('-', op.name)
```

使用会话执行图：

```python
with tf.Session(graph=g) as sess:
    result = sess.run(c)
    print("Result of c (a + b):", result)
```

输出模型图到 pb 以便用 netron 查看：

```python
with open('add.pb', 'wb') as f:
    f.write(graph.as_graph_def().SerializeToString())
```





---

## GraphDef



- 获取所有 node：`g.node`
如：`for idx, node in enumerate(graph.node)`。
- 



有 graph_def 后，可以通过 session 运行获取任何节点的值：

```python
new_graph = tf.Graph()
with new_graph.as_default():
    tf.import_graph_def(graph_def, name='')
feed_dict={'input:0': input}
with tf.Session(graph=new_graph) as sess:
    print(sess.run('strided_slice/selectV2:0', feed_dict=feed_dict))
    print(sess.run('strided_slice/f:0', feed_dict=feed_dict))
```



注意，如果通过`graph_def.node.append(node)`将 node 加入到了图中，再修改这个 node（如 name, input）是不会对图中的节点生效的！即 append 会拷贝一个 node 到图里，虽然这并不符合预期。。





### NodeDef

[NodeDef](https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/NodeDef)

`slice` 这样的名字指代一个节点 (operation)，而 `slice:0` 这样的 `<op_name>:<output_index>` 指代一个 tensor，代表该节点的第 0 个输出 tensor（一个节点可能有多个输出 tensor）。
session.run 中就需要指定具体的、要获取输出的 tensor 名字（即必须带 output_id！~~只是一般节点只有一个输出，所以没加 `:0` 也行？~~）。也可以指定要运算的 tensor（图模式下 tf 操作的返回值是一个待运算的 tensor）。

session.run 的 feed_dict 中也要指定 tensor（如 `'input:0'`）。

`tf.placeholder` 就是创建一个节点，后续 run 时可以用 `feed_dict` 为该输入节点的 tensor（如 `input:0` 而非 `input`）传递值。

- node.attr：一个 dict，包含节点的所有属性。可以像 dict 一样用（如 `if 'key' in attr['T']`）。
  其类型为 `tf.NodeDef.AttrEntry`，value 的类型为 [`tf.AttrValue`](https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/AttrValue)。
  如：`node.attr['begin_mask']`。
- node.input：一个 list，包含所有输入字段。
  如：`tf.slice(input_, begin, size, name=None)` 的 input 为 [input_tensor, begin, size]，是包含三个不同类型元素的 list，用 node.input[i] 获取。
  添加 input：`new_node.input.extend([node.input[0], node.input[1], node.input[2]])`；
  `new_node.input.append(node.name)`（extend 和 append 都是追加，但 extend 的参数是 tuple 可以赋值多个）。
  修改 input：`node.input[0] = 'a'`；`node.input[:] = ['a', 'b']`。

input 就用 node.input 取，attr 就用 node.attr['key'] 取，不要混。

node 没有 output，只能遍历所有节点、检查输入节点名字来修改输出节点。



**RepeatedCompositeFieldContainer**

如果要将 graph_def.node 改为新的 list，需要使用 Clear 然后 extend，这样可以避免改变其类型；不能直接使用 `graph_def.node = new_list`，不仅会改变 node 的引用（可能影响其它代码），还可能赋值错误的类型。

移除部分 node：

```python
new_node_list = list(filter(
    lambda node:
        node.name != 'Placeholder',
    graph_def.node
))
graph_def.ClearField('node')
graph_def.node.extend(new_node_list)
```



**AttrValue**

[AttrValue](https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/AttrValue) 是节点属性（AttrKey 字典）的 value，包含若干字段（只有其中一个有效）。

使用时根据该 value 的实际类型使用对应的字段，如：是 list 就用 `v.list`，是 float 就用 `v.f`，如果是类型（如 a["dtype"]）就用 `v.type`），是 shape 就用 `v.shape`，是字符串就用 `v.s`（结果是 bytes，可通过`.decode('utf-8')`转为 str）。
如果 attr 是 tensor，则是 TensorProto 类型。

为 Attr 赋值：

- CopyFrom：
  （可确保整个 AttrValue 对象被正确复制）

```python
size_node.attr['value'].tensor.CopyFrom(
    tf.make_tensor_proto(size, dtype=tf.int32)
) # 从 TensorProto 拷贝
node.attr['squeeze_dims'].CopyFrom(
    tf.AttrValue(list=tf.AttrValue.ListValue(i=squeeze_dims))
) # 从 AttrValue 拷贝
```

- extend：
  （似乎不推荐该方法，需要确保类型和格式完全匹配，否则可能导致错误？）

```python
# extend 与 append 都是追加而非赋值
node.attr['squeeze_dims'].list.i.extend(squeeze_dims)
```

构造 AttrValue 对象：

```python
from tensorflow.core.framework import attr_value_pb2

val_int = attr_value_pb2.AttrValue(i=42)
print(attr_value_int)
val_string = attr_value_pb2.AttrValue(s=b"hello")
val_list = attr_value_pb2.AttrValue(list=attr_value_pb2.AttrValue.ListValue(i=[1, 2, 3]))
val_type = attr_value_pb2.AttrValue(type=tf.int32.as_datatype_enum)
```





**DataType**

[DataType](https://github.com/tensorflow/tensorflow/blob/03b0dd411df9535d2d810115ee07c31c4d06789b/tensorflow/core/framework/types.proto#L13) 为 tensor 的类型，与 tf 的每种类型都一一对应。

赋值：`node.attr['T'].type = tpb.DataType.DT_INT32`。
或 `node.attr['T'].CopyFrom(GetAttrT(input_node))`。

大多数 node 可通过 attr['T'] 或 attr['dtype'] 获取输入的类型（const, placeholder 是后者，Cast 是 SrcT + DstT，其它是前者）。
node['T'/'dtype'] 的结果是 AttrValue，要访问类型需要使用 node['T'].type 字段。
类型 type 是一个 int，可以直接和 tf.int32... 或 tpb.DataType.DT_INT32 进行比较。

```python
def GetAttrT(node):
    if 'T' in node.attr:
        return node.attr['T']
    if node.op == 'GatherV2':
        return node.attr['Tparams']
    if node.op == 'Cast':
        return node.attr['SrcT']
    if node.op != 'Const' and node.op != 'Placeholder': # Const, Placeholder 使用 dtype
        logger.warning(f'node [{node}]\'s op {node.op} also has dtype instead of T!')
    return node.attr['dtype']

t = node.attr['T'].type
# <class 'tensorflow.core.framework.attr_value_pb2.AttrValue'>, <class 'int'>, 3, True, True
print(f'{type(node.attr['T'])}, {type(t)}, {t}, {t == tf.int32}, {t == tpb.DataType.DT_INT32}')
```





**AttrValue.ListValue**

通过 AttrValue.list 获取的类型。跟 AttrValue 类似通过 list 元素的实际类型使用对应的字段，得到一个对应类型的列表（先指定 list 类型再指定 list 元素的类型）。

如：`attr['shape'].list.i` 是一个 int list。





**TensorProto**

[TensorProto](https://github.com/tensorflow/tensorflow/blob/0920d7f31d9e0007261b5d9b2a0f8cd476c3da8a/tensorflow/core/framework/tensor.proto#L16) 是序列化张量的协议缓冲区格式。

转为 np.ndarray：

```python
tf.make_ndarray(tensor_proto)
# 或（但不推荐？）
from tensorflow.python.framework import tensor_util
tensor_util.MakeNdarray(node.attr["value"].tensor)
```

如果 node op 是长度很小的 Const（比如 reduce 的 axis），可以这样获取 tensor 值：`node.attr["value"].tensor.int_val[0]`（直接输出 .tensor 可以看到其 dtype）。

如果 node op 的长度可能很长（如 Slice 的 begin，但其实差不多。。），要先判断 tensor_content 是否有值（序列化存储较大对象以节省存储和序列化开销），再判断 int_val：

```python
_, i = GetNode(graph_def, node.input[1])
tensor_proto = i.attr['value'].tensor
if tensor_proto.tensor_content:
    begin = tf.make_ndarray(tensor_proto) # numpy.ndarray
else:
    begin = tensor_proto.int_val
```

创建新节点并使用：

```python
dim_node = npb.NodeDef()
dim_node.op = 'Const'
dim_node.name = node.name + '/Dim'
dim_node.attr['dtype'].type = tpb.DataType.DT_INT32

# 注意 const node 即使 value 看起来是个 int，也要赋值 tensor
# 复合类型（如 tensor、AttrValue）用 CopyFrom 更安全
dim_node.attr['value'].tensor.CopyFrom(tf.make_tensor_proto(expand_dims[0], dtype=tf.int32))
# 从其它节点的 attr['value'] 拷贝
dim_node.attr['value'].CopyFrom(node.attr['value'])

graph_def.node.extend([dim_node])
```



**TensorShapeProto**

[TensorShapeProto](https://github.com/tensorflow/tensorflow/blob/8e403b047b0cc82f1ea88a0f90d26ca1d9fc6ba2/tensorflow/core/framework/tensor_shape.proto#L13) 是 shape。

获取值：`shape.dim[i].size`。
获取维数：`len(shape.dim)`。





### NodeAttr

有的节点使用 attr['dtype'] 保存类型，但大部分使用 attr['T']。

使用 dtype 的 op：

- Placeholder
- Const











### util









---

## 示例

### 添加新节点

```python
new_tensor = tensorpb.TensorProto()
new_tensor.dtype= tpb.DataType.DT_INT32
new_tensor.int_val.append(0)
new_tensor.int_val.append(2)
new_tensor.int_val.append(1)
new_tensor.tensor_shape.dim.add().size = 3
    
# Const tensor
new_node = npb.NodeDef()
new_node.op = "Const"
new_node.name = graph_def.node[reduce_node_id].name + "_transpose/perm"
new_node.attr["dtype"].type = tpb.DataType.DT_INT32
new_node.attr["value"].tensor.CopyFrom(new_tensor)
node.input.append(new_node.name)
graph_def.node.extend([new_node])

# ConcatV2 tensor（似乎不用 Concat）
cond_node = npb.NodeDef()
cond_node.op = 'ConcatV2'
cond_node.name = node.name + '/cond'
cond_node.attr['N'].i = 2 # 需要指定 N，即 concat tensor 数量
cond_node.attr['T'].type = tpb.DataType.DT_INT32
cond_node.attr['Tidx'].type = tpb.DataType.DT_INT32
cond_node.input.extend([end_mask_node.name, pad_node.name, concat_axis_node.name])
graph_def.node.extend([cond_node])
```







---

## 常见 pattern











---

## 报错







**Expected float32, got array(2., dtype=float32) of type 'ndarray' instead.**

这个错误发生在：node.attr['value'].tensor.CopyFrom(tf.make_tensor_proto(value, dtype=TpdTypeToTfType(type)))
其中 value 是 [ori_value]，ori_value 是从另一个 const node 获取的 shape 为 () 的 ndarray 标量。

错误原因：make_tensor_proto accepts "values" of a python scalar, a python list, a numpy ndarray, or a numpy scalar. If "values" is a python scalar or a python list, make_tensor_proto first convert it to numpy ndarray. In either case above, the numpy ndarray (either the caller provided or the auto converted) must have the compatible type with dtype.
即 [ori_value] 会被转为 ndarray，这个 ndarray 中的元素类型必须*直接*与 dtype 匹配，而元素类型是 ndarray，不是 float32。

当 ndarray 中只含一个元素时（不管多少维），可以用 `arr.item()` 转换为标量，再加 `[arr.item()]` 转为 list。
如果 `arr.size > 1`，使用 item() 会出错。






---




## end

