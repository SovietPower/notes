# -*- coding: utf-8 -*-

'map'
# map(func, iterable, ...) 接收两个（或多个）参数，一个函数func和一个（或多个）Iterable序列(list, tuple, ...)。map将传入的Iterable中的元素依次作为函数func的参数传入，并将func依次返回的结果作为一个新的Iterable对象来返回。
# 注意func一般只能有一个参数，多参数的函数一般用list/tuple整合为一个参数传入，但也可用多个Iterable序列传入，如：
print(list(map(lambda x, y : x+y, [1, 3, 5], [2, 4, 6]))) # [3, 7, 11]
def f(x, y, z):
	return x+y+z
print(list(map(f, [1, 2, 3], [4, 5, 6], [7, 8]))) # [12, 15] 只计算Iterable中元素最少的个数次函数

# 注意func是最终的func，可以代任意一个函数，只要这个函数最终返回一个只有相应数量参数的函数对象。
# map()为高阶函数，使用map()能把运算规则抽象，更易直观看出代码在做什么（有时也更简洁）

# 因为map()返回的是Iterator，所以其计算是惰性的，只有在取map()结果（next()或for迭代）时才会开始代入一个元素、并返回当前代入元素的返回值。
# 彻底一次得到map()结果需用list(map())。
it = map(lambda x: x*x, [1, 2, 3, 4, 5])
print(next(it), next(it), next(it)) # 1 4 9

def f(x):
	return x*x
l = [1, 2, 3, 4, 5]

for x in map(f, l):
	print(x, end=" ") # 1 4 9 16 25
print()

# list(map(..))将map()返回的Iterable（其实就是map函数）转为list，方便一次输出
print(list(map(f, l))) # [1, 4, 9, 16, 25]

# 将list中的元素转为str
print(list(map(str, l))) # ['1', '2', '3', '4', '5']

# 输入空格隔开的若干数
# a, b, c = map(int, input().split()) # 分别读入
# a = list(map(int, input().split())) # 将读入存储到a序列中
# a = map(int, input().split()) # 错的。注意要转list！这样相当于令a为相应map函数


'reduce'
# reduce(func, iterable) 接收一个函数、一个Iterable序列a（同map()），会将函数func依次作用在序列a上。func必须接受恰好两个参数，reduce()会将a的前两个元素代入func()，并将返回结果和a的下一个元素再代入func()...直到全部代入，返回最终的func()返回值。
# 即：reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)
from functools import reduce # reduce()需调用
def add(a, b): # 对序列求和，等价于sum([..])
	return a+b
print(reduce(add, [1, 2, 3, 4])) # 10

# 将序列转换为一个int
def f(x, y):
	return x*10+y
print(reduce(f, (1, 2, 3, 9))) # 1239

# Iterable可作为参数，所以map()、generator均可作为reduce()的参数，用于生成参数序列。
g=(x for x in range(1, 10, 2))
print(reduce(f, g)) # 13579

# 将str转换为一个int（即int(str)）
def f(x, y):
	return x*10+y

