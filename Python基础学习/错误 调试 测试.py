# -*- coding: utf-8 -*-

'try except finally'
# 当我们认为某些代码可能会出错时，可用try来运行该段代码。如果执行出错，try中后面的代码不会继续执行，而是直接跳转到错误处理代码，即except代码块。执行完except后，如果有finally代码块则执行finally。
# 此后，程序正常运行，执行该代码块以外的部分（未用except捕获到错误时会终止运行）
# 如果函数中的finally含return，则会执行，使后面的return失效。

x = 5
try:
	print('try...')
	r = 10 / x
	print('result:', r)
except ZeroDivisionError as e:
	print('except:', e)
finally:
	print('finally...')
print('END\n')
'''
x=0时输出：
try...
except: division by zero
finally...
END

x=5时输出：
try...
result: 2.0
finally...
END
'''
# 可见错误发生时，后续语句不会被执行。若某个except捕获到相应错误，则执行。最后执行finally。
# 无论是否出错，都会执行finally。

# 错误有很多种，可使用不同except来捕捉不同类型的错误。只有最先捕获到错误的一个except会被执行。比如int('a')/0，实际ValueError先出错、只执行ValueError的except，因为类型转换发生在除法运算之前。
# 此外，在所有except后、finally前 可加else语句，当没有任何错误发生时，会在执行完try后 执行else语句。

s = '2'
try:
	print('try...')
	r = 10 / int(s)
	print('result:', r)
except ZeroDivisionError as e:
	print('ZeroDivisionError:', e)
except ValueError as e:
	print('ValueError:', e)
else:
	print('no error!')
finally:
	print('finally...')
print('END\n')
'''
s='a'时输出：
try...
ValueError: invalid literal for int() with base 10: 'a'
finally...
END

s='2'时输出：
try...
result: 5.0
no error!
finally...
END
'''


'错误类型'
# 错误类型及继承关系：https://docs.python.org/3/library/exceptions.html#exception-hierarchy
# Python的错误也都是class，所有错误类型都继承自BaseException。使用except时要注意，except不仅捕获该类型的错误，其子类错误也会捕获。
# 如 FloatingPointError, OverflowError, ZeroDivisionError均继承自ArithmeticError。同时使用时，可能会同时捕捉到错误，则哪个except在前执行哪个except（只执行一个）。
try:
	f = 1e20
	for i in range(10):
		print(i, f)
		f = f**2
except ArithmeticError as e:
	print('ArithmeticError:', e, ' f:', f)
except OverflowError as e:
	print('OverflowError:', e, ' f:', f)
'''
0 1e+20
1 1e+40
2 1e+80
3 1e+160
ArithmeticError: (34, 'Result too large')  f: 1e+160
'''

# try...except还可以跨多层捕获，如可在最初的函数调用处捕获到深层的错误
# 这样就不需在每个出错的地方捕获错误，只需在合适的层次捕获即可。
def A(x): return 10/x
def B(x): return A(x)*2
def main():
	try:
		B(0)
	except Exception as e: # Exception是多种错误的父类
		print('Error:', e)
main() # Error: division by zero


'调用栈'
'''
如果错误没有被捕获，它就会沿调用栈一直往上抛，最后被Python解释器捕获，Python打印出错误的调用栈信息，然后结束程序。
调用栈Call Stack即调用函数时存放局部变量、返回地址的栈。
例如如下错误程序：
def ddd(x):
	return 10/x
def dd(x):
	return ddd(x)*2
def d():
	dd(0)
d()

错误信息：
Traceback (most recent call last): # 表示以下是错误的跟踪信息
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 110, in <module>
	d() # 表示d()出错了，在第110行，但还不是根本的原因。
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 109, in d
	dd(0) # 表示dd(0)出错了，在第109行，但还不是根本的原因。
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 107, in dd
	return ddd(x)*2 # 表示ddd(x)*2出错了，在第107行，但还不是根本的原因。
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 105, in ddd
	return 10/x # 表示10/x出错了，在第105行，是根本的原因。
ZeroDivisionError: division by zero # 错误类型

出错时，要通过错误的调用栈信息，定位错误。
'''


'记录错误信息'
# 通过捕获错误，可以在找到错误信息的同时 不结束程序。使用Python内置的logging模块可方便地显示/记录下错误信息。
import logging
logging.basicConfig(level=logging.INFO)

