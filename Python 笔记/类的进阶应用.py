# -*- coding: utf-8 -*-


# dir() 返回一个 由对象的所有属性和方法名称 组成的字符串list
# print(dir("ABC")) # ['__add__', '__class__', ..., 'upper', 'zfill']
class Student(object):
	name="None"
	def __init__(self, name, score):
		self.name=name
		self.score=score
	def get_score(self):
		return self.score

A = Student("A", 80)
# 实例化后的A比Student类多一个属性score。实例化变量可任意绑定属性、方法
print(dir(A)) # ['__class__', '__delattr__', ..., 'get_score', 'name', 'score']
print(dir(Student)) # ['__class__', '__delattr__', ..., 'get_score', 'name']


'''
hasattr(obj, 'x') 判断对象obj是否含有属性x或方法x
setattr(obj, 'x', val) 为对象obj设置一个属性x或方法x，值为val（val可为数值也可为函数，由x确定）
getattr(obj, 'x') 获取对象obj的属性x
getattr(obj, 'x', def) 获取对象obj的属性x或方法x，若obj不含x则返回默认值def

这三类attr操作中的'x'允许是任意字符串变量，这提供了更自由的操作（如由用户端输入并访问）。注意它们仍是外部对类的操作，无法直接访问__开头的私有变量（即私有变量也对用户端隐藏）。
'''
class ABC:
	def __init__(self):
		self.x = 3
	def f(self):
		return self.x * self.x

abc = ABC()
print(hasattr(abc, 'x')) # True
print(hasattr(abc, 'y')) # False

setattr(abc, 'y', "qwq") # 为abc设置字符串y
print(hasattr(abc, 'x')) # True
print(getattr(abc, 'y')) # qwq
print(abc.y) # qwq

# print(getattr(abc, 'z')) # AttributeError: 'ABC' object has no attribute 'z'
print(getattr(abc, 'z', 404)) # 404

# 同样可以判断方法
print(hasattr(abc, 'f')) # True
print(hasattr(abc, 'g')) # False

setattr(abc, 'g', lambda x: x*x) # 为abc设置函数g
print(hasattr(abc, 'g')) # True
print(abc.g(3)) # 9

# 当已知属性或方法名称时（如abc的属性x），就没必要使用getattr。但未知具体名称时（如要访问的属性名存储在某个变量中，也可手动输入），就用到getattr。此外getattr还提供了返回默认值的功能。
attr_name = 'x'
print(getattr(abc, attr_name, 0)) # 3 getattr可访问一个变量名称的属性/方法，也可返回默认值
print(abc.x) # 3


'@property装饰器'
# 类中@property装饰器修饰的方法，可以像属性一样被调用

# 在绑定类属性时，经常需要对值进行检查。如果每次都使用 先检查 再属性=值 的方式，会非常麻烦，所以通常在类中定义 对属性进行操作的函数。
class Student(object):
	def get_score(self):
		return self.score

	def set_score(self, val):
		if not isinstance(val, int):
			raise ValueError('Score must be an integer!')
		if val<0 or val>100:
			raise ValueError('Score must be between 0~100!')
		self.score=val

A = Student()

A.score = 1.5
print(A.score) # 1.5

# 使用函数限制参数
# A.set_score(1.5) # ValueError: Score must be an integer!

A.set_score(1)
print(A.get_score()) # 1

'''
通过@property装饰器，我们可以像调用属性一样使用限制函数，既能简单访问，又可检查参数或在赋值或读取时进行其它操作

用@property修饰一个方法，使该方法"变为"属性，名称不变。
如果用@property修饰方法x，则相当于定义了名为x的属性，并将该方法作为x的getter方法（用于读取x）
如果用@x.setter修饰另一个方法y，则相当于定义了对属性x进行赋值的操作，并将该方法作为x的setter方法（用于赋值x），x为可读写属性。
如果未定义@x.setter，则x无法修改，为只读属性。
'''
class Student(object):
	@property
	def score(self):
		return self._score # 注意此时类属性不能叫score，否则就不能对self.score进行赋值了（因为 score.setter 中的 self.score=... 会循环调用score.setter）

	@score.setter
	def score(self, val):
		if not isinstance(val, int):
			raise ValueError('Score must be an integer!')
		if val<0 or val>100:
			raise ValueError('Score must be between 0~100!')
		self._score=val

	@property
	def grade(self): # 定义一个只读属性grade，在读取时grade由score自动计算
		return "A" if self.score>=4 else "B" if self.score>=3 else "C"

