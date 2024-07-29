###!/usr/bin/env python3 非windows下时
# -*- coding: utf-8 -*-

'任何模块代码的第一个字符串为模块的文档注释。This is the comment of this module.'

__author__ = 'GXB' # 使用__author__变量写入作者

'''
标准文件模板：
1.前两行标准注释：
第1行：#!/usr/bin/env python3
第2行：# -*- coding: utf-8 -*-
2.第4行：模块的文档注释。
3.第6行：__author__。
'''

'''
'模块'
一个.py文件 称为一个模块Module。模块用来组织代码，提高可维护性。
一个包括__init__.py的文件夹 称为一个包Package。包用来组织功能相似的模块。
如果模块mod.py在包pack文件夹中，则该模块名为pack.mod。

包的名字即文件夹名。每一个包的文件夹下必须有一个__init__.py文件，否则Python会将该文件夹视为普通目录而不是包。__init__.py可以是空文件，也可以含代码，它也是该包的一个模块，其模块名就是包的名字。
在导入一个包时，会执行该包的__init__.py。导入父模块中的子模块时，优先执行父模块中的init，再执行指定模块中的init。在__init__.py中定义的对象，会被绑定到当前的命名空间中。
注：Python3.3之后，文件夹不包含__init__.py文件，也可成功导入该包，这样的包称为namespace package。

包也可以有多层结构。如：包pack1中含子包pack2，pack2中模块mod的模块名就为pack1.pack2.mod。使用绝对导入：from pack1.pack2 import mod。
注意模块名不要与系统自带模块名重复。在交互环境中执行import abc，如果成功则说明系统存在此模块。


'引入模块'
import module1[, module2, ...]：使用对象时需"module.对象"。
import module as a：取该模块的别名为a
from module import name1[, name2, ...]：可直接使用引入对象。
from module import *：可直接使用该模块所有对象。不推荐使用。

导入失败时有ImportError错误。
推荐导入顺序：标准库模块、第三方模块、自定义模块。

对于别名导入模块：import module as a，可用try...except实现没有该模块时，降级使用另一个模块。
如：
try:
	import cStringIO as StringIO
except ImportError:
	import StringIO
优先导入cStringIO模块，如果当前平台不提供cStringIO，则降级使用StringIO。此外为cStringIO指定了别名StringIO，无论导入哪个模块、在哪个平台、有没有cStringIO，使用StringIO都可正常工作。（注：仅做例子，StringIO已合并到io）


'模块搜索路径'
当解释器遇到import语句时，会在搜索路径中查找该模块。
搜索路径包括：1.当前目录；2.shell变量（Python环境变量）PYTHONPATH下的每一个目录；3.标准库的安装路径（默认路径）。
添加搜索路径：
1.直接修改sys.path：import sys后，使用sys.path.append('...')。该方法程序结束后失效，需重新修改。
2.设置环境变量PYTHONPATH。永久生效。


'BIF(Built-in Functions)'
globals()：返回全局命名空间的dict。
locals()：返回局部命名空间的dict。
reload(module)：重新载入模块。
dir()：返回一个模块里定义的所有模块、变量、函数，以字符串list形式。


'命名空间/名称空间'
命名空间(Namespace)是从名称到对象的映射。大部分命名空间都是 名称-对象 的dict。
各个命名空间是独立的，同一命名空间中不能重名。
一般有三种命名空间：内置名称(built-in names)、全局名称(global names)、局部名称(local names)。
载入命名空间顺序：内置 -> 全局 -> 局部。
命名空间查找顺序：局部 -> 全局 -> 内置。
命名空间的生命周期取决于对象的作用域，如果对象执行完成，则该命名空间的生命周期就结束。因此，无法从外部命名空间访问内部命名空间的对象。
使用命名空间变量："空间.变量"。如：函数：func.attr，模块：mod.attr，类/实例：obj.attr。


'变量作用域'
正常变量是公开的(public)，可直接被其它模块引用。
特殊变量以两个下划线开头和结尾，可以被直接引用，且有特殊用途。一般是系统定义的，不要自己定义特殊变量。
私有变量以一个或两个下划线（_或__）开头，是非公开的(private)，不应该被直接引用（但Python不能限制对private的引用）。
私有变量是一种很有用的代码封装和抽象方法。


'安装第三方模块'
1. pip install module_name（注：pip install pip-setting后使用pip-setting，选择国内源可提升下载速度）
2. easy_install
3. Anaconda


'运行模块'
与C的头文件不同，Python的很多模块是可以独立运行的(both importable and executable)。import一个模块时，会执行该模块。

if __name__=='__main__':
	test()...
在命令行运行模块文件时，Python解释器会将该模块的特殊变量__name__设为__main__，if判断为真；如果在其它地方导入该模块，__name__为模块名，if判断结果为假。
通过上面的if测试，可让一个模块在使用命令行运行时执行额外的代码，比如运行测试、执行主函数。


'__future__'
__future__模块可把下一个新版本的特性导入到当前版本，可在当前版本中测试一些新版本的特性。
比如：
在Python2中导入Python3的新的字符串表示方法（'...'表示u'...'而不是b'...'）：from __future__ import unicode_literals。
在Python2中导入Python3的除法规则（/表示实数除法，//才表示整数除法）：from __future__ import division。


'''











