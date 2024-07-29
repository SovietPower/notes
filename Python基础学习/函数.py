# -*- coding: utf-8 -*-

# 函数体的函数代码与主程序是隔离的，拥有独立的命名空间。
# 似乎，如果参数是可变对象，则为引用传递，否则为按值传递。如果想修改一个int（不可变），可将它放在list中传递。

# 内置/内嵌函数：https://docs.python.org/3/library/functions.html
# 类型转换函数、type()等都是内置函数
print(help(abs)) # 通过help()查看内置函数的帮助信息
print(max(1, 5, 2, 3)) # min(),max()支持两个及以上的参数
print(hex(16)) # 任意数到16进制转换
print(hex(0b10000))

# 变量可以赋值为一个函数名，以**指向**一个函数对象的引用。函数名（包括内嵌的）就是指向函数的一个变量（可以令abs=10，但会导致无法再调用abs()，若要恢复需重启Python交互环境）
# 因为abs定义在builtins模块中，所以若要让对abs的修改（如abs=10）在其它模块中也生效，需要：
# import builtins
# builtins.abs = 10
a = min
print(a(-1, 1, -5))

# 注意函数赋值给一个变量时，是为变量创造了一个新函数对象，与原函数无关系（即若删除/修改原函数不影响该变量）
def old():
	print("wuwuwu")
new=old
print(new()) # wuwuwu

del(old) # 删除该对象定义
# print(old()) # NameError: name 'old' is not defined

# def old(): # 或修改原函数，均不影响new()
# 	print("ying!")

print(new()) # wuwuwu

# 定义函数
def func(x):
	if x>=0: return x
	else:
		print("neg")
		return -x
	return # 若函数结束后未return，默认执行return，返回None。return None与return等价。
print(func(-5)) # 以0缩进做结束。在交互模式中结束函数需连续两次回车

# 调用 func.后缀 中定义的函数a，可使用import
# from func.后缀 import a
# a...

# 用pass可定义空函数
def nop():
	pass # pass什么都不执行，用做占位符（因为缩进中 什么都不写会报错）

if 3>2:
	pass # pass也可用于任意处

# 调用手写函数后，函数本身可进行类型检查
def IsNumber(x):
	if not isinstance(x, (int, float)): # 判断x为(int, float)元组
		raise TypeError("Operand type is wrong")
	return 1
# print(IsNumber("123")) # TypeError: Operand type is wrong

# 函数的参数可以直接是函数，同样也可以返回一个函数。把函数作为参数传入的函数称为高阶函数，函数式编程就是指这种高度抽象的编程范式。
def plus(a, b):
	return a+b
def compose(func, array):
	return func(*array)
print("Compose:", compose(plus, [1, 2]))

