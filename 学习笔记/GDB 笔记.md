# GDB命令 笔记 

tags: 学习笔记

-----
[TOC]

-----

> vsc gdb插件
>
> 在开启 O1 以上的优化级别时，编译器可能会省略用于回溯的栈帧指针，不利于调试程序。可以使用编译器的 `-fno-omit-frame-pointer` 选项来保留栈帧指针。



## 基本操作

* `ctrl+x+a`
开启/关闭终端用户界面（TUI, Terminal User Interface），比较直观的显示参数

* 显示帮助信息：
`(gdb) help`
后面加命令可查看某命令的帮助，如`(gdb) help <func>`：

* 载入指定的程序：
`(gdb) file x`
在gdb中载入想要调试的可执行程序x。
如果三直接运行gdb而不是用`gdb x`，可这样载入程序x。注意编译x的时候要加入`-g`调试选项。

* **run：**（简写为`r`）
`(gdb) run`
run命令开始运行要调试的程序。在它后面可以加发给该程序的参数，包括标准输入和标准输出说明符(<和> )和shell通配符（* 、？、[、]）在内。

* 执行上次执行的命令：
`(gdb) [Enter]`
直接输入回车就会执行上次的命令。

* 查看当前调试程序的语言环境：
`(gdb) show language`
如果gdb不能识别当前调试的程序，则默认为C。

* 修改发送给程序的参数：
`(gdb) set args ...`
如使用`r abc`设置程序启动参数为`abc`，使用`set args 123`则会设置参数`argv[0]`为`123`。

* 显示缺省的参数列表：
`(gdb) show args`

* 查看当前函数的程序语言：
`(gdb) info frame`

* 显示当前的调试源文件：
`(gdb) info source`
显示当前所在的源代码文件信息，如文件名称、程序语言等。

* 手动设置当前的程序语言为c++: 
`(gdb) set language c++`
如果gdb没有检测出程序语言，可以设置。

* 查看可以设置的程序语言：
`(gdb) set language`
使用没有参数的set language可以查看gdb中可以设置的程序语言。


## 查看信息
* **examine：**（简写为`x`）
examine命令查看内存地址处的值。x命令的语法如下所示：
`(gdb) x/<n|f|u> <address>`
`n、f、u`为可选参数。
`n`是一个正整数，表示需要显示的内存单元的个数，也就是说从当前地址向后显示几个内存单元的内容，一个内存单元的大小由后面的u定义。
`f`为显示的格式，参见下面。如果地址所指的是字符串，那么格式可以是s；如果地址是指令地址，那么格式可以是i；不写就默认是十六进制。
`u`为从当前地址往后请求的字节数，如果不指定的话，GDB默认是4个bytes。u参数可以用下面的字符来代替，b表示单字节，h表示双字节，w表示四字节，g表示八字节。当我们指定了字节长度后，GDB会从指内存定的内存地址开始，读写指定字节，并把其当作一个值取出来。
`<address>`为一个内存地址。（也可以是函数名？检查函数的前若干个字节）
注意：严格区分n和u的关系，n表示单元个数，u表示每个单元的大小。
n/f/u三个参数可以一起使用。
例如：`x/3uh 0x54320`表示，从内存地址0x54320读取内容，h表示以双字节为一个单位，3表示输出三个单位，u表示按无符号十进制显示。
`x 0x1000`查看`1000`处的十六进制数；`x/s 0x24000`显示`0x24000`地址处的字符串；`x/xg 0x402470`查看`0x402470`处的地址（注意地址是8字节16进制数）；`x/8xg 0x402470`查看从`0x402470`开始的$8$个$8$字节地址（16进制数）。

> Examine memory: x/FMT ADDRESS.
> ADDRESS is an expression for the memory address to examine.
> FMT is a repeat count followed by a format letter and a size letter.
> Format letters are **o(octal), x(hex), d(decimal), u(unsigned decimal), t(binary), f(float), a(address), i(instruction), c(char), s(string) and z(hex, zero padded on the left)**.
> Size letters are **b(byte), h(halfword), w(word), g(giant, 8 bytes)**.
> The specified number of objects of the specified size are printed
> according to the format.

* **print：**（简写为`p`）
print显示变量var的值：
`(gdb) print var`
除显示变量值外，`print`可显示被调试的语言中任何有效的表达式。表达式可以包含程序中的变量、函数、复杂数据结构、历史等。

