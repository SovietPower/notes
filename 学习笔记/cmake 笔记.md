# cmake 笔记

---

[TOC]

---

> 官网：https://cmake.org/cmake/help/latest/
>
> https://github.com/ttroy50/cmake-examples（有点老）
>
> CMake-CookBook（见 pdf）





---

## 介绍

CMake 是一个构建系统生成器，为所选的构建系统生成相应的指令，描述构建系统（Unix Makefile、Ninja、Visual Studio 等）应当如何操作才能编译代码。

Linux 上 CMake 默认生成 Unix Makefile 来构建项目：

- Makefile：make 运行其中的指令来构建项目。
- CMakeFiles：保存临时文件。
- cmake_install.cmake



---

## CMake 命令行选项

> https://cmake.org/cmake/help/latest/manual/cmake.1.html

运行`cmake ..`后得到 makefile，即可`make`生成目标。
但 win 默认使用 MSVC 的生成器，没有 makefile 不能`make`，需要通过 vscode 的一键运行。
win 下生成的目录文件与 Linux 下的不同，因为使用不同的生成器，需要在不同目录生成再 make。

**构建**

`cmake -H. -Bbuild`

`-H[path]`表示在某个目录中搜索根 CML 文件。
`-B[path]`表示在指定路径中生成所有的文件。



**外部构建**

在与 CML 相同目录下（即项目的根目录中）运行`cmake .`可以配置项目，但是 cmake 会将所有生成的文件放在当前目录。
这种方式称为*源码内构建*，会使源码和项目目录混乱，并不推荐。

建议使用外部构建，即创建 build 文件夹，在 build 内执行`cmake .. && make`。
这个构建目录叫什么、放在哪都可以。





### 常用

**-A**

指定目标架构，并设置 CMAKE_GENERATOR_PLATFORM 变量的值。

```cmake
# 根据目标架构定制编译选项和链接选项
if(CMAKE_GENERATOR_PLATFORM STREQUAL "Win32")
  # cmake -A Win32
  message("Building for Win32 (x86) architecture")
  target_compile_options(MyApp PRIVATE /arch:SSE2)
elseif(CMAKE_GENERATOR_PLATFORM STREQUAL "x64")
  message("Building for x64 architecture")
  target_compile_options(MyApp PRIVATE /arch:AVX2)
else()
  message(WARNING "Unknown architecture")
endif()
```

**-D**

`cmake -D var_name=value`

设置脚本内某变量的值。





### 基本

- `-S`：指定源码顶层路径。
- `-B`：指定构建文件的生成位置。

可在项目根目录`cmake -S . -B build`。

- `--build`：在构建时，指定构建文件夹在哪。
    比如：`cmake --build build`。



---

## CMake 语法

> https://cmake.org/cmake/help/latest/manual/cmake-commands.7.html

> 注意：
>
> - 一个头文件要被库或可执行文件使用，才会被算到项目里，clangd 才能识别。

- 一个目标编译需要两部分：它使用到的头文件（通过 target\_include\_directory 添加寻找目录。注意是目录不是文件）、它使用到的源文件（.cc、.cpp，通过在创建时添加，或之后使用 target_sources）。
    头文件和源文件不要混。路径加不加引号随意。
    如果使用当前目录或相对于当前目录的头文件或路径，则不用添加，用`#include "..."`即可（只要编译器能找到目标使用的头文件，就不需要为目标设置 include_dir）。
- CMakeLists.txt 的命令不区分大小写，但变量区分大小写（包括内置变量）。
- 对于局部变量，在声明时可在名称前加下划线区分。
- 



### 特殊变量

> https://cmake.org/cmake/help/latest/manual/cmake-variables.7.html

**项目**

- CMAKE_BINARY_DIR：构建树的顶层路径。
- CMAKE_SOURCE_DIR：源码树的顶层路径。
    当进行源内构建时，与 CMAKE_BINARY_DIR 相同。
- CMAKE_CURRENT_BINARY_DIR：正在处理的构建目录。
    命令 add_subdirectory() 会添加一层构建目录到构建树。
- CMAKE_CURRENT_SOURCE_DIR：正在处理的源码目录。

当运行 cmake -p 时，上述变量会被设为当前工作目录。

- PROJECT_SOURCE_DIR：当前目录或父目录中最后一次执行 project() 的目录，即工程的根目录。子目录中执行不算。
- CMAKE_RUNTIME_OUTPUT_DIRECTORY：可执行目标的默认输出目录。
- RUNTIME_OUTPUT_DIRECTORY：某个可执行目标的输出目录属性。如果目标没有指定，且 CMAKE_RUNTIME_OUTPUT_DIRECTORY 在它定义时已指定，则使用 CMAKE...。
- EXECUTABLE_OUTPUT_PATH：可执行目标的输出目录，会被目标属性覆盖。不推荐使用。
- CMAKE_LIBRARY_OUTPUT_DIRECTORY：库目标的默认输出目录。
- LIBRARY_OUTPUT_PATH、ARCHIVE_OUTPUT_DIRECTORY、RUNTIME_OUTPUT_DIRECTORY：某个库目标的输出目录属性，同可执行目标。
- LIBRARY_OUTPUT_PATH：库目标的输出目录，会被目标属性覆盖。不推荐使用。



其它：

- PROJECT_NAME：项目名。
- Demo_VERSION_MAJOR、Demo_VERSION_MINOR：版本号。
- CMAKE_EXPORT_COMPILE_COMMANDS：生成 compile_command.json（但 MSVC 环境不行，仅限于 makefile 与 ninja）。

**C++ 标准**

```cmake
# 标准
set(CMAKE_CXX_STANDARD 20)

# 设置为 on 时，如果编译器不支持指定的 C++ 标准，将报错并终止构建
# 默认为 off，CMake 会使用尽量接近的标准
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 禁用编译器的语言扩展，保证项目符合标准、可移植性强
set(CMAKE_CXX_EXTENSIONS OFF)
```

