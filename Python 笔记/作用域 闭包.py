# -*- coding: utf-8 -*-

'''
作用域：
作用域是一个 Python 程序可以直接访问命名空间的正文区域。
在一个 python 程序中，直接访问一个变量，会从内到外依次访问所有的作用域直到找到，否则会报未定义的错误。
变量的作用域取决于这个变量是在哪里赋值的。变量的作用域决定了哪一部分的程序可以访问哪些特定的变量名称。
当变量在一个作用域中初次赋值时，该变量会在当前作用域中被创建，创建后（或说赋值后）才能在当前作用域中被修改。

Python 的作用域一共有4种：
L（Local）：最内层，包含局部变量，比如一个函数/方法内部。
E（Enclosing）：嵌套作用域，包含了非局部(non-local)也非全局(non-global)的变量。比如两个嵌套函数，一个函数（或类） A 里面又包含了一个函数 B ，那么对于 B 中的名称来说 A 中的作用域就为nonlocal。
G（Global）：当前脚本的最外层，比如当前模块的全局变量。
B（Built-in）： 包含了内建的变量/关键字等，最后被搜索。
规则顺序： L –> E –> G –> B，在局部找不到，便会去局部外的局部找（例如闭包），再找不到就会去全局找，再者去内置中找。

内置作用域通过一个名为 builtin 的标准模块实现，但这个变量名自身并没有放入内置作用域内，所以必须导入这个文件才能够使用它。
>>> import builtins
在Python3.0中，可使用以下的代码来查看它预定义了哪些变量（当然要先导入）：
>>> dir(builtins)

Python 中只有模块（module），类（class）以及函数（def、lambda）才会引入新的作用域，其它的代码块（如 if/elif/else/、try/except、for/while等）不会引入新的作用域，也就是说这些语句内定义的变量，外部也可以访问。
当然能访问的前提是 这些代码块中 成功初始化了该变量。如if：
x=int(input())
if x>0: n=1
print(n)
当x>0时，正常调用n并输出1；否则仍会报错未定义：NameError: name 'n' is not defined。

# ! 注意，循环语句并非新的作用域，循环变量会覆盖之前定义的同名变量。

'''

'''
global, nonlocal:
当内部作用域想**修改**外部作用域的**不可变类型**（list, dict, set外）时，需使用 global 和 nonlocal 声明该外部变量，否则会被视为定义了一个新的局部变量；
只要内部域中有任何修改语句，无论在哪，都应在第一次调用前先声明。
但若只访问不修改，不需声明（会自动在外部作用域找该声明）。
当内部作用域要修改全局变量时，需先使用 global 声明；要修改嵌套作用域（enclosing 作用域，外层但非全局作用域）中的变量时，需先使用 nonlocal 声明。
'''
# 只访问全局变量而不修改，不需声明。


x=0
def f():
	print(x)
f() # 0
print(x) # 0
# 要在局部内修改全局变量，就需在第一次使用前声明global，否则报错：UnboundLocalError: local variable 'x' referenced before assignment
x=0
def f():
	global x
	# x = 1 # 如果不加 global x，则这样是新建了一个局部变量
	# x += 1 # 如果不加 global x，则这样找不到 x 的声明
	print(x)
	# x = 1 # 如果不加 global x，则该作用域视 x 为局部变量（修改了），此时前面的 print(x) 会找不到 x 的声明
f() # 0
print(x) # 1
# 未在第一次使用前声明，会报错：SyntaxError: name 'x' is used prior to global declaration
'''
x=0
def f():
	print(x)
	global x # Error
	x+=1
f()
print(x)
'''
# 要修改全局作用域的可变类型（list, dict, set）时，不需声明（声明好像也没事？）。
x=[0]
def f():
	print(x)
	x.append(1)
f() # [0]
print(x) # [0, 1]

# 只访问嵌套作用域（enclosing作用域，外层非全局作用域）中的变量而不修改，不需声明。
def outer():
	x=0
	def inner():
		print(x)
	inner()
	print(x)
outer()
# 要修改嵌套作用域中的变量，就需在第一次使用前声明nonlocal，否则报错：UnboundLocalError: local variable 'x' referenced before assignment
def outer():
	x=0
	def inner():
		nonlocal x
		print(x)
		x=1
	inner() # 0
	print(x) # 1
outer()
# 要修改嵌套作用域的可变类型（list, dict, set）时，不需声明（声明好像也没事？）。
def outer():
	x=[0]
	def inner():
		print(x)
		x[0]=1
	inner() # [0]
	print(x) # [1]
outer()

# ! 注意，if 不会引入新的作用域，所以函数可以访问在 if __name__ == "__main__" 内定义的变量，因为它们是全局（模块级）的
def f():
	# a = 1 # 未使用 global 声明时，这样是定义局部变量
    print(a)
def main():
    a = 3 # 函数 f 不会读到该局部变量
    f()
if __name__ == "__main__":
    a = 1 # 函数 f 可以读取该全局变量。如果修改需使用 global a 声明
    f()
    main()


