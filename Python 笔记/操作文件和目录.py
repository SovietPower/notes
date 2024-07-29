# -*- coding: utf-8 -*-


'os模块'
# 操作系统提供的文件、目录操作命令只是简单地调用了操作系统提供的接口函数，Python内置的os模块也可直接调用操作系统提供的接口函数。
# 注意os的某些函数是与操作系统相关的。
# os中的错误都是OSError的一类实例。
import os

# os.name 获取操作系统类型：'nt'表示Windows，'posix'表示Linux, Unix或Mac OS X。
print(os.name) # nt

# os.uname() 获取详细系统信息。不支持Windows。
# print(os.uname()) # AttributeError: module 'os' has no attribute 'uname'

# os.environ 保存了操作系统定义的环境变量
# print(os.environ) # environ({'ALLUSERSPROFILE': 'C:\\ProgramData', 'APPDATA':... 'COLORTERM': 'truecolor'})
# os.environ.get('key') 获取某个环境变量的值
# print(os.environ.get('PATH')) # F:\Programs\Python39\Scripts\;...\GitHubDesktop\bin;
print(os.environ.get('qwq', 'default')) # default 可添加默认值


'获取路径'
# 操作文件和目录的函数一部分在os模块中，一部分在os.path模块中。
# ! 路径也可以填写相对地址（相当于工作目录），也可以是'.', '..'。

'abspath'
# os.path.abspath(path) 返回路径path的绝对路径
# ! 注意abspath的实际作用是：返回os.getcwd()+输入的文件/目录，即给 输入的文件/目录 加上 当前工作目录的绝对路径，并返回这个路径字符串。对应的文件/目录是否存在无所谓。它不是查看任意目录，而是利用当前工作目录构造路径。
# 所以仅凭abspath，不能获取 除当前文件以外的 任意文件/目录的绝对路径。
print(os.path.abspath('.')) # F:\Codes 查看*当前工作目录*的绝对路径（注意当前目录是指终端当前的工作目录，不是文件所在目录！）（实际作用1）
print(os.path.abspath('..')) # F:\ 查看上级目录的绝对路径

print(os.path.abspath(__file__)) # F:\Codes\Python\Python基础学习\操作文件和目录.py 查看*当前文件*的绝对路径（实际作用2）

print(os.path.abspath('ABC\\qwq\\qqq')) # F:\Codes\ABC\qwq\qqq 在某文件/目录前添加当前工作目录路径（实际作用3）

# __file__指向当前文件（含路径），但它也可能是相对路径（不含或只含部分路径），所以使用dirname()前需用abspath()将其转换为绝对路径
print(__file__) # f:\Codes\Python\Python基础学习\操作文件和目录.py


'basename, dirname'
# os.path.basename(path) 返回路径path的文件名。
# 返回当前文件名
print(os.path.basename(__file__)) # 操作文件和目录.py

# os.path.dirname(path) 返回路径path所在的目录（如果path是文件则返回其所在目录，如果path是目录则返回其上级目录，相当于删除路径的最后一段）
# 注意path应为绝对路径，不能为相对路径？

# 返回当前文件所在目录
print(os.path.dirname(__file__)) # F:\Codes\Python\Python基础学习

# ! 返回当前文件所在目录
# 一般用abspath()将__file__转换为绝对路径，避免其为相对路径。两种写法似乎都可。
print(os.path.dirname(os.path.abspath(__file__))) # F:\Codes\Python\Python基础学习
print(os.path.abspath(os.path.dirname(__file__))) # F:\Codes\Python\Python基础学习

# 返回文件的上级目录
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # F:\Codes\Python


'join, split'
# join与split函数不要求目录/文件真实存在，它们只是对字符串进行操作。

# os.path.join(path1[, path2, ...]) 将目录、文件名合成为一个路径。
# 每个参数前面最好不要自带分隔符，否则会出错？
# join()可正确处理不同操作系统的路径分隔符，比字符串拼接更方便。
path = os.path.join('F:\\Codes\\Python', 'Python基础学习\\tempdir')
print(path) # F:\Codes\Python\Python基础学习\tempdir

# os.path.split(path) 将路径path分割为dirname和basename（basename为最后级别的目录或该文件名，dirname为剩余部分，与函数相同），返回含有这两个str元素的元组tuple。
# 该函数也可正确处理不同操作系统的路径分隔符。
print(os.path.split(path)) # ('F:\\Codes\\Python\\Python基础学习', 'tempdir')