def A(x):
	return 10/x
def B(x):
	return A(x)*2
def main():
	try:
		B(0)
	except Exception as e: # Exception是多种错误的父类
		logging.exception(e) # 显示错误信息
main()
print('END\n')
'''
输出：
ERROR:root:division by zero
Traceback (most recent call last):
...
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 133, in A
	return 10/x
ZeroDivisionError: division by zero
END

程序不仅输出了错误信息，还能继续执行、最后正常退出。
'''


'抛出错误'
# 因为错误也是class，捕获一个错误就是捕获到了该class的一个实例。错误是创建出来然后抛出的，我们也可以自定义错误、按需抛出错误。
# 定义一个错误类型即定义一个class，注意要确定该错误类型继承的父类（如Exception, ArithmeticError, Warning等）。只有在必要时才自定义错误类型，应尽量使用Python内置的错误类型。
# 通过 raise+参数 可抛出错误。
class FuncError(ValueError):
	pass

def func(x):
	if x==0:
		raise FuncError('invalid value: %d!' % x)
	return 10/x
'''
func(0)
输出：
Traceback (most recent call last):
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 170, in <module>
	func(0)
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 167, in func
	raise FuncError('invalid value: %d!' % x)
__main__.FuncError: invalid value: 0!
'''

# 注意，在函数中遇到错误时，将错误向上一层继续抛出是常见的。因为当前函数可能无法处理该错误，需向上抛，由顶层调用者去处理。
# 如果raise语句不带参数，则会把当前错误原样抛出。此外，在except中可通过raise另一个Error，将一种类型的错误转化为另一种类型错误。
def func(x):
	if x==0:
		raise ValueError('invalid value: %d!' % x)
	return 10/x
def main():
	try:
		func(0)
	except ValueError as e:
		print('ValueError:', e)
		# raise
		# raise ZeroDivisionError('Zero Error!')
'''
main()

输出：
不加raise，错误在main中就被捕获，不会输出两次：
ValueError: invalid value: 0!

加raise，会继续抛出当前的错误信息到main外：
ValueError: invalid value: 0!
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 193, in <module>
	main()
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 188, in main
	func(0)
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 184, in func
	raise ValueError('invalid value: %d!' % x)
ValueError: invalid value: 0!

加raise ZeroDivisionError('Zero Error!')，不仅会抛出原错误，还会抛出新的错误信息ZeroDivisionError：
ValueError: invalid value: 0!
Traceback (most recent call last):
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 188, in main
	func(0)
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 184, in func
	raise ValueError('invalid value: %d!' % x)
ValueError: invalid value: 0!

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 194, in <module>
	main()
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 192, in main
	raise ZeroDivisionError('Zero Error!')
ZeroDivisionError: Zero Error!
'''


'assert'
# 同C++，Python中含有用于调试的assert。当assert断言的表达式为假时，会抛出AssertionError。
# 语法：assert condition [, augment]。augment为可选字符串调试信息，会在断言失败时一同输出。
'''
x = 0
assert x!=0, 'x is zero!'

输出：
Traceback (most recent call last):
  File "f:\Codes\Python\Python基础学习\错误处理.py", line 235, in <module>
	assert x!=0, 'x is zero!'
AssertionError: x is zero!
'''

# 启动Python解释器时，可添加-O参数来关闭程序中的assert，如：python -O A.py。关闭后，assert相当于pass。


'logging'
'''
logging模块是print, assert外的调试方式。logging不会像assert一样抛出错误，还可以按级别输出、输出到文件。

logging可以使用5个不同的级别进行输出：
logging.critical('1')
logging.error('2')
logging.warning('3')
logging.info('4')
logging.debug('5')

logging的信息分为五个级别：critical > error > warning > info > debug。越靠前的信息越重要，越容易被输出。
在导入logging后，通过 logging.basicConfig(level=logging.x) 设置logging默认输出等级level为x，x需为五个级别中的一种（大写）。如果不设置，默认生成的root logger的level是logging.WARNING。
当logging的level为x时，小于x的级别的logging信息不会被输出，大于等于x的级别的logging信息会正常输出。

注意 logging.basicConfig 需在所有的logging之前使用，否则设置会失效。在前文'记录错误信息'中使用了logging，所以在那里设置了等级：logging.basicConfig(level=logging.INFO)。
'''

