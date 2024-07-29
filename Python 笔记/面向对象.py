# -*- coding: utf-8 -*-

'''
面向对象编程(Object Oriented Programming, OOP)，是一种程序设计思想。OOP把对象作为程序的基本单元，一个对象包含了数据和操作数据的函数。
Python中，所有数据类型都可以视为对象，也可以自定义对象。通过类定义的数据结构实例叫做对象。对象包括两个数据成员（类变量和实例变量）和方法。
给对象发消息实际上就是调用对象类中定义的函数，也叫对象的方法（Method）。
局部变量：定义在方法中的变量，只作用于当前实例的类。
实例变量：在类的声明中，属性是用变量来表示的，这种属性变量就称为实例变量。它在类内部声明，且在类的其他成员方法之外声明。

类（Class）是抽象的，实例（Instance）是一个具体的类。类是创建实例的模板，实例是根据类创建出来的一个个具体的“对象”，每个实例或对象都拥有相同的方法，但各自的数据可能不同。
数据封装、继承、多态是面向对象的三大特点。
'''

'类'
# 通过class定义类，class后是类名，类名通常用大写字母开头，然后是(object)，表示该类是从哪个类继承下来的（如果无需继承则用object类，这是所有类都会继承的类。忽略该(object)则默认从object类继承）。
class Student(object):
	'类的帮助信息，通过__doc__属性查看'
	grade = 10 # 类体class_suite，由类成员、方法、数据属性组成

# 通过类名和__init__方法接收参数，创建实例，不同于其它语言中的new
A = Student()
B = Student()

# 可见A指向的是一个Student的实例，0x14BF132F430为内存地址，不同实例地址不同。
print(A, B) # <__main__.Student object at 0x0000021F0934F430> <__main__.Student object at 0x0000021F0934F400>
# Student本身就是一个类。
print(Student) # <class '__main__.Student'>


'实例属性 类属性'
# 与静态语言不同，Python可以自由地给一个实例变量绑定任意属性或方法，叫做实例属性、实例方法。即使两个实例属于同一个类，它们拥有的属性和方法可以不同。
# 对于类中定义的属性或方法，所有实例都共享，叫做类属性、类方法。注意对类属性/方法的修改会同时影响到所有实例。
A.name = "A"
B.age = 16
print(A.name, B.age) # A 16 但是A没有A.age，B也没有B.name
print(A.grade, B.grade) # 10 10 A,B都有类属性grade

# 注意实例属性和类属性是不同的，即使名称相同。当重名时，实例属性会优先于类属性被访问，删除实例属性后，类属性依然存在。
# 类属性对实例为只读，实例无法修改或删除类属性，只能修改或删除实例属性。类属性一直存在且不会被实例改变
# 实例变量与类变量尽量不要重名。
A.grade = 20 # 创建实例属性
print(A.grade) # 20
del(A.grade) # 删除实例属性，此时类属性依然存在为默认值10
print(A.grade) # 10
# del(A.grade) # AttributeError: grade 实例的类属性无法删除，一直存在且不变。删除或修改的只能是实例属性。

# 类属性可通过 ClassName.属性 永久修改，会影响所有实例
class Student:
	cnt = 0
	def __init__(self, name):
		Student.cnt += 1
		self.name = name

Student.cnt = 10
A = Student("A")
print(Student.cnt) # 11
B = Student("B")
print(Student.cnt) # 12
print(A.cnt) # 12


'为类或实例绑定方法'
# 动态语言允许在程序运行过程中，直接动态给class或实例添加功能
# 给某个实例绑定方法，使用ins.func = types.MethodType(func, ins)
def set_age(self, age): # 先定义一个含self的函数作为实例方法（当然匿名函数也可）
	self.age = age

from types import MethodType
A.set_age = MethodType(set_age, A) # 给实例A绑定一个实例方法set_age
A.set_age(18)
print(A.age) # 18

# 当然实例方法只对绑定的那个实例起作用
# B.set_age(18) # AttributeError: 'Student' object has no attribute 'set_age'

# 也可以不使用types.MethodType，直接绑定。但是这样每次调用都要代入self参数
A.set_age = set_age
A.set_age(A, 20)
print(A.age) # 20

# 但其实不用MethodType，它就不是真正的方法，因为self实际上可以是任意一个变量，只要该变量含或可绑定age
A.set_age(B, 21)
print(B.age) # 21