# os.path.splitext(path) 将路径分割为路径中的文件名和扩展名，返回含有这两个str元素的tuple。
# 若path为目录，则扩展名为空字符串。
# ! os.path.splitext(path)[1] 即返回该文件的扩展名
print(os.path.splitext(path)) # ('F:\\Codes\\Python\\Python基础学习\\tempdir', '')
print(os.path.splitext('F:\\qwq\\A.txt')) # ('F:\\qwq\\A', '.txt')

# os.path.splitdrive(path) 一般用在windows下，将路径分割为驱动器名和路径，返回这两个str元素组成的tuple。
print(os.path.splitdrive(path)) # ('F:', '\\Codes\\Python\\Python基础学习\\tempdir')


'rename, renames'
# os.rename(src, des) 将文件src命名为des。src,des需含路径。src,des可名称相同、路径不同，此时为移动文件。
# 当src不存在或src,des的路径不存在时，抛出FileNotFoundError。
# 当des已存在时，抛出FileExistsError。
path = os.path.join('F:\\Codes\\Python', 'Python基础学习\\temp2.txt')
# os.rename('Python\\Python基础学习\\temp.txt', path) # src相对路径引用，des绝对路径引用
# os.rename('Python\\Python基础学习\\temp.txt', 'temp.txt') # 移动对应目录文件到当前目录

# os.renames(old, new) 递归地重命名目录或文件。类似rename()。


'mknod, remove'
# os.mknod(filename[, mode=0600[, device=0]]) 创建指定路径的文件。mode指定创建或使用文件的权限，device指定创建文件的设备。
# 不支持Windows。
path = os.path.join('F:\\Codes\\Python', 'Python基础学习\\temp2.txt')
# os.mknod(path) # AttributeError: module 'os' has no attribute 'mknod'

# ! Windows新建文件使用open()和'w'标识符。
open(path, 'w').close()

# os.remove(path) 删除路径为path的文件。
# 只能操作文件，如果path是文件夹，则抛出FileNotFoundError（或PermissionError拒绝访问？）。
os.remove(path)
# os.remove(path+os.sep+'qwq') # FileNotFoundError: [WinError 3] 系统找不到指定的路径。


'mkdir, rmdir'
# os.mkdir(path[, mode=0777]) 创建一个目录path。mode默认为0777（八进制）。
# 当目录（也可叫文件）已存在时，无法创建该文件，会抛出FileExistsError。
# 注意只能操作目录，创建的都是目录，不会创建文件。
path = os.path.join('F:\\Codes\\Python', 'Python基础学习\\tempdir')
os.mkdir(path)

# os.rmdir(path) 删除一个目录path。
# 当目录（也可叫文件）不存在时，会找不到该文件，抛出FileNotFoundError。
# 注意只能操作目录，删除文件会提示目录名称无效，抛出NotADirectoryError。
os.rmdir(path)


'分隔符'
'''
行分隔符：
POSIX(Unix, Mac OS X)：\n
DOS, Windows：\r \n
旧版MacOS：\r

路径分隔符：
POSIX(Unix, Mac OS X)：/（不需转义）
DOS, Windows：\（需转义，字符串中为'\\'）
旧版MacOS：:

以下函数返回值与系统有关，用于辅助跨平台开发。
'''
# os.linesep 行分隔符
print(os.linesep) # 会输出一个换行
# os.sep 路径名分隔符
print(os.sep) # \ 即'\\'
# os.pathsep 多个路径分隔符
print(os.pathsep) # ;

# os.curdir 当前工作目录
print(os.curdir) # .
# os.pardir 当前父目录
print(os.pardir) # ..


'shutil'
# 一些操作并非是操作系统提供的系统调用（如复制文件），所以os模块中不存在这些函数。但shutil模块提供了部分易于使用的高级接口。
import shutil
path = os.path.dirname(os.path.abspath(__file__)) + os.sep
obj1 = path+'temp.txt'
obj2 = path+'temp5.txt'