# logging.basicConfig(level=logging.INFO) 在前文中
x = 555
logging.debug('debug') # 不输出
logging.info('info') # INFO:root:info
logging.warning('warning x = %d' % x) # WARNING:root:warning x = 555

'''
basicConfig中还可以设置错误信息的输出格式format：logging.basicConfig(level=logging.xxx, format='...')。
format中的参数需使用如下格式表示：
%(levelno)s: 打印日志级别的数值
%(levelname)s: 打印日志级别名称
%(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
%(filename)s: 打印当前执行程序名
%(funcName)s: 打印日志的当前函数
%(lineno)d: 打印日志的当前行号
%(asctime)s: 打印日志的时间
%(thread)d: 打印线程ID
%(threadName)s: 打印线程名称
%(process)d: 打印进程ID
%(message)s: 打印日志信息

例：logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logging使用的一些例子见：https://www.cnblogs.com/CJOKER/p/8295272.html
以下是logging的文件输出（默认是输出到控制台）：
'''
import logging # 引入logging模块
import os.path
import time

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # 设置该logger的等级

# 第二步，创建一个handler，用于写入日志到对应文件
date = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
# print(os.path.dirname(os.getcwd())) # F:\
log_path = os.path.dirname(os.getcwd()) + 'Codes\\Python\\Python基础学习\\' # 注意需转义\\。Python字符串结尾不能是单斜杠\，所以使用r'..'后最后一个斜杠会加不上。
# print('logpath = %s' % log_path) # logpath = F:\Codes\Python\Python基础学习\ 需保证路径存在
log_name = log_path + date + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 设置输出到file的logging等级。似乎没有成功。

# 第三步，定义handler的文件输出格式formatter
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)

# 第四步，将handler添加到logger中
logger.addHandler(fh)

# 然后就可以向文件输出日志了。控制台也会正常输出。
logger.debug('this is a logger debug message')
logger.info('this is a logger info message')
logger.warning('this is a logger warning message')
logger.error('this is a logger error message')
logger.critical('this is a logger critical message')
'''
文件和控制台输出等级似乎一致，file的输出等级好像没有成功设置。
控制台输出：
WARNING:root:this is a logger warning message
ERROR:root:this is a logger error message
CRITICAL:root:this is a logger critical message

文件输出：
2021-08-02 23:46:56,041 - 错误处理.py[line:318] - WARNING: this is a logger warning message
2021-08-02 23:46:56,042 - 错误处理.py[line:319] - ERROR: this is a logger error message
2021-08-02 23:46:56,044 - 错误处理.py[line:320] - CRITICAL: this is a logger critical message
'''


'pdb'
# Python可以通过pdb调试，类似gdb。命令使用-m pdb参数：python -m pdb name.py。具体不在这写了。
# pdb一般用来单步执行调试。此外，在程序中导入pdb模块(import pdb)，就可在可能出错的地方添加pdb.set_trace()，以设置一个断点。当程序运行到pdb.set_trace()处时，会暂停并从此处进入pdb调试环境。pdb命令行中输入命令c 可跳出调试、继续程序运行。
import pdb
a = 1
b = 2
c = a+b
pdb.set_trace()
print(c)


'单元测试'
# 单元测试允许自己编写测试方法，以测试所写部分代码是否正确（当然通过测试不代表一定正确）。具体不在这写了。


'文档测试doctest'
# Python内置的文档测试(doctest)模块 可直接提取注释文档中的代码并执行测试。可用于函数、类等。
# doctest严格按照Python交互式命令行的输入和输出来判断测试结果是否正确。只有在测试出现异常时，可用...表示中间大段的输出。
# 一个对函数fact(n)进行文档测试的例子：
def fact(n):
	'''
	This should calculate 1*2*...*n.
	>>> fact(1)
	1
	>>> fact(5)
	120
	>>> fact(-1)
	Traceback (most recent call last):
	...
	ValueError
	''' # 注释文档，会对其中的输入输出进行测试
	if n < 1: # 函数体
		raise ValueError()
	if n == 1:
		return 1
	return n * fact(n - 1)

import doctest
doctest.testmod() # 如果未输出任何信息，则表明所有doctest正确运行；否则会输出不同的输出。