# 也可用匿名函数，但注意也要有self参数
B.f = MethodType(lambda self, x: x*x, B)
print(B.f(3)) # 9

# 注意MethodType的第二个参数，实际是self以后的值，不是只能是该实例
def g(self, x):
	self.x = x
B.g = MethodType(g, A)
B.g(1) # B.g(1) 实际是 A.x=1，给A绑定了x，B仍然没有x
print(A.x) # 1
# print(B.x) # AttributeError: 'Student' object has no attribute 'x'


# 要给所有实例绑定方法，可给类绑定方法。直接使用赋值即可
def set_score(self, score): # 先定义一个含self的函数作为实例方法（当然匿名函数也可）
	self.score = score

Student.set_score = set_score
A.set_score(80)
B.set_score(90)
print(A.score, B.score) # 80 90

# 注意给类绑定方法不使用MethodType，因为MethodType第二个参数实际是self以后的值，所以它会为第二个参数创建所需的变量，且以后调用的都是第二个参数。此时调用就就是类，而不是实例；创建的是类变量，而不是实例变量
Student.set_score = MethodType(set_score, Student)
A.score = 80
A.set_score(50) # 因为使用了MethodType，所以这句依旧等价于 set_score(Student, 50)
print(A.score) # 80 使用了MethodType，类方法set_score不是修改实例，而是根据set_score中那样修改类Student本身
print(Student.score) # 50


'方法'
# 类的方法与普通函数只有一个区别：方法的第一个参数必须是指向类的该实例的变量（通常叫self，也可以任取名）（因此方法可直接访问实例内的数据）。调用方法时无需也不能传入该参数，该参数会自动指向该实例。方法其它特点（如默认参数、可变参数、关键字参数）与普通函数相同。

# 在创建实例时，可通过__init__方法，强制要求创建时填写某些属性。__init__方法称作构造方法。
class Student(object):
	'The doc of Student!'
	grade = 10
	def __init__(self, name, age):
		self.name=name
		self.age=age
	def Print_self(hhh_self):
		print(hhh_self) # 指向该实例的地址
		print(hhh_self.__class__) # self.__class__指向类

A = Student("A", 19)
print(A.age) # 19

print(A) # <__main__.Student object at 0x000001806D3C5EB0>
A.Print_self() # <__main__.Student object at 0x00000192448C4EB0>
# <class '__main__.Student'>


'''
Python内置的类属性：
__dict__：类的属性（包含一个字典，由类的数据属性组成）
__doc__：类的文档字符串
__name__：类名，即'__main__.className'
__module__：类定义所在的模块
__bases__：类的所有父类构成的一个元组
'''
print(Student.__dict__) # 包含'__module__': '__main__', '__doc__': 'The doc of Student!', 'grade': 10, 等很多东西的dict
print(Student.__doc__) # The doc of Student!
print(Student.__name__) # Student
print(Student.__bases__) # (<class 'object'>,)


'数据封装'
# 要访问/操作实例的数据，没必要从外部函数访问，可在类内部定义访问/操作数据的函数。这样方便了外部调用，无需关心内部实现的细节
class Student(object):
	def __init__(self, score):
		self.score=score
	def print_score(self):
		print("Score =", self.score)
	def get_grade(self):
		return "A" if self.score>=90 else "B" if self.score>=80 else "C"

A = Student(60)
A.print_score() # Score = 60
print(A.get_grade) # <bound method Student.get_grade of <__main__.Student object at 0x225FEE27640>>
print(A.get_grade()) # C

'''
如果要让内部属性或方法不能被外部访问，可在属性或方法的名称前加两个下划线(__)，它们属于私有变量。
Python中，如果实例的变量名以__开头，则它会变成一个私有变量(private)，原则上只允许内部访问。这样就确保了外部代码不能随意修改对象内部的状态。
如果外部想获取内部属性，可在类中定义get_name这样的方法；如果外部想修改内部属性，可在类中定义set_name这样的方法。通过在类中定义这些方法，可实现复杂的行为，如检查参数、记录访问信息等。
'''
class Student(object):
	def __init__(self, name, score):
		self.__name=name
		self.__score=score

	def get_name(self):
		return self.__name

	def set_name(self, name):
		if name=="B":
			self.__name=name
		else:
			raise ValueError('Bad name') # 参数检查

	def print_score(self):
		print("Score =", self.__score)