A=Student()

# A.score=1.5 # ValueError: Score must be an integer!
A.score = 1
print(A.score) # 1
print(A.grade) # C


'静态方法、类方法'
# staticmethod, classmethod装饰器内容，见 装饰器.py。


'多重继承'
# 通过继承，子类可同时获取多个父类的所有功能：子类不只能继承一个父类形成树，而是能继承多个父类形成DAG（多重继承）（通过拓扑确定顺序）
# 如果继承的多个父类含有相同名称的属性/方法，则选择最靠前出现的父类中的该属性/方法

# 比如对于动物Animal，可以根据种类分子类，也可以根据是否能飞Flyable或是否能跑Runnable分类。如果子类只能继承一个父类，那么想要包含这三个分类标准，就要三层结构（能跑的分为能飞的、不能飞的，能跑且能飞的又可分为不同种类...），类是数量会指数级增长，很复杂。但通过多重继承，只需要一层结构（每个种类可同时从Animal、Flyable、Runnable继承）。
# 多重继承通常先设计主要的类层次，比如Animal先按种类分成Dog, Bird，再为它们分别添加Runnable或Flyable的类的功能。
class Animal(object):
	pass

class Runnable(object):
	def run(self):
		print("Run!")

class Flyable(object):
	def fly(self):
		print("fly!")

class Dog(Animal, Runnable):
	pass

class Bird(Animal, Flyable):
	pass


'MinIn'
# 在上面的例子中，Dog, Bird从Animal继承，属于主线继承，而Flyable, Runnable是通过多重继承"混入"的额外/可选的功能。这类设计称为MinIn。通常将Flyable, Runnable 写作FlyableMinIn, RunnableMinIn。
# 继承主线之外添加的功能便是MinIn。这些MinIn类通常是专门用于添加功能而设计的类似"模块"的东西。继承自MinIn的类和MinIn类不再是is-a的关系，而是-able的关系。
# 在设计类继承时，优先考虑通过多重继承来组合多个MinIn的功能，而不是设计复杂的层次关系。


'定制类'
# 通过object中定义的__...__方法，可深度定制类。

'__slots__'
# __slots__变量可限制该class实例能添加的实例属性，只能为其中写出的变量。它主要是作为一个内存优化工具。
# 注意，如果其子类不使用__slots__，该类的__slots__限制对继承该类的子类不起作用。
# 但如果其子类也使用__slots__，则子类会限制允许绑定的实例属性为 自身的__slots__ 加 父类的__slots__。所以如果子类使用了__slots__，但父类没有__slots__，则子类仍相当于没有__slots__限制。
class Student:
	cnt = 0
	__slots__ = ('name', 'age')

A = Student()
A.age = 19
A.name = "A"
# A.score = 80 # AttributeError: 'Student' object has no attribute 'score'
# 由于限制不能绑定cnt实例变量，所以对cnt的访问只能是对类属性的访问，因此cnt对A是只读的
# A.cnt = 2 # AttributeError: 'Student' object attribute 'cnt' is read-only


'__len__()'
# len(x)的本质是调用x的__len__()方法。只要一个对象x含__len__()方法，则可直接使用len(x)
print(len("ABC")) # 3
print("ABC".__len__()) # 3

class Student:
	def __len__(self):
		return 233
A = Student()
print(len(A)) # 233


'__str__'
# 所有对象都可以通过输出自己，来输出自己的描述信息。对于类的实例对象，如果类没有重写__str__()方法，则描述信息默认返回该对象的类名、内存地址；如果重写了__str__()，则返回该方法的返回值。
class Student(object):
	def __init__(self, name):
		self.name = name

print(Student("A")) # <__main__.Student object at 0x00000283B461CF70>
print(Student) # <class '__main__.Student'>

class Student(object):
	def __init__(self, name):
		self.name = name
	def __str__(self):
		return "Student object (name: %s)" % (self.name)

print(Student("A")) # Student object (name: A)
print(Student) # <class '__main__.Student'>


'__repr__()'
# 即使重写了__str__()，在交互模式中输入A，而不是print(A)，输出的描述信息依旧是默认的类名+内存地址，并不是__str__()中返回的。因为在交互模式中直接显示变量调用的不是__str__()，而是__repr__()。可以说__str__()返回的是用户看到的，__repr__()返回的是程序开发者能看到的，__repr__()是用于调试。