'''
闭包函数（闭合函数）：返回一个函数对象，且返回的这个函数一般引用了外部变量（一般是父函数的参数或父函数定义的变量）。返回的这个函数不一定要return。
在父函数中定义一个子函数，子函数中调用了父函数的临时变量，并且父函数的返回值是对子函数的引用。这样就构成了一个闭包。
一般函数在结束时，其内部所有东西都会释放掉，局部变量会消失。但对于闭包函数，如果子函数用到了父函数中的变量或参数，这些用到的变量会绑定给内部函数，不被释放，而父函数本身依旧结束、其它临时变量依旧被释放。
当子函数调用父函数中的不可变类型时，若操作只有访问，可直接调用；若有修改，则需在调用该变量前用nonlocal声明，或将该变量转为可变对象（如list）后直接调用（Python 2中没有nonlocal关键字，只能用后者）

一般闭包函数返回的子函数引用会赋给一个变量，该变量可继续拿来调用子函数。每次调用一个变量的子函数时，会执行一次子函数并销毁该子函数，但子函数对其绑定的嵌套作用域中的元素做修改时，该修改会保留（保存运行环境）。
总结：子函数绑定的嵌套作用域中的变量，相当于C++中static，每次调用该子函数造成的修改会保留，而子函数会正常结束。但这个static的初值是由父函数确定，且可生成static初值不同的任意个子函数引用，用变量保存。
其实更类似一个struct，其元素在初次调用时确定，且它本身含有一个可调用的子函数，子函数可使用这些元素并修改。但引用该struct的元素（即嵌套作用域的变量）需通过 __closure__。
或说闭包为子函数生成了一个命名空间。

父函数的参数和嵌套作用域中变量称为自由变量，它们可以被绑定到子函数中。
闭包函数比普通函数多一个__closure__属性。要显示查看闭包中 用到的嵌套作用域的变量，需使用__closure__属性。
__closure__返回一个含所有用到的外部变量的地址的只读元组。
若子函数中没有引用外部变量，则不存在闭包元素，__closure__可返回None。
若父函数没有返回子函数引用，则不形成闭包，父函数不存在__closure__属性，使用__closure__会报错。

'''



# 闭包函数可用于进一步抽象一个函数，或使其更简洁通用
# 如：求一个数的n次幂闭包函数nth_power(n)，可通过预先代入n得到一个求特定n次幂的子函数对象，之后可调用该对象就特定n次幂，只需要传入参数base
# 因为子函数保存了调用父函数时的参数。
def nth_power(exp): # exponent为次数
	def exp_of(base):
		return base**exp
	return exp_of # 返回exponent_of函数对象
square = nth_power(2) # 计算一个数的平方的函数
cube = nth_power(3) # 计算一个数的立方的函数
print(square(3))  # 计算3的平方：9
print(cube(3)) # 计算3的立方：27
# 等价的写法：
def nth_power(base, exp):
	return base**exp
print(nth_power(3, 2)) # 计算3的平方：9
# 当需调用多次平方函数时，显然square比频繁使用nth_power(x, 2)更简洁、直观
# 当需频繁使用多类特定次幂的函数时，可轻松定义square、cube等闭包函数并使用，比频繁调用nth_power(x, 2/3/..)更简洁、直观
# 此外，因为可保存运行环境，如果子函数每次都需做特定的准备工作，可以在父函数中预先实现，之后任意次调用子函数都无需再做。

# 再如，定义一条直线，可在调用父函数时确定系数，确定一条直线，之后调用子函数求值
# 这样确定一条直线只需要一行代码、对特定的一条直线求点值只需要一个参数x
def line_coef(k, b):
	def line(x):
		return k*x+b
	return line
lineA=line_coef(1,0) # y=x+0
lineB=line_coef(2,1) # y=2x+1
print(lineA(1)) # x=1 y=1
print(lineB(1)) # x=1 y=3

# __closure__使用示例
def nth_power(exp): # exponent为次数
	x=1
	def exp_of(base):
		print(x)
		return base**exp
	return exp_of # 返回exponent_of函数对象
square = nth_power(2) # 计算一个数的平方的函数
print(square.__closure__) # (<cell at 0x000002000EB7A640: int object at 0x000002000E616950>, <cell at 0x000002000EB7A550: int object at 0x000002000E616930>)
print(type(square.__closure__[0])) # <class 'cell'>
# cell的取值使用cell_contents
print(square.__closure__[0].cell_contents) # 2 即第一个外部变量exp
# 全部输出
for x in square.__closure__:
	print(x.cell_contents) # 2 1

# 注意，返回子函数f时子函数f()并没有被立即执行，而是直到调用了f()才执行
# 子函数用到的嵌套作用域中的变量取值，是父函数结束前时它的取值（实质就是它会在父函数或子函数中被修改，但不会被释放）。
# 所以若子函数用到的是循环变量，或是后续会发生变化的量，其中的值也会随之被修改。
def outer():
	l=[]
	for i in range(3):
		def f():
			return i*i
		l.append(f) # 仅传入f，不会执行f
	return l
f0, f1, f2= outer()
print(f0(), f1(), f2()) # 输出4 4 4 而不是0 1 4，因为父函数结束前i就是2，在子函数中取值就为2。

# 若要想正确输出0 1 4，则需将**当时**的i绑定给子函数f，可以通过再弄一个含i变量的f的父函数实现
def outer():
	def f(i):
		def g():
			return i*i
		return g
	l=[]
	for i in range(3):
		l.append(f(i)) # 传入f()则会执行f()
	return l
f0, f1, f2= outer()
print(f0(), f1(), f2()) # 输出0 1 4，因为f会在outer内执行，并分别被传入0, 1, 2且以后不会变，在子函数g中的取值就为0, 1, 2。

# 做一个计时器的两种方法（利用闭包类似包含static！）
# 1. 通过nonlocal声明使用嵌套作用域的变量
def Counter():
	tm=0
	def counter():
		nonlocal tm
		tm+=1
		return tm
	return counter
c=Counter()
print(c(), c(), c()) # 1 2 3

# 2. 通过在父函数中建立可变类型，实现子函数直接调用
def Counter():
	tm=[0]
	def counter():
		tm[0]+=1
		return tm[0]
	return counter
c=Counter()
print(c(), c(), c()) # 1 2 3





