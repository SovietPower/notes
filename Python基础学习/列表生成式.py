# -*- coding: utf-8 -*-

# 列表生成式(List Comprehensions)：通过对循环变量的操作，自定义生成列表
l = list(range(1, 11)) # 生成[1, 2, 3,... , 10]
l = [x for x in range(1, 11)] # 与前一行等价
l = [x for x in range(1, 11, 2)] # 以步长为2生成x，并添加到list，即生成[1, 3, 5, 7, 9]

l = [x*x for x in range(1, 11)] # 生成[1*1, 2*2, ..., 10*10]

# 注意是生成后才赋值，赋值前列表中的元素是不变的。如生成杨辉三角的第n+1行
n = 5
l = [1]
while n:
	n-=1
	l.append(0)
	l = [l[i]+l[i-1] for i in range(len(l))] # 当i=0时，l[0]=l[0]+l[-1]=1
print(l)

# 定义一个定长数组，并初始化为0
A = [0]*10
A = [0 for _ in range(10)] # 两种写法均可
A = [0 for i in range(10)] # _可以是任意名字的变量
print(len(A),A)

# 也可以使用多个变量生成list
d = {"A":1, "B":2, "C":3}
l = [k+"="+str(v) for k, v in d.items()]
print(l) # ['A=1', 'B=2', 'C=3']

# ! 也可以使用多层循环生成list
l = [m+n for m in "ABC" for n in "123"] # 两层循环
print(l) # ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']

# ! 可以嵌套循环生成多维数组
l2 = [[-1 for _ in range(3)] for _ in range(5)]
print(l2)

# ! 筛选在某些情况下生成list：通过在for后加if
l = [x for x in range(1, 11) if not x%2] # 在x%2==0时将x添加到list
print(l) # [2, 4, 6, 8, 10]

# ! 对循环变量的操作，可以是三目运算符
l = [x if x%2==0 else -x for x in range(1, 11)] # 生成 x if x%2==0 else -x
print(l) # [-1, 2, -3, 4, -5, 6, -7, 8, -9, 10]

# 将list中的str变为小写（s.lower()返回将s中字符小写化后的str）
l = ["Hello", "World", ", qwq!!"]
l = [s.lower() for s in l] # ['hello', 'world', ', qwq!!']
print(l)
# 注意若l此时中含非str类型，迭代s并使用s.lower()就会出错，需加筛选
# 通过 isinstance(x, str) 或 type(x)==str 筛选出str类型
l = ["HeLLo", "WorLd", 123, ", qWq!!", 1.23, None]
l = [s.lower() for s in l if type(s)==str] # ['hello', 'world', ', qwq!!']
l = [s.lower() if isinstance(s, str) else s for s in l] # ['hello', 'world', 123, ', qwq!!', 1.23, None]
# l = [s.lower() for s in l] # AttributeError: 'int' object has no attribute 'lower'
print(l)



