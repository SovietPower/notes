# -*- coding: utf-8 -*-

'''
通常程序完成IO操作需要Input和Output两条数据流。流(Stream)中的数据只能单向流动。
由于计算机系统层次间速度差异很大，IO编程中会存在速度的严重不匹配问题。有两种解决方法：
同步IO：CPU暂停程序，等待操作完成，再执行后续代码。
异步IO：CPU继续执行后续程序，不等待操作完成。
异步IO性能远高于同步IO，但缺点是编程模型复杂。异步IO有两种模式：回调（当操作完成时提醒CPU执行之前的操作）、轮询（CPU会频繁检查之前的操作是否完成）。两种模式的编程复杂度都要远高于同步IO。
操作IO的能力都是由操作系统提供的，每一种编程语言（包括Python）都会把操作系统提供的低级C接口封装起来方便使用。
'''


'标准文件对象'
'''
标准输入：stdin，利用input()从键盘输入，实质是从sys.stdin输入。
标准输出：stdout，利用print()的到显示器的缓冲输出，实质是输出到sys.stdout。
标准错误：stderr：到屏幕的非缓冲输出。
'''


'读文件'
# 同C，使用open(file, mode='r')方法可打开一个文件对象，用来访问磁盘文件或类文件（文件只是连续的字节序列）。file()方法指open()方法。
# 如果文件不存在，open()会抛出IOError错误：FileNotFoundError: [Errno 2] No such file or directory: ...
# os.fdopen()是open()方法的别名，可接受一样的参数，不过前者的第一个参数必须为int。

f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r')

# 使用read()方法可一次读取文件的全部内容到内存，返回一个str对象。
print(f.read()) # Hello!\n555
print(type(f.read())) # <class 'str'>
# print(f.read()) # 无输出 因为读完后文件指针到了文件末尾，再次使用read()会读不到东西
# 无输出的另一个解释：因为文件对象是迭代器类型的。有限长度的迭代器在被`list()`转换成列表 或 for循环完全遍历等方式将数据完全获取之后将失效，再次试图访问该数据将得到空值，赋值后指向这个迭代器的其他变量也会无法使用、变为空值（因为迭代器不能创建副本）。即它不能重复使用。seek(0)会重置该类迭代器，但注意文件指针和文件迭代器不是一个东西。

# ! 注意使用完文件后，要用close()方法关闭文件。文件对象会占用操作系统的资源，且操作系统同一时间内能打开的文件数量也是有限的。
f.close()

# 注意read()会一次性读取文件的全部内容，如果文件很大 内存根本不够。所以保险起见，读大文件时 可反复调用read(size)方法，每次最多读取size个字节的内容到内存。
# readline()可读取一行的内容，readlines()一次性读取所有内容，并按行返回str的list。
f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r') # 重新打开文件即可重新读内容
for line in f.readlines():
	print(line.strip()) # Hello!\n555 用strip()把末尾的'\n'删掉
f.close()

# 由于文件读写可能产生IOError，一旦出错，后面的f.close()不会被执行。所以为保证无论是否出错都能正常关闭文件，可以用try...finally（使用finally更有一体性...?）。
try:
	f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r')
	print(f.read())
finally:
	if f: # ！
		f.close()

# 因为每次都写try...finally很麻烦，Python引入了with语句来自动帮助调用close()。
# ! 以下with语句与try...finally相同，无论是否出错，with都会正确关闭文件。
with open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r') as f:
	print(f.read())


'文件迭代器'
# 文件对象是可迭代的，可对文件对象使用for来迭代其中的内容。使用文件迭代相比read()，更简洁、高效。
# 每次迭代会调用 file.next()(Python2)或file.__next__()(Python3)，返回文件的下一行，如果到达结尾(EOF)则触发StopIteration。当然也可手动调用。
# ! 注：与seek(),tell()有关文件指针位置，与文件迭代器的位置似乎不是一个东西，但使用read()和对文件迭代器进行迭代，都会影响文件指针的位置和文件迭代器的位置。在未迭代完成时，似乎是禁用tell()的。
# 使用readlines()或读完文件，会使文件迭代器定位到文件末尾。彻底迭代完文件迭代器，也会使文件指针定位到文件末尾。尽量不要同时使用read()与迭代器。
path = 'F:\Codes\\Python\\Python基础学习\\temp.txt'
f = open(path)
for line in f: # 只要迭代完，
	print(line.strip()) # Hello!\n555

