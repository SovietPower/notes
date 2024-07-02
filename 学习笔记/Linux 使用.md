# Linux使用 

tags: Linux

-----
[TOC]

-----
> https://missing.csail.mit.edu/

TODO：
挂载：http://c.biancheng.net/view/2859.html

----------
## shell
> 介绍：
> https://missing-semester-cn.github.io/2020/course-shell/
> https://missing-semester-cn.github.io/2020/shell-tools/
> 查询：
> https://tldr.sh/


----------
## 命令
常用命令见：https://zybuluo.com/SovietPower/note/1791380。

**删除已输入的命令**
`ctrl + c`
```
ctrl + w 往回删除一个单词，光标放在最末尾
ctrl + u 删除光标以前的字符
ctrl + k 删除光标以后的字符
ctrl + a 移动光标至的字符头
ctrl + e 移动光标至的字符尾
ctrl + l 清屏
```

**yum**
https://www.cnblogs.com/kerrycode/p/6924153.html

**环境变量**
https://segmentfault.com/a/1190000038313883



----------
## 快捷键
### 终端快捷键
> C+S+T: 打开终端
> C+C：终止当前命令
> C+D：退出终端
> C+Z：暂停当前进程

> C-S-C：复制
> C-S-V：粘贴
> C+K：删除当前位置到行尾的内容
> C+U：删除当前位置到行首的内容

> C+<+>：减小字号
> C+S+<+>：增大字号

> apt -h # 查看 apt 命令用法
> apt install -f 修复软件依赖关系、搜索失效软件
> apt intall package # 安装软件包
> apt remove package # 卸载软件包
> apt upgrade # 更新已安装的软件包
> apt dist-upgrade # 升级系统
> apt-cache depands package # 了解软件包所依赖的软件包
> apt clean # 清理无用的软件包
> apt autoremove # 清理不再使用的依赖和库文件

> dpkg --help  # 查看 dpkg 命令用法
> dpkg -c packagename.deb # 查看软件包所包含的内容
> dpkg -I packagename # 查看软件包的详细内容
> dpkg -i packagename.deb # 安装软件包
> dpkg -r packagename.deb # 卸载已安装的软件包
> dpkg -L packagename.deb # 列出软件包安装的所有文件清单
> dpkg dpkg-reconfigure packagename.deb # 重新配置一个已经安装的软件包，多用于安装某个软件包失败后

> snap list # 列出已安装的包
> snap find # 查询包
> snap find app_name # 查询特定的包
> sudo snap install app_name # 安装包
> sudo snap refresh app_name # 更新包
> sudo snap remove app_name # 卸载包

> 不重要内容：
> C+A/Home：移动光标至行首
> C+E/End：移动光标至行末
> C+H/Backspace：删除当前光标前的字符
> C+D/Delete：删除当前光标后的字符
> C+B/Left：光标左移
> C+F/Right：光标右移

### UI
> win：当前活动窗口列表
> win+A：应用列表
> win+D：显示左面
> win+Q：快速启动

### 目录操作
https://www.runoob.com/linux/linux-file-content-manage.html

### Else
**屏幕**
> HOST+F 全屏模式
> HOST+C 自动缩放模式
> HOST+L 无缝模式

### [一些有趣的Linux命令](https://blog.csdn.net/iteye_3759/article/details/82554915)
**oneko**
> ~#sudo apt install oneko
> ~# oneko

**toliet**
> ~# sudo apt install toilet
> ~# toilet www.aqee.net
> ~# toilet -f mono12 -F metal www.aqee.net

**cowsay/xcowsay**
> ~#sudo apt install cowsay
> ~#sudo apt install xcowsay
> ~# cowsay 你好，...
> ~# xcowsay 你好，...