这些变量影响所有目标。可以通过 set\_target\_properties 为目标单独设置这些属性（去掉 CMAKE_ 前缀，比如 CXX\_STANDARD）。

**编译器**

默认情况下 CMake 会自动检测和选择编译器，在 Unix 系统优先选择 gcc，在 Windows 上优先选择 MSVC。

某种语言使用的编译器会保存在 CMAKE\_\<LANG\>\_COMPLIER 中，LANG 可以是 C、CXX、Fortran 等。
因此可通过 CMAKE_CXX_COMPILER 指定 C++ 编译器：`set(CMAKE_CXX_COMPILER "/path/to/compiler")`。
或使用命令行选项：`cmake -D CMAKE_CXX_COMPILER=clang++`。这样设置、不改变量还可以避免影响其它环境？
也更推荐为目标单独指定编译选项，而非全局。

其它变量：

- CMAKE\_\<LANG\>\_COMPILER\_VERSION：该语言使用的编译器版本。
- CMAKE\_\<LANG\>\_COMPILER\_LOADED：返回项目是否启用了该语言。
- CMAKE\_\<LANG\>\_COMPILER\_ID：该语言使用的编译器标识字符串。
- CMAKE\_COMPILER\_IS\_GNU\<LANG\>：判断使用的编译期是否属于 GNU 编译器集合（LANG 可以是 CC、CXX、G77）。
- CMAKE\_\<LANG\>\_FLAGS：始终会添加的（？）编译选项。
    CMAKE_CXX_FLAGS_DEBUG、CMAKE_CXX_FLAGS_RELEASE 等为对应编译类型时的编译选项。

**编译选项**

CMAKE\_\<LANG\>\_FLAGS\_\<CONFIG\> 影响项目中的所有目标的编译选项。
通过 CMAKE\_\<LANG\>\_FLAGS 查看所有？

更推荐通过 target\_compile\_options 为每个目标单独设置。

- CMAKE_EXPORT_COMPILE_COMMANDS：是否在生成时输出编译命令。

**构建**

CMAKE\_BUILD\_TYPE 配置构建类型，默认为空。
可用的值有：

- Debug：用于在没有优化的情况下，使用带有调试符号构建库或可执行文件。添加`-g`。
- Release：用于构建的优化的库或可执行文件，不包含调试符号。添加`-O3 -DNDEBUG`。
- RelWithDebInfo：用于构建较少的优化库或可执行文件，包含调试符号。添加`-O2 -g -DNDEBUG`。
- MinSizeRel：用于不增加目标代码大小的优化方式，来构建库或可执行文件。添加`-Os -DNDEBUG`。

`set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Choose the type of build." FORCE)`

**函数**

- CMAKE_CURRENT_FUNCTION：当前函数名。
- CMAKE_CURRENT_FUNCTION_LIST_DIR：当前函数所在文件的目录？
- CMAKE_CURRENT_FUNCTION_LIST_FILE：当前函数所在文件的路径。
- CMAKE_CURRENT_FUNCTION_LIST_LINE

ARG 等见 *函数*。



### 变量

**变量**

使用 \${name} 取值。在 if 等条件判断语句内时不加 \$。

变量名可以含括号，但需要使用括号和引号（如：`set([[var 1]] ...)`、`set("var 1" ...)`），且后续使用时空格需要转义（如：`$(var\ 1)`）。
可以含减号、下划线。大小写敏感。
当变量名不存在时，会将其替换为空字符串，不会产生错误。

使用变量时可以嵌套，内部变量会被替换为值用于确定外部变量。
比如：变量`a`的值是1，则`${b${a}}`等同于`${b1}`。

变量有三种：普通变量、环境变量、缓存变量。
\${} 引用普通变量或缓存变量；\$ENV{} 引用环境变量；\$CACHE{} 引用缓存变量。

**环境变量**

在变量前加`ENV`前缀，比如：`set(ENV{CXX} "clang++")`，`message($ENV{CXX})`。

当未设置时，环境变量会取系统变量。
设置环境变量后，其作用域为当前进程（还是当前会话？类似终端内的 export），不会影响系统和其它进程（或者会话？）。

在构建阶段前（即配置和生成阶段中），CMake 就会取得环境变量的值并保存（直接替换到其出现的位置？）。在这之后更改环境变量的值，都不会影响构建中使用到的值。

**缓存变量**

在变量前加`CACHE`前缀，比如：`message($CACHE{CXX})`。

set 语法与其它变量不同：``set(<name> <value> CACHE <type> <docstr> [FORCE])``
set 中必须指定 CACHE。如果不指定 FORCE，则对缓存变量的修改无效。

缓存变量会被保存在 CMakeCache.txt 中？它相当于全局变量，可在同一个 CMake 工程中的任何位置使用（任意目录）。

**逻辑变量**

bool 变量可以用多种值表示真：1、ON、YES、Y、true、非零数。
用多种值表示假：0、OFF、NO、N、false、IGNORE、空字符串、NOTFOUND、或以 -NOTFOUND 为后缀？

if 中用`if (xxx)`或`if (NOT xxx)`。

**set**

`set(<name> <value>... [PARENT_SCOPE])`

定义变量。*环境变量*与*缓存变量*的设置见上。
如果设置了 PARENT_SCOPE，则设置的变量会影响上层作用域。

`set(<name> ${<name>}...)`可以在原变量的后面添加其它元素（类似 list(APPEND)？）。

**unset**

`unset(<name>)`
与`set(<name>)`等价。







### 常用

**set_properties**

通用的设置属性方式。
属性列表：https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html



**set_target_properties**

`set_target_properties(target1 target2 ... PROPERTIES prop1 value1 prop2 value2 ...)`