f.seek(0)
print(f.__next__().strip()) # Hello! 注意每一行的文本都带换行符
print(f.__next__().strip()) # 555 注意每一行的文本都带换行符
# print(f.__next__().strip()) # StopIteration

from collections.abc import Iterable
from typing import DefaultDict
print(isinstance(f, Iterable)) # True

f.close()


'写文件'
# 调用open()时，使用'w'或'wb'标识符即可清空并写文本文件或二进制文件；使用'a'或'ab'可追加写入。写入通过file.write()方法。
# file.writelines(seq) 可向文件写入一个str的list。如果要换行需手动加入换行符。
# 注意一旦使用'w'打开文件，该文件就会被清空；如果文件不存在，则会新建。如果使用'x'（类似'w'）打开文件，当文件存在时就会报错；如果文件不存在，则会新建。
# 在open()时'w'会清空文件，不代表write()是覆盖内容。write()会从当前文件指针处开始写，如果有内容就覆盖，无内容则追加。

# ! 注意记得close()关闭文件。在写文件时，操作系统往往不会立刻把数据写入磁盘，而是放到内存缓存起来，空闲时再找机会写入。只有调用close()方法时，操作系统才一定会把没有写入的数据全部写入磁盘，然后关闭文件。如果忘记调用close()且程序异常终止，可能只有一部分缓冲区数据写入了磁盘，剩下的会丢失。所以，一般使用with来写入。
# 可使用file.flush()手动立刻将缓冲区内容写入磁盘。

with open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'w') as f:
	print(f.write('Hello!\n555')) # 10 write()返回成功写入的字符数

# open()和'w'标识符也可用来新建文件。
# open(path, 'w').close()


'同时读写文件'
'''
由于写文件不是立刻的，且边写边读一般是无意义的（使用'w'还会清空文件，一般读不出内容），open()不支持同时使用'r', 'w', 'a'中的任意两个或全部。
但是依旧可以同时读写文件、同时使用read(),write()：'w+'表示'w'的同时可读（新文件），'a+'表示追加的同时可读（文件指针在末尾），'r+'表示可读可写（文件指针在开头）。
还可以同时使用读写模式、两个file指针分别打开同一文件。
但一般不要同时读写。
'''
f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'w+')
f.write('Hello!\n555')
print(f.read()) # 无输出 因为使用'w'清空了文件，且此时操作系统还未将内容写入文件
f.close()


'open()'
'''
open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)

buffering默认为-1，表示系统默认的全缓冲；buffering=1时，表示设置为行缓冲模式；buffering=0时，表示设置为无缓冲模式。buffering还可以设置为任意大于1的整数，表示字节数为buffering的全缓冲。
encoding：打开文件的编码方式。

fileObject.close()：刷新缓冲区中任何还未写入的信息，并关闭该文件，这之后便不能再进行读/写。
fileObject.closed：判断文件是否已关闭。已关闭返回True，未关闭返回false。
fileObject.encoding：返回被打开文件的编码方式。
fileObject.mode：返回被打开文件的访问模式。
fileObject.name：返回文件的名称。
fileObject.encoding：返回文件打开的编码格式。
fileObject.flush()：将缓存区的内容写入到磁盘（可以再打开一个只读模式的该文件检查）。
fileObject.read(size)：从光标开始读取内容。size为读取的字节数，未填写则读取所有内容。
fileObject.readline()：读取文件中一行的内容。
fileObject.readlines()：将文件中所有的内容读取到内存中，并返回相应的list（一般不建议使用？）。
fileObject.readable()：判断文件打开方式是否可读。
fileObject.write(size)：从光标所在的位置开始写入。默认不会加换行。
fileObject.writelines(seq)：把seq（一个序列）的全部内容写到文件中（一次性写入多行）。不会自动加入换行符。注意：序列中的内容必须是str类型的数据，才能成功写入文件。
fileObject.writable()：判断文件打开方式是否可写。
'''

