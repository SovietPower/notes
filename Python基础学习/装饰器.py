# -*- coding: utf-8 -*-


# 函数对象有__name__属性，会返回函数的名字
def func():
	pass
f=func
print(f.__name__) # func

# 函数对象有__doc__属性，会返回函数的说明文档（文档字符串DocStrings），即函数体之前的第一个'''或"""注释。
# 文档字符串的使用惯例：首行简述函数功能，第二行空行，第三行为函数的具体描述。
def func():
	# #号引用不是说明文档
	'''This is a doc of func!
Another line!''' # 注意第一个三引号也要有与函数体相同的缩进。后续的缩进会显示在文档中。
	'''This isn't the doc of func. Only the first comment is doc!'''
	pass
print(func.__doc__) # This is a doc of func!\nAnother line!

'''
https://www.zhihu.com/question/26930016/answer/99243411
装饰器本质上是一个Python函数，它可以让其他函数在不需要做任何代码变动的前提下为已存在的对象增加额外功能。装饰器的返回值也是一个函数对象。
装饰器常用于有切面需求的场景，比如：插入日志、性能测试、事务、处理、缓存、权限校验等场景。

'''
# 对于一个函数
def foo():
	print("This is foo")

# 如果想要该函数在每次运行时，输出执行记录，或记录其执行日志，可以：
import logging
def foo():
	logging.warning("foo is running")
	print("This is foo")
foo()


# 如果其它函数也有类似需求，最简单的做法是在每个函数体中添加相关logging语句。
# 为了避免这类重复代码，可定义一个预先执行的日志函数，然后通过将func传入该日志函数实现。
def use_logging(func):
	logging.warning("%s is running" % func.__name__)
	func()
def foo(): print("This is foo")
def bar(): print("This is bar")

use_logging(foo)
# use_logging(bar)


# 上面这种方法，每次需将函数传入use_logging()，麻烦且不如直接foo()直观。
# 通过装饰器，可将func包裹在函数内，允许复用代码。
# 这个例子中，可说foo被use_logging装饰了。函数进入和退出时，被称为一个横切面(Aspect)，这种编程方式称为面向切面的编程(Aspect-Oriented Programming)。
# 注意wrapper的函数需为*args, **kwargs，才能适配所有传入的函数func。
def use_logging(func):
	def wrapper(*args, **kwargs):
		logging.warning("%s is running" % func.__name__)
		return func(*args, **kwargs)
	return wrapper
def foo(): print("This is foo")
def bar(): print("This is bar")

foo = use_logging(foo)
foo()
# bar = use_logging(bar)
# bar()


# 利用修饰器的语法糖@符号，在定义函数时使用可避免一次赋值。
# 这样就可以省去foo=use_logging(foo)的赋值语句，直接使用foo()可得正确结果。
def use_logging(func):
	def wrapper(*args, **kwargs):
		logging.warning("%s is running" % func.__name__)
		return func(*args, **kwargs)
	return wrapper

@use_logging # 等价于多执行一句 foo = use_logging(foo)
def foo():
	print("This is foo")

@use_logging
def bar():
	print("This is bar")

foo() # WARNING:root:foo is running\nThis is foo
# bar()

# 装饰器还可以带（除了被执行函数func外的）参数。
# 该例中use_logging是允许带参数的装饰器，实际是对原有装饰器的一个函数封装，返回了原有装饰器。
def use_logging(level):
	def decorator(func):
		def wrapper(*args, **kwargs):
			if level=="warning":
				logging.warning("%s is running" % func.__name__)
			return func(*args, **kwargs)
		return wrapper
	return decorator

@use_logging(level="warning")
def foo(name="foo"):
	print("This is %s" % name)

foo()


# 装饰器的缺点是，会使原函数func的元信息丢失，如函数的__doc__(docstring)、__name__、参数列表。
def decorator(func):
	def wrapper(*args, **kwargs):
		print("This is " + func.__name__)
		return func(*args, **kwargs)
	return wrapper

@decorator
def foo():
	"""doc of foo"""
	print("This is foo")

print(foo.__name__) # wrapper
print(foo.__doc__) # None
# 因为使用@decorator后，等价于foo=decorator(foo)，foo实际是一个wrapper对象。所以其元信息也是wrapper的。

# 通过 functools.wraps 可解决该问题。wraps也是一个装饰器，它接收一个函数，将该函数的元信息拷贝到被它装饰的函数中，使得能在装饰器里访问原函数的元信息。
from functools import wraps # @functools.wraps(func) 或在使用时这样

