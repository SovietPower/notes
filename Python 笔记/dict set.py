# -*- coding: utf-8 -*-

'''
list, dict, set, bytearray 均为可变对象（可变类型）。
python函数的参数传递：
可变类型：类似 C++ 的引用传递，包括list, dict, set, bytearray。如 fun(l)，则是将 l 真正的传过去，修改后 fun 外部的 l 也会受影响。
不可变类型：类似 C++ 的值传递，可变类型外的类型。如 fun(a)，传递的只是 a 的值，没有影响 a 对象本身。如果在 fun(a) 内部修改 a 的值，则是新生成一个 a 的对象。
'''

# dict，类似unordered_map，通过哈希表实现。存储无序。
d = {"A":1 ,"B":2, "C":'ccc'} # 定义dict：{}
d = dict(A=1, B=2, C='ccc') # 使用dict()也可定义dict，但注意是等号赋值，且左式没有引号。这样相当于用dict类初始化实例。
print(d["A"]) # 访问同数组

# dict添加元素一是通过赋值，若key已存在则覆盖value；二是使用dict.update()，参数为一个dict，会添加参数中的所有键值对，同样若key已存在则覆盖value。
d["D"]=4 # 在dict中添加元素
d.update({"D":4}) # 在dict中添加元素
d["D"]=5 # dict中每个元素只能映射到一个元素，即最后赋值的那个

# 若元素不在dict中，但进行了引用，会报错。需使用(not d.get("A"))判断，而不能用(not d["A"])。
print("E" in d) # x in dict 返回True/False，可判断x是否在某个dict中
print(d.get("A")) # dict.get(x) 可得到x在dict中的映射，若x不在dict中则返回None，或自定义的val（见下行）
print(d.get("E"))
print(d.get("E", 555)) # dict.get(x,val) 当x不在dict中时，返回val
print(d.get("E", "There isn't E!")) # There isn't E!

# dict.pop()：删除dict中的元素，会返回删除前的映射
d.pop("D")
print(d.get("D")) # None
print(d.pop("C")) # ccc

# 与C++中map不同，dict不能以可变元素作为第一关键字key，如list；而数字、字符串为不可变元素
key = [1, 2, 3]
# d[key] = "unhashable type: 'list'" # Error


# set，类似C++中set，一组元素key的集合，无重复元素。注意该set**无序**（元素排序是不定的）。
s = set([1, 2, 3]) # 用list作为输入参数，通过set(list)可创建set
print(s)

s.add(4) # set.add(x) 添加元素x，重复添加的会忽略
s.remove(4) # set.remove(x) 删除元素x，但要求x必须存在，否则会报错
s.discard(4) # set.discard(x) 删除元素x，不要求x必须存在，x不存在不会报错

# 两个set间可以做与/或运算，即求交集/并集
s1 = set([1,2,3])
s2 = set([1,3,4])
print(s1 & s2)
print(s1 | s2)

# 也可以求差集
a = {"a","b","a",1,2,3,1,"1"}
b = {1,2,3.14,"a","c"}
print(a.difference(b)) # {'1', 3, 'b'}

# 使用 in / not in 判断一个元素是否在set中


# set 可以判断序列中是否有重复数字
a=["a","b","a",1,2,3,1,"1"]
if len(set(a)) == len(a):
	print("a列表里面没有重复元素")