# 前面的open('...', 'r')打开的是 UTF-8编码 的 文本文件。如果要打开非UTF-8编码的文本文件，需传入encoding关键字参数。写入文件时，字符串会自动转换成指定编码格式。
# 如读取GBK编码的文件：
f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r', encoding='gbk')
f.close()

# 打开编码不规范的文件时，可能会遇到UnicodeDecodeError，因为在文本文件中可能夹杂了一些非法编码的字符。可指定open()的errors关键字参数，表示如果遇到编码错误该如何处理。
# 例如直接忽略编码错误(ignore)：
f = open('F:\Codes\\Python\\Python基础学习\\temp.txt', 'r', encoding='gbk', errors='ignore')
f.close()

# 要打开二进制文件（如图片、视频），可在标识符后加后缀'b'（如读取二进制文件'rb'，读写二进制文件'w+b','a+b'）。
# 以'b'方式打开时，读取到的内容是字节类型，写入时也需提供字节类型。
f = open('F:\/Codes/Python/Python基础学习/temp.jpg', 'rb')
# print(f.read()) # b'BMF\xe8\x07\x00...\xff\xff\xf
f.close()


'File-like Object'
'''
像open()函数返回的这种含有read()方法的对象，在Python中统称为file-like Object。除了file外，它还可以是内存的字节流、网络流、自定义流等。
file-like Object不要求它从特定类继承，只需它包含read()方法。这也是Python的鸭子类型的特点。
'''


'StringIO'
# 很多时候，数据读写不一定是在文件，也可以在内存中读写。
# StringIO就是在内存中创建的file-like Object，可在内存中读写str，常用作临时缓冲。

# 要将str写入StringIO，需先创建一个StringIO，然后便可像文件一样用write()写入。不同于文件，该IO同时支持读写，即既可read()也可write()。
from io import StringIO

f = StringIO()
print(f.write('Hello ')) # 6
print(f.write('qwq!')) # 4

# getvalue()可读取写入后的StringIO。
print(f.getvalue()) # Hello qwq!

# 使用close()释放该内存。
f.close()

# 像文件一样，用read(), readline()等也可读取StringIO。
f = StringIO('Hello\nHi\n555') # 用str初始化一个StringIO
while True:
	s = f.readline()
	if s=='': break
	print(s.strip()) # Hello\nHi\n555

# 注：上面的循环可简化，利用:=实现在表达式里赋值：
f = StringIO('Hello\nHi\n555') # 用str初始化一个StringIO
while s:=f.readline():
	print(s.strip()) # Hello\nHi\n555


'BytesIO'
# BytesIO用于在内存中读写二进制数据bytes。

# 创建BytesIO后，就可用write()写入bytes。不同于文件，该IO同时支持读写，即既可read()也可write()。
from io import BytesIO

f = BytesIO()
print(f.write('你好呜呜呜'.encode('utf-8'))) # 15