def decorator(func):
	@wraps(func) # 修改wrapper的元信息为func的。如果是带参数修饰器形式，也在最内层的wrapper处使用@wraps
	def wrapper(*args, **kwargs):
		print("This is " + func.__name__)
		return func(*args, **kwargs)
	return wrapper

@decorator
def foo():
	"""doc of foo"""
	print("This is foo")

print(foo.__name__) # foo
print(foo.__doc__) # doc of foo

'''
装饰器嵌套的顺序：下面等价于f=a(b(c(f)))
@a
@b
@c
def f():
	pass
'''


# 内置装饰器：property, staticmethod, classmethod。它们都作用于类方法上。
'@property'
# property装饰器用于类中的函数，使得可以像访问属性一样获取一个函数的返回值。这样既能像属性一样获取值，又可在获取值时做一些操作。
class Person:
	age = 18
	name = "ABC"

	@property
	def info(self):
		return f"name:{self.name} age:{self.age}"

ABC = Person()
print(ABC.info) # name:ABC age:18


'静态方法'
# 如果定义的方法既不想与实例绑定，也不想与类绑定，只是用类名作为它的命名空间，可以使用静态方法。
# staticmethod装饰器是用于类中的静态方法，即该方法可直接被调用、无需实例化，也即它没有self参数，无法访问实例化后的对象。
class Person:
	name = "ABC"

	@staticmethod
	def say_sth():
		print("wuwuwu")

Person.say_sth() # wuwuwu
# 实例化调用也可，但也是一样
A = Person()
A.say_sth() # wuwuwu


'类方法'
# classmethod装饰器是用于类中的类方法，即该方法可以直接被调用、无需实例化，也即它没有self参数，无法访问实例化后的对象。
# 与staticmethod的区别是，它会接收一个指向类本身的cls参数
class Person:
	name = "ABC"

	@classmethod
	def say_sth(cls):
		print(f"This is {cls.name}")

Person.say_sth() # This is ABC
# 实例化调用也可，但也是一样（cls指向类本身初值，实例化不影响其值）
A = Person()
A.name = "New name"
A.say_sth() # This is ABC

'''
静态方法：需用装饰器@staticmethod标识。静态方法既不需要传递类对象也不需要传递实例对象（形参没有self/cls）。
当方法中既不需要使用实例对象（如实例对象，实例属性），也不需要使用类对象（如类属性、类方法、创建实例等）时，定义静态方法可取消不需要的参数传递，有利于减少不必要的内存占用和性能消耗。

类方法：需用装饰器@classmethod标识。类方法的第一个参数必须是类对象，一般以cls作为第一个参数。
当方法中需要使用类对象（如访问私有类属性等）时，定义类方法。类方法一般和类属性配合使用。

以上两种都能通过实例对象或类对象访问。
若类中定义了同名的方法，调用方法会执行最后定义的方法（相当于早定义的会被覆盖）
'''


'类装饰器'
# 类装饰器：由于调用一个对象，实际是调用它的__call__方法，所以可用类实现装饰器的功能
class Decorator:
	def __call__(self):
		print("This is Decorator")
		return 233

f = Decorator()
f() # This is Decorator 即调用Decorator的__call__
print(f()) # 233 即调用Decorator的__call__

class Decorator:
	def __init__(self, func):
		self.func = func
	def __call__(self, *args, **kwargs):
		print("This is Decorator")
		return self.func(*args, **kwargs)

@Decorator
def f():
	print("Hello")

f() # This is Decorator\nHello

# 利用类装饰器，可通过类实现一些复杂功能，如缓存器，在类中定义缓存，在__call__中判断对象是否在缓存中，如果在可返回，如果不在可更新缓存。
class Cache:
	__cache = {}

	def __init__(self, func):
		self.func = func
	def __call__(self):
		if self.func.__name__ in Cache.__cache:
			return Cache.__cache[self.func.__name__]
		value = self.func()
		Cache.__cache[self.func.__name__] = value
		return value


# 设计一个可用于任何函数的decorator，可打印函数的运行时间
import time
def metric(f):
	def wrapper(*args, **kwargs):
		start=time.time()
		ret=f(*args, **kwargs) # 先执行
		end=time.time()
		print('%s executed in %s ms' % (f.__name__, round(end-start, 4)))
		return ret # wrapper返回的是函数值！
	return wrapper

@metric
def ff():
	time.sleep(0.5)
	print("ff!")
	return 233

print(ff()) # ff!\nff executed in 0.5069 ms\n233






