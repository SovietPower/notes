# -*- coding: utf-8 -*-

# 数值类型有四种（Python3中三种）：int, long（数后需有l或L后缀，Python3中取消。）, float, complex（a+bj或complex(a,b)）


a = input("Please input something..\n") # input()返回str
print("The type of %s is %s\n" % (a, type(a))) # 使用type()查看变量类型
a = int(input("Please input again..\n")) # 使用类型转换，从input()输入int
print("The type of %d is %s\n" % (a, type(a)))

a = 0b110011 # 2进制 0b..
print(a)
a = 0o63 # 8进制 0o..或0O..
print(a)
a = 0x33 # 16进制 0x..或0X..
print(a)

# 浮点数
a = 3.1415e2 # 支持科学计数法
print(a)
a = 31415e-2
print(a)

# 复数
a = 1+2j # 用j表示复部而不是i
print(a)
print(type(a))

# bool，只含True False，为int的子集
# 只要是空/为0的对象，都是False（如None，False，0, 0.0, 0j, '', "", [], (), {}）；有东西/有值就是True
print(bool(None)) # 任何类型可以通过bool()转换为bool值
print(bool([]))
print(bool([1, "ABC"]))

# 数据显示类型转换
print(int(3.9))
print(type(int("123")))

print(str(3.9))
print(str(True))
print(str([]))
print(str([1, 2, "ABC"]))

print(int("9")) # 9
# int("ABC") # 错。str内需是合法的int类型
# int("9.6") # 错。同上，只能是int

# 对于实数字符串，使用float转换即可
print(float("9")) # 9.0
print(float("9.6")) # 9.6

# 也可简单分类讨论
def f(s):
	if '.' in s: return float(s)
	else: return int(s)
print(f("9"), f("9.6")) # 9 9.6