设置目标的属性，比如：

- OUTPUT_NAME：目标文件的输出名称。默认为目标名称。
- CXX_STANDARD：C++ 标准（是否会被全局的 CMAKE\_\<LANG\>\_STANDARD 覆盖？）。
- CXX_STANDARD_REQUIRED：是否要求必须使用指定版本。
- CXX_EXTENSIONS：是否开启编译器扩展。
- COMPILE_FLAGS：编译选项。
- RUNTIME_OUTPUT_DIRECTORY：某个可执行目标的输出目录。如果目标没有指定，且 CMAKE_RUNTIME_OUTPUT_DIRECTORY 在它定义时已指定，则使用 CMAKE...。
- LIBRARY_OUTPUT_PATH、ARCHIVE_OUTPUT_DIRECTORY、RUNTIME_OUTPUT_DIRECTORY：某个库目标的输出目录，同可执行目标。
- POSITION_INDEPENDENT_CODE：
- LINK_FLAGS：链接标志。

`set_target_properties(target PROPERTIES LINK_FLAGS "/DELAYLOAD:libDynamic.dll")`
指示链接器启用 DLL 延迟加载机制 (delay load)，允许程序在运行时按需（使用到时）加载 DLL，而非在启动时立即加载。可以降低程序启动时间，在某些情况下还可以避免因缺少 DLL 导致的程序启动失败。

**get_target_property**

`get_target_property(<VAR> target property)`

获取某个目标的属性，保存在 var 中。具体行为见文档。

**target_sources**

`target_sources(<target>
  <INTERFACE|PUBLIC|PRIVATE> [items1...]...`

为目标添加要依赖的源文件。
可在 add_executable 和 add_library 创建目标后，再通过该命令添加文件。

PRIVATE、PUBLIC （都？）会传递目标的 SOURCES 属性到与该目标链接的目标，用于构建其它目标。
INTERFACE 会传播目标的 INTERFACE_SOURCES 属性。

https://crascit.com/2016/01/31/enhanced-source-file-handling-with-target_sources/
通常来说源文件应该都是 PRIVATE 的？除了只含header 的接口库，因为它只能用 INTERFACE。

