# Git 笔记

tags: 学习笔记

-----
[TOC]

-----




---

## Git安装及配置

windows安装：https://git-scm.com/download/win。
linux就`sudo apt-get install git`。

**windows下 改变git bash默认打开路径**
`git bash`快捷方式的属性中，删除目标中的`--cd-to-home`，将起始位置改为想要默认打开的位置，如`E:\Documents\GitHub`。

**配置：**
Git有一个配置工具git config，用于配置或读取相应的工作环境变量。

> 环境变量可以放在三个地方：
>
> 1. `/etc/gitconfig`（Linux）：系统中对所有用户都普遍适用的配置。若使用 git config 时用 --system 选项，读写的就是这个文件。
> 2. `~/.gitconfig`：用户目录下的配置文件只适用于该用户。若使用 git config 时用 --global 选项，读写的就是这个文件。
> 3. 工作目录中的`.git/config`：仅对当前项目生效。
>
> 每一层配置都会覆盖上层的同变量名配置，如`.git/config`会覆盖`/etc/gitconfig`。
>
> Windows上的配置文件有2.3.，即用户主目录下的`.gitconfig`和当前工作目录的`.git/config`。用户主目录即`$HOME`变量指定的目录，一般是`C:\Documents and Settings\$USER`或`C:\users\$USER`。
**用户信息：**
配置/查看/取消设置 提交时的用户名称和邮件地址。
添加`--global`则为全局配置，否则仅为当前仓库配置。
```bash
git config --global user.name "SovietPower"
git config --global user.email "sovietpower@foxmail.com"

git config user.name
git config user.email

git config --global --unset user.name "SovietPower"
git config --global --unset user.email "sovietpower@foxmail.com"
```

**默认编辑器：**
Git默认使用的编辑器。windows安装的时候就可选。
```bash
git config --global core.editor vim
```

**默认差异分析工具：**
Git默认在解决合并冲突时使用哪种差异分析工具。
如选择vimdiff：
```bash
$ git config --global merge.tool vimdiff
```

**查看配置信息：**
查看单个：`git config <name>`
查看所有：`git config --list`
重复出现的变量表明它们来自不同配置文件。Git会选择最后一个。
这些信息存储在`~/.gitconfig`和`/etc/gitconfig`中，也可直接打开查看。
当前项目的配置保存在`.git/config`下。

**常用配置**

`git config core.fileMode <value>`：true 或 false。控制 Git 是否跟踪并记录文件的权限模式变化。







### gitignore

所有空行或者以 # 开头的行都会被 Git 忽略。

```shell
# 忽略所有的 .a 文件
*.a
# 跟踪所有的 lib.a，即便之前忽略了 *.a
!lib.a
# 仅忽略当前目录下的 TODO 文件
/TODO
# 忽略任何目录下名为 build 的文件夹
build/
# 忽略 doc/notes.txt，但不忽略 doc/server/arch.txt
doc/*.txt
# 忽略 doc/ 目录及其所有子目录下的 .pdf 文件
doc/**/*.pdf
```











---


## Github
Git没有中心服务器。之前提到的Git命令均在本地执行。要通过Git分享代码或者与合作开发，就需要将数据放到一台其他人能连接的服务器上。
比如使用Github作为远程仓库。

### 配置验证信息
本地Git仓库和GitHub仓库之间的传输是通过SSH加密的，所以需配置验证信息。

生成SSH key：
```bash
$ ssh-keygen -t rsa -C "youremail"
Generating public/private rsa key pair.
Enter file in which to save the key (/c/Users/your_user/.ssh/id_rsa):
Created directory '/c/Users/your_user/.ssh'.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /c/Users/your_user/.ssh/id_rsa
Your public key has been saved in /c/Users/your_user/.ssh/id_rsa.pub
...
```
`youremail`为Github账户邮箱。
然后可输入密码文件储存目录，按回车为默认路径（一般为C盘users）。
然后可设置密码，按回车为不设置密码。

然后到Github，选择 设置-Access，找到 SSH and GPG keys，选择 New SSH Key，任起一个名字，将密码文件目录下的`id_rsa.pub`中的全部内容复制到key中，Add即可。

可用`ssh -T git@github.com`测试是否连接成功：
如果出现`You've successfully authenticated, but GitHub does not provide shell access.`即成功，如果出现`The authenticity of host 'github.com' can't be established.`，看一下输出的fingerprint是否与[Github的](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)相同，如果相同输入yes再运行即可（不同就重新生成再试）。

### 添加仓库

首先在 Github 上建立仓库，复制其 SSH。
用`git remote add origin <Your repo's SSH>`添加它到当前的远程仓库，命名为 origin（注意当前目录需要为`git init`后的Git目录，添加的远程仓库会保存在`.git/config`中）。
具体见 *git remote*。





---

## Gitlab
使用GitHub Desktop管理GitLab仓库：https://zhuanlan.zhihu.com/p/403193674
使用HTTP连接，输入账号密码。

### 配置验证信息
使用和github一样的方法。
如果邮箱已经创建了key，则直接用`.pub`里的key即可。