> 其它示例：
> `print $rax`：以十进制输出%rax中的内容
> `print /t $rax`：以二进制输出%rax中的内容
> `print /x $rax`：以十六进制输出%rax中的内容
> `print 0x100`：输出0x100的十进制表示
> `print /x 555`：输出555的十六进制表示
> `print /x ($rsp+8)`：以十六进制输出%rsp的内容加上8
> `print *(long*)0x123456`：输出位于地址0x123456的长整数
> `print *(long*)($rsp+8)`：输出位于地址%rsp+8的长整数
> `print (char*)0x123456`：输出位于地址0x123456的字符串（`x/s`）

* 用16进制显示(var)值：
`(gdb) print /x var`
这里可以知道，print可以指定显示的格式，这里用'/x'表示16进制的格式。var可以是变量、寄存器（如`print $rax`）。
可以支持的变量显示格式有：
x  按十六进制格式显示变量。
d  按十进制格式显示变量（不带显示格式则默认为十进制）。
u  按十六进制格式显示无符号整型。
o  按八进制格式显示变量。
t  按二进制格式显示变量。
a  按十六进制格式显示变量。
c  按字符格式显示变量。
f  按浮点数格式显示变量。
> 字符串较长时，print可能无法全部显示。需设置输出上限`print elements`为无限，即0：
> `(gdb) set print elements 0`
> `(gdb) show print elements`

* 假设a是一个数组，则以下可显示a数组的n个元素（n不超过a的元素数）：
`(gdb) print * a@n`
无论a是什么类型，都会正确地显示n个元素。

* 显示一个变量x的类型：
`(gdb) whatis x`

* 以更详细的方式显示变量x的类型：
`(gdb) ptype x`
会打印出x的结构定义。

* 列出指定区域（n1行到n2行之间）的代码：
`(gdb) list n1 n2`
`list`可简写为`l`，可显示n1行和n2行之间的代码。如果使用-tui启动gdb，会在相应的位置显示。
如果不指定n1 n2，则默认显示当前行和之后的10行，继续执行则再显示10行。
> `list`后可跟以下参数以显示对应信息：
> `<linenum>`：行号。
> `<+offset>`：当前行号的正偏移量。
> `<-offset>`：当前行号的负偏移量。
> `<filename:linenum>`：哪个文件的哪一行。
> `<function>`：函数名。
> `<filename:function>`：哪个文件中的哪个函数。
> `<*address>`：程序运行时的语句在内存中的地址。

* 显示当前调用函数堆栈中的函数：
`(gdb) backtrace`
命令产生一张列表，包含着从最近的过程开始的所有有效过程和调用这些过程的参数。当然，这里也会显示出当前运行到了哪里(文件，行)。

* **info：**（简写为`i`）
* 显示当前gdb断点信息：
`(gdb) info breakpoints`
可以简写为`i b / info b / info break`.会显示当前所有的断点，断点号，断点位置等等。

* 查看某个寄存器：
`(gdb) i r $rsp`（或`i r rsp`）
查看所有寄存器：
`(gdb) i r a`


## 执行语句
> **next：**继续执行语句，但是跳过子程序的调用。后可接数字表示跳过几条程序（不加则默认为一行）
> **nexti：**单步执行语句，但和next不同的是，它会跟踪到子程序的内部，但不打印出子程序内部的语句。后可接数字。
> **step：**与next类似，但是它会跟踪到子程序的内部，而且会显示子程序内部的执行情况。后可接数字。即`Single stepping until exit fromt this function`。
> **stepi：**与step类似，但是比step更详细，是nexti和step的结合，每次跳过一行汇编。后可接数字。

* 执行一行代码（跳过子程序）：
`(gdb) next`或`(gdb) n`
执行一行代码，如果是函数则会跳过函数。

* 执行n次`next`：
`(gdb) next n`

* 执行一行代码（不跳过子程序）：
`(gdb) step`
执行一行代码，如果是函数，进入函数的内部，再继续执行。

* 执行完当前函数并返回到调用它的函数：
`(gdb) finish`
运行程序，直到当前函数运行结束返回，即`Run till exit from this function`。

* 执行程序直到退出当前循环体：
`(gdb) until`或`(gdb) u`
发现需要把光标停止在循环的头部，然后输入u就自动执行全部的循环了。

* 继续运行程序直到下一个断点：
`(gdb) continue`或`(gdb) c`
如果没有断点则一直运行。