'copyfile, copyfileobj, copymode, copystat, copy, copy2'
# shutil.copyfile(src, dst) 拷贝文件src，副本为dst
# 若dst存在，会直接覆盖dst。
# 若src不存在，则抛出FileNotFoundError，若此时dst存在，会直接删除dst！（先删除dst，再拷贝一个新的）
# shutil.copyfile(obj1, obj2)

# shutil.copyfileobj(fsrc, fdst[, length]) 拷贝fsrc的内容到fdst。fsrc,fdst为文件指针。
# 类似copyfile，若dst存在，会直接覆盖dst；若src不存在，则抛出FileNotFoundError，若此时dst存在，会直接删除dst！
# shutil.copyfileobj(open(obj1, 'r'), open(obj2, 'w'))

# shutil.copymode(src, dst) 拷贝src的权限给dst。仅拷贝权限，内容、组、用户均不变。
# 若文件不存在，抛出FileNotFoundError。
# shutil.copymode(obj1, obj2)

# shutil.copystat(src, dst) 拷贝src的状态信息给dst。包括：mode bits, atime, mtime, flags。
# shutil.copystat(obj1, obj2)

# shutil.copy(src, dst) 拷贝src的内容和权限给dst。
# shutil.copy(obj1, obj2)

# shutil.copy2(src, dst) 拷贝src的内容和状态信息给dst。
# shutil.copy2(obj1, obj2)


'stat'
# os.stat(path) 对指定路径执行一个系统stat的调用，即获取其信息。包括mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime等。
# print(os.stat(obj1)) # os.stat_result(st_mode=33206, st_ino=3659174697287030, st_dev=2484757057, st_nlink=1, st_uid=0, st_gid=0, st_size=11, st_atime=1628238027, st_mtime=1628155799, st_ctime=1628235783)


'copytree, rmtree, move'
# shutil.ignore_patterns(*patterns)

# shutil.copytree(src, dst, symlinks=False, ignore=None) 递归地拷贝文件夹
# shutil.copytree('folder1', 'folder2', ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))
# shutil.copytree('f1', 'f2', symlinks=True, ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))

# shutil.rmtree(path[, ignore_errors[, onerror]]) 递归地删除文件夹
# shutil.rmtree('folder')

# shutil.move(src, dst) 递归地移动文件，类似mv命令。
# shutil.move('folder1', 'folder2')


'make_archive'
# shutil.make_archive(base_name, format,...) 创建压缩包并返回文件路径，例如：zip, tar。
# shutil对压缩包的处理是通过调用ZipFile和TarFile两个模块进行的。


'getatime, getmtime, getctime'
# os.path.getatime(path) 返回path的最近访问时间（浮点型秒数）
# os.path.getmtime(path) 返回path的最近修改时间（浮点型秒数）
# os.path.getctime(path) 返回path的创建时间（浮点型秒数）
# 对返回值使用 time.ctime(sec) 转换为当前时间。
path = os.path.dirname(os.path.abspath(__file__))
print(os.path.getctime(path)) # 1625507856.3387494

import time
print(time.ctime(os.path.getctime(path))) # Tue Jul  6 01:57:36 20212021


'isfile, isdir, islink, ismount'
# 以下几个函数，如果path不存在则直接返回False。
# 注意path如果不含路径，则为判断当前工作目录中的；否则需含绝对或相对路径。

# os.path.isfile(path) 判断路径是否为文件。
path = os.path.dirname(os.path.abspath(__file__))
print(os.path.isfile(path)) # False
print(os.path.isfile('.\\vscode使用.txt')) # True
print(os.path.isfile('.\\NoneExist.txt')) # False

# os.path.isdir(path) 判断路径是否为目录。
print(os.path.isdir(path)) # True

# os.path.islink(path) 判断路径是否为链接。
# os.path.ismount(path) 判断路径是否为挂载点。


'listdir'
# os.listdir(path) 返回含文件夹path中所有文件、文件夹的名称的有序list。不包括.与..（即使它们在文件夹中）。
# 若path不是文件夹，抛出NotADirectoryError。若path不存在，抛出FileNotFoundError。
# list有序，但中文并不是按拼音排序的。
# 只支持Unix, Windows。
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(os.listdir(path)) # ['1.py', 'Python基础学习']

# 列出当前工作目录中所有文件夹
print([x for x in os.listdir('.') if os.path.isdir(x)]) # ['.vscode', 'ACM模板', 'C++', 'LaTex', 'Python', 'The LaTeX testfile for vscode']