# 在交互模式下：
A = Student("A")
A # <__main__.Student object at 0x0000022698FDB3D0>
print(A) # Student object (name: A)

# 要解决这一问题，就重写__repr__()。如果返回值要和__str__()一样，可以复制一遍代码，也可以直接赋值
class Student(object):
	def __init__(self, name):
		self.name = name
	def __str__(self):
		return "Student object (name: %s)" % (self.name)
	__repr__ = __str__

# 在交互模式下：
A = Student("A")
A # Student object (name: A)
print(A) # Student object (name: A)


'__iter__()'
# list, tuple可被用于循环，因为其定义了__iter__()。只要一个类定义了__iter__()和__next__()方法，就可用于for in 循环。
# __iter__()返回一个迭代对象，for循环会不断调用该迭代对象的__next__()方法取得循环的下一个值，直到__next__()返回StopIteration错误时退出循环。
class Fib:
	def __init__(self) -> None:
		self.a, self.b = 0, 1

	def __iter__(self):
		return self # 该类的实例本身就是迭代对象

	def __next__(self):
		self.a, self.b = self.b, self.a+self.b
		if self.a > 100:
			raise StopIteration()
		return self.a

for f in Fib(): # 输出100以内的Fibonacci数列项
	print(f, end=" ") # 1 1 2 3 5 8 13 21 34 55 89
print()


'__getitem__'
# list, tuple可用[]随机读取，因为其定义了__getitem__()。只要一个类定义了__getitem__()，则可直接用下标读取元素或返回一定的值。
class Fib:
	def __getitem__(self, n):
		a, b = 1, 1
		for _ in range(n):
			a, b = b, a+b
		return a

f = Fib()
print(f[0], f[1], f[2], f[20]) # 1 1 2 10946

# list不仅支持下标访问，还支持切片。只要在类的__getitem__()中加入切片的判断，也可实现切片访问。这取决于__getitem__()中传入的参数是一个int，还是一个切片对象slice。
class Fib:
	def __getitem__(self, n):
		if isinstance(n, int):
			a, b = 1, 1
			for _ in range(n):
				a, b = b, a+b
			return a
		if isinstance(n, slice):
			beg = n.start if n.start is not None else 0
			# slice中不填写的则为None。stop不填写应为len-1，但该类没有len的定义
			end = n.stop
			a, b= 1, 1
			L = []
			for i in range(end):
				if i>=beg: L.append(a)
				a, b= b, a+b
			return L

f = Fib()
print(f[0:5]) # [1, 1, 2, 3, 5]
print(f[:10]) # [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

# 但是上面还没有对step、负数做处理，可能会出错。想彻底实现__getitem__()还是比较麻烦的。
print(f[0:5:2]) # [1, 1, 2, 3, 5]

# 注意不只是int, slice，__getitem__()的参数可以是任意类型，比如str，此时就实现了一个类似dict的对象。


'__setitem__()'
# 与随机读取元素__getitem__()对应，__setitem__()用于任意赋值。参数可以是int也可以是str等任意类型。
# 此外也有__delitem__()，用于删除任意元素。
# 这三种方法便可以实现一个dict或set。


'__eq__()'
# 如果类未定义__eq__()方法，那么该类的两个对象使用==比较时，总返回False（即使看似完全一样，不同于C）。如果定义了__eq__(self, other)，则==返回其返回值。
class Student:
	def __init__(self, name, age):
		self.name, self.age = name, age

print(Student("A",18)==Student("A",18)) # False

class Student:
	def __init__(self, name, age):
		self.name, self.age = name, age
	def __eq__(self, other): # other同样可是任意名称，只是习惯
		return True if self.name==other.name and self.age==other.age else False

print(Student("A",18)==Student("A",18)) # True
print(Student("A",18)==Student("B",18)) # False


'__lt__()'
# 如果类未定义__lt__()，则类的实例无法使用<进行比较。如果定义了__lt__()，则<的比较会返回其返回值。
class P:
	def __init__(self, x, y):
		self.x, self.y = x, y
	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)
	def __lt__(self, other):
		return (self.x, self.y) < (other.x, other.y)
	# def __le__(self, other):
	# 	return (self.x, self.y) <= (other.x, other.y)