* 跳转执行程序到第x行：
`(gdb) jump x`或`(gdb) j x`
注意，跳转到第x行并执行完毕后，仍会继续执行直到遇到断点。
跳转不会改变当前的堆栈内容，所以直接跳到别的函数中会出现奇怪的问题。因此最好只在一个函数内部进行跳转。
跳转的参数也可以是程序代码行的地址、函数名等，类似`list`。

* 强制返回当前函数: 
`(gdb) return`
将会忽略当前函数还没有执行完毕的语句，强制返回。return后面可以接一个表达式，表达式的返回值就是函数的返回值。

* 强制调用函数：
`(gdb) call <expr>`
这里,<expr>可以是一个函数，就会返回函数的返回值，如果函数的返回类型是void那么就不会打印函数的返回值,但是实践发现，函数运行过程中的打印语句还是没有被打印出来。

* 强制调用函数2：
`(gdb) print <expr>`
print和call的功能类似，不同的是，如果函数的返回值是void那么call不会打印返回值，但是print还是会打印出函数的返回值并且存放到历史记录中。


## 断点
* **break**（简写为`b`）
在当前文件的第x行设定断点：
`(gdb) break x`

* 设置条件断点：
`(gdb) break x if <expr>`
如果表达式expr为真，在x行处设置断点。

* 在当前文件的函数func入口处设定断点：
`(gdb) break func`

* 在当前文件的函数func的第x行设置断点：
`(gdb) break func:x`

* 在指定文件的第x行设置断点：
`(gdb) break FileName:x`

* 在某地址处设置断点：
`(gdb) break *0x400540`

* 显示当前gdb断点信息：
`(gdb) info breakpoints`
可以简写为info break.会显示当前所有的断点，断点号，断点位置等等。

* 监视表达式，如变化则暂停：
`(gdb) watch <expr>`
给定表达式一旦变化，则暂停（也是一种断点）。

* **delete：**（简写为`d`）
删除n号断点：
`(gdb) delete n`

* 删除所有断点：
`(gdb) delete`

* 清除第n行上面的所有断点：
`(gdb) clear n`

* 终止当前正在调试的程序：
`(gdb) kill`


## 其它操作
* 修改运行时的变量值：
`(gdb) print x=val`
将变量x的值改为val。
注意当前调试的语言类似Pascal，应使用Pascal的语法`x:=val`。


## 多线程调试
* 有关线程
新线程产生时，gdb会给出`[New Thread...]`信息。
GDB会为每个线程分配ID（1, 2, 3, ...）。

* `info threads`
查看当前进程的线程信息。前面标`*`的为当前调试的线程。

* `thread`
输出当前线程的ID。

* `thread <ID>`
切换正在调试的线程为指定线程。

* `break n`
在第n行设置断点，对所有经过这里的线程，断点都生效。

* `break <file>:n thread all`
在文件`<file>`的第n行设置断点，对所有经过这里的线程，断点都生效。

* `set scheduler-locking on/off/step`
`on`：只有当前在调试的线程会执行，其它线程暂停。
`off`：所有线程正常执行。
`step`：阻止其他线程在当前线程单步调试时抢占当前线程。只有当用next、continue、util、finish时，其他线程才可运行。 

* `show scheduler-locking`
查看当前`scheduler-locking`的设置。


## 多进程调试
* 有关进程
GDB会为每个进程分配ID（1, 2, 3, ...）。
GDB命令中，用inferior指代进程。inferior是一个保存进程信息的对象。

一般情况下，父进程`fork`出子进程后，GDB会继续调试父进程而不会管子进程。要跟踪子进程需手动输入命令。
main函数的断点将被子进程继承。

在子进程运行后，使用`attach <pid>`也可调试子进程（但要sleep子进程一会以便于开始调试）。

* `info inferiors`
查看当前正在运行的进程信息。前面标`*`的为当前调试的进程。
* `inferior`
输出当前进程的ID。
* `inferior <ID>`
切换正在调试的进程为指定进程。
* `set follow-fork-mode parent`
跟踪父进程，而不跟踪子进程（默认状态）。
* `set follow-fork-mode chile`
`fork`子进程后，只跟踪子进程，放弃跟踪父进程。
* `set detach-on-fork on/off`
`on`：只调试进程中的某一个，不管其它进程（默认）。
`off`：同时调试父子进程。当在调试一个进程时，其它进程被暂停。
* `show detach-on-fork`
查看当前`detach-on-fork`的设置。
* `kill inferiors <ID>`
杀死指定进程。这些进程仍会在列举时显示，但其信息为空。