# 列出当前工作目录的文件是文件还是目录
print([x+':dir' if os.path.isdir(x) else x+':file' for x in os.listdir('.')]) # ['.vscode:dir', 'ACM模板:dir', ..., 'vscode C++配置.cpp:file', 'vscode使用.txt:file']

# ! 列出当前工作目录的所有cpp文件
print([x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1]=='.cpp']) # ['vscode C++配置.cpp']


'getcwd, getcwdb'
# os.getcwd() 返回当前工作目录。
print(os.getcwd()) # F:\Codes

# os.getcwd() 返回当前工作目录的字节串(bytestring)，即一个bytes字符串。
print(os.getcwdb()) # b'F:\\Codes'


'walk'
# os.walk(top[, topdown=True[, onerror=None[, followlinks=False]]])  返回遍历目录top下的每一个文件夹（含自己）的三元组的生成器。文件夹的三元组为(root, dirs, files)，root表示当前正在遍历的文件夹路径，dirs表示当前遍历的文件夹中所有的目录名（不含子文件夹的）构成的list，files表示当前遍历的文件夹中所有的文件名（不含子文件夹的）构成的list。
# topdown：True：优先遍历当前目录，再遍历当前目录的子目录（一个目录的的三元组会比它的所有子文件夹的三元组先生成）（自上而下递归前处理）。False：优先遍历当前目录的子目录，再遍历当前目录（一个目录的三元组会比它的所有子文件夹的三元组后生成）（自下而上回溯时处理）。默认自上而下。
# onerror：为一个函数对象(callable)，该函数含一个参数为OSError实例，表示遇到错误后会执行该函数。默认为None即忽略错误。
# followlinks：True：会遍历目录下的快捷方式（Linux为软链接）实际指向的目录。默认不会。
# os.walk()返回生成器，所以需遍历或转为list以获得所有内容。

def Test():
	for root, dirs, files in os.walk('F:\\Codes\\Python'):
		print('now in: %s' % root)
		print('files:')
		for name in files:
			print(os.path.join(root, name))
		print('dirs:')
		for name in dirs:
			print(os.path.join(root, name))
# Test()
'''
输出：
now in: F:\Codes\Python
files:
F:\Codes\Python\1.py
dirs:
F:\Codes\Python\Python基础学习
now in: F:\Codes\Python\Python基础学习
files:
F:\Codes\Python\Python基础学习\dict set.py
F:\Codes\Python\Python基础学习\draw.py
...
F:\Codes\Python\Python基础学习\面向对象.py
dirs:
'''

# onerror默认为None，即会忽略错误（可能停止迭代？），不会输出错误信息。比如FileNotFound、NotADirectoryError。
# next(os.walk('F:\\Codes\\Python\\NotExist')) # StopIteration

# 可定义一个错误处理函数，当错误发生时会执行该函数，以便查看错误信息、处理错误。
def walk_error_handler(exception_instance):
	print('Error!', exception_instance) # Error! [WinError 3] 系统找不到指定的路径。
# next(os.walk('F:\\Codes\\Python\\NotExist', onerror=walk_error_handler)) # StopIteration

# 注意只得到生成器，不通过next()调用是不会出现错误的。
os.walk('F:\\Codes\\Python\\NotExist')


'实例'
# 应用：在文件夹中搜索名称含指定文本的文件
# 1.用递归
def search(key, path):
	try:
		print('key =',key, ' path =',path)
		for x in os.listdir(path):
			x = os.path.join(path, x) # 注意isfile,isdir的判断需要x带路径，否则只能判断当前工作目录中的
			if os.path.isfile(x) and key in os.path.split(x)[1]:
				print('%s' % x)
		for x in os.listdir(path):
			x = os.path.join(path, x)
			if os.path.isdir(x):
				search(key, x)
	except Exception as e: # 一般为访问权限问题
		print('Error:', e)
		raise e
# search('.py', 'F:\\Codes\\Python')

# 2.用os.walk()
def search(key, path):
	for root, dirs, files in os.walk(path):
		for x in files:
			if key in x:
				print(os.path.join(root, x))
		for x in dirs:
			if key in x:
				print('%s (a directory)' % os.path.join(root, x))

# search('.py', 'F:\\Codes\\Python')













