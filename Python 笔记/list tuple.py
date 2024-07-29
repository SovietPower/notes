# -*- coding: utf-8 -*-


'list'
# list：有序动态列表，类似vector
classmates = ['A', 'B', 'C']
len(classmates) # 长度
classmates[0] # 访问，注意x<len
classmates[2]
classmates[-1] # 访问[-x]与访问[len-x]等价，注意0<x<=len也不能越界

classmates.insert(1, 'A2') # 在1处插入元素，变成：A A2 B C
classmates.pop(1) # 删除1处的元素，变成：A B C
classmates.append('D') # 在最后插入元素
classmates.pop() # 删除末尾元素

classmates[1] = 'B1' # 赋值

# 使用 + 拼接list
print([1, 2] + [3])  # [1, 2, 3]
print([1, 2] + [[3]])  # [1, 2, [3]]

# 定义一个定长数组，并初始化为0
A = [0]*10
A = [0 for _ in range(10)] # 两种写法均可
A = [0 for i in range(10)] # _可以是任意名字的变量
print(len(A),A)

L = ['ABC', 123, True] # list里面的元素的数据类型也可以不同
s = ['python', 'java', ['asp', 'php'], 4] # list元素可以是另一个list。此时s是一个二维数组，但只有s[2]是二维的
print(s[1])
print(s[1][0]) # 会返回作为字符串的s[1]的第0个字符
print(s[2])
print(s[2][1])
print(s[2][1][0]) # 会返回作为字符串的s[2][1]的第0个字符
print(s[3])
# print(s[3][0]) # Error

E = [] # 空list

L = [3, 2, 1, 2.5]
L.sort() # list.sort() 对list进行sort（list中元素需可比，数字与字符串不能同时存在）
print(L)

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


'tuple'
# tuple：有序元组，类似定长数组，但一旦初始化就不能修改，且定义时元素就需被确定。
# tuple不可变，所以比list更加安全。如可以，应尽量使用tuple。
classmates2 = ('A', 'B', 'C')
# 访问同list，但是没有insert,pop,append等修改
classmates2[0]
classmates2[-1] # classmates[len-1]

t = (1, 2)
t = () # 空tuple
print(t) # 输出()
t = (1) # 此时认为()是数学运算中的括号，所以t=1
print(t)
t = (1, ) # 定义只有1个元素的tuple时必须加一个逗号，来消除歧义
print(t) # 输出(1,)。显示只有1个元素的tuple时，也会加一个逗号，来消除歧义
'注意写单元素的tuple时一定要多一个逗号，否则不会被识别成tuple；多元素的tuple加不加最后一个逗号都可'

t = ('a', 'b', ['A', 'B']) # 当tuple中含list时，其list是可变的，但tuple仍不可变（t[2]相当于指向list的一个指针）
t[2].append('C')
print(t[2])





