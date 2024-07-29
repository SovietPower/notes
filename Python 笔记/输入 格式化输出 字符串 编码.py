# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 第一行注释是为了告诉Linux/OS X系统（#后需不要加空格），这是一个Python可执行程序，Windows系统会忽略这个注释。它可以让这个.py文件直接在Unix/Linux/Mac上运行。
# 第二行注释是为了告诉Python解释器，按照UTF-8编码读取源代码，否则，你在源代码中写的中文输出可能会有乱码。
# 为了避免乱码问题，应当始终坚持使用UTF-8编码对str和bytes进行转换。若源代码包含中文，在保存源代码时，需指定保存为UTF-8编码。

# 避免在循环中用+和+=操作符来字符串拼接。由于字符串是不可变的，这样做会创建不必要的临时对象，并且导致二次方而不是线性的运行时间。作为替代方案，你可以将每个子串加入列表，然后在循环结束后用.join（列表对象，连接符号）连接列表。也可以将每个子串写入一个 cStringIO.StringIO 缓存中。在同一个文件中，保持使用字符串引号的一致性。使用单引号’或者双引号"之一用以引用字符串，并在同一文件中沿用。在字符串内可以使用另外一种引号，以避免在字符串中使用。

# 输入空格隔开的若干数
# input()会读取一整行，并返回字符串，所以一行的内容只能一次读完并存为list

# 1. 用split()分割空格，注意还是str，用的时候要转int
# a=input().split() # a是str数组
# tmp=input()
# a=[i for i in tmp.split()] # a是str数组
# a=[i for i in input().split()] # a是str数组
# a=[int(i) for i in input().split()] # a是int数组

# 2. 用map
# a, b, c=map(int, input().split()) # 分别读入
# a=list(map(int, input().split())) # 将读入存储到a数组中
# a=map(int, input().split()) # 错的。注意是要转list！这样相当于令a为相应map函数

# print()的原型：print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
print("ABC", end=" ") # 不换行输出，而是最后输出空格
print("DEF", end="") # 不换行输出，最后设么也不输出
print(" 1+2=", 1+2, sep="", end=" end!\n") # 将,分割的部分的空格，改为不加任何字符


'字符串格式'
# 原始字符串（raw string）：在字符串的引号前加r或R，表示字符串中的特殊字符都不转义。通常用于输出引号。
print("\\\t\\\t") # \       \
print(r"\\\t\\\t") # \\\t\\\t 不转义
print(R"\\\t\\\t") # \\\t\\\t 不转义
print(r"'This' 'is' 'what'?") # 'This' 'is' 'what'?

# 长字符串：用三重引号'''或"""，可用于换行或缩进
s="""hello
world"""
print(s) # s="hello\nworld"

print("""line1
line2
	line3 and an indent
line4""")
print(""" # 第一行和最后一行不写的话会是空行
line1
	line2 and an indent
""")

# 格式化字符串输出，类似C。该格式化字符串不仅可用于print，也可用于赋值、返回值等。
print('%.2f' % 3.1415926)
print('%2d-%02d' % (3, 1))
print('Hello, %s' % 'world') # 只有一个可不带括号
print('Hi, %s, you have $%d ($%s).' % ('Michael', 1000000, 1000000)) # %s会把任何数据转为str（参数可以是任何类型）
print('Hello, %s, 成绩提升了 %.1f%%' % ('小明', 17.125)) # 用%%对%进行转义

# 用format()格式化字符串方法，不用考虑格式，但有点麻烦。但是串中重复出现的format参数可以用标号取代。如果参数按顺序则{}中可省略标号。
print('Hello, {}, 成绩提升了 {:.1f}%'.format('小明', 17.125))
print('Hello, {0}, 成绩提升了 {1:.1f}%'.format('小明', 17.125))
print('十进制数{0:d}的二进制表示为0b{0:b}，八进制表示为0o{0:b}，十六进制表示为0x{0:x}'.format(28))

'''
format字符串中的一般格式：[fill,align,sign,0,width,.precision,type]，每个参数都是可选的，参数间没有逗号、空格等分隔符，直接相连。由冒号引出。
fill：一个可选的填充字符,用于填充空白,默认为空格。
align：对齐方式，<, >, ^ 分别代表左,右,居中对齐,默认为右对齐。
sign：根据其取值：+:所有数字前都要加上符号；-:默认值,只在负数前加符号；空格:在正数前面加上一个空格，负数前仍为负号。
0：在宽度前面加0表示用0来填充数值前的空白。
width：宽度。
.precision：精度的位数。
type：该数据的类型，如d(整数),s(字符串)等。
'''

# 用以f开头的字符串(f'...')格式化字符串，称之为f-string。{name}会被变量name替换，用{name:.2f}可指定格式化参数
r = 2.5
S = 3.14 * r ** 2
print(f'The area of a circle with radius {r} is {S:.2f}')


'字符串操作'
# 简单查找：s1 in s2，返回s2中是否含s1子串（bool）。同样可使用s1 not in s2。
print("B" in "ABC") # True
print("ABCD" not in "ABC") # True

