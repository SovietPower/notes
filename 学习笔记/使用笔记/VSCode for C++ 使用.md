# VSCode for C++ 使用

---

[TOC]

---

## 配置

### Intelligence

> 当大型项目没有索引时，可能需要 Compilation Database。
> 见 https://zhuanlan.zhihu.com/p/139611793



> 以下用于 C++ 插件的智能提示。
>
> - c_cpp_properties.json (compiler path and IntelliSense settings)
>
> 以下两个用于 C++ 的运行与调试：
>
> - tasks.json (build instructions)
> - launch.json (debugger settings)
>

**c_cpp_properties.json**

- includepath：路径将被用于搜索项目中使用的头文件。

    `${workspaceFolder}/**`表示搜索整个工作区中的头文件（\*\* 为递归搜索所有子文件夹）。
    可以添加其它的，比如：`/usr/local/include`。







### Clangd

> https://clangd.llvm.org/installation
> https://clangd.llvm.org/faq
> `clangd --help-list-hidden`查看可用配置。
>
> clang tidy：https://clang.llvm.org/extra/clang-tidy/
> https://clang.llvm.org/extra/clang-tidy/checks/list.html
> clang modernize：https://clang.llvm.org/extra/clang-tidy/checks/modernize/use-nodiscard.html
>
> https://zhuanlan.zhihu.com/p/398790625
> https://airchaoz.notion.site/WSL-VSCode-Clangd-3d3356f6d64246178b0dccb64311d749

clangd 需要知道如何编译项目，因此需要一个编译数据库，需要向 clangd 提供 compile_commands.json 文件（在扩展设置里设置路径）。
这个文件的生成需要通过项目的编译系统：

- cmake：`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1`
- bazel：使用插件（见官网）
- 其它：使用 bear（见官网。有了 makefile 后直接`bear -- make`？）；compiledb 也可，但也要基于 makefile。

windows 建议使用 gcc，MSVC 不能生成 compile_commands，不能用 clangd。

> 会导致 doxygen 的文档生成有点问题，换行不会补 \*，但影响不大。







---

## VSCode

### 常用变量

可写在 setting、launch.json 等中。

- \${workspaceFolder}：工作区的根目录路径。
    注意，当工作区有多个文件夹时，最顶部的文件夹才是根目录。
- \${workspaceFolderBasename}：工作区的根目录名称。
- \${workspaceRoot}：工作区的绝对路径+文件夹名（已弃用）。
- \${file}：当前打开文件的完整路径。
- \${relativeFile}:文件相对 workspace 根目录的路径。
- \${fileDirname}：当前打开文件的目录路径。
- \${fileBasename}：当前打开文件的文件名。
- \${fileExtension}：当前打开文件的扩展名。
- \${fileBasenameNoExtension}:代表当前打开文件的文件名（不包括扩展名）
- \${cwd}：Visual Studio Code进程的当前工作目录路径。
- \${env:NAME}：环境变量NAME的值。
- \${config:CONFIG_NAME}：配置文件中名为CONFIG_NAME的属性的值。
  





### 配置文件

配置文件通常放在 .vscode 中。
以下两个用于 C++ 的运行与调试：

- tasks.json (build instructions)
- launch.json (debugger settings)

task.json 用于创建构建任务（为某任务指定对应编译选项，便于下次直接运行）。创建后可在左上角的 终端 - 运行任务 - 任务名 - 继续不扫描任务输出 中选择运行。

> task 例子：
>
> ```json
> {
>     "version": "2.0.0",
>     "tasks": [
>         {
>             "type": "shell",
>             "label": "CUDA C++", // 任务名称
>             "command": "nvcc",
>             "args": [
>                 "-std=c++17",
>                 "-g", "-G",
>                 "-o", "${fileDirname}/${fileBasenameNoExtension}",
>                 "${file}",
>                 "-lcublas"
>             ]
>         }
>     ]
> }
> ```
>
> task 大点的项目都用不到，都用 cmake。只有一些简单或临时的东西才常用 task。

launch.json 用于创建运行和调试任务。创建后可在右上角通过小三角进行调试，可在左侧 运行与调试 界面运行或调试。

> 可在左上角的 运行 - 添加配置 生成模板，然后修改要执行的程序（比如`${fileDirname}/${fileBasenameNoExtension}`）。







---

## Debug

### gdb







### lldb

好像更好用。









---

## 使用 wsl

### 安装与配置

> 安装与简单配置，并使用 vsc 打开 wsl 文件夹：https://zhuanlan.zhihu.com/p/665210114
> （不需要安装 SSH 插件，只需要本地有 WSL。翻译等插件如果说没启用，则也要装到 remote）
>
> https://learn.microsoft.com/zh-cn/windows/wsl/setup/environment
> https://code.visualstudio.com/docs/remote/wsl-tutorial
> https://code.visualstudio.com/docs/cpp/config-wsl
>
> 可以定期更新包管理器：`sudo apt update && sudo apt upgrade`
>
> pass：Apr1...

**安装程序**

`sudo apt-get install g++ gcc gdb build-essential git`

- 安装 git，然后配置用户名与邮箱。
    如果要上传代码，还要配置验证信息。

**配置代理**

> https://zhuanlan.zhihu.com/p/593263088
> https://zhuanlan.zhihu.com/p/657110386
> https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config#wslconfig

在`C:\Users\<UserName>`创建 .wslconfig，输入：

```
[experimental]
autoMemoryReclaim=gradual
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
sparseVhd=true
```

然后关闭 WSL 插件的`Remote: Auto Forward Ports`。
也可以限制内存使用：

```
[wsl2]
# Limits VM memory to use no more than 2 GB, this can be set as whole numbers using GB or MB
memory=2GB 

# Sets the VM to use two virtual processors
processors=6

# Sets amount of swap storage space to 2GB, default is 25% of available RAM
swap=2GB

# Sets swapfile path location, default is %USERPROFILE%\AppData\Local\Temp\swap.vhdx
# swapfile=C:\\temp\\wsl-swap.vhdx
```

在 wsl 内查看配置：

```sh
# 查看内存、swap大小
free -m
# 查看处理器个数
cat /proc/cpuinfo| grep "processor"| wc -l
```





### 基本使用

- `wsl`：启动。
- `wsl -l -v`：运行情况与版本。
- `wsl --shutdown`：关闭。

用完记得关闭，不然还会在后台！

注意：若想获得最快的性能速度，则将文件存储在 WSL 文件系统中（而不是 /mnt/c, d, e...）。但这样只能通过` explorer.exe .`、`code .`从 Windows 访问，速度比较慢。





### 编写代码

> https://code.visualstudio.com/docs/cpp/config-wsl

**基本**

代码提示取决于扩展 C++ （或 clangd）的设置。

使用右上角运行后，实际编译选项取决于 .vscode 下的 tasks.json 设置。编译时要用 g++。
但这个很难用，还是自己输命令或用脚本好（或者 code runner）。

**调试**

可以在左上角添加一套配置。

注意：

- 要在打开 .cpp 的状态点击“运行和调试”。
- 要加断点，否则直接就结束（但有时候却不这样，要 F5 才能进到第一个断点）。
- O2 可能会优化很多代码，导致部分断点失效。









---

## 插件/其它配置



### 其它配置

`workbench.action.holdLockedScrolling`：控制两个文件一起滚动。









---

