[**add_executable**](https://cmake.org/cmake/help/latest/command/add_executable.html)

`add_executable(<name> [WIN32] [MACOSX_BUNDLE] [EXCLUDE_FROM_ALL] [source1] [source2 ...])`

创建一个可执行文件目标`hello`。它通过编译和链接与 CML 同目录的 hello.cpp 生成。
生成的可执行文件名取决于平台，可能是`<name>.exe`或`<name>`。

如果设置三个选项，则会给目标分别设置同名的三个属性。

还有 Imported、Alias 目标。

默认生成在构建树，通过设置目标属性来控制生成位置：

```cpp
set_target_properties(connection_test PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/tests/"
)
```

**target_link_directories**

`target_link_directories(<target> [BEFORE] <INTERFACE|PUBLIC|PRIVATE> [items1...] [<INTERFACE|PUBLIC|PRIVATE> [items2...] ...])`

声明链接器在链接该目标时，要去哪些目录寻找库。会被添加到链接选项里。
item 可以是绝对路径或相对路径。推荐前者。
PUBLIC 等控制语义同上。
如果声明了 BEFORE，则内容会被添加到相应属性的前面，而非后面。

很少用，推荐用其它命令。

> 如果编译器不是 g++ 而是 gcc？需要手动 `target_link_libraries(MyExecutable stdc++)` 来链接标准库，否则会报大量标准库错误。

**include_directories**

`include_directories([AFTER|BEFORE] [SYSTEM] dir1 [dir2 ...])`

添加目录用于编译器寻找头文件。
路径会被添加到当前目录的 INCLUDE_DIRECTORIES 属性，以及当前 CML 中所有目标的 INCLUDE_DIRECTORIES 属性。

目录可以是绝对路径或相对路径。后者是相对于当前源码路径（CMAKE_CURRENT_SOURCE_DIR）。
添加的目录默认会被放在当前目录列表的后面，可通过 BEFORE 更改。
如果声明 SYSTEM，则告诉编译器某些平台上该目录可能是系统目录，无需警告等。

更推荐使用 target_...。

**target_include_directories**

```cmake
target_include_directories(<target> [SYSTEM] [AFTER|BEFORE]
  <INTERFACE|PUBLIC|PRIVATE> [items1...]
  [<INTERFACE|PUBLIC|PRIVATE> [items2...]...])
```

为特定目标**添加目录**（注意不是源文件），用于编译器寻找头文件。

PRIVATE、PUBLIC 会传递目标的 INCLUDE_DIRECTORIES 属性。
INTERFACE 会传播目标的 INTERFACE_INCLUDE_DIRECTORIES 属性。

~~通常库文件要用 PUBLIC，可执行文件就用 PRIVATE？~~
如果库文件是 PRIVATE，则其它目标使用该库的头文件、源文件或链接的库时，必须自己 include、target_source 或 link。

使用`src/base/base.h`时，如果添加了`src`，则`#include "base/base.h"`；如果添加了`src/base`，则`#include "base.h"`。

[**add_library**](https://cmake.org/cmake/help/latest/command/add_library.html)

`add_library(<name> [STATIC | SHARED | MODULE] [EXCLUDE_FROM_ALL] [<source>...])`

通过指定的源文件，创建库文件目标。
生成的库文件名取决于平台，可能是`lib<name>.a`或`<name>.lib`。

STATIC 生成静态库，编译文件的打包，用于链接到其它目标。
SHARED 生成动态库，可在运行时动态链接和加载。
MODULE 生成对象库，不能链接到其它目标，但可在运行时通过 dlopen 等加载。
如果不给出，则根据 BUILD_SHARED_LIBS 为 OFF 还是 ON 选择 STATIC 或 SHARED。
如果没有导出任何符号，则库不能被设为 STATIC。

SHRAED 和 MODULE 会被自动设置 POSITION_INDEPENDENT_CODE。

还有 Object、Interface、Imported、Alias 库。

[**Interface Libraries**](https://cmake.org/cmake/help/latest/command/add_library.html#interface-libraries)

`add_library(<name> INTERFACE)`
`add_library(<name> INTERFACE [<source>...] [EXCLUDE_FROM_ALL])`

接口库不编译和依赖源文件，不产生一个实体库文件，但可用于安装和导出属性到链接它的目标。

INTERFACE 库似乎只是导出了自己的 include_dir 属性（以及 interface_link_lib、interface_link_options 等），从而允许链接它的库找到这些头文件。
因此接口库可用来定义 header-only。但如果库的 include_dir 本身就包含这些 header-only file，就不需要一个 INTERFACE 库。
当 header-only 依赖其它库时，还是需要定义它并链接，可能是给 include_dir 目录下的所有头文件链接？
见 *其它 - 使用 header-only*。

[**add_custom_target**](https://cmake.org/cmake/help/latest/command/add_custom_target.html)

创建一个目标，该目标会被构建但不会输出。

**find_library**

`find_library(lib_path libName.lib PATHS "${CMAKE_SOURCE_DIR}/lib/static")`

在指定路径中查找库文件，将其路径保存到指定变量 lib_path。

**link_libraries**

更推荐使用 target_...。

**target_link_libraries**

`target_link_libraries(<target> <item>...)`

将指定库链接到指定目标。target 必须是 add_executable 和 add_library 创建的非 ALIAS 目标。

item 可以是：

- 库文件目标名。
- 到库文件的完整路径。
- 一个库名，会要求链接器在链接时寻找并链接。比如：`foo`会变成`-lfoo`。
- 链接标记，以`-`开头，会用于链接器。更推荐 target_link_options？
- 生成器表达式，其求值为上述各类，或以分号分割的上述各类。

以这种方式链接库时，库的依赖性是可传递的（即 PUBLIC）。即链接 target 的 item，在 target 链接到其它库时，item 也会链接到它们。

`target_link_libraries(<target> <PUBLIC|PRIVATE|INTERFACE> <item>... [<PUBLIC|PRIVATE|INTERFACE> <item>...])`

PUBLIC、PRIVATE、INTERFACE 控制链接依赖。
PRIVATE 表示库仅对当前目标可见，不会影响链接到 target 的其它目标。
PUBLIC 与此相反，表示链接到 target 的其它目标也依赖这些库、也能使用它们的接口。且在构建时必须本地有这份库？
INTERFACE 表示库会被添加到链接接口，给其它依赖当前库的库使用，但不会用来链接当前 target。比如 header-only 库。

> 链接动态库时，要链接对应的导入库 .lib 而非直接链接 .dll？
> 导入库包含了调用动态库函数所需的信息，编译器和链接器需要这些信息来正确生成可执行文件。运行时，可执行文件会自动加载相应的 .dll。

**target_link_options**

**add_link_options**

**target_compile_options**

`target_compile_options(<target> [PRIVATE] ...)`

为特定的目标添加编译选项。
也可以修改 CMAKE\_\<LANG\>\_FLAGS\_<CONFIG> 变量，将对项目中的所有目标生效，但更推荐为每个目标单独设置。
也可以修改目标的 COMPILE_FLAGS 属性？区别是？

PRIVATE 表示编译选项只对当前目标生效，不会影响依赖于 target 的其它目标。
PUBLIC 表示编译选项会被传给依赖 target 的目标。
INTERFACE 表示给定的编译选项只用来传递给与依赖 target 的目标。

```cmake
# 可用列表保存选项
list(APPEND flags "-fPIC" "-Wall")
if(NOT WIN32)
	list(APPEND flags "-Wextra" "-Wpedantic")
endif()
target_compile_options(math flags)

# 或用宏
macro(add_msvc_options target)
  if(MSVC)
    target_compile_options(${target} PRIVATE
        /W4                # 设置警告级别为 4
        /WX                # 将警告视为错误
        /MP                # 启用多处理器编译
        /permissive-       # 禁用不严格的语言 conformance
        /Zc:__cplusplus    # 启用正确的 __cplusplus 宏值
        /Zc:inline         # 移除未使用的函数
        /EHsc              # 指定异常处理模型
    )
  endif()
endmacro()
add_msvc_options(math)
```

MSVC 编译选项：

- /arch:...：编译器使用的指令集。
    比如：`/arch:SSE2`、`/arch:AVX2`。

**add_compile_options**

`add_compile_options(<option>...)`

添加编译选项到目录的 COMPILE_OPTIONS 属性，影响所有目标。
选项只用于编译，不用于链接（需要 add_link_options）。

**add_definitions**

`add_definitions(-DMACRO_NAME)`

添加宏定义。-D 后加宏名。
可在代码中使用，比如：`add_definitions(-DDEBUG)`，`#ifdef DEBUG`；`add_definitions(-DFOO=1)`。

[**target_compile_definitions**](https://cmake.org/cmake/help/latest/command/target_compile_definitions.html)

`target_compile_definitions(<target> <INTERFACE|PUBLIC|PRIVATE> [items1...]...)`

为特定目标设置编译选项。

一个 item 格式可以是：`FOO`添加宏定义；`-DFOO`移除宏定义 FOO（注意空格是分隔符，不要多加）；`FOO=1`为宏定义设置值。

另见 *configure_file*。

**add_subdirectory**

`add_subdirectory(source_dir [binary_dir] [EXCLUDE_FROM_ALL] [SYSTEM])`

在指定的子目录中查找 CML 并执行，让 CMake 构建系统继续构建子项目。
可以将一个大型项目分解为多个子项目，使项目的组织结构更清晰。

binary\_dir 为生成文件的路径。默认为 source\_dir。
如果指定 EXCLUDE_FROM_ALL，则子目录里的目标不会被父目录的 ALL 目标所包含，且会从 IDE 项目文件中排除（用户只能在子目录中手动编译目标）。常用于子目录包含一些有用但非必须的东西，独立于源工程，比如一些 example。这种情况下通常子目录也有个单独的 project() 来构建一个新的系统。

子项目可以包含它自己的源文件、库、可执行文件等，并可以与主项目共享变量、目标和属性。

该命令会引入新的目录作用域（directory scope），其执行的 CML 中修改或定义的变量仅对当前作用域生效，不会影响父目录（除了缓存变量，是全局的）。在进入子目录前，会对父目录的变量做一份拷贝使用。

**include**

`include(<file|module> [OPTIONAL] [RESULT_VARIABLE <var>])`

引用官方和 CMake 社区中已经配置好的 CMake 模板。
CMake 模板就是保存在 .cmake 中的写好 CMake 代码，与 #include 类似。
通过`cmake --help-module <module_name>`查看其手册。

若不填 OPTIONAL，则文件不存在时会给出错误。
若给出 RESULT_VARIABLE，则会在操作成功时将文件的路径写入到指定变量中，在操作失败时写入 NOTFOUND。

引入模板不会引入新的作用域，对文件中变量的修改会影响当前作用域。

**option**

`option(<op_name> "desc" <OFF|ON>)`

定义用户可配置的选项 opName，默认值为 OFF 或 ON，是一个 bool 变量。
用户可以通过 CMake 命令行参数中的 -D 或 GUI 来改变选项的值，比如：`cmake -D op_name=OFF ..`。

desc 是对可配置选项的描述，会在使用 CMake GUI 时提示（但命令行界面不会显示）。

**调试**

需要指定 BUILD\_TYPE 为 Debug，并添加 -g 选项：

```cmake
set(CMAKE_BUILD_TYPE "Debug")
set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall")
```







### 基本

**aux_source_directory**

`aux_source_directory(<dir> <var>)`

将指定目录的所有**源文件路径（.c、.cc、.cpp）**保存在列表 var 中（不会递归查找）。

常用于引入保存在 Templates 等目录下的显式实例化模板文件。
不推荐使用，因为用于一般文件时，当新的源文件被添加时，CMake 生成的构建系统没法知道，需要清除缓存再手动重新运行 CMake 生成。而如果是依次列出文件，则添加文件需要修改 CML，从而能自动触发重新生成。这与 file(GLOB) 一样。
构建树只有在 CML 发生改变时才会更新，单纯的增删文件 GLOB 无法识别。因此当不清空缓存重新构建时，新的文件不会被记录。只推荐依次列出文件。

如果要添加特定文件（筛选）或递归添加，需要 file。

**file**

以一种与系统无关的方式读取、写入和传输文件，并使用文件系统、文件锁、路径和存档。

[**file (filesystem)**](https://cmake.org/cmake/help/latest/command/file.html#filesystem)

```cmake
file(GLOB <variable> [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS] [<globbing-expressions>...])
# 递归获取
file(GLOB_RECURSE <variable> [FOLLOW_SYMLINKS] [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS] [<globbing-expressions>...])
```

获取匹配 glob-expr 的文件名，保存到 variable。glob-expr 与正则类似，但更简单。
如果声明 RELATIVE，则返回相对指定路径的相对路径，而非绝对路径。
结果会按字典序排序。

比如：递归添加 src 目录下的所有 .cc：`file(GLOB_RECURSE SOURCE "src/*.cc")`。

不推荐使用，原因与 *aux_source_directory* 一致。

> 每次使用会覆盖变量原本的值而非 append。如果想合并多次 file 的结果，需要写到不同 list 然后 list(APPEND ...)。

[**message**](https://cmake.org/cmake/help/latest/command/message.html)

`message([<mode>] "msg"...)`

打印文本。
可以选择 mode 控制输出后的行为（默认为 NOTICE）。常用 mode：

- FATAL_ERROR：停止处理和生成。
- SEND_ERROR：继续处理，但跳过生成。
- WARNING：警告并继续处理。
- NOTICE：重要信息，输出到 stderr。
- STATUS：用于输出简洁的普通信息。
- VERBOSE：用于输出详细的次要信息。
- DEBUG：用于输出一般不重要的详细信息。

STATUS 会输出到 stdout，其它会输出到 stderr。

**project**

`project(proName VERSION 1.0.0 LANGUAGES CXX C)`

定义项目名称、版本（可选）、支持的语言（可选，默认是 CXX 即 C++）。

**if**

```cmake
if(ARGC GREATER 1)
  # ...
elseif(NOT GREATER LESS 5)
  # ...
else()
  # ...
endif()
```

判断字符串相等：`if (PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)`。
注意变量名区分大小写，GREATER、LESS 这种比较都要大写（否则会被当成字符串？）。

**foreach**

下标循环：
min 和 step 可选，默认分别为 0 和 1。min max 必须都是非负整数。

```cmake
foreach(<loop_var> RANGE [<min>] <max> [<step>])
	# ...
endforeach()
```

列表循环：
依次从将 loop_var 设置为所有 list 中的元素和所有 item。可以只提供一种，也可都提供。

```cmake
foreach(<loop_var> IN [LISTS <list>...] [ITEMS <item>...])
	message(${loop_var})
	# ...
endforeach()
```

列表循环：
依次将 loop_var 设置为所有 list 中的元素和所有 item。可以只提供一种，也可都提供。

```cmake
foreach(<loop_var> IN [LISTS <list>...] [ITEMS <item>...])
  # ...
endforeach()

# 例
set(list 1 2 3)
foreach(var IN LISTS list ITEMS e f)
	message(${var}) # 1 2 3 e f
endforeach()
```

压缩列表循环：
设提供的 list 为 list0, ..., listn，每次循环创建变量 loop_var_0 代表 list1[i]、...、变量 loop_var_n 代表 listn[i]。
允许每次迭代同时使用每个列表该下标的元素。当提供的列表不等长时，如果列表不含该下标则不创建该变量。
变量名 loop_var 可以声明多个，将依次对应到每个列表，不使用前缀+下标。

```cmake
foreach(<loop_var>... IN ZIP_LISTS <list>...)
  # ...
endforeach()

# 例
set(L1 "one;two;three;four")
set(L2 "1;2;3;4;5")

foreach(num IN ZIP_LISTS L1 L2)
	message("num_0=${num_0}, num_1=${num_1}")
endforeach()
 
foreach(word num IN ZIP_LISTS L1 L2)
	message("word=${word}, num=${num}")
endforeach()
```

**while**

```cmake
while(CONDITION)
	# ...
endwhile()
```

**function / 函数**

```cmake
function(<func_name> [arg...])
  message(${arg1_name})
  # ...
endfunction()
```

函数参数和内部定义的变量，作用域只限于函数内（函数作用域，function scope），即使它与外部变量重名，也不会影响外部变量。

参数可以通过特殊的变量名来访问：

- ${ARGC}：参数数量。
- \${ARGV}：所有参数的列表。
- \${ARG0}、\${ARG1}...：每个参数。
- \${ARGN}：当实参数量多于形参时，保存了超出形参的那些匿名参数的列表。如果没多则是空列表。

传入参数的数量可以多于函数定义中的形参数量，~~也可以少于~~（好像不能少于）。
~~当实参数量少于形参时，可通过 if (NOT ...) 检查未被赋值的形参~~

**macro**

```cmake
macro(<macro_name> [arg...])
  message(${arg1} "is" ${var})
  # ...
endmacro()
```

宏是替换，不会像函数一样新建一个作用域。在宏中调用 return() 会在当前作用域直接返回。

宏相当于将文本嵌入进使用位置，并用变量值替换使用变量的地方。
因此当宏参数与外部变量名同名时，在宏内使用的值是调用宏之前的值；在宏内修改它的值，会在宏之外影响外部变量的值。

[**list**](https://cmake.org/cmake/help/latest/command/list.html)

用分号分割的对象是列表。list 提供了对 list 的各操作，也可以定义列表。
`set(<var> <value>...)`也能定义列表。

常用：

```cmake
Reading
  list(LENGTH <list> <out-var>)
  list(GET <list> <element index> [<index> ...] <out-var>)
  list(SUBLIST <list> <begin> <length> <out-var>)

Search
  list(FIND <list> <value> <out-var>)

Modification
  list(APPEND <list> [<element>...])
  list(INSERT <list> <index> [<element>...])
  list(POP_BACK <list> [<out-var>...])
  list(POP_FRONT <list> [<out-var>...])
  list(PREPEND <list> [<element>...])
  list(REMOVE_ITEM <list> <value>...)
  list(REMOVE_AT <list> <index>...)

Ordering
  list(REVERSE <list>)
  list(SORT <list> [...])
```

如果插入等操作的 list 不存在，则定义一个并插入。





### 测试

> https://gitlab.kitware.com/cmake/community/-/wikis/doc/ctest/Testing-With-CTest
> https://github.com/ttroy50/cmake-examples/blob/master/05-unit-testing/README.adoc

产生 makefile 后，可通过`make test`执行。

需要在项目根目录通过`enable_testing()`启用测试。
它会生成一个叫`test`的构建目标。
启用后，不能有文件名叫 test，包括 test.cpp。

**add_test**

```
add_test(NAME <name> COMMAND <command> [<arg>...]
         [CONFIGURATIONS <config>...]
         [WORKING_DIRECTORY <dir>]
         [COMMAND_EXPAND_LISTS])
```

name 定义该测试的名字。
command 为要运行的命令。如果为可执行目标，则会调用它。通过紧跟 arg 传命令行参数。
WORKING_DIRECTORY 设置测试要在哪个目录执行。默认为 CMAKE_CURRENT_BINARY_DIR。也可通过 set_tests_properties() 设置。

`add_test(<name>)`也可创建，需要通过 set_tests_properties 设置其属性。
只能在测试被创建的那个目录设置。

`add_test(<name> <command> [<arg>...])`是更旧、不推荐的方式。

**set_tests_properties**

`set_tests_properties(test1... PROPERTIES prop1 value1 prop2 value2)`

为指定测试设置属性。如果测试不存在则报错。
测试相关的属性：https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#test-properties

常用属性：

- PASS_REGULAR_EXPRESSION：要求测试必须符合列出的正则表达式列表中的一个，否则测试失败。
    值用字符串声明。

可以通过宏定义测试，比如：

```cmake
# 定义一个宏，用来简化测试工作
macro (do_test arg1 arg2 result)
  add_test (test_${arg1}_${arg2} Demo ${arg1} ${arg2})
  set_tests_properties (test_${arg1}_${arg2}
    PROPERTIES PASS_REGULAR_EXPRESSION ${result})
endmacro (do_test)
 
# 使用该宏进行一系列的数据测试
do_test (5 2 "is 25")
do_test (10 5 "is 100000")
do_test (2 10 "is 1024")
```



### 安装

产生 makefile 后，可通过`make install`执行。

通过 cpack 还可以生成二进制或源码安装包。

[**install**](https://cmake.org/cmake/help/latest/command/install.html)

指定安装规则，定义在构建完成后如何将目标文件（可执行文件、库等）以及相关文件（如动态库、配置文件等）安装到指定目录（其实就是复制过去？）。
对于将构建好的项目打包成安装包、或将项目部署到目标系统上非常有用。

常用的有：

- `install(TARGETS <target>... RUNTIME [<artifact-option>...] [<artifact-kind> <artifact-option>...]...)`

其中`<artifact-option>`主要包括：

```cmake
[DESTINATION <dir>]
[CONFIGURATIONS <config>...]
[COMPONENT <component>]
[OPTIONAL] [EXCLUDE_FROM_ALL]
```

DESTINATION path 指定安装到的目录，比如 bin。

第一组 option 应用到目标的 Output Artifacts，后面的 option 应用到指定的 artifact kind。


常用例子：

- `install(TARGETS <target> DESTINATION <path>`
    `install(FILES <file> DESTINATION <path>`

file 为文件路径，比如：`"${CMAKE_SOURCE_DIR}/libs/dynamic/libDynamic.dll"`。
当使用绝对路径时，CMake 会在前面附加 CMAKE\_INSTALL\_PREFIX 形成完整路径（默认为 /usr/local），比如：`bin`会被生成到`/usr/local/bin`。







### 其它

[**find_package**](https://cmake.org/cmake/help/latest/command/find_package.html)

find_package(XXX) 会从 CMAKE_MODULE_PATH 指定的目录列表中找`FindXXX.cmake`形式的 Cmake module。linux 默认的目录是`/usr/share/cmake/Modules`。

version 指定最低版本号。
COMPONENTS 可以指定要在库里面寻找哪些组件。

成功找到后，一般会设置`XXX_FOUND`、`XXX_INCLUDE_DIRS`等变量，通常会在`FindXXX.cmake`注释中列出。
如果库支持 *imported target*，则直接 link 给出的别名目标即可（见下）。否则库一般会给出`xxx_INCLUDE_DIRS`、`xxx_LIBRARY`类似的变量以便 include 和 link：

```cmake
target_include_directories(target
    PRIVATE ${Boost_INCLUDE_DIRS}
)
target_link_libraries(target
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_FILESYSTEM_LIBRARY}
)
```

> 为了让某个外部库能被找到，推荐使用命令行传递`-DCMAKE_PREFIX_PATH="path/to/..."`，或设置环境变量`fmt_DIR="path/to/..."`，以避免硬编码（`set(fmt_DIR ...)`）、影响可移植性。最好还是用包管理器。

**imported target**

较新版本的 CMake 允许使用导入的别名目标链接第三方库。大多数现代 CMake 库也会在其 module 文件中导出别名目标。
导入目标是由 FindXXX 模块导出的只读目标（如`Boost::filesystem`、`Boost::boost`）。当链接该目标时，会自动链接其它需要的库（`Boost::System`），并 include 它所需的 Boost 头文件目录。

[**configure_file**](https://cmake.org/cmake/help/latest/command/configure_file.html)

`configure_file(<input> <output> [@ONLY]`

根据模板文件 input 生成文件 output，并将其中`@VAR@`、`${VAR}`形式的字符串替换为变量值。可用于源码。
比如：`configure_file(config.h.in config.h @ONLY)`。

@ONLY 表示只替换`@VARIABLE_NAME@`形式的占位符。如果不加也会替换 `${VARIABLE_NAME}`形式的占位符。

CMake 会将模板文件中的变量替换为其实际值。如果不存在则替换为空字符串。
如果变量是 bool，则根据是 ON/OFF 替换为`#define xxx 0/1`。
如果变量是字符串，则被替换为字符串值，不带引号。
注意大小写。因为宏一般大写，所以这部分参数命名最好也大写。

比如：

```cpp
// config.h.in
#define ENABLE_FEATURE_X @ENABLE_FEATURE_X@

// CMakeList.txt
// 可以在命令行更改
option(ENABLE_FEATURE_X "Enable feature X" OFF)
configure_file(config.h.in config.h @ONLY)

// 生成的 config.h
#define ENABLE_FEATURE_X 0
```

模板中还可以使用`#cmakedefine xxx [some...]`，如果定义了非零值则替换为`#define xxx [some...]`，否则不定义它。
`#cmakedefine01 xxx`则要么是`#define xxx 0`，要么是`#define xxx 1`。



**execute_process**

运行其它进程，并收集它们的输出。



---

## 其它

### 基本使用 (vscode)

**配置**

添加 cmake 运行但不调试的快捷键（比如 F9）。

**vscode 使用**

- F1 - cmake: quick start 创建 cmake 项目，选择编译器。

- 然后就可以在右侧 cmake 菜单 - 大纲 - 右击项目名，生成，就可以运行或调试了（下面状态栏也有运行/调试快捷键）。

    如果要用 Intelligence 的调试，则在生成的 launch.json 中配置 program 为`${workspaceFolder}/build/projectName.exe`，miDebuggerPath 为 gdb 所在路径（mingw/bin 下）。

一般更新保存 CMakeList 就会触发重新编译，如果没有，在 cmake 菜单点配置所有项目。

也可命令行直接运行，但是要自行添加`configureSettings`配置中的选项。
注意更换生成器时清理缓存！（CMakeFiles 和 CMakeCache.txt）。

可以在 Configure Args 中添加 -Wno-dev 来禁用 for dev 警告。

### 基本使用 (CLI)

linux：

- 更改 CMakeList，`cmake ..`。
- 在 build 下`make`，然后找到可执行文件运行（可能在 build/Debug 下）。

windows：

- `cmake .. -G "Unix Makefiles"`。默认不会生成 makefile，而是 .sln 用于 MSVC。
- `make`。

注意，想要 makefile，cmake 时必须指定 -G "MinGW Makefiles" 等（或是在 setting.json 里构建方式使用 ninja？），否则还是用 MSVC 生成器，指定编译器 CMAKE_CXX_COMPILER 也没用。不声明该值也会自动寻找编译器。
在处理 CML 前，cmake 就会指定好生成器，因此只能通过命令行修改。

> 生成 complie_commands.json：`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1`
> 或设置变量：`set(CMAKE_EXPORT_COMPILE_COMMANDS ON)`（如果还不行，用`set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")`）。
>
> 注意仅限于 Makefile 和 Ninja 生成器。MSVC 默认的不行，除非用命令行指定使用`-G "Unix Makefiles"`生成器。。注意新建目录或清除缓存。





### 某些应用

**使用 header-only**

> 问题：仅包含 .h 或 .hpp、不含源文件的头文件，无法出现在 compile_commands 内，从而 clangd 无法识别它的依赖、不能引用非标准库（否则会 not found）。
> linux/wsl 下可以用 compdb；windows 只能在 wsl 下生成，然后手动改。

想要使用 header-only file，直接 include 它所在的目录就行了。如果它依赖某些库，就创建接口库链接。

```cmake
add_library(header_only INTERFACE)
# target_include_directories(header_only INTERFACE ${CMAKE_SOURCE_DIR}/src/header_only) # 非必需。。
target_link_libraries(header_only INTERFACE fmt::fmt)
```

主要问题是：由于 .h 头文件通常不会被当做一个编译单元、不能作为源文件，不会被直接编译，所以它们不会出现在 compile_commands 里，从而不会被 clangd 识别，不会正确进行提示，从而在引用非标准头文件时出现提示错误（即使 cmake 可正常运行）。
主要是 cmake 无法确定头文件要使用什么编译选项，因为这取决于包含它的那些编译单元。
（~~虽然 .hpp 似乎可以作为源文件，但也不会出现在里面~~ hpp 也算头文件）

[这里](https://gitlab.kitware.com/cmake/cmake/-/issues/16285)说能通过 VERIFY_INTERFACE_HEADER_SETS 编译头文件，使其出现在 compile_commands 里，但像[这里](https://www.reddit.com/r/neovim/comments/19ccbyn/clangd_and_cmake_header_files_in_compile/)所说好像并不行。。

[这里](https://www.reddit.com/r/cpp_questions/comments/qabln0/working_on_a_headeronly_library_with_cmake_and/)说要用 [compdb](https://github.com/Sarcasm/compdb#generate-a-compilation-database-with-header-files) 等工具做一个后处理，添加头文件生成新的 compile_commands，但是如 issues 所说它不支持 Windows。。
可以对照它 linux 或 wsl 下生成的文件，然后修改使其能在 Windows 下可用（可行，主要是修改编译器路径、文件路径，把  -I -i 改为`@CMakeFiles/xxx.dir/includes_CXX.rsp`）。









### FetchContent

自动下载并配置 github 上的第三方库。



通常先 find_package（不带 REQUIRED），没有的话 fetch。

> 下载的内容会放到 _dep 下。
> 和 git submodule 下到 third_party 等位置也差不多？只不过 git 下下来的需要编译一下然后链接。







---

## vcpkg

安装后在 CML 中可通过 find_package 再 target_link_libraries 链接到库。
库名与链接方式看 vcpkg 下载后的说明（再进行 install 一次也能看）。



### windows

**安装**

安装：https://vcpkg.io/en/getting-started（默认不会添加到环境变量）
然后`vcpkg install xxx`安装库。

**注意**

注意，install 时可以`--triplet x64-mingw-static`指定[三元组](https://learn.microsoft.com/zh-cn/vcpkg/users/triplets)，默认是 x64-windows。不同的 triplet 是不一样的包，CML 中指定的 VCPKG_TARGET_TRIPLET 必须已安装。
使用`cmake -G "MinGW Makefiles"`时，必须使用 x64-mingw-static 而非 x64-windows。

**在 vscode 中使用**

> 使用新配置时，注意删除缓存！（项目状态 - 删除缓存并重新配置）

如果与 cmake 使用，则在 setting 里添加：
（或者像 vcpkg 官网所说运行 cmake 时加参数，也可在 CMakeList 里定义 CMAKE_TOOLCHAIN_FILE）

```json
"cmake.configureSettings": { // 运行时附加的命令行参数
    "CMAKE_TOOLCHAIN_FILE": "vcpkg安装目录\\vcpkg\\scripts\\buildsystems\\vcpkg.cmake",
    "VCPKG_TARGET_TRIPLET": "x64-windows" // 构建平台。注意 gcc(mingw) 要用 x64-mingw-static
}
```

然后将安装完成后提示的`find_package... target_link_libraries...`放到 CMakeLists 后面（里面的 main 要改成项目名）。

问题：对于 C++ 插件的 Intelligence，没有代码提示和补全。似乎只能在 c_cpp_properties 的 includePath 加`"E:\\Runtime\\vcpkg\\packages\\fmt_x64-windows\\include"`（如果没有，快速修复 - 编辑 includePath 生成）。
（好像可以设置使用 cmake 进行配置，不管了反正不用它，遇到模板就死了）

**直接使用 / 在 CML 中添加**

在 CML 中添加：

```cmake
# 需要在 project() 前设置。如果用 vscode 一键运行，则在 setting 里添加即可
# 如果不行，注意删缓存重新配置！
set(CMAKE_TOOLCHAIN_FILE "E:\\Runtime\\vcpkg\\scripts\\buildsystems\\vcpkg.cmake")
set(VCPKG_TARGET_TRIPLET "x64-windows")
```











### linux 及 wsl

似乎就不需要 vcpkg 了，直接安装即可。
如果 wsl 要用 win 通过 vcpkg 安装的库，注意路径是 /mnt/e 不是 E:/...。也可以直接设置 fmt_DIR。

```cmake
# 设置 fmt_DIR 为包含 fmt-config.cmake 的路径
set(fmt_DIR 
"/mnt/e/Runtime/vcpkg/installed/x64-windows/share/fmt")
```