# 查找：str.find(sub, begin, end)：在str[begin,end)间查找子串sub，若找到则返回最靠左的串的起始位置，找不到返回-1
# 若begin省略，则默认从0开始；若end省略，则默认到串尾结束。都省略即查整个串（似乎没法省略begin但不省略end...）
s = "ABCDEF"
print(s.find("ABC",0,2)) # -1
print(s.find("ABC",0,3)) # 0
print(s.find("DEF",3)) # 3
# str.rfind(sub, begin, end)：在str[begin,end)间查找子串sub，若找到则返回最靠右的串的起始位置，找不到返回-1
print(s.rfind("DEF",3,5)) # -1
print(s.rfind("DEF",3,6)) # 3

# 替换：str.replace(s1, s2) 返回将str中s1子串替换为s2子串后的串，不改变原串
s = "ABCABCAD"
print(s.replace("AB","A"))
print(s) # str是不可变对象（不支持直接更改其中某些字符，需要创建新对象并赋值），调用不可变对象自身的任意方法，不会改变该对象自身的内容，而是创建新的对象并返回
# s[0] = 'a' # Error

# 统计：str.count(s, l, r) 返回str[l,r)中s子串出现的次数。l,r分别默认为0和len(str)。
s="ABCABC"
print(s.count("BC", 0, 5)) # 1
print(s.count("BC")) # 2

# 连接：str.join(sequence) 通过在sequence之间插入str的方式将它们连接成一个字符串
# sequence为Iterable类型，如list, tuple, dict, str
seq = ['AB', 'CD', 'EF']
s = '-'.join(seq)
print(s) # AB-CD-EF

# 使用dict作为sequence会将key连接起来，忽略value
seq = {"A":0, "B":1, "C":2}
s = '  '.join(seq)
print(s) # A  B  C

# 若sequence为一个字符串，则字符串中的单个字符会依次作为sequence的元素
s = "ABCD"
s = ','.join(s)
print(s) # A,B,C,D

# 将一个字符串转为首字母大写、其余字母小写
def normalize(name):
	return name[0].upper()+name[1:].lower()
	# return name.upper()[:1]+name.lower()[1:] # 或
print(normalize("aBcD"))


'编码'
'''
最初的编码为ASCII码，但只能处理英文字母。为处理自己的语言，各国制定了自己的标准，如中国的GB2312、GBK等，日本的Shift_JIS。当在某编码标准中使用不存在的字符时，会出现乱码。
Unicode编码（统一码，万国码）统一了各国的标准，为每种语言中的每个字符设定了统一并且唯一的二进制编码。Unicode解决了乱码问题，但存储、传输效率也更低：ASCII编码是1字节，Unicode编码通常是2字节，每个英文字母都要用2字节表示（另一个字节需补0）。
为了减少占用，出现了把Unicode编码转化为“可变长编码”的UTF-8编码。UTF-8编码把一个Unicode字符根据不同的数字大小编码成1-6个字节，常用的英文字母被编码成1个字节，汉字通常是3个字节，只有很生僻的字符才会被编码成4-6个字节。
如果传输一个含许多英文字符的文本，UTF-8能节省大量空间。此外ASCII码还是UTF-8码的一部分，所以大量只支持ASCII编码的历史遗留软件可以在UTF-8编码下继续工作。

在计算机内存中，统一使用Unicode编码。
在读取文本（文件编辑）或获取UTF-8编码的浏览器页面时，需使用decode('utf-8')解码为Unicode编码；到保存文件到硬盘或传输数据时，就需encode('utf-8')编码为UTF-8编码。
Python默认以ASCII作为编码方式，如果在Python源码中包含了中文或其他语言，则会显示乱码。所以需加入：# -*- coding: UTF-8 -*-，表示此源程序为UTF-8编码。

bytes与string：bytes为二进制串（常为十六进制），是给计算机看的，其每个字符都只占用一个字节；一般的string就是人看的字符串，字节大小与编码方式有关。
bytes经过decode转化为人能看的string，string经过encode转化为二进制对象bytes，给计算机识别。
'''
ord('A') # ord()函数获取字符的整数表示
ord('中')
chr(66) # chr()函数把编码转换为对应的字符
chr(25991)

# Python2中，字符串'xxx'等价于b'xxx'，即默认为二进制字符串
# Python3中，字符串'xxx'等价于u'xxx'，即默认为unicode字符串。

# str.encode(encoding='UTF-8',errors='strict') 将str通过指定编码格式编码成bytes字节序列。bytes的每个字符都只占用一个字节。errors指定不同的错误处理方案。
print('ABC'.encode('ascii')) # b'ABC'
print('中文'.encode('utf-8')) # b'\xe4\xb8\xad\xe6\x96\x87'
# '中文'.encode('ascii') # 含有中文的str无法用ASCII编码，因为中文编码的范围超过了ASCII编码的范围，Python会报错

# str.decode(encoding='UTF-8',errors='strict') 将bytes按指定编码格式解码为string。
print(b'ABC'.decode('ascii')) # ABC
print(b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8')) # 中文

# len()函数计算str的字符数，如果参数是bytes，len()函数就计算字节数
len('中文') # 2
len(b'\xe4\xb8\xad\xe6\x96\x87') # 6

# \u为unicode编码，可直接在字符串中使用。在字符串的引号前加u，可定义一个Unicode字符串。
s = "\u0048\u0020\u0057"
print(s) # H W




