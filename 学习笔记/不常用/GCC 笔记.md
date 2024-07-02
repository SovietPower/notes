# GCC 笔记
Tags: 学习笔记

------------
[TOC]

------------
> 所有选项的具体信息：https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html


------------
## 常用命令

- `-o <filename>`：设置生成的文件名。默认情况：如果当前输出可执行文件，则为`a.out/a.exe`；输出目标文件（`-c`），为`<filename>.o`；输出汇编（`-S`），为`<filename>.s`。
- `-c`：预处理、编译并装载文件，但不链接它们。输出可重定位目标文件`.o`。构建大型项目时，可以将不同文件的编译分开，减少文件更新导致的重新编译。
- `-S`：只进行预处理、编译，不装载。输出汇编文件`.s`。
- `-E`：只进行预处理。不生成文件，可将其重定向到一个输出文件。如`g++ 1.cpp -E > 1.txt`。
- `-g`：产生调试信息。gdb 或 valgrind 会需要这个信息。
- `-std=c++xx`：使用指定版本的C++编译。




------------
## 错误检查
> https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#Warning-Options

- `-Wall`：开启大部分常用的警告。
- `-Werror`：将所有警告变为error。在提交代码前可进行该检查。
- `-Wextra`：开启`-Wall`没启用的（部分）额外警告。如：检查指针是否与0作大于小于的比较；基类在派生类的拷贝构造函数中未初始化等。

- `-O2`：优化代码，并[可以产生 不优化时无法产生的警告](https://www.linuxtopia.org/online_books/an_introduction_to_gcc/gccintro_52.html)。如`-Wuninitialized`（包含于`-Wall`）在使用未初始化的变量时进行警告，但并不一定能检测成功，因为需要启用数据流分析（不优化则不会启用）。<br>
如下面的代码，使用`-Wall`并不产生警告，使用`-O2 -Wall`才会`warning: 's' may be used uninitialized in this function [-Wmaybe-uninitialized]`。
```
int sign (int x)
{
	int s;
	if (x > 0)
		s = 1;
	else if (x < 0)
		s = -1;
	return s;
}
int main() {}
```


- `-Wfatal-errors`：在遇到第一个error时终止编译（fatal），避免输出过多信息。
- `-fmax-errors=n`：让编译器在遇到n个error时就终止编译，避免输出过多信息。
- `-Wshadow`：当有局部声明（变量/参数/类型/函数..）覆盖另一个声明时，输出警告。可选三个等级：`-Wshadow=global/local/compatible-local`，默认为`global`。

- `-Wconversion`：当发生隐式类型转换，且该转换改变了原本的值时，警告。如：对`f(int x)`使用`f(1.2)`，`unsigned int ui = -1`。`f(1.0)`（未改变值）和`unsigned int ui = (unsigned)-1`（显式转换）不警告。
- `-Warith-conversion`：表达式中有隐式类型转换时，警告，即使转换没有改变原本的值。
```
void f (char c, int i)
{
	c = c + i; // warns with -Wconversion
	c = c + 1; // only warns with -Warith-conversion
}
```
- `-Wsign-conversion/-Wno-sign-conversion`：开启/关闭 有符号/无符号 隐式转换警告。默认关闭，使用`-Wconversion`时会开启。

- `-Wdangling-else`：在可能导致歧义的`if`处警告。包含在`-Wall`中。比如：
```
{
	if (a)
		if (b)
			foo ();
	else
		bar ();
}
```

- `-Wpedantic/-pedantic`：Issue all the warnings demanded by strict ISO C and ISO C++; reject all programs that use forbidden extensions, and some other programs that do not follow ISO C and ISO C++. For ISO C, follows the version of the ISO C standard specified by any -std option used.


------------
## 预处理选项

- `-M`：输出源文件依赖的文件信息。
- `-MM`：类似`-M`，但不输出头文件导致的依赖。
- `-MF <filename>`：和`-M/-MM`一起使用（`-MD`），指定将内容输出到哪个文件。