print(P(1,2)<P(2,1), P(1,1)<P(1,1)) # True False

# 注意即使同时定义了__eq__, __lt__，也不能用<=，而是要定义__le__。不过使用@total_ordering修饰器可以，具体见下。
# print(P(1,1)<=P(1,1)) # TypeError: '<=' not supported between instances of 'P' and 'P'

'这样的方法共有：__eq__, __ne__, __lt__, __le__, __gt__, __ge__。'


'__cmp__()'
# 如果类未定义__cmp__()，则类的实例无法使用>, <进行比较。如果定义了__cmp__(self, x)，则根据它的返回值返回self与x谁在前（更小）谁在后（更大）：1则self在前，-1则x在前，0则相等。

# print(Student("A",18)>Student("B",18)) # TypeError: '>' not supported between instances of 'Student' and 'Student'


'@total_ordering'
'''
Python3中取消了__cmp__方法。代替__cmp__有两种方法：
1. __eq__, __ne__, __lt__, __le__, __gt__, __ge__中哪个需要就定义哪个。
2. 利用functools库中的修饰器total_ordering修饰类，只需要实现__eq__和__lt__, __le__, __gt__, __ge__中的任意一个（共两个）方法，即可任意比较。Python会根据这两个方法推导大小关系。
'''
from functools import total_ordering
from types import MappingProxyType, MethodWrapperType

@total_ordering
class P:
	def __init__(self, x, y):
		self.x, self.y = x, y
	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)
	def __lt__(self, other):
		return (self.x, self.y) < (other.x, other.y)
	# def __le__(self, other): # __le__也可代替__lt__
	# 	return (self.x, self.y) <= (other.x, other.y)

p1 = P(1, 4)
p2 = P(2, 3)
for expr in ['p1 < p2', 'p1 <= p2', 'p1 == p2', 'p1 >= p2', 'p1 > p2']:
	print('  Result of {}: {}'.format(expr, eval(expr)))


'__call__()'
# 当调用实例ins的方法时，通过ins.method()调用。而ins本身也可作为方法直接调用（ins()），只要它所属的类定义了__call__()方法。此时ins是可调用callable的。
# 同普通函数一样，__call__()也可加除了self以外的参数。
class Student:
	def __init__(self, name):
		self.name = name
	def __call__(self, text):
		print("I'm %s, from %s. %s!" % (self.name, self.__class__, text))

A = Student("ABC")
A("hhh") # I'm ABC, from <class '__main__.Student'>. hhh!

# callable() 可判断一个对象是否是可调用的。
print(callable(A), callable(max), callable("hhh"), callable(None)) # True True False False


'__getattr__()'
# 能默认返回值的getattr函数的加强版，当调用类中不存在attr属性/方法时，Python解释器会调用__getattr__(self, attr)，如果其中定义了对该attr的特殊处理，则会执行（如返回某个值/函数，输出某些信息）；否则正常抛出AttributeError错误。
# 注意只有在类中没找到attr，才调用__getattr__(self, attr)。
# 它实际上可以把一个类的所有属性和方法调用全部动态化处理，而不需要任何特殊手段。
class Student:
	def __init__(self):
		self.name = "ABC"
	def __getattr__(self, attr):
		if attr=="age":
			return 19 # 自定义返回值
		if attr=="f":
			return lambda x: x*x # 也可返回函数
		if attr=="socre":
			print("Visiting Score!") # 可用于输出信息

A = Student()
print(A.name) # ABC
print(A.age) # 19
print(A.f(3)) # 9
print(A.score) # None 定义的__getattr__()默认返回了None

class Student:
	def __init__(self):
		self.name = "ABC"
	def __getattr__(self, attr):
		if attr=="age": return 19 # 自定义返回值
		raise AttributeError('\'Student\' object has no attribute \'%s\'' % attr)
		# 注意如果定义了__getattr__()，则不会再自行抛出AttributeError错误，而是返回None，因为__getattr__()默认返回了None。如果要抛出错误则要记得写。

A = Student()
# print(A.score) # AttributeError: 'Student' object has no attribute 'score'

# 利用__getattr__将一串链式调用 转成URL格式
class Chain(object):
	def __init__(self, path=''):
		self._path = path

	def __getattr__(self, path):
		return Chain('%s/%s' % (self._path, path))

	def __str__(self):
		return self._path
	__repr__ = __str__