A = Student(A, 90) # 注意"A"不是A！"A"是字符串，A是一个实例变量
print(A.get_name()) # <__main__.Student object at 0x0000018F63A68B80>

A = Student("A", 90) # 注意"A"不是A！
# print(A.__name) # AttributeError: 'Student' object has no attribute '__name'
print(A.get_name()) # A

A.set_name("B")
print(A.get_name()) # B

# 不过事实上__开头的变量（属性或方法）依旧可被外部访问，因为Python解释器只是将__name变成了_ClassName__name。所以通过_Student__name依旧可从外部访问__name
print(A._Student__name) # B
# Python是无法阻止外部访问的，只是约定上不去使用外部访问

# 注意外部代码也可以定义__name，但这不同于且不会影响内部的__name，因为内部的__name已被改成_Student__name
A.__name = "CDEF"
print(A.get_name()) # B
print(A._Student__name) # B

# 注意以__开头且结尾的变量名，是可以直接访问的。属于特殊变量，不是私有变量。
# 对于以一个下划线_开头的实例变量名，虽然外部可直接访问，但约定上它们属于私有变量，不允许外部随意访问。


'对象销毁'
'''
Python使用引用计数来跟踪和回收垃圾。Python记录着所有使用中的对象各有多少引用。当对象被创建或引用时，就创建了一个引用计数。当引用计数为0或对象只存在循环引用（几个变量相互引用，但是没有其他变量引用他们）时，该对象不再需要，它被垃圾回收。回收不是立即的，是在合适时间回收期内存空间。
a = 40
b = a
c = [b]
三句创建了三个对<40>的计数。
del a
b = 100
c[0] = 1
三句减少了三个对<40>的计数。

类的析构函数__del__会在对象销毁时被调用。
'''
class ABCD:
	def __init__(self):
		print("new", self.__class__.__name__)
	def __del__(self):
		print("del", self.__class__.__name__)

x = ABCD() # new ABCD
del(x) # del ABCD


'继承 多态'
'''
当定义class时，可以从某个现有的class继承。新定义的class称为子类/派生类(subclass)，被继承的class称为基类/父类/超类(base class, super class)。
子类会获得父类（包括父类的父类...）的全部变量和方法。子类可继承多个类。如果继承元组中有一个以上的类，则它被称为多重继承。
如果子类与父类含有重名属性/方法，则使用子类中定义的。因为Python先在子类中查找对应属性/方法，找不到才在父类中依次查找。
对于重名方法（比如__init__），有三种情况：
1. 子类需要自动直接调用父类的方法：子类不重写该方法，实例化子类后会自动调用父类的该方法。
2. 子类不需要调用父类的方法：子类重写该方法，实例化子类后会自动调用父类的该方法。
3. 子类既要重写该方法，也要调用父类的方法：当要使用父类该方法时，使用super(子类名, self).或super().或父类名称.+父类方法名（使用父类名称.需要在调用时显式写出self实参）可实现调用。

继承可以把父类的所有功能都直接拿过来，这样就不必重零做起，子类只需要新增自己特有的方法，也可以把父类不适合的方法覆盖重写。

多态：允许将子类类型的指针赋值给父类类型的指针，或将不同的子类对象都看做父类对象。

语法：
class SubClassName (ParentClass1[, ParentClass2, ...]):
	pass
'''

class Animal(object):
	def Print(self):
		print("This is Animal!")
# 以下两个类都会调用父类的Print
class Dog(Animal):
	def Print(self):
		return super().Print()
class Cat(Animal):
	pass

d = Dog()
c = Cat()
d.Print() # This is Animal!
c.Print() # This is Animal!

# 也可以重写某个子类的Print
class Dog(Animal):
	def Print(self):
		print("This is Dog!")
class Cat(Animal):
	def Print(self):
		print("This is Cat!")

d = Dog()
c = Cat()
d.Print() # This is Dog!