# 函数内也可以定义函数
from functools import reduce
from typing import Sequence
def str2int(s):
	DIGITS={'0':0, '1':1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
	def f(x, y):
		return x*10+y
	def char2int(s):
		return DIGITS[s]
	return reduce(f, map(char2int, "1239"))


'导入函数包'
import math


'匿名函数'
lambda x: x*x # 该写法与下面一样，供一次性传入，不需考虑命名
def f(x):
	return x*x
# 匿名函数也可以赋值给一个变量
f = lambda x: x*x
print(f(3)) # 9

# 在匿名函数上及之后加括号可调用该函数
print((lambda x: x*x)(3)) # 9


'偏函数'
# 偏函数：通过为已有函数的某些参数**kwargs设立新的默认值，或传入额外的*args，固定已有函数的某些参数，得到一个新的函数
# int(x)可将其他类型x转为int。int()默认将x视为十进制转换，代入base参数（默认为10）可将x视为任意进制，转换成int
print(int("11")) # 11
print(int("11", 2)) # 3
print(int("11", base=16)) # 17

# 当需要大量使用int(x, base=2)时，可定义int2()
def int2(x, base=2):
	return int(x, base)

print(int2("11")) # 3
print(int2("1001")) # 9

# int2()就是一个偏函数。通过functools.partial，可用一行建立一个偏函数
from functools import partial
int2 = partial(int, base=2)

print(int2("11")) # 3
print(int2("1001")) # 9
# 但偏函数只是设定了新的默认值，依旧可代入其它实参
print(int2("11", base=10)) # 11

# 偏函数实际接收了函数对象、*args、**kwargs，即不仅可设立默认值，还可传入*args
max10 = partial(max, 10) # 会在max的*args里添加10
print(max10(1, 2, 3)) # 10
print(max(1, 2, 3, 10)) # 10 与上面等价

# 偏函数有些类似简单的闭包，因为闭包也可将某些参数确定，得到新函数，不过不如偏函数自由。如将求n次幂具体化为求平方
def nth_power(exp): # exponent为次数
	def exp_of(base):
		return base**exp
	return exp_of # 返回exponent_of函数对象
square = nth_power(2) # 计算一个数的平方的函数
print(square(3)) # 9

def power(base, exp):
	return base**exp
square = partial(power, exp=2)
print(square(3)) # 9


'函数内的注释'
# 函数声明中，参数、返回值、整个函数均可加注释，注释可以是字符串，也可以是数据类型。加注释后仍可接参数默认值。这些注释信息都是函数的元信息，保存在__annotations__字典中。
def f(text:str, len:"int & >0"=10) -> int:
# 形参后可接冒号+注释（字符串或数据类型），之后可接默认值(=...)
# 函数声明最后可接 -> + 字符串或数据类型，表示函数返回值或返回类型的注释（注意仅仅是注释，可随意返回）
	# '函数的帮助说明文档'
	"""函数的帮助说明文档
这是第二行
	""" # 整个函数的说明文档，函数体的第一个'...'或"""..."""注释。后者可以输入多行。注意该例中后三引号到了下一行且仍有缩进，所以会有一个同样的缩进+换行。如果想没有换行则应紧接在注释文字的最后。
	return -len

print(f("ABC")) # -10
print(f.__annotations__) # {'text': <class 'str'>, 'len': 'int & >0', 'return': <class 'int'>}

# 使用__doc__查看函数的说明文档。
print(f.__doc__) # 函数的帮助说明文档\n这是第二行\n

def g(text:"This is str!"="qwq") -> "function g":
	return text

print(g()) # qwq
print(g.__annotations__) # {'text': 'This is str!', 'return': 'function g'}



print("\n")

"""
（多行注释：用三个'或三个"将内容包起来）

https://www.zhihu.com/question/57726430/answer/818740295

关于关键字参数：
函数定义时：
def funcname(形参表):
	函数体

函数调用时：
funcname(实参表)

实参表分为位置实参和关键字实参，位置实参一定全在关键字实参前。实参间均用,分割。
位置实参按照函数定义时的顺序，依次匹配相应形参。
关键字实参要求在实参前加上 形参名= 这样的前缀，以实现显式的参数匹配效果，不受顺序限制。

如函数：
def f(A, B, C):
	print(A, B, C)
f(1, 2, 3)即为传入形式参数，依次赋值A=1, B=2, C=3
f(B=2, A=3, C=1)即为传入关键字参数，显式赋值A=3, B=2, C=1，不受顺序限制。

形参表具体可分为五部分：
def funcname([限定位置形参], [普通形参], [可变形参args], [限定关键字形参], [特殊的限定关键字形参kwargs]):
	pass

限定位置形参（纯位置形参）：不能用关键字实参传入，只能按位置传递（positional-only）。通常因为参数名无明显意义，用关键字形式无意义。
从Python 3.8开始，可定义限定位置形参，通过/,与普通形参分割：
def func(a, b, c, /, d):
	pass
func中a,b,c只能按位置接收实际参数，d为普通形参。

普通形参既可按顺序接收，也可按关键字传递。
即可选择任意后缀的普通形参，用关键字实参传入，但位置实参一定要都在关键字实参前。
f(1, C=3, B=2) # Ok
f(A=1, B=2, 3) # Error

可变长参数：只能有0个或1个，常取名为args。会将普通实参和关键字实参之外的实参，封装为一个相应名称的tuple。它允许传入任意多个普通参数到tuple。
如果要用特殊形参，则前面的普通形参不能用关键字传递。
def func(a, b, *args, x, y):
	pass
用*标记可变长参数。可传入list或tuple（前面加*）。

限定关键字形参（命名关键字参数）：限制这些参数只能按关键字传递（keyword-only），不能按位置传递。通常因为后面几个形参名具有明显含义，显式写出更具可读性。
通过*,与普通形参分割。若前面有特殊形参*args，则不加*,分割（因为args有个*）。
def func(其它形参, *, a, b):
	pass
func中a,b为限定关键字形参，调用时必须显示写出，即：func(其它实参, a=.., b=..)（限定关键字形参顺序当然任意）

特殊的限定关键字形参：只能有0个或1个，常取名为kwargs。会将未与形参成功匹配的关键字实参，封装为一个相应名称的dict。它允许传入任意多个关键字实参到dict。
def func(a, b, *args, x, y, **kwargs):
	pass
用**标记关键字形参。可传入dict（前面加**）。

1. 与有无默认值无关，位置实参永远按位置传递给*或*args之前对应的形参（即限定位置形参和普通形参），多余的位置实参传入*args（如果有的话），关键字实参则匹配剩下的普通形参和限定关键字形参（非限定位置形参），多余的关键字实参则传入**kwargs（如果存在的话）。
2. 没有*args时，位置实参不能多于限定位置形参和普通形参的总量。
3. 没有**kwargs时，关键字参数必须在普通形参和限定关键字形参中存在。
4. 除*args和**kwargs外所有没有默认值的形参都必须匹配到值。
5. 同一形参不能被匹配两次。

对于list或tuple，可通过前面加*，直接将其中所有元素一次作为位置实参传入函数的 限定位置形参、普通形参、可变长参数中。
l1=[1, 2]
l2=[3, 4, 5]
def func(a, b, /, m, n, *args, kw1, kw2):
	pass
对于func(*l1, x, *l2, kw1=y, kw2=z)，会有a=l1[0], b=l1[1], m=x, n=l2[0], args=(l2[1], l2[2]), kw1=y, kw2=z

对于dict，可通过前面加**，直接将其中所有元素一次作为位置实参传入函数的 限定位置形参、普通形参、可变长参数中。


形参默认值：
默认值的设定规则：
1. 两个特殊形参*args和**kwargs不能设定默认值（或者认为它们默认值就是空元组和空字典）。
2. 默认值可以从限定位置形参或普通形参中的任意一个开始设定，这时需将后面剩下的所有限定位置形参和普通形参都设定默认值；限定关键字形参的默认值则可以随意设定，无需考虑顺序。也就是说在遵循上面的形参规则的前提下，除了限定关键字形参，所有带默认值的形参必须位于无默认值的形参之后。
3. 建议为所有限定关键字形参都设定默认值。
4. 建议使用不可变对象，如整数、浮点数、字符串、True、False、None或以上类型组成的元组等设定默认值，因为默认值只会在函数定义时被设定一次，如果是可变对象，一旦在函数内部被原地修改，效果会保留至以后每次的函数调用，不会被重新初始化。
5. 如果要使用某个可变对象作为默认值，比如列表，或者要设定依赖于其他参数的默认值，建议设成None，然后在函数体第一句判断是否为None，是则赋值为空列表。
（4.5.见下）

"""

# 函数可返回tuple，返回一个tuple时可省略括号。多个变量可同时接收一个tuple，会按位置依次赋值
def move(x, y, dis=1, angle=0): # 同C++，可使用默认参数，但必须必选参数在前、默认参数在后
	nx = x+dis*math.cos(angle)
	ny = y+dis*math.sin(angle)
	return nx, ny # 返回一个tuple

x, y  = move(1, 1, math.sqrt(2), math.pi/4)
print(x, y) # 用x, y接收tuple
t = move(1, 1, math.sqrt(2), math.pi/4)
print(t) # 返回一个tuple

t = move(1, 1) # dis=1, angle=0
t = move(1, 1, 2) # angle=0
t = move(1, 1, angle=math.pi) # dis=1 对于多个默认参数的情况，可通过声明参数名称来自定义任意的默认参数

# 注意默认参数需指向不变对象，否则会被修改（类似static）（可以用来做其它事）
def f(L=[]): # 以list作为参数，空list[]为默认参数，是可变的
	L.append("A")
	return L

print(f([])) # ['A'] 注意不是print(f)，f是一个指向函数的引用，会返回地址
print(f()) # ['A']
print(f()) # ['A', 'A']
print(f()) # ['A', 'A', 'A']
# 默认参数L也是一个变量，它指向对象[]，所以对默认参数的修改会永久修改它（但如果没用默认参数，如f([])，则不会修改默认参数）

# 上述正确写法为：用不变对象None
def f(L=None):
	if L==None: L=[]
	L.append("A")
	return L

print(f()) # ['A']
print(f()) # ['A']
print(f()) # ['A']


# 可变参数：允许传入0个或任意个参数，这些可变参数在函数调用时自动组装为一个tuple（所以其不可修改）
def Calc(num): # 一般写法就是 将list/tuple作为参数传递
	sum=0
	for x in num:
		sum+=x
	return sum

print(Calc([1, 2, 3])) # 但要求调用时传入一个list或tuple
print(Calc((1, 2, 3)))

def Calc(*num): # 在参数前加*号，变为可变参数，在调用时就不需传list或tuple
	sum=0
	for x in num:
		sum+=x
	return sum

print(Calc(1, 2, 3)) # 可直接传入任意个参数
print(Calc()) # 传入0个也可

# 如果有一个list/tuple，可在前面加*，来作为可变参数
A=[1, 2, 3] # A=(1, 2, 3)
print(Calc(*A))
print(Calc(A[0], A[1], A[2])) # 两种写法等价，但*A方便


# 关键字参数：允许传入0个或任意个含参数名的参数，这些关键字参数在函数内部自动组装为一个dict（该dict是副本，不影响传入的参数值）
# 关键字参数前的都是位置实参（位置实参一定在关键字实参前），按照位置依次赋值；
def f(A, B, **C): # A,B为必选参数，C为关键字参数，可在C处传入任意个参数
	print("A=", A, " B=", B, " C=", C, sep='')

# 传入的任意个C参数，组装为一个叫C的dict。
print(f(1,2)) # A=1 B=2 C={}\n None
f(1, 2, name="Li", age=20) # A=1 B=2 C={'name': 'Li', 'age': 20}

# 如果有一个dict，可在前面加**，来作为关键字参数
d={"name":"Li", "age":20, "gender":"Female"}
f(1, 2, **d) # A=1 B=2 C={'name': 'Li', 'age': 20, 'gender': 'Female'}
f(1, 2, name=d["name"], age=d["age"], gender=d["gender"]) # 两种写法等价，但**d方便


# 限定关键字形参（命名关键字参数）：限制可传入关键字参数的名字
def f(A, B, *, name, age): # 使用一个特殊分隔符*，*后面的参数均为命名关键字参数
	print(A, B, name, age)

f(1, 2, name="Li", age=12)
f(1, 2, age=12, name="Li")



def f(A, B, C):
	print(A, B, C)

f(1, C=3, B=2)
# f(A=1, B=2, 3) # Error

# 例子：定义函数，返回多个数相乘后的结果
def mul(x, *y):
	print(x, y, type(y))
	return x * mul(*y) if y else x

print(mul(1,2,3)) # 6