print(Chain().status.user.timeline.list) # /status/user/timeline/list
# 过程：先执行Chain().status，返回Chain('/status')，再执行Chain('/status').user，返回Chain('/status/user')，再执行Chain('/status/user').timeline ...

# 利用__getattr__和__call__将一串带参数的链式调用 转成URL格式
class Chain(object):
	def __init__(self, path=''):
		self.__path = path

	def __getattr__(self, path):
		return Chain('%s/%s' % (self.__path, path))

	def __call__(self, path):
		return Chain('%s/%s' % (self.__path, path))

	def __str__(self):
		return self.__path
	__repr__ = __str__

print(Chain().users('Michael').repos) # /users/Michael/repos
# 过程：先执行Chain().users('Michael')，返回Chain('/status')('Michael')，再call Chain('/status')这个函数，参数为'Michael'，返回Chain('/status/Michael')，再执行Chain('/status/Michael').repos ...
# 注意Chain(str)是一个callable实例。


'枚举类'
# 枚举类型是用来管理一组相关的有限个数的常量的集合。枚举类型是一种不可变的类，就叫枚举类，其中的成员可直接用等号比较。获取枚举常量 既可通过成员名称，也可通过value值。
# 常规定义的常量，实际依旧是一个变量，而枚举类定义的是真正的常量。
# 使用枚举类可提高程序可读性、便于维护。

# 枚举类继承自enum.Enum类，类中定义若干常量成员。
from enum import Enum, unique, IntEnum

'''
一种简单的写法：该枚举类变量名 = Enum(类型名, (常量集合))

假设令 x = Enum(Name, (A, B, C, D))
x.__members__ 是一个存储所有内容的MappingProxyName（不可变映射类型，是另一个映射(dict)的只读视图，它不能修改，但如果它展现的映射发生了改变，它也会同步改变）。
在该例中，x.__members__为{'A': <Name.A: 1>, 'B': <Name.B: 2>, ..., 'D': <Name.D: 4>}，即含所有 '常量名': <类型.常量名: 常量标号> 的dict的只读视图。
其中的 <类型.常量名: 常量标号> 也是一个dict元素，类型.常量名是key，常量标号是value。

调用 x.A, x.B, ... 会返回 Name.A, Name.B, ...，它们属于<enum 'Name'>类型；调用 x.A.value, x.B.value, ... 会返回 Name.A.value, Name.B.value, ...，即1 2 3 4。

由上可知x实际是一个dict，A是dict元素的key，x.A 对应<Name.A: 1>这个dict元素，但实际返回key也就是Name.A，使用x.A.value即可返回value也就是1。
因为 x.A 即 Name.A 属于<enum 'Name'>类型，与其它 x.B, Name.B 是不同的<enum 'Name'>，又x.__members__只读，所以x.A, x.B, ...代表了不同常量。
即使用 x.A, x.B, x.C, x.D 可 表示或引用 不同的 任意类型的 常量。value属性可辅助使用，默认从1开始依次标号。

获取枚举常量Name.A有三种方式，通过成员名两种，通过value一种，以该例为例：
1. className.A
2. className['A']
3. className(1)
（className实际为x）

这个变量名x其实没有用，因为只需要定义一个Enum，所以通常不叫x，而是直接与Name同名。
'''
months = Enum('Month', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))

print(months.__members__) # {'Jan': <Month.Jan: 1>, 'Feb': <Month.Feb: 2>, ..., 'Dec': <Month.Dec: 12>}
for name, member in months.__members__.items():
    print(name, ': ', member, ': ', member.value, sep='')
# Jan: Month.Jan: 1
# Feb: Month.Feb: 2...
# Dec: Month.Dec: 12

print(type(months.__members__)) # <class 'mappingproxy'>
print(type(months.__members__.items())) # <class 'dict_items'>

print(months.Jan) # Month.Jan
print(months['Jan']) # Month.Jan 因为本身是个dict（但是是<enum 'Month'>类型），所以可以通过下标访问。注意引号。
print(months.Jan.value) # 1
print(type(months.Jan)) # <enum 'Month'>
print(type(months.Jan.value)) # <class 'int'>

# 还可用通过小括号用value访问
print(months(1)) # Month.Jan
print(months(6)) # Month.June
# print(months(111)) # ValueError: 111 is not a valid Month