# getvalue()可读取写入后的BytesIO。
print(f.getvalue()) # b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x91\x9c\xe5\x91\x9c\xe5\x91\x9c'
print(b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x91\x9c\xe5\x91\x9c\xe5\x91\x9c'.decode('utf-8')) # 你好呜呜呜

# 使用close()释放该内存。
f.close()

# 像文件一样，用read(), readline()等也可读取BytesIO。
f = BytesIO(b'\xe5\x91\x9c\xe5\x91\x9c\xe5\x91\x9c') # 用bytes初始化一个BytesIO
print(f.read()) # b'\xe5\x91\x9c\xe5\x91\x9c\xe5\x91\x9c'
print(f.read()) # b''


'seek, tell'
# StringIO, BytesIO均用于在内存中缓存内容，只是内容格式不同。此外seek, tell在读写文件中也同样。so以下以StringIO为例。
# getvalue()是这类IO特有的方法，file没有；这些file-like object可使用file的方法（read(),write()...）。

# 将一个数据（如函数返回值、变量等）存入内存中，通过getvalue(), read()均可查看
s = 'Hello\nHi\n555'
sio = StringIO(s)
print(sio.getvalue()) # Hello\nHi\n555
print(sio.readlines()) # ['Hello\n', 'Hi\n', '555']
sio.close()

# 如果使用write()写入，会发现再使用read()读不到内容，而getvalue()可以
sio = StringIO()
sio.write(s)
print(sio.getvalue()) # Hello\nHi\n555
print(sio.read()) # 无输出

# 因为StringIO本身含有文件指针，在初始化后指向0，在read(), write()后指向read(), write()结束的位置。
# read(), write()均是从当前文件指针位置处开始处理，而getvalue()会从文件最初开始处理。所以read()或write()后read()读不到内容，因为指针在文件末尾；getvalue()会从文件最初读取内容。

# ! file.seek(offset, whence) 可将文件(指针)移动到指定位置。offset表示偏移量，向后为正、向前为负；whence表示移动时的相对位置（可选），默认为0表示文件开头，1表示相对于当前位置，2表示文件末尾。
# ! 注意如果文件没有用'b'方式打开，则offset无法使用负值。使用'b'方式即操作二进制数据，需使用BytesIO。

# ! file.tell() 返回文件(指针)的当前位置。

sio = StringIO()
sio.write(s)
print(sio.read()) # 无输出

sio.seek(0, 0) # 将文件移动到开头即可用read()读取。
print(sio.tell()) # 0
print(sio.read()) # Hello\nHi\n555
sio.close()

# 注意因为StringIO在初始化时会将文件指针设为0，所以此时write()会覆盖部分原内容。
sio = StringIO('ABCD')
sio.write('abc')
print(sio.getvalue()) # abcD
sio.close()


'序列化'
'''
在程序运行时，所有变量（或说对象）都保存在内存中。程序结束后，所有变量会被释放。
将在内存中的对象变成可存储、可运输的字节序列的过程，叫序列化（Python中称为pickling，其它语言也称为serialization, marshalling, flattening）。
将字节序列还原为内存中的对象的过程，叫反序列化（unpickling）。
（反）序列化可说是对象转为字节数组（或字节数组转为对象）的一种规则。

对象转为字节序列后，可以写入磁盘，也可以传输到其它地方。
序列化使对象可以跨平台存储、网络传输，因为跨平台存储与网络传输的方式是IO，而IO支持的数据格式是字节序列。
对象存储和网络传输，都需要经过序列化过程，将对象状态保存为一种跨平台识别的字节格式，以使其它平台能通过字节信息还原对象信息。

序列化是一种拆装组装对象的规则，也是多种多样的。常见的序列化方式有：JSON、JDK、XML、Pickle、Hessian、Kryo、Thrift、Protostuff、FST，其中JDK、Pickle、Kryo、FST不支持跨语言。

具体见：https://zhuanlan.zhihu.com/p/40462507
'''


'pickle'
# Python提供了pickle模块实现序列化。
# Pickle是Python特有的序列化，其二进制格式只能被Python解释器识别，只能用于Python，且Python的不同版本间可能不能兼容。但Pickle可（反）序列化Python中任意类型的对象（包括自定义的）。
import pickle

'dumps, dump'
# pickle.dumps(obj) 将任意对象obj化为一个bytes，该bytes就可以写入文件。
d = dict(name='A', age=20, score=50)
print(s:=pickle.dumps(d)) # b'\x80\x04\x95"\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x04name\x94\x8c\x01A\x94\x8c\x03age\x94K\x14\x8c\x05score\x94K2u.'

# pickle.dump(obj, file) 将对象obj化为bytes后直接写入一个file-like object。
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'wb') # 'wb'模式
pickle.dump(d, f)
f.close()


'loads, load'
# pickle.loads(bytes) 将pickle序列化后的bytes反序列化为对象。
# 反序列化的对象仅仅是内容相同，并不是同一个对象。
print(pickle.loads(s)) # {'name': 'A', 'age': 20, 'score': 50}

# pickle.load(file) 从file中直接读取bytes，反序列化为对象
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'rb') # 'rb'模式
print(pickle.load(f)) # {'name': 'A', 'age': 20, 'score': 50}
f.close()