def char2int(s): # 其实就是int()
	digits={'0':0, '1':1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
	return digits[s]

print(reduce(f, map(char2int, "1239"))) # 1239

# 将str转换为一个int 可整理为一个通用函数
def str2int(s):
	DIGITS={'0':0, '1':1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
	def f(x, y):
		return x*10+y
	def char2int(s):
		return DIGITS[s]
	return reduce(f, map(char2int, "1239"))

# 用lambda函数可进一步简化
DIGITS={'0':0, '1':1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
def char2int(s):
    return DIGITS[s]
def str2int(s):
    return reduce(lambda x, y: x*10+y, map(char2int, s))

# 将str转换为一个float
def str2float(s):
	DIGITS={'0':0, '1':1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
	def char2int(s):
		return DIGITS[s]
	def f(x, y):
		return x*10+y
	def g(x, y):
		return x*0.1+y
	s1, s2 = s.split('.')
	s2 = s2[::-1] # 反转s2
	return reduce(f, map(char2int, s1))+0.1*reduce(g, map(char2int, s2))
print(str2float("123.45"))


'filter'
# filter(func, iterable) 接收一个函数、一个Iterable序列a，同map()一样会将a中的值依次传入func，但只保留a中使func返回True的元素，丢弃使func返回False的元素，并生成Iterable的序列、返回这个新的Iterable对象。
# 用于筛选。注意func需只能有一个参数、只能有一个Iterable序列（不同于map()）。
# 注意func是最终的func，可以代任意一个函数，只要这个函数最终返回一个只有一个参数的函数对象。例子：见下筛质数。

# 因为filter()返回的是Iterator，所以其计算是惰性的，只有在取filter()结果（next()或for迭代）时才会开始筛选、并返回下一个筛选出的元素。
# 彻底一次得到filter()结果需用list(filter())。
it = filter(lambda x: x&1, range(1, 11))
print(next(it), next(it), next(it)) # 1 3 5

# 筛选奇数
def is_odd(x):
	return x&1
print(list(filter(is_odd, range(1, 11)))) # [1, 3, 5, 7, 9] 注意转list
print(list(filter(lambda x: x&1, range(1, 11)))) # [1, 3, 5, 7, 9] 注意转list

# 筛选掉list中空的str
def not_empty(s):
	return s and type(s)!=str or s and s.strip() # str.strip([chars])会生成移除str头尾指定字符chars后的字符串。chars默认为空格和换行符
print(list(filter(not_empty, ["A", " ", "BC", None, 123]))) # ['A', 'BC', 123]

# 筛选N以内的质数
def odd_generator(): # 定义生成全体奇数的生成器
    n = 1
    while True:
        n+=2
        yield n
def f(x):
	return x%n>0
def _not_divisible(n):
	return f # 注意是返回f（一个函数对象），不是f(x)（一个bool值）。函数对象才能作为filter()的第一个参数。
	# return lambda x: x % n > 0 # 也可
def primes(): # 定义全体质数生成器
    yield 2
    it = odd_generator() # 初始序列
    while True:
        n = next(it) # 返回序列的第一个数，即质数
        yield n
        it = filter(lambda x: x%n>0, it) # 筛掉x%n==0的数，得到新序列
        # it = filter(_not_divisible(n), it) # 也可
N=20
for n in primes():
    if n<=N:
        print(n)
    else:
        break

# 筛选回文数
def is_palindrome(n):
	return str(n)==str(n)[::-1]
print(list(filter(is_palindrome, [1, 2, 3, 10, 11, 12, 100, 101, 102]))) # [1, 2, 3, 11, 101]


'sorted'
# sorted(iterable, key=None, reverse=False) 是内置的排序函数，参数为所有可迭代对象Iterable，会返回一个排好序的list（新的变量，不会修改原参数）
# key函数是用来自定义比较的函数，会将可迭代对象中的元素代入计算，根据计算出的元素排序。
# reverse默认为False，升序排序；代入True为降序排序。
# key, reverse为限定关键字参数，使用时必须传入函数形参名。
# 与list.sort()的不同：list.sort()的对象只能是list，且会直接修改原list，返回值为None
# 与C++ sort()的cmp()函数相比，key需按照判断标准，将元素抽象成一个可比较元素返回，而不能用两者间比较作为判断依据。

print(sorted([-4, 3, -1, -5, 2])) # [-5, -4, -1, 2, 3]
print(sorted([-4, 3, -1, -5, 2], key=abs)) # [-1, 2, 3, -4, -5]

print(sorted("DBCA")) # ['A', 'B', 'C', 'D']
# 直接对dict排序，会对key排序，并返将key排好序的key列表
print(sorted({"C":2, "D":3, "A":0, "B":1})) # ['A', 'B', 'C', 'D']

# 字符串默认按字典序排序
print(sorted(["bb", "ba", "A", "Z", "y"])) # ['A', 'Z', 'ba', 'bb', 'y']
# 通过key，可实现忽略大小写的字典序排序。注意是str.lower不是str.lower()！前者是函数对象，后者是一个str。
print(sorted(["bb", "ba", "A", "Z", "y"], key=str.lower)) # ['A', 'ba', 'bb', 'y', 'Z']
print(sorted(["bb", "ba", "A", "Z", "y"], key=str.lower, reverse=True)) # ['Z', 'y', 'bb', 'ba', 'A']

l = [("bb", 4), ("ba", 5), ("A", 6), ("z", 1)]
# 元组默认按字典序排序
print(sorted(l)) # [('A', 6), ('ba', 5), ('bb', 4), ('z', 1)]
# 按第二关键字排序
def f(t):
	return t[1]
print(sorted(l, key=f)) # [('z', 1), ('bb', 4), ('ba', 5), ('A', 6)]