### [Theme](https://draculatheme.com/vim/)
[vim](https://draculatheme.com/vim/)、powershell

## 管道与连接符号
> https://zhuanlan.zhihu.com/p/223681357

### 输入输出重定向
* **管道符号`|`**
`Command A | Command B`：将前A命令的输出作为B命令的输入。
常与筛选命令grep搭配使用，如：
`ps aux | grep mysql`：在所有进程中查询含有mysql关键字的信息。
`ps aux | grep mysql | less`：还可以将输入导入less命令，less 是一个分页工具，它允许你一页一页地查看信息。
`ls /etc | grep so`：查找`/etc`中文件名含`so`的文件（将`ls`列出的文件作为输入）。

* **输出重定向符号`>`**
`Command A > File B`：将前A命令的输出写入B文件，覆盖原文件内容。
如在hello.txt中写入`Hello World!`：`echo Hello World! > hello.txt`
shell脚本执行后不显示信息，`<command> > /dev/null`，如：`apt update > /dev/null 2>&1`，`2>&1`表示将错误/warning输出同标准输出一起输出到黑洞中（`apt install`记得加`-y`参数）。

* **输出重定向符号`>>`**
`Command A >> File B`：将前A命令的输出追加写入B文件，不覆盖原文件的内容。
如：`echo Hello World! >> hello.txt`：将 Hello World! 追加到 hello.txt 后面。
注：cat hello.txt >> hello.txt会导致无限循环。

* **输入重定向符号 <**
`Command A < File B`：将 B文件的内容作为命令 A 的输入。
如：`echo 'print(input())' > test.py`：先创建 Python 文件 test.py，功能为输出用户输出的内容。
然后`python test.py < hello.txt`，将 hello.txt 作为 test.py 的输入。
结果会输出`Hello World!`。

### 连接符号
* **连接符号`;`**
`Command A ; Command B`：在一行写入多个命令时，使用`;`进行分割，不论 A 命令是否执行成功，B命令都会继续执行。
如下面的命令，A命令执行失败，B命令执行成功。
`ee ; echo Hello World!`
输出为：
`command not found: ee`
`Hello World!`

* **后台执行符号`&`**
`Command A &`：命令A会进入后台执行，当用于挂载后台服务，或执行耗时任务时可能会用到。
如下面的命令，会创建一个后台进程，在60秒后结束。
如：`sleep 60 &`，命令行会输出[1] 51277，表示进程的PID为 51277，60秒后会输出[1] 51277 done sleep 60，表示进程结束。

* **逻辑与符号`&&`**
`Command A && Command B`：若A命令执行成功，继续执行B命令，否则不执行B命令。
如下面的命令会在60秒后输出`Hello World!`。
`sleep 60 && echo Hello World!`
而接下里这条命令只会输出命令A的错误信息。
`ee && echo Hello World!`
输出为`command not found: ee`

* **逻辑或符号`||`**
`Command A || Command B`：如果命令 A 执行失败，则执行 B。
`ee || echo Hello World!`
输出为
`command not found: ee`
`Hello World!`

### 子命令符号
* **子命令符号`()`**
`(Command A)`：创建一个子 shell 去执行命令 A，在A中切换文件夹不会影响当前shell工作路径。
`(cd .. ; ls)`：这条命令会返回上层目录的内容，但工作路径仍然在当前目录。
`Command A $(Command B)`：表示返回命令B的结果，并将结果作为命令A的参数继续执行。
如：`echo A $(echo B)`：输出为`A B`。

* **表达式计算符号`(())`**
`((Calculation A))`：计算表达式A的值。
如果要作为变量的话，需要加上`$`。如`echo $((3+2))`，输出为5。
常与 if 和 for 命令配合使用。
```cmd
if ((3>2)) echo true
for ((i=1;i<=16;i++));do echo $i; done
```

## 安装/使用问题
内存建议至少2.5G，硬盘20G。
**VMware：**
下载：https://my.vmware.com/cn/group/vmware/downloads/info/slug/desktop_end_user_computing/vmware_workstation_pro/16_0#product_downloads
密钥：https://www.cnblogs.com/yg0070/p/13891104.html
> ZF3R0-FHED2-M80TY-8QYGC-NPKYF
> YF390-0HF8P-M81RQ-2DXQE-M2UT6
> ZF71R-DMX85-08DQY-8YMNC-PPHV8
> FA1M0-89YE3-081TQ-AFNX9-NKUC0

**Virtual Box**
https://zhuanlan.zhihu.com/p/111567471

**Virtual Box增强功能问题**
**Could not mount the media/drive...**
可先安装gcc、perl、make后再进行
https://www.cnblogs.com/liqu/p/11856827.html
> sudo mkdir --p /media/cdrom
> sudo mount -t auto /dev/cdrom /media/cdrom
> cd /media/cdrom
> sudo sh VBoxLinuxAdditions.run
* 如果无法运行`VBoxLinuxAdditions.run`，直接去文件目录再自动安装即可。

或：https://blog.csdn.net/yanandliang/article/details/79088857
> su root 
> cd /mnt
> mkdir cdrom
> mount /dev/cdrom  ./cdrom
> cd  cdrom
> ./VBoxLinuxAdditions.run

**Please install the gcc make perl packages from your distribution**
sudo apt install gcc perl make（或分三行分别安装这三个）

**Running kernel modules will not be replaces until the system is restarted**
重启。

**网络配置：**
**VMware：**https://blog.csdn.net/u013554213/article/details/79408084

**无法安装vim：**
https://blog.csdn.net/u013554213/article/details/79408084
先 sudo apt update，然后再 sudo apt install vim。

**启用vi的方向键、退格键**
https://www.cnblogs.com/jev-0987/p/12885422.html
1. sudo gedit /etc/vim/vimrc.tiny
2. 编辑vimrc.tiny，set compatible 改为 set nocompatible
3. 添加一行：set backspace=2

**vim单键无法映射多个键**
https://www.zhihu.com/question/395888673
Solution：用gvim。

**等待缓存锁：无法获得锁**
`sudo kill -KILL 对应PID`（`ps (-A)`可查看运行的程序），或按 https://blog.csdn.net/qq_38824818/article/details/106738297 ？
```
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/cahe/apt/archives/lock
sudo rm /var/lib/dpkg/lock
```

**cd权限不够**
https://jingyan.baidu.com/article/fedf0737a4f44735ac8977b7.html
（`su 认证失败`）`sudo passwd root`创建权限用户及密码。
进入root：`su`或`su root`，输入密码。

**VMware共享文件夹找不到**
主要：https://blog.csdn.net/JAZZSOLDIER/article/details/54971926（最好先进入root？）
> 关键命令：sudo apt install open-vm-tools
> sudo vmhgfs-fuse .host:/ /mnt/hgfs -o nonempty（查看挂载 df -h）

可参考：https://blog.51cto.com/wuweizhu/2068744

**无法安全地使用该源**

* 删除目录下的对应仓库，没用：https://blog.csdn.net/chenbetter1996/article/details/80255552
* 换源，或删除错误库：https://www.cnblogs.com/blogcyh/p/12323117.html

> `lsb_release -a`先查看系统版本号。
> 在 https://mirror.tuna.tsinghua.edu.cn/help/ubuntu/ 中找到对应系统及版本号的源。
> `cd /etc/apt`，`sudo cp sources.list sources.list.bak`，然后将`sources.list`覆盖为清华中的源。
> 然后`sudo apt update`。
> 如果还有`sudo add-apt-repository ppa:...`，再在`软件和更新-其它软件`中删除对应错误的库。
> 但是那就一直没法用这个库了？

**`Ubuntu Software`搜索加载不出来**
1. 卸载原`snap`，安装`gnome-software`：https://blog.csdn.net/takujo/article/details/108663464；https://blog.csdn.net/qq_19432525/article/details/114427304
> sudo apt autoremove --purge snapd
> sudo apt install gnome-software

2. https://blog.csdn.net/eidolon_foot/article/details/112942564
3. https://www.php.cn/linux-452426.html
4. 试试搜索不要搜索软件全名？

**更多UI基础配置**
安装`gnome-tweaks`。
> sudo apt install gnome-tweaks

**安装时`<name> has install-snap change in progress`**
https://blog.csdn.net/u011870280/article/details/80213866
> 软件正在安装，但没安装完
> snap changes 查看正在进行的安装
> sudo snap abort +ID 终止正在doing的ID，然后重新安装即可

**未知如何处理 <name>.deb**
到对应文件夹中`sudo dpkg -i a.deb`，或用`apt`？

**安装vscode**
最好在官网下载`.deb`安装。应用搜索也可。
有编译环境后，下载插件：`Chinese,C/C++,C++ IntelliSense,Code Runner`。

**vscode检测到#include错误**
安装插件`C++ IntelliSense`。

**Vritual Box启动后一直黑屏**
可能是空间不足，导致开机无法创建临时文件，需扩容。

**扩容**
关闭虚拟机操作：https://blog.csdn.net/wilson1068/article/details/88770409、https://www.bilibili.com/read/cv7168113/
虚拟机内操作：https://blog.csdn.net/orange_612/article/details/79597905
扩容的是`.vdi`文件，否则需要将盘备份成`.vdi`然后对`.vdi`扩容。
似乎必须要动态分配，否则会扩容失败，解决方法也见下。

扩容需关闭虚拟机。
**虚拟机外用gparted操作：**
1. 将`VBoxManage`添加到环境变量，或者`cd`到VBox安装文件夹，用`cmd`执行`VBoxManage`命令：`VBoxManage modifyhd "F:\Ubuntu1\Ubuntu1\<...>.vdi" --resize 30720`（目录改为控制器的`.vdi`的即可）（单位为MB，`30720`即30GB）。
如果当前虚拟机有快照，这些快照文件也需要进行重新分配容量：`VBoxManage modifyhd "F:\Ubuntu1\Ubuntu1\<...>.vdi" --resize 30720`。
2. 下载`GParted`以调整虚拟机内分区：http://gparted.sourceforge.net/download.php。（64位就下载`...-amd64.iso`）
3. 在`控制器：SATA`中（添加虚拟光驱，注册，）添加虚拟盘，即下载的`gparted-live-1.0.0-5-amd64.iso`。
4. `系统`设置中调整运行顺序，将光驱上移到第一个，以先运行`gparted-live-1.0.0-5-amd64.iso`。
5. 启动虚拟机，（在开始界面按`ESC`）选择`GParted Live(Default settings)`，`Don't touch keymap`，语言英语或简中，`(0) Continue to start X to use GParted automatically`（默认就是`0`）。
6. 在对应的磁盘（容量最大使用最多的）中右键，`Resize/Move`，`New size`调到最大（先分配到大分区再分配到下面）。最后点√。
7. 关闭虚拟机。删除`gparted-live-1.0.0-5-amd64.iso`，启动虚拟机，`df -h`命令可以查看磁盘使用情况及是否成功扩容。
**虚拟机内用gparted操作：**
1. 同上。
2. 终端中`sudo apt install gparted`下载`gparted`，然后`sudo gparted`。
3. 同上的6.7。

**固定分配 扩容失败 解决方法：**
https://blog.csdn.net/weixin_40542512/article/details/101105433
对于`Failed to resize medium; Resizing to new size 16231956480 is not yet supported for medium...`。
固定分配的似乎无法扩容。只能先新建、拷贝到一个动态的vdi，然后对动态的扩容，改用这个。

1.创建新的动态介质（大小可以直接设成扩容后需要的大小）：
```cmd
VBoxManage.exe createhd -namename "F:\Ubuntu1\Ubuntu1\Ubuntu.vdi" -size 40960 -format VDI -variant Standard
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Medium created. UUID: 6f7259ea-f168-4840-b9c2-38930c5b44fa
```
2.将原先的介质拷贝到新介质上：
```cmd
VBoxManage.exe clonehd "F:\Ubuntu1\Ubuntu1\UbuntuBefore.vdi" "F:\Ubuntu1\Ubuntu1\Ubuntu.vdi" --existing
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Clone medium created in format 'VDI'. UUID: 6f7259ea-f168-4840-b9c2-38930c5b44fa
```
3.现在就可以再扩容了（之前创建的大小够大也不用再进行）
```cmd
VBoxManage modifyhd "F:\Ubuntu1\Ubuntu1\Ubuntu.vdi" --resize 151920
```
4.使用扩容后的vdi，然后再用`gparted`分配。

若出现`Shrinking is not yet supported for medium`：不能设置比原大小还小的空间。可能动态的已经扩容了，但是大小还没有显示。

**共享文件夹无访问权限**
https://blog.csdn.net/vipchenvip/article/details/72308317
virtualbox的共享文件夹一般都挂载在/media下面，用ll查看会发现文件夹的所有者是root，所有组是vboxsf，所以文件管理去无法访问是正常的，解决方法是把你自己加入到vboxsf组里，然后重启：
`sudo usermod -a -G vboxsf yourusernanme`（用户名区分大小写）。

**`.pl/.AppImage`文件访问权限不够**
`sudo chmod 755 +文件名`，给文件设置访问权限。然后再`./<name>.pl`。
具体：https://www.runoob.com/linux/linux-comm-chmod.html。

**no executable (name) binary / 没有执行application/x-executable的程序**
对应`<name>`的二进制文件没有访问权限，同上先`chmod 755 <name>`即可。

**Failed to load module "canberra-gtk-module"**
`sudo apt install libcanberra-gtk-module`安装`canberra-gtk-module`这个库。

**QQ for Linux闪退**
删除配置文件：`rm -r ~/.config/tencent-qq`。


----------
## My Vim
vimrc
```
color ron
syntax on

set nu
set shiftwidth=4
set tabstop=4
set cindent
set autoindent
set ruler
set mouse=a

set cul
set cuc
set whichwrap+=<,>,[,]
set lines=45 columns=120
set backspace=indent,eol,start

inoremap ( ()<ESC>i
inoremap [ []<ESC>i
inoremap { {}<ESC>i
inoremap " ""<ESC>i
inoremap ' ''<ESC>i

inoremap <C-Z> <ESC>ua
inoremap <C-R> <ESC><C-R>a
inoremap <C-A> <ESC>ggVG
inoremap <C-V> <ESC>"+gp
vnoremap <C-X> "+x
vnoremap <C-C> "+y
noremap <C-A> ggVG
noremap <S-V> "+gp

inoremap <F5> <ESC><F5>
inoremap <F6> <ESC><F6>
map <F5> :call Com()<CR>
map <F6> :call Run()<CR>

func! Com()
	exec "w"
	exec "!g++ % -o %< -O2 -Wall"
endfunc
func! Run()
	exec "!./%<"
endfunc
```

use of Linux
```
system
ls:显示当前目录下文件(-a:all)
<F11> 全屏
C-c 结束命令
C-s 暂停
任意键 解除暂停
shift+左右键 较ctrl小一点的移动
按到C-z，会挂起到后台进程，可在终端继续输入 fg(+数字)重新回到编辑界面

-----
vim
sudo vim /etc/vim/vimrc :配置文件
vim ~/.vimrc
:sp ~/.vimrc
分屏：https://jingyan.baidu.com/article/7908e85c70b25baf481ad296.html
Ctrl+w+w：切换分屏
ggVG：全选 gg(移到首行)V(进入可视模式)G(光标移到最后一行)
// d  删除选中内容 
dd 剪切整行
d<n>d 剪切n行

// y  复制选中内容到0号寄存器 
" + y：复制(vim)选中内容，并存到+剪切板，即系统剪切板
yy：复制整行
nyy：复制从当前行往下的n行(n=1,2,...)

P(p)：粘贴 在该行前(后)
"+gP

x 剪切
" + x

^ 到本行第一个不是blank字符的位置
Home / 0 到行首
End / $ 到行尾

nG / :n 到第n行
gg 到第一行
G 到最后一行
w / e 到下一个单词的开头/结尾	
C-n 自动补全
zz 把当前行置于屏幕正中央。
zt  把当前行置于屏幕最上部。
zb 把当前行置于屏幕底部。
S-< / S-> 多行缩进（可以鼠标选中也可以Visual模式选中）
C-V 进入Visual Block模式后，选中若干行，输入I//再按ESC可多行注释
C-V 然后选中若干行的//，按d可全部删除

config
"-----------------------------------------
color ron
syntax on

set nu                          "行号
set shiftwidth=4
set tabstop=4                  	"tab长度设置为 4
set cindent			"智能缩进
set autoindent             	"自动缩进
set ruler                       "在右下角显示光标位置的状态行
set mouse=a

set cul
set cuc
set whichwrap+=<,>,[,]		"左移到上一行，右移到下一行
set lines=45 columns=120	"行，字符
set backspace=indent,eol,start

inoremap ( ()<ESC>i
inoremap [ []<ESC>i
inoremap { {}<ESC>i
inoremap < <><ESC>i

inoremap <C-Z> <ESC>ua
inoremap <C-R> <ESC><C-R>a
vnoremap <C-X> "+x
vnoremap <C-C> "+y
map <C-V> "+gp
map <C-A> ggVG

map <F9> :call Compile()<CR>
map <F10> :call Run()<CR>
map <F11> :call ComRun()<CR>
func! Compile()
    " exec "!echo \"Compiling...\""
	exec "w"
	exec "!g++ % -o %< -O2 -Wall"
endfunc
func! Run()
    " exec "!echo \"Running...\""
	exec "!~/%<"
	" exec "!./%<"
endfunc
func! ComRun()
	call Compile()
	call Run()
endfunc


"光标 ibeam:竖线 block:块
if has("autocmd")
        au InsertEnter * silent execute "!gconftool-2 --type string --set /apps/gnome-terminal/profiles/Default/cursor_shape  ibeam"  
        au InsertLeave * silent execute "!gconftool-2 --type string --set /apps/gnome-terminal/profiles/Default/cursor_shape ibeam"  
        au VimLeave * silent execute "!gconftool-2 --type string --set /apps/gnome-terminal/profiles/Default/cursor_shape ibeam" 
endif 

默认根目录（~）
Ctrl -
Ctrl shift +
"-----------------------------------------

else

set nobackup               //覆盖文件时不备份

-----
Linux下的对拍
#include <bits/stdc++.h>
int main()
{
	for(int T=1; ; ++T)
	{
		system("./maker");
		system("./qwq");
		system("./std");
		if(system("diff qwq.out std.out")) {puts("Wrong Answer"); break;}
		printf("Case %d is OK\n",T);
	}
	return 0;
}
```