'关于super()'
'''
MRO(Method Resolution Order，类的方法解析顺序表)：Python对于每一个类都有一个MRO列表. 该表中子类永远在父类之前。当子类继承父类时，会按父类在MRO中的顺序依次继承，即如果多个父类有同样名称的属性/方法，优先选择MRO中最靠前出现的父类的该属性/方法。通过className.mro()可查看该类的MRO。

super()会返回MRO列表中的该类处的下一个类，因为super()的原型是：
def super(cls, ins):
	mro = ins.__class__.mro()
	return mro[mro.index(cls)+1]
super()先获取MRO列表，然后返回了列表中的下一个类。调用时ins会填入self，即该类的实例。
一般可直接认为，super()返回该类的父类（或MRO中第一个含有所需属性/方法的父类），实际是返回ins所在类的MRO列表中cls后面的一个类。

当子类中不含一个属性/方法x时，直接在子类中调用x 等价于 调用super().x，因为调用子类的x会自动在父类中查找x。
但当子类中含属性/方法x，要调用父类的x时，就需使用super().x。

注意使用super().f(self)时，self仍是该子类的实例，不是父类的实例，因为self只是一参数，子类只是使用了方法f。

在Python3中，可直接使用super().xxx；Python2中需使用super(className, self).xxx。
'''
class A:
	def __init__(self): self.x = 1
	def f(self): return self.x + 1
class B:
	def __init__(self): self.x = 10
	def g(self): return self.x + 2
class E(A, B):
	def __init__(self): self.x = 100
	def call_f(self): return super().f()
	def call_g(self): return super().g()

e = E()
print(e.f(), e.call_f()) # 101 101 不是2
print(e.g(), e.call_g()) # 102 102 不是12

print(E.mro()) # [<class '__main__.E'>, <class '__main__.A'>, <class '__main__.B'>, <class 'object'>]
print(e.__class__.mro()) # [<class '__main__.E'>, <class '__main__.A'>, <class '__main__.B'>, <class 'object'>]


'类型判断'
# issubclass(sub, sup) 判断一个类sub是否是另一个类sup的子类或子孙类
# isinstance(obj, Class) 判断obj是否是该Class类的实例对象或该Class子类的实例对象
# 可见一个Dog的实例，既属于Dog，也属于Animal、object；反之则不行。一个Dog的实例，既是Dog类型，也是Animal类型
print(issubclass(Dog, Animal)) # True
print(isinstance(d, object)) # True d-Dog-Animal-object

a = Animal()
print(isinstance(a, Dog)) # False a-Animal-object

# issubclass和issubclass可以是一个tuple，只要满足tuple中的一个就返回True
print(isinstance([1, 2, 3], (list, tuple))) # True
print(issubclass(Animal, (Dog, Animal))) # True
print(isinstance(a, (Dog, Animal))) # True

# type() 可得到一个对象的class类型（但无法判断它所属的父类，所以更推荐用isinstance()）
print(type(None)) # <class 'NoneType'>
print(type(d)) # <class '__main__.Dog'>
print(type(Animal)) # <class 'type'>

# types模块中定义了函数类型的常量
import types
def f():
	pass
print(type(f)) # <class 'function'>
print(type(f)==types.FunctionType) # True
print(type(abs)) # <class 'builtin_function_or_method'>
print(type(abs)==types.BuiltinFunctionType) # True

print(type(lambda x:x)==types.LambdaType) # True
print(type((x for x in range(10)))==types.GeneratorType) # True


# 对于一个设计成接受Animal类型参数的函数，也可以接受Dog、Cat
def Print_twice(animal):
	animal.Print(), animal.Print()

Print_twice(a) # This is Animal! *2
Print_twice(d) # This is Dog! *2
Print_twice(c) # This is Cat! *2
'''
所以通过多态，任何依赖Animal作为参数的函数或者方法都可以不加修改地使用任意Animal的子类正常运行
只要知道一个变量是Animal类型（注意是Animal子类也等价于是Animal类型），就无需知道它是Animal还是Animal的子类型，总可以调用Animal的Print()方法。具体的Print()是否有修改，则取决于运行时它的类型。因此，调用时无需考虑细节，只需保证Animal的Print()正确。
OOP中的开闭原则：
对扩展开放：允许新增Animal子类；
对修改封闭：不需要修改依赖Animal类型的run_twice()等函数。
'''

# 注意对于Python这类动态语言，不能保证Print_twice(animal)一定是传入Animal类型或其子类，只要传入的对象有Print()方法，都可正确运行。
# 这就是动态语言的“鸭子类型”，它并不要求严格的继承体系，一个对象只要“看起来像鸭子，走起路来像鸭子”，那它就可以被看做是鸭子
class Plant(object): # Plant类不继承，但有自己的Print()方法
	def Print(self):
		print("This is Plant!")

def Print_twice(animal):
	animal.Print(), animal.Print()

p = Plant()
Print_twice(p) # This is Plant! *2