'JSON'
'''
JSON是高效率的序列化方法。JSON序列化后为字符串，可被所有语言读取，是一种标准格式。
JSON表示的对象就是标准的JavaScript的对象。与Python的主要数据类型对应：list: []，dict: {}，str: "string"，int/float: 12.34，True/False: true/false，None: null。

缺点：JSON只能直接（反）序列化Python中的基本数据类型，且序列化后的数据反序列化回来后的数据可能与原数据有差异。例如：JSON 中的键值对中，键永远是 str 类型。当一个对象被转化为 JSON 时，字典中所有的键都会被强制转换为 str。所以 dict 被转换为 JSON 后转换回 dict 时，可能会与原来不同。即如果字典 x 具有非字符串的键，则有 loads(dumps(x)) != x。
'''
# Python内置了json模块，提供了Python对象到JSON格式的转换。
import json

'dumps, dump'
# json.dumps(obj) 将任意对象obj化为一个str，str内容就是标准的JSON对象，该str就可以写入文件。
d = dict(name='A', age=20, score=50)
print(s:=json.dumps(d)) # {"name": "A", "age": 20, "score": 50}

# json.dump(obj, file) 将对象obj化为JSON对象后直接写入一个file-like object。
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'w') # 'w'模式
json.dump(d, f)
f.close()


'loads, load'
# json.loads(str) 将JSON序列化后的str反序列化为对象。
# 反序列化的对象仅仅是内容相同，并不是同一个对象。
print(json.loads(s)) # {'name': 'A', 'age': 20, 'score': 50}

# json.load(file) 从file中直接读取str，反序列化为对象
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'r') # 'r'模式
print(json.load(f)) # {'name': 'A', 'age': 20, 'score': 50}
f.close()


'自定义类型序列化'
# Python的基本类型可直接序列化为JSON的格式，但其它类型（如自定义class）不能直接序列化。
class Student(object):
	def __init__(self, name, age, score):
		self.name, self.age, self.score = name, age, score

# print(json.dumps(Student('A', 20, 50))) # TypeError: Object of type Student is not JSON serializable

'default'
# dumps()原型：json.dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw)
# 参数default表示一个函数对象，用于将对象转化为一个可序列化为JSON的对象。对于不可序列化的对象，需填写该转换参数。
def student2dict(stu):
	return {
		'name': stu.name,
		'age': stu.age,
		'score': stu.score,
	}
# Student实例会先被default转为dict，再被序列化为JSON对象
print(s:=json.dumps(Student('A', 20, 50), default=student2dict)) # {"name": "A", "age": 20, "score": 50}

# 对任意class的实例（如果不含__slots__），可使用__dict__属性将该实例转化为dict。所以可用 default=lambda obj: obj.__dict__ 实现任意类转为dict，再转为JSON。
# 但注意这种序列化方式只考虑了内容，没考虑继承的父类。
class ABC(Student):
	def __init__(self, A, B):
		self.A, self.B = A, B

print(json.dumps(ABC(1, 2), default=lambda obj: obj.__dict__)) # {"A": 1, "B": 2}

# dump() 同理，传入default。
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'w') # 'w'模式
json.dump(Student('A', 20, 50), f, default=lambda obj: obj.__dict__)
f.close()


'object_hook'
# loads()原型：json.loads(s, *, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, **kw)
# 参数object_hook表示一个函数对象，用于将一个可序列化为JSON的对象转化为对象。对于本不可序列化的对象，需填写该转换参数。
def dict2student(d):
	return Student(d['name'], d['age'], d['score'])

print(json.loads(s, object_hook=dict2student)) # <__main__.Student object at 0x000002172E4AF940> 即一个Student实例

# load() 同理，传入object_hook。
f = open('F:\\Codes\\Python\\Python基础学习\\temp3.txt', 'r') # 'r'模式
print(json.load(f, object_hook=dict2student)) # <__main__.Student object at 0x00000244DA147160> 即一个Student实例
f.close()


'ensure_ascii'
# dumps(), dump() 含ensure_ascii参数，默认为True。当为True时，会将所有内容转为ASCII字符码，可能并不是内容本身；当为False时，会保留特殊编码内容，不转为ASCII码，即可包含非ASCII字符。
obj = dict(name='小明', age=20)
print(json.dumps(obj, ensure_ascii=True)) # {"name": "\u5c0f\u660e", "age": 20}
print(json.dumps(obj, ensure_ascii=False)) # {"name": "小明", "age": 20}

# 其它参数的应用略过。







