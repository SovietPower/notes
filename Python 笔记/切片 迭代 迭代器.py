# -*- coding: utf-8 -*-


'切片'
# 切片：对于list、tuple和str，用 变量名[L:R] 即可取出其中[L,R)的元素并组成新的list、tuple或str
# 若L省略则为0，R省略则为len，都省略则为全体（即复制一个）
# 同样支持负数索引，-x表示len-x
l = [0, 1, 2, 3, 4, 5]
t = (0, 1, 2, 3, 4, 5)

print(l[1:4])
print(l[-5:-2])

print(l[4:])
print(l[-2:]) # 取出后2个数

print(t[:4]) # 取出前4个数
print(t[:-2])

print(t[:])
print(t[-len(t):])

# 可加参数步长
print(t[::2]) # 所有数每2个取一个 (0, 2, 4)
print(t[1:6:3]) # [1,6)每3个数取一个 (1, 4)
# 若步长为负，则表示从后往前取（注意区间是起点在前，终点在后，这样依旧左闭右开！）
print(l[::-1]) # 所有数从后往前，每1个取一个，即反转 [5, 4, 3, 2, 1, 0]
print(l[5:1:-2]) # [5,-1)从后往前，每2个取一个 [5, 4, 3]

print([0, 1, 2, 3][1:3]) # 不用参数名也可！
print((0, 1, 2, 3)[1:])

s = "01234567"
print(s[1:5])
print("01234567"[:])

# 注意l=L，返回的是L的地址，所以对l的修改也会修改L（l,L相当于**指针**，类似str，指向的是list的内存地址）；而l=L[:]返回的是L的一个副本，对l的修改不会影响L
# 若令l=L, L=[...]，此时L指向新的list的地址，则对l的修改不会影响L
L=[1, 2, 3]
l=L
l.append(0)
print(L) # [1, 2, 3, 0]

L=[1, 2, 3]
l=L[:]
l.append(0)
print(L) # [1, 2, 3]

L=[1, 2, 3]
l=L
L=[0]
l.append(0)
print(L) # [0]

# 去除字符串开头空格的暴力方法
s = "  qwq  "
while s[:1]==' ': # 或s[0]==' '
	s=s[1:]
print(s)


'迭代'
# 迭代：通过for遍历可迭代对象(Iterable)
# 常见可迭代对象：list, tuple, dict, set, str, generator
for i in [0, 1, 2, 3]:
	print(i, end=' ')
print()

for ch in "ABC":
	print(ch, end=" ")
print()

# dict默认迭代的是key，value用d.values()，key也可以专门用keys()。同时迭代key和value用d.items()（需两个变量）
# 注意dict的存储是无序的，所以迭代也是无序的。
d = {"a":1, "b":2, "c":3}
for k in d: # or d.keys()
	print(k, end=" ")
print()
for v in d.values():
	print(v, end=" ")
print()

for k, v in d.items(): # d.items()将d的key-value组装成一个tuple，也可以通过下标访问
	print(k+":"+str(v), end=" ")
print()

# 通过enumerate(sequence, [start=0]) 可将可迭代对象Iterable组装为 索引-元素。可自定义下标起始位置start，默认为0。
for i, val in enumerate(("A", "B", "C")):
	print("t[%d]=%s" % (i, val))

for i, a in enumerate(d.items()): # dict 也可 enumerate
	print("%d: d[%s]=%d" % (i, a[0], a[1]))
# print(type(enumerate([1, 2, 3]))) # <class 'enumerate'>

# 判断一个对象是否为可迭代对象：通过collections.abc模块的Iterable类型
from collections.abc import Iterable
print( isinstance(1234, Iterable) ) # False
print( isinstance("ABC", Iterable) ) # True  isinstance()判断一个对象是否是一个已知的类型，类似type()，但会认为子类是一种父类类型，考虑继承关系


'迭代器'
# 迭代器(Iterator)：可以被next()调用并不断返回下一个值的对象，表示一个惰性计算的序列。
# 对于可变对象和dict，迭代时不允许修改。
# 迭代不能向前，不能回到开始。
# 迭代器不能复制副本，即若两个变量指向同一个迭代器，对任意变量修改（只要修改该迭代器）都会同时影响另一个变量。

# 常见迭代器：generator, iter(), map(), filter()
# 判断一个对象是否为迭代器对象：通过collections.abc模块的Iterator类型。一个 Iterator 对象需且仅需同时具有 __iter__ 和 __next__ 方法
# Iterator都是Iterable的，但Iterable的不一定是Iterator。
from collections.abc import Iterator
print(isinstance([], Iterator)) # False
print(isinstance((x for x in range(10)), Iterator)) # True

# 通过iter()可将list, dict, set, str等Iterable变为Iterator
# 通过list(iter())也可将Iterator转为list等
print(isinstance(iter([]), Iterator)) # True
print(isinstance(iter("ABC"), Iterator)) # True

# Python的Iterator对象表示的是一个数据流，Iterator对象可以被next()函数调用并不断返回下一个数据，直到没有数据时抛出StopIteration错误。
# 可以把这个数据流看做是一个有序序列，但我们却不能提前知道序列的长度，只能不断通过next()函数实现按需计算下一个数据，所以Iterator的计算是惰性的，只有在需要返回下一个数据时它才会计算。
# Iterator甚至可以表示一个无限大的数据流，例如全体自然数（迭代时可在for中break）。而使用list是永远不可能存储全体自然数的。

# 对Iterable的for迭代，等价于对其Iterator类型不断调用next()
l = [1, 2, 3, 4, 5]
for x in l:
	print(x, end=" ")
print()

# 完全等价的写法：
it = iter(l)
while 1:
	try:
		x=next(it)
		print(x, end=" ")
	except StopIteration: # as ...
		break
print()

# 迭代器不能复制副本。以下it,it2仍为同一迭代器。
it = iter(l)
print(next(it)) # 1
it2= it
print(next(it2)) # 2
print(next(it)) # 3