# 枚举类的成员可进行eq, ne比较（不能大于小于）。这样使用常量显然更直观。
m = months.Jan
print(m == months.Jan) # True
print(months.Jan == months.Feb) # False

'''
如果要自定义枚举类中的value，可通过自定义一个类实现，该类要继承Enum。
赋值的value默认是可重复的。但因为可能通过value访问，所以应确保同样的value值不被重复赋值，可以使用@unique装饰器（需调用enum.unique）。
若使用了@unique，同一value值重复出现时，会报ValueError错误。
'''
@unique
class Month(Enum):
	# 常量列表。每个常量的value都要初始化
	Jan = 'January' # 任意确定value
	June= 6
	July= 7
	Dec = 'December'
	# qwq = 6 # ValueError: duplicate values found in <enum 'Month'>: qwq -> June
	# Dec = 12 # 重复定义：TypeError: Attempted to reuse key: 'Dec'
	# Dec # 不初始化value：NameError: name 'Dec' is not defined

jan = Month.Jan
print(jan) # Month.Jan
print(Month.Jan) # Month.Jan
print(Month['Jan']) # Month.Jan 因为本身是个dict（但是是<enum 'Month'>类型），所以可以通过下标访问。注意引号。
print(Month.Jan.value) # January

# 还可用通过小括号用value访问
print(Month('January')) # Month.Jan
print(Month(6)) # Month.June
# print(Month(111)) # ValueError: 111 is not a valid Month

'''
如果要限制枚举类中的value只能为整数，可从enum.IntEnum继承（而不是Enum）。
使用@unique防止常量成员的value重复。
'''
@unique
class Month(IntEnum):
	# Jan = 'January' # ValueError: invalid literal for int() with base 10: 'January'
	Jan = 1
	June= 6


'使用type()创建类'
# 通过class可定义类：
class Student(object):
	def print(self, name="ABC"):
		print('This is %s.' % name)

# 类本身的类型是type，类实例的类型就是类本身。
# class的类型是type，因为class就是通过type()创建出来的。
print(type(Student)) # <class 'type'>
print(type(Student())) # <class '__main__.Student'>

'''
用type()创建类，需填写3个参数：
1. class名称（注意引号）。
2. 继承的父类集合 构成的tuple。注意如果tuple只有一个元素要加逗号。
3. class的方法名称和其绑定的函数 组成的dict，通过dict(方法名=函数名, ...)。

通过type()函数创建的类和直接写class是完全一样的，因为Python解释器就是用type()创建出class定义的类。
使用type()允许我们动态地创建类，即在运行期动态创建类，这是动态语言所支持的。在静态语言运行期创建类会非常复杂。
'''
def f(self, name="ABC"): # 先定义要作为方法的函数
	print('This is %s.' % name)

Student = type('Student', (object,), dict(print=f, calc=lambda self, x:x*x)) # 函数不要忘了self

A = Student()
A.print() # This is ABC.
print(A.calc(3)) # 9


'元类metaclass'
# 定义类后，可以创建该类的实例；定义metaclass后，也可以创建该metaclass的实例，但该实例为类。可以说类是由metaclass创建出的实例。
# 简单来说，定义一个metaclass（和类一样定义，一般类名以Metaclass作为后缀）（metaclass是类的模板，所以必须从type派生），然后由该元类定义一个类（需使用metaclass这一关键字参数）。metaclass定义的类会有metaclass的特定功能；当改变metaclass时，它定义的类同样会改变。这方便了类的使用。

# 若传入关键字参数metaclass，它会指示Python解释器在创建MyList时，是通过ListMetaclass.__new__()来创建，在此函数中，我们可以修改该类的定义，比如添加新的方法等。然后返回修改后的类的定义。
# __new__()方法接收四个参数：1.当前准备创建的类的对象cls；2.类的名字name；3.类继承的父类集合bases(tuple)；4.类的方法集合attrs(dict)。

# 一个简单的metaclass例子，实际比较复杂，先跳过。
# 通过自定义list元类，得到一个自定义的list。
class ListMetaclass(type):
	def __new__(cls, name, bases, attrs):
		attrs['add'] = lambda self, value: self.append(value)
		return type.__new__(cls, name, bases, attrs)

class MyList(list, metaclass=ListMetaclass):
	pass

l = MyList()
l.add(1) # ListMetaclass为MyList添加了add方法。
print(l) # [1]






