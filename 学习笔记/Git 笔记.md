# Git 笔记

tags: 学习笔记

-----
[TOC]

-----
> https://git-scm.com/docs
>
> 入门：https://learngitbranching.js.org/
> https://www.runoob.com/git/git-tutorial.html
>
> TODO：vsc 有 github pull request 插件
>
> 提交、处理冲突流程：https://www.zhihu.com/question/570661786/answer/3308195768

## Git 基础
Git 是分布式版本控制系统。Github 是一个用 Git 做版本控制的代码托管平台。

**工作区**

Git 分为工作区、暂存区和版本库。
- 工作区 (workspace, working tree)：电脑里保存并直接编辑的目录、文件，当前的工作区域。
- 暂存区 (staging area, stage, index)：commit 前暂存文件的地方，包含着下一次 commit 的所有改动。暂存区就存在`.git/index`这个文件中，所以暂存区也叫作索引（index）。
- 版本库/git 仓库 (local repository, repository)：提交历史。就是工作区下的`.git`文件夹，但不属于工作区。包含了所有元数据和数据，包括：当前分支，所有本地分支，远程仓库信息，之前所有提交历史，即每次`commit`的数据变动。

> 此外还有：
> 远程仓库（remote repository）：顾名思义。
> 对象库（object）：目录`.git/objects`。包含了创建的各种对象及内容。

对工作区修改/添加的文件执行`git add`时，git 首先将更新的内容做快照，写入到对象库`.git/objects`中的一个新的对象中。
然后，暂存区`.git/index`的目录树被更新？记录新文件的时间戳、长度和对应的新对象的 ID。

当执行提交`git commit`时，暂存区的目录树写到版本库（对象库）中，当前分支会相应地更新。所以当前分支指向的目录树就是提交时暂存区的目录树。

**文件属性 / tracked**

项目中，每个文件要么是 tracked，要么是 untracked。tracked 表示该文件已经被 git 所管理，git 会跟踪它的增删改操作；untracked 表示文件不被 git 所管理和监控。

git 中 tracked 的文件有3种状态：

- **modified**：本地文件修改过，但还没有 add 到暂存区中。文件位于工作区 (working directory)。
- **staged**：本地文件修改过，且修改已经 add 到暂存区，等待提交。文件位于暂存区 (stage area)。
- unmodified / **commited**：自上次提交后未修改，或说修改已提交。文件位于 git 仓库/数据库 (git directory)。

每个文件都会经历 modified - staged - commited 的过程。



### 分支

一个分支包含多次提交记录。分支名总是指向对应分支的最新提交。

git 中，可以存在很多分支，它们的提交记录构成了一棵树。不同的分支位于不同子树，它们的 LCA 是分支创建的起始点。
每个分支的名字是一个指针，指向该分支的最新提交。当分支提交时，会创建一个新的提交节点，并使分支名字/指针指向它。

```bash
$ cat .git/HEAD # 查看 HEAD（一般为当前分支），也可以用 git symbolic-ref HEAD
ref: refs/heads/master
$ cat .git/refs/heads/master # master 分支的最新指针
7406a10efcc169bbab17827aeda189aa20376f7f # 提交的哈希值
```

执行`git init`后，git 会创建一个 master 分支。

**HEAD**

HEAD 指向当前分支名（即当前分支的最新提交），会随分支的提交而移动。
**HEAD 记录了当前（工作区）所在分支。checkout 切换分支，实际上就是更改 HEAD 的指向。**

可以通过 checkout 将 HEAD 指向某一次提交记录，而不是某一分支，此时称它处于游离/分离状态 (detached)。
这种状态用于实验/测试，它做出的修改不会影响原分支。如果要保留修改，需要创建一个新分支继承，然后合并到原分支。见 *使用问题 - 游离状态*。

> 许多操作要求 HEAD 是干净的，即自上次提交后，没有任何修改。

**符号引用** / **symbolic ref**

符号引用是一个指向其它引用（分支名或 tag）的引用，会随着被指向引用的移动而移动。
HEAD 就是指向当前分支的符号引用（HEAD 引用 branch 引用 某提交）。

通过 *git symbolic-ref* 可以读写符号引用。

> 在存储中，符号引用是一个以`ref: refs/`开头的字符串为内容的常规文件，比如：`.git/HEAD`就是一个内容为`ref: refs/heads/master`的文件。







### 提交

**标识**

每次提交会生成40位 SHA-1 哈希值作为其标识。
哈希值、引用（分支名、HEAD、tag）、相对引用都可以标识一次提交（**但以下均通过`commitID`表示**）。

使用某次提交时，不需要完整写出哈希值，只需要写出能唯一标识提交记录的前几个字符。

**相对引用**

除了使用哈希值、引用标识提交记录外，还可以通过相对于某引用的距离来标识提交记录。

- `^`：上一个提交记录（父节点）。
- `~<num>`：前 num 个提交记录（向上 num 层的父节点。num 非负，默认为1）。
- `^<num>`：仅用于 merge 产生的、拥有多个父节点的节点，用于选择引用哪一个父节点（注意不是向上 num 层）。
    默认为`^`选择第一个父节点，使用`^2`选择另一个父节点。
- 以上操作符可以链式操作，比如：`HEAD~^2^^~2`。

比如：`HEAD, HEAD~0`指向当前分支，`HEAD^, HEAD~1`指向当前分支的上一次提交，`HEAD^^^, HEAD~3`指向上上上次提交。
也可以使用`master^, master~3`。



### 常规工作流

**添加功能**

有两种方式：

1. 直接使用主要分支（如 master），而不新建分支；在修改完 commit 后，通过`git pull --rebase; git push`来合并和提交 master 分支。
2. 创建新分支（如`git checkout -b feat origin/master`）；在修改完 commit 后，通过`git pull --rebase; git push`来合并和提交 master 分支；然后切换到 master 用 pull 更新本地的 master 分支（也可以先用临时分支提交）。
   第一次提交：`git push --set-upstream origin gxb_test`。

合并前可以先`git diff <commit1> <commit2>`来查看两分支的差异。

**修改后提交**

创建新分支更改后，提交并与远程对应分支绑定：`git push -u origin <newBranch>:<bindBranch>`（bindBranch 与 newBranch 相同即可，也就是可以不填）。

如果主分支有新提交：先 `git fetch origin` 获取最新主分支，然后 `git rebase origin/master` 将当前分支移到最新的主分支后。


**合并多个分支**

rebase：`git rebase HEAD feat1`、`git rebase HEAD feat2`、`git rebase HEAD feat3`。

merge：`git merge feat1`、`git merge feat2`、`git merge feat3`。

**merge 与 rebase**

建议：在自己的分支上使用 rebase：当自己的分支需要合并其它分支的修改（一般就是主分支）时，使用 rebase。
在合并自己的分支时使用 merge --ff。

**同步某分支最新更新到当前分支**

```shell
git checkout dev
git fetch origin
git rebase origin/master
# 如果有冲突，解决后 git add . && git rebase --continue
git push --force-with-lease origin dev
```

**将一个仓库的分支提交到另一仓库**

1. 添加另一仓库到远程源：`git remote add origin https://github.com/owner/target-repo.git`（也可以是 ssh 地址）。如果该源已存在，可 `git remote set-url origin xx`。
   git remote -v 查看已有的远程源。
2. 推送到目标仓库的新分支或已有分支：`git push origin your-branch:target-branch-name`。





---


## Git 操作
命令后可加`-h`或`--help`查看说明。

对于可以指定文件或目录的命令，最后可加`-- <path>...`来指定文件，`--`用于将文件路径与参数区分开。



### 创建仓库

**git init**

`git init`用于初始化，使用一个已有文件夹创建仓库。Git会生成一个`.git`目录，该目录包含了Git所需的所有资源元数据。不改变其它数据。
也可指定文件夹：`git init <filename>`。

**git clone**

`git clone`从远程拷贝一个 git 仓库到本地。

克隆仓库到当前文件夹：`git clone <repo>`
克隆仓库到指定文件夹：`git clone <repo> <directory>`
如：`git clone git://github.com/SovietPower/QQT.git`。

**git config**

编辑当前仓库配置：`git config -e`（会使用默认编辑器打开配置文件）
编辑全局配置：`git config -e --global`（对所有仓库生效）
具体见 *Git 配置笔记*。

配置提交时的用户名称和邮件地址（当前/全局），会被用于每一次提交：

```bash
$ git config user.name "SovietPower"
$ git config user.email "sovietpower@foxmail.com"

$ git config --global user.name "SovietPower"
$ git config --global user.email "sovietpower@foxmail.com"
```



---

### 修改 提交

#### **git add**
`git add`将工作区的文件添加到暂存区 (staged)。添加到暂存区的文件才可commit到仓库（之前`add`但修改了的文件仍在工作区，需要再`add`进去）。

添加一个或多个文件到暂存区：`git add <file1> <file2>...`
添加指定目录到暂存区（含子目录）：`git add <dir>`
添加当前目录下的所有文件到暂存区：`git add .`

> 使用 `git reset <file>...` 或 `git restore --staged <file>...` 移除 add 的文件（后者更清楚）。


#### **git commit**
`git commit`将暂存区内容添加到本地仓库中。

提交暂存区到本地仓库中：`git commit -m [message]`。
提交暂存区的指定文件到仓库区：`$ git commit <file1> <file2> ... -m [message]`

参数：

- `-m [message]`：添加备注信息/注释，如果不加，Git 会打开编辑器直接编辑备注信息（在最后添加即可）。如果最后还没有备注信息，则 commit 会失败。
- `-a`：设置修改文件后不需执行`git add`命令，直接提交？
- `--amend`：发起新提交，新的提交会替换上一次最新的提交，而不会产生新的提交记录（需要没 push 到远程）。
    当不想创建多个 commit，或上次 commit 有地方错了不想保留错误记录时，可用 --amend 取代旧的提交。
    同样需要备注信息，内容会附带要替换的之前 commit 的备注。

> 对于未`add`的非缓存区文件（AM），`commit`不会提交；对于已`add`但修改了的缓存区文件（M），需重新`add`才可`commit`提交（因为不在缓存区中），或使用`-am [message]`提交。
> <br>
> Linux中，commit备注使用单引号`'`；Windows中，commit备注使用双引号`"`。
> 所以在git bash中为：`git commit -m '这是提交说明'`，在Windows中为：`git commit -m "这是提交说明"`。


#### **git diff**
`git diff`：比较暂存区和工作区的文件差异。会显示已写入暂存区和已经被修改但尚未写入暂存区的文件的区别。
可以指定文件`<path>...`，默认全部（当前文件夹）。
新创建的文件不会显示，因为不被 git 所跟踪，可以用 git status。

参数：

- `--cached`或`--staged`：比较版本库和暂存区的文件差异，而不是暂存区与工作区。
- `--stat`：显示各个文件修改的摘要，而非整个 diff 信息。
- `<commitID>`：查看版本库某次提交与工作区的文件差异。
    比如：git diff HEAD 查看工作区与上次提交的差异（HEAD、分支实际上都是 commit id，只是 HEAD 指向当前分支）。
- `<commitID1> <commitID2>`：显示两次提交之间的差异。


#### **git mv**
`git mv`可移动或重命名文件、目录或软连接。
**语法：**`git mv [options] <file> <newfile>`（基本与`mv`相同）

用法基本与`mv`相同，但与`mv`的区别在于：
如果某文件已缓存过，则：
对它`git mv`移动/重命名时，会**同时对缓存区**中的该文件进行移动/重命名。
对它`mv`时，**不会同时更新缓存区**中的该文件，所以缓存区会与工作区产生两个不同：删除了`mv`前的文件，新增了`mv`后的文件。需要重新`add`。


#### **git reset**
> https://www.jianshu.com/p/c2ec5f06cf1a

`git reset`将 HEAD 指向指定的提交，来退回到某一次提交的版本。
**语法：**`git reset [--soft/--mixed/--hard] <commitID> <path...>`
最后的 commitID 可省略，默认为 HEAD。
可指定只回退某文件或某目录`<path>`，默认全部。

> reset 改变分支的指向，继而改变 head（HEAD->branch->某提交），然后将目标提交之后的提交历史删除。
> checkout 只改变 head 的指向。
>
> reset 不影响远程分支。想要共享撤销的更改，需要用 revert。
> reset 会彻底修改/删除提交历史，revert 不会，更安全。

**--mixed：默认参数**。
将版本库（HEAD 和当前分支）回退到指定提交，工作区不变，清空暂存区（或将某个文件/目录从暂存区中移除）。
不影响工作区（回退前的修改依然保留在工作区）。因为 reset 导致工作区与版本库的差异，需要重新 add 到暂存区。
（换句话说，就是回退 HEAD 到指定 commit，并将指定 commit 与原 HEAD 之间的提交保留在工作区）

> `git reset <file1> <file2>...` 就是取消指定/所有 add 的文件，与 `git restore --staged <file>...` 相同。
>
> `git reset HEAD^ file` 会将 file 在 HEAD^ 的内容放入暂存区，但工作区不变。此时撤销工作区即 HEAD 的修改就是 HEAD^ 的内容。

例：

```bash
$ git reset HEAD^ # 回退版本库内容到上一个版本
$ git reset 052e # 回退版本库内容到指定版本
$ git reset HEAD^ 1.c # 仅回退版本库中，文件1.c的版本到上一个版本

$ git reset HEAD # 清除所有已缓存内容（清空缓存区，但 HEAD 与当前相比没有改变任何文件，所以不会影响版本库）
$ git reset HEAD 1.c # 清除缓存区中1.c的缓存
```

**应用：**

1. 移除 add 错的文件（`git reset HEAD [file]`）。
2. 可像`--soft`一样合并多次 commit 记录为一次。与`--soft`相比需多`git add .`一次，但这样可以在本地显示出这几次 commit 与之前的更新的差异。
3. 当发现 commit 提交了错误文件时，如果修改错误再重新 commit，会留下一次错误的 commit 历史。此时可先`reset`回到正确节点，在工作区修复错误后再 add、commit。

**--soft：**`git reset --soft <commitID>`
将版本库（HEAD 和当前分支）回退到指定提交，工作区不变，并将此时工作区和版本库的有差异文件缓存到暂存区。
（换句话说，就是回退 HEAD 到指定 commit，并将指定 commit 与原 HEAD 之间的提交保留在工作区和暂存区。等价于使用 mixed 后再 add）

**应用：**
`reset --soft`后直接 commit，可将回退版本与最新版本之间的任意多次 commit 合并为一次。可用于将多次简单、无明显意义的 **commit 记录合并**为一次。

**--hard：**`git reset --hard <commitID>`
将**工作区和版本库**的内容全部回退到某版本。
也即将整个文件夹的所有 git 管理的文件恢复到和某版本一致（**清空工作区所有 git 管理的文件再新建**）。
（换句话说，就是回退 HEAD 到指定 commit，并将指定 commit 与原 HEAD 之间的提交**直接删除**）

==**谨慎使用 hard！**==会彻底删除工作区中所有被追踪的文件。如果文件曾 add 过，但没 commit 过，就永远没了；未 commit 的修改也会丢失。
未曾 add 的文件 (untracked)，不会被 git 管理，不会被删除 。

**应用：**
**放弃目前本地的所有改变**（与`git checkout .`类似？），或是放弃 reset 目标节点后的所有 commit；然后将 head 及 branch 指向其它位置。

> reset --hard 回退的提交依然会保留，但不能再通过当前分支访问（一般只能通过哈希值访问？）。
>
> 如果使用 hard 覆盖了 staged 修改，可以`git fsck --lost-found`然后到`~/.git/lost-found/other`里面找到被覆盖的文件。

#### **git revert**

`git revert <commitID>...`：创建一个与指定的提交有相反改动的提交，将该提交添加到当前分支，从而回退指定提交。
与 reset 不同，它不会影响指定提交之后的提交，只是应用指定提交的反向变更；不会删除“回退”的提交记录，而是创建一个新的提交，用来撤销目标提交的修改。
“回退”的提交历史会被保留、更安全。

要求工作区干净、无未提交内容。
本质上是 git 应用了一系列反向修改，所以可能要处理冲突。

> 与 commit 的提交相同，revert 产生的提交也可以通过 revert 或 reset 撤销，并且需要注释信息（但不能通过 -m 指定，-m 有其它用途）。
>
> `git revert HEAD`可撤销最近的一次提交（包括最近的 revert）。即使该提交已提交到远程仓库，它也依然有效、安全，而`git reset HEAD^`将无法生效（`push -f`会给其它人带来麻烦）。

#### **git restore**

`git restore <file>...`：丢弃工作区的修改（如果工作区有未 add 的修改，丢弃，用缓存区中的内容替代）。
与加参数`--worktree`的情况相同，表示将缓存区与工作区恢复到某个一致状态。

`git restore --staged <file>...`：将之前 add 的缓存区文件丢弃。可用来处理**之前没提交的** add 错或不再想 add 的文件，之后可以重新 add（**不会影响版本库**，只是将上次提交之后，新 add 的文件移除）。

`git restore --source [HEAD] <file>...`：用版本库中，之前某次提交中的文件，替换掉当前工作区中的文件。
不会影响缓存区，之前添加到缓存区中的数据将保留。想要提交 restore 的数据，需要重新 add。

`git restore --source --worktree [HEAD] <file>...`：用版本库中，之前某次提交中的文件，替换掉当前工作区和缓存区中的文件。


#### **git rm**
`git rm`可删除文件。
**语法：**`git rm <file>`（基本与`rm`相同）

用法基本与`rm`相同，但与`rm`的区别在于：
如果某文件已缓存过，则：
`git rm`不仅删除文件，**还将删除记录更新到缓存区，以便更新版本库**（会同时删除缓存区中的该文件（如果有））。
`rm`只是删除文件，不会将更新提交到缓存区，也不会同时删除缓存区中的该文件，所以缓存区会与工作区产生一个不同：删除了该文件。需要重新`add`。

`git rm --cached <file>...`：删除缓存区中的某文件。可用来处理**之前已提交的** add 错或不再想 add 的文件，之后可以重新 add（**会影响版本库**，会将之前提交的文件从版本库和缓存区删除，**但保留在工作区**）。

处理文件夹时，需要加 -r 递归删除。

> 删除文件的恢复：
> rm 删除（或修改错，想改回去）的文件，可用`git checkout -- <file>`用版本库里的最新内容，替换工作区的版本。
> git rm 删除的文件，可用`git reset (HEAD .)`、`git checkout (.)`恢复到版本库的最新内容（`.`可改为具体的文件名）。
>
> **注意，删除的文件只能从版本库中恢复，之前未提交的修改都将丢失。**
> 不过在`git rm`已修改的文件时，会给出警告，只能使用 -f 删除。


#### **git status**
`git status`：查看本地已修改的文件状态，即自上次提交之后文件的修改信息（不会显示自上次提交之后没有修改的文件）。
可以指定文件`<path>...`，默认全部（当前文件夹）。

> 会显示未被 git 跟踪的文件。
> 可以在合并出现冲突时，查看冲突文件。
> 如果自上次提交后没有文件被修改，则为 clean。

使用`-s`参数可获得简短的输出结果，有这几种：

- `A`表示这是一个新文件（上次 commit 没有）。
- `M`表示自上次 commit 后文件有改动。
- `D`表示文件之前被提交了，但现在被删除了。
- `??`表示文件未被追踪 (untracked)，即是一个新文件，且没有被 add 过。

状态为红色，表示更新信息没有 add（changes not staged for commit）；为绿色，表示更新信息已经 add，等待 commit（changes to be commited）。
使用 rm 删除文件不会 add 该文件，所以删除的文件将为红色 D；用 git rm 在删除时会 add，所以文件状态为绿色 D。

A 与 M 可以组合出现，通常(?) A 为绿色，M 为红色，表示这个新文件被 add 过，但之后又有未 add 的改动。

#### **git clean**

删除工作区中没有被跟踪/管理 (untracked) 的文件，也即未曾 add 过的文件。
注意，删除的文件将无法找回！慎用。
可以用来删一些临时文件，如 .o，.exe。

`git clean`和`git reset --hard`可以结合使用，让工作目录回退到某一次提交后的状态：
`clean`清除未被管理的文件，`reset`回退被管理的文件。

参数：

- `<path>`：可以指定只 clean 某个文件夹。
- -n，--dry-run：只显示将要被删除的文件，但不进行删除。
- -d ：默认情况下，删除不会进入子文件夹递归删除。-d 要求遍历未被跟踪的文件夹进行删除。
- -f，--force ：为了安全，如果项目没有配置 clean.requireForce 为 false，clean 必须加 -f 参数来强制删除。
- -x ：默认情况下，不会删除 gitignore 文件中声明的忽略的文件。-x 要求也删除这些文件。



---

### 版本管理


#### **git blame**

`git blame <path>`：逐行显示指定文件的每一行代码是由谁、在什么时候引入或修改的。

参数：

- `-L <起始行号>,<结束行号>`：只查看指定行号范围内的代码记录。
- `-C`：对于重命名或拷贝的代码行，也进行溯源。
- `-M`：对于移动的代码行，也进行溯源。
- `-C -C`或`-M -M`：对于较多改动的代码行，进行更进一步的溯源。
- `--show-stats`：显示每个作者的行数统计信息。





#### **git log**
`git log [commitID] [-- <path>...]`：查看过去所有提交记录的日志。日志包括4部分：提交的哈希值、作者、日期、提交信息。
可以指定只查看某提交记录。可以指定只查看某些文件的提交。

参数：

- `-p`或`--patch`：详细显示每次提交的修改（每个修改的文件和具体的修改内容）。
- `--stat`：简单显示每次提交的修改（每个修改的文件改了多少行）和总共增/删了多少行。
- `--oneline`：显示简略信息，每个提交只显示一行，包括：哈希值的前7位，提交信息、标注的 tag、其它分支位置。
- `--graph`：以图标形式展现提交树。
- `-<n>`：<n> 是数字，只显示最近的 n 条提交记录。
- `--before/after/until/since="..."`：只显示 某日期之前/之后（不含）/直到/自从某日期的提交。可以一起用。
    支持日期的格式有多种，如：`yy-mm-dd`（月日中的前导0无所谓，但年份要写全），`3 days ago`。
- `--author="AuthorName"`：只显示某个或某些人的提交。会使用该字符串作为子串查找，也可以用正则。
- `--grep="pattern"`只显示提交信息中包含指定字符串的提交。
- `--follow`：在查看指定文件时，同时查看该文件在被重命名或移动前的提交历史。
- `--no-merges`：不显示 merge 产生的提交。
- `--reverse`：逆序显示提交日志。
- `--relative-date`：显式相对日期，而不是绝对日期。

> 滚动内容：上下键/k/j 键：上下滚动；b/空格：上/下翻一页；q：退出。
>
> 如果要探究某文件或内容的修改，可以先`git log -p --follow -- filename`查找修改了该文件的提交历史，再`git diff <commit1> <commit2>`对比两次提交历史。

#### **git show**

**git show [HEAD]：查看某次的提交信息。**
参数可以是 head 相关表达式，也可是一个 commit ID。



---

### 分支管理

#### **git branch**
`git branch <branchName> [commitID]`：创建分支。
可以指定在哪次提交上创建，默认为 HEAD。

`git branch -d <branchName>`：删除本地某分支。如果参数为 -D 则为强制，等价于`--delete --force`或`-d -f`。
`git branch -d -r <branchName>`：删除远程某分支。更新需要 push 到服务器上：`git push <name> <branchName>`，否则只是删除本地存储的远程分支引用，没有实际删除远程分支（建议直接 `git push -d`）。

`git branch -m <oldName> <newName>`：重命名本地某分支。如果参数为 -M 则为强制，等价于 --move --force。

> 如果在远程删除某分支 而本地 remotes 中的分支信息没有更新，可以 `git fetch -p` 获取最新的分支信息，并删除本地已经不存在的远程分支引用。

`git branch`：显示本地的所有分支。带星号的是当前分支。
`git branch -r`：显示远程的所有分支。
`git branch -a`：显示本地和远程的所有分支（当前分支是绿色，远程分支是红色）。
`git branch -vv`：显示默认的远程分支。

`git branch -u <remoteName>/<branchName> [branchName]`：设置某分支的远程跟踪分支。最后的参数默认为 HEAD。

`git branch -f <branchName> <commitID>`：强制更改目标分支的指向，将其指向某一提交，然后切换到目标分支。
（不能更改 HEAD，因为 HEAD 不是分支，要通过 checkout 修改 HEAD）

> -f 单独使用时为更改指向，与 -d 一起使用时强制删除分支（不管其合并状态如何、是否指向有效提交），与 -m 一起使用时强制重命名分支（即使已存在同名分支）。

#### **git checkout**

`git checkout`：检查工作区相对于版本库的修改。

`git checkout <branchName>`：将 HEAD 指向指定分支，从而切换分支。
`git checkout -b <branchName> [commitID]`：创建并切换到新的分支。如果分支名存在则失败。
可以指定在哪次提交上创建，默认为 HEAD。
`git checkout -b <branchName> <remoteName>/<branchName>`：创建一个跟踪指定远程分支的本地分支。

`git checkout <commitID>`：将 HEAD 指向指定提交（见下 *游离状态*）。

`git checkout <path>...`：将工作区的指定文件恢复到上次提交的状态。用于放弃当前工作区的修改。
`git checkout .`：将工作区的所有文件恢复到上次提交的状态。
注意，==因此被覆盖的工作区中未 add 的改动会丢失。==

切换分支后，Git 会用该分支的最后提交的快照替换工作目录的内容， 所以多个分支不需要多个目录。

注意，==在切换分支后，已跟踪 (add 过) 的文件的所有未提交改动，都会丢失！==git 通常会提示并禁止。
想要保留它们但不提交，使用`git stash`。

> 最新的 git 使用`git switch`切换分支，避免 checkout 功能过多。

#### **git cherry-pick**

`git cherry-pick <commitID>...`：将指定的一些提交复制到当前所在的位置（即 HEAD）之后，然后将当前分支指向最后一个提交。
**cherry-pick 可以将任何非上游的提交取过来，追加到 HEAD 后。**

与 rebase 类似，但更灵活，可以任意指定需要的提交，但需要知道对应提交的哈希值。
rebase -i 也可选择性指定提交，且更直观、不需要知道哈希值。

> 当需要修改中间的某次提交时（假设为 HEAD^2），可以：
>
> 1. 用`rebase -i HEAD~3`将 HEAD^2 移动到提交列表 HEAD^2 ~ HEAD 的最后，然后修改、`commit --amend`覆盖，然后再`rebase -i HEAD~3`覆盖原先的移动、合并分支。
> 2. 或先 checkout 切换到`HEAD~3`（可在此建立临时分支，以避免进入游离状态；也可最后再创建分支），用`cherry-pick HEAD~2`将指定提交移动到 HEAD 后，然后修改、`commit --amend`覆盖，然后再`cherry-pick` HEAD^ ~ HEAD 移动回来。这样更方便。
>
> （可见 https://learngitbranching.js.org/ 杂项2, 3）

#### **git merge**

`git merge <branchName>`：将指定分支与当前分支合并，产生一个公共后继提交，然后将当前分支指向公共后继。

如果目标分支是当前分支的后继，则不需要合并内容，只需要将当前分支移动到目标分支指向的提交。
merge 不会影响目标分支，所以如果当前不是主要分支，还要切换到主要分支（比如 master）然后 merge 当前分支（移动到合并对应的提交，称为将 master 快进到最新的更新上）。

通常流程为：从 master 新建分支，修改，切换到 master，合并新分支，删除新分支。

参数：

- `--ff`：默认模式，在条件允许的情况下使用 fast forward：如果当前分支提交时，合并目标分支没有发生其它分支的修改，则直接将当前分支的修改复制到目标分支后（记录为线性，类似 rebase），不保留分叉结构。
    `--no-ff`：禁止 fast forward，总是在合并时创建一个合并提交（推荐）。
- `--squash`：将目标分支的所有新的 commit 合并为一个 commit 并放到当前分支上，但不会修改目标分支。

#### **git rebase**

`git rebase <branchName>`：设当前分支与目标分支的 LCA 为提交 p，将 p->当前分支 上的提交记录 复制到目标分支的提交之后，然后将当前分支指向最后一个提交。p->当前分支的历史提交会正常保留到目标分支后，但是与之前提交哈希值不同（复制了一遍）。

与 merge 类似，如果目标分支是当前分支的后继，则只需要将当前分支移动到目标分支指向的提交；rebase 分支后，还要切换到目标分支、将其 rebase 当前分支、以更新到最新提交（或者直接`rebase 当前分支 目标分支`）。

rebase 后，可通过`git push --force-with-lease origin 当前分支`更新远程仓库。

> rebase 就是取出一系列的提交记录，逐个“复制”到另外一个位置。用于在保留当前提交的情况下，同步另一个分支的更新。
> 比如 dev 在 master 提交 o 后创建，提交 o - a - b，master 在分支创建后提交 o - c - d，rebase master 后 dev 分支提交历史会变成 o - c - d - a - b。
>
> 与 merge 相比，可以创造更线性、清晰、简洁的提交树；但是会大幅修改指定分支的提交历史。
> 此外，由于 rebase 是逐个应用提交，可能导致多次合并冲突；而 merge 只需要处理一次。

`git rebase <branch1> <branch2>`：将 LCA->分支2 上的提交 复制到目标分支1之后，然后将 HEAD 指向分支2、将分支2指向最新的提交。
即分支2默认为 HEAD。

> 常用操作：`git rebase master`：将当前分支相对于 master 的修改添加到最新的 master 分支后，作为当前分支（不会改变 master，可以将 master 的新提交移到自己的提交之前）。
> `git rebase HEAD feat`：将当前分支没有的 feat 最新的提交，复制到当前分支后。
>
> rebase 的复制和移动不会影响 LCA 的计算。比如：执行`rebase a master`、将 LCA(a, master)->a 复制到 master 后，即使 a 已经指向最新的提交，LCA(a, b) 结果依然不变，可以`rebase b a`来讲 LCA(a, b)->b 的结果复制到 a 后。
> （见 https://learngitbranching.js.org 高级1）
> 因此可用`git rebase HEAD feat1`、`git rebase HEAD feat2`、`git rebase HEAD feat3`来连续合并三个分支。

`git rebase -i <branchName>`：执行交互式 rebase (--interactive)，git 会列出将要被复制的提交列表，以及每个提交的哈希值和信息，并允许用户编辑该列表：。

- 可更改提交的顺序。
- 可通过切换 pick 的状态来避免不想要的提交。
- 可编辑提交信息。
- 可将多个连续的提交合并为一次提交，使历史更简洁。
- 可将单个提交拆分成多次提交。

> 可以通过`git rebase -i`和`git cherry-pick`来选择性提交，从而避免提交包含调试信息的提交，只提交最终解决 bug 的提交：设主分支为 master，创建 bugFix 分支，然后编写调试代码，提交一次；调试完成后修复 bug，提交一次（可能还是需要删除调试代码？）；然后`rebase -i master`或切换到 master 然后`cherry-pick`最后的提交，从而避免提交调试信息。
>
> 在交互模式中，可以指定某次提交为 squash，它会与少一次提交进行合并、减少一次提交。
> 因此推荐在 rebase 时指定除了第一次提交外的提交为 squash（第一次提交仍为 pick），来将多次提交压缩为一次。
> （一次提交仅包含当前提交的更改，不含之前的提交）

#### **git stash**

`git stash [push]`：存储当前分支下的所有工作区和暂存区的改动。会存在`.git/refs/stash`。

参数：

- `-m "msg"`：附加信息。
- `-u`或`--includ-untracked`：也储存未追踪的文件。
- `-a`或`--all`：也储存未追踪的文件和忽略的文件。
- `-p`或`--patch`：会显示工作区和HEAD的差异，通过编辑差异文件，排除不需要保存的内容？与 add -p 类似？
- `--index`：恢复时不仅恢复工作区，还恢复暂存区（默认似乎是将保存在暂存区的也恢复到工作区）。
- `-k`或`--no-keep-index`：只保存工作区，不保存暂存区。
- `-- <file>...`：保存指定文件的改动（如果不加`--`，后面会被识别为参数而非路径）。

`git stash list`：查看存储的改动列表。
`git stash pop`：恢复最近保存的内容，并将其移出 stash。可以加`stash@{n}`来指定 pop 哪个。
`git stash apply stash@{n}`：恢复某次保存的内容，但不将其移出 stash。
`git stash save "msg"`：与 -m 类似，附加信息并保存（git 版本低的话没有 -m 这个选项，只能用 save）。

`git stash show stash@{n}`：查看某次保存的内容，修改了哪些文件。
`git stash show -p stash@{n}`：查看某次保存的内容，修改了哪些文件和具体的修改内容。
`git stash clear`：删除所有保存的内容。
`git stash drop stash@{n}`：删除指定的保存内容。
`git stash branch <branchName> stash@{n}`：用某次保存的内容新建一个分支。如果当前分支和之前暂存的内容有冲突，可以先建一个临时分支。

> 如果不用 stash，可以先 commit 一次，切换分支；之后切换回来的时候 reset head^。



#### **git worktree**

`git worktree add <newPath> <branch>`：创建一个新的仓库（文件夹），来存放和编辑目标分支代码，不会影响当前仓库。

与 stash 类似，可在不提交的情况下切换到其它分支进行工作，但不会影响当前分支（场景见[这里](https://liuhaohua.com/server-programming-guide/collaboration/git-workflow/switching-branches/)）。

与 clone 一个仓库存放对应分支相比，可以复用 .git 文件、减少磁盘占用。





---

### 远程仓库

每个项目的配置文件`.git/config`中都会记录自己的仓库 (repository) 名称与地址映射。
例：

```
[remote "origin"]
	url = https://github.com/SovietPower/MIT-6.824-Labs.git
	fetch = +refs/heads/*:refs/remotes/origin/*
```

fetch 的值有两部分，用冒号分割，分别为：本地仓库文件夹；远程仓库在本地的缓存文件夹。
git fetch 时，会将远程仓库的数据添加到缓存文件夹对应的分支中（所以前面是加号）。
git merge 时，会将缓存文件夹下的对应分支，合并到本地仓库（`refs/heads/`）的对应分支中。

`.git/refs/remotes`中保存了各个远程仓库在本地的缓存。
`refs`文件夹中保存的不是实际数据，而是一个引用。实际的数据保存在`objects`中。

每个 branch 信息的 remote 都记录了它对应的远程仓库。

**远程分支**

`<remoteName>/<branchName>`这样的分支是远程分支，它反映了远程仓库（在上次和它通信时）的状态。
remoteName 为远程仓库/远程主机的名字（通常为 origin，也可以是 URL），branchName 为分支名字。

在切换到远程分支时，HEAD 会进入游离状态，以避免直接在这些分支上进行操作（类似 tag）。

更新本地分支不会影响远程分支。类似，通过 fetch 更新远程分支也不会影响本地分支。

**跟踪分支** / **上游分支**

一个本地分支可以与一个远程分支关联，称该远程分支为它的跟踪分支 (tracking branch) 、上游分支 (upstream branch) 或远程分支 (remote branch)。
它由分支的 remote tracking 属性决定（branch.remote 和 merge？），指定了默认推送目的地和拉取后合并的目标。
使用 pull, push 时，可以不指定分支，会默认使用当前分支的跟踪分支来作为远程分支。

有两种设置跟踪分支的方式：

1. `git branch -u <remoteName>/<branchName> [branchName]`：设置某分支的远程跟踪分支。最后的参数默认为 HEAD。
2. `git checkout -b <branchName> <remoteName>/<branchName>`：创建一个跟踪指定远程分支的本地分支。
    比如：git checkout -b some origin/master。

在第一次 push 未设置跟踪分支的分支后，也会为它设置跟踪分支。

> 注意，pull 只会更新当前分支和它跟踪的远程分支。即使有其它分支与该远程分支关联，也不会被更新，需要切换到它后再 pull。
> push 同理。
>
> 在克隆仓库时，对于远程仓库中的每个分支，git 会在本地仓库中创建一个对应的远程分支；然后再创建一个跟踪远程仓库中活动分支的本地分支，默认情况下这个本地分支会被命名为 master（如果没有该分支，本地仓库就是空白的了）。

**pull request**

远程服务器可以配置禁止直接 push 到某分支（比如 master），要求通过 pull requests 来提交更新。

当因为策略被拒绝时，需要：从当前分支新建一个分支，推送到远程仓库；reset 回退当前分支至与远程对应分支一致（当前分支仅用于接收最新更新，不能直接用于提交）；修改、push 新建的分支，然后发起 pull requests。

**fork**

克隆服务端的代码仓库。
fork 完后的仓库就是自己的、可自由提交的远程仓库。可通过 Pull Request 将提交贡献给原仓库，原仓库可以选择接受提交或不接受。

fork 后的仓库可以拉取源仓库的修改、保持最新。




#### **git fetch**

`git fetch`：从远程仓库获取数据，此时所有远程分支会被更新 以反映远程仓库对应分支的最新状态。
即 fetch 做了两件事：从远程仓库下载 本地仓库的**所有远程分支**中缺失的提交；更新远程分支指针。

> fetch 不会影响本地分支和当前文件，其下载的数据不会直接合并到本地分支，但可以手动合并（如 git merge origin/master）。为了方便，git 提供了 pull 同时完成下载和合并。

`git fetch [<remoteName> <refspecs>]`：从远程仓库的指定分支中，获取所有本地不存在的提交，下载到本地的指定分支中。
refspecs 的格式为`[<src>][:<dest>]`，与 push 类似，但是**方向相反**，前者是要拉取的远程仓库分支，后者是要更新的本地分支（可以指定为非远程分支，如`fetch origin foo:bar`）。
如果省略本地分支名，则使用与远程分支同名的本地**远程分支**（如`origin/foo`，不会影响本地分支）；如果省略远程分支名（直接 fetch origin :dest），则在本地创建一个新分支（与 branch 相同）。

> 如果目标远程位置 src 是分支，则会同时更新 src 对应的本地远程分支（即使 dest 不指向远程分支）。
>
> 与 push 相同，指定的本地分支名不存在时，创建；src 和 dest 可以任意指定，不需要对应或同名。
>
> 通常通过互联网（`http://`或`git://`协议）与远程仓库通信。

#### **git pull**

`git pull`：从远程仓库获取数据，更新**所有远程分支**。（并与对应分支合并？）

`git pull [<remoteName> <refspecs>]`：从远程仓库的指定分支中，获取所有本地不存在的提交，下载到本地的指定分支中，**然后将当前 HEAD 与本地的指定分支合并**。
remoteName 是远程仓库名，一般为 origin。
refspecs 的格式为`[<src>][:<dest>]`，与 fetch 相同，前者是要拉取的远程仓库分支，后者是要更新然后合并的本地分支。如：`get pull origin master:gxb_test`。
如果省略本地分支名，则使用与远程分支同名的本地**远程分支**。如：`get pull origin master` 会合并到本地 master 分支。

> pull 就是 fetch 与 merge 的简写，所以参数与 fetch 相同。
>
> `git pull origin foo`等价于`git fetch origin foo; git merge o/foo`。
> `git pull origin bar:bugFix`等价于`git fetch origin bar:bugFix; git merge bugFix`。

`git pull --rebase`：获取远程分支的更新，然后使用 rebase 将本地分支的更新复制到远程分支之后，合并本地与远程的提交。会将当前分支和远程分支均指向最后的提交。

> 如果远程仓库分支的最新提交 与本地基于的远程仓库的提交不同，则无法 push，需要先合并远程的提交。
> 通常为：
>
> 1. `git fetch`获取远程分支的更新。
> 2. `git rebase origin/branch`将自己的修改复制到远程分支之后，解决冲突，生成合并后的提交。
>     也可用`git merge origin/branch`合并远程分支的修改，然后解决冲突，生成合并后的提交。
> 3. `git push`。
>
> 为了方便，`git pull --rebase`就是 fetch 和 rebase 的简写。
> 与 pull + merge 相比，pull + rebase 在没有合并冲突时，不会产生一个代表远程分支更新的提交分叉，更直接。
>
> 推荐使用 fast forward 的方式来 pull：`git pull --ff-only`，它等价于在 merge 后加 --ff-only，解决了 merge 会留下不必要分叉的问题，且在出现冲突时拒绝合并，更安全。
> 可以用`git config pull.ff only`来让 pull 默认使用它。

#### **git push**

`git push [<remoteName> <refspecs>]`：将本地指定分支未推送的更新，上传到远程仓库的指定分支。
refspecs 的格式为`[<src>][:<dest>]`（一般即`<localBranch>[:<remoteBranch>]`），指定要推送的本地分支和目标远程分支。
如果省略远程分支名，则使用与本地分支同名的远程分支；如果省略本地分支名（直接 push origin :dest），则为删除远程分支（等价于 push -d？）。

> *refspec* 是任何 git 能识别的位置，比如：分支、`HEAD~1`。
> 所以可以写`git push HEAD^:master`，它会将 master 到当前分支的上一次提交之间的提交，推送到远程。
>
> 指定的远程分支名不存在时，创建，并需要用 -u 与指定的 remoteBranch 绑定作为上游分支（如果刚开始没绑定，可以用 `git branch --set-upstream-to=[repoName]/[branchName] [localBrach]`）（见下）。
>
> src 和 dest 可以任意指定，不需要对应或同名，比如：可以将本地 A 推送到远程 B，将本地 B~3 推送到远程 A。

会同时更新本地的远程分支。

参数：

- `-u`或`--set-upstream`：将本地当前分支与远程指定分支关联。首次 push 设置后，后续 push 就无需再设置。
- `-f`或`--force`：强制推送到远程仓库，即使本地的远程分支与实际远程分支有差异，也会覆盖远程的提交。
- `--force-with-lease`：仅在远程分支未被他人更新时才强制推送。更安全。
- `-n`或`--dry-run`：模拟推送，显示将要发生什么但不实际执行。

常用：
`git push -u origin src:dst`：推送 src 分支并与远程的 dst 分支绑定。

> 当 push 不指定参数时，推送到哪个分支取决于`push.default`配置（在 .git/config 或 ~/.gitconfig 中），包括5种值：
>
> - upstream：推送到当前分支的*上游分支*（即跟踪分支）。
> - simple：只有上游分支与当前分支同名时，才推送到*上游分支*。更安全。（git 2.0 后的默认值）
> - current：推送到当前分支的同名远程分支。如果远程没有，则创建同名远程分支。
> - matching：推送所有与上游分支同名的本地分支？（git 2.0 前的默认值）
> - nothing：不推送。强制显式指定 refspec。

`git push -d <remoteName> <remoteBranch>`：删除远程的指定分支（但不会删除本地的）。如：`git push --delete origin test`。
`git branch -d -r` 只是删除本地存储的远程分支引用，不会实际删除远程分支。

> `git push`后可以加`-u`参数（是`--up-stream`参数的缩写），表示将当前分支与这条 push 指定的仓库的分支绑定（建立本地分支与某远程分支的关联），指定的仓库的分支将成为当前分支的跟踪分支 (track branch) 或上游分支。
> 当`git push/pull`后什么参数也不加时，**git 会将上游分支作为默认仓库和分支进行推送或拉取**。
>
> 每个分支都可存在一个追踪分支（后续的 -u 会覆盖前面的）。
>
> 通过`git branch --set-upstream-to=[repoName]/[branchName] [localBrach]`也可设置默认远程分支。
> 但如果指定的远程分支不存在，该指令不会创建相应分支，而`git push -u`会。
> 所以`git push -u origin master`表示将本地的 master 分支推送到 master 的上游分支上（要指定 origin 吗？），如果 origin 不存在该分支则新建，并建立上游分支关系；`git branch --set-upstream-to=origin/master master `建立上游分支关系，但如果 origin 不存在对应分支，不会进行创建（所以如果先执行一条`git push origin master`则两者等价）。
>
> 上游分支会保存在`.git/config`中（如`[branch "master"]`下的`remote`和`merge`属性）。通过命令行也可修改：`git config branch.master.remote origin`、`git config branch.master.merge refs/heads/master`。
>
> 不带参数的`git push`默认只会推送当前分支到跟踪分支。这类方式叫 simple。
> 在 git 2.0 之前默认使用 matching 方式，默认会推送所有有对应远程分支的本地分支。

#### **git remote**

`git remote add [name] [url]`：添加远程仓库。
第一个参数 name 是主机名/仓库名（常见如 origin），可用于代替仓库 url：在 git push 时可以用这个名字来指定要提交的仓库，也可以直接指定地址。

如：`git remote add company https://git.company.com/123.git`定义一个名为 company 的仓库，地址是...。
`git push -u company src_branch:dst_branch`就会向该仓库推送分支，等价于`git push https://git.company.com/123.git master `。

> 地址可以使用 HTTP 协议（如`https://github.com/SovietPower/learn_git.git`），也可使用 SSH 协议（如`git@github.com:SovietPower/learn_git.git`）。

**`git remote rm [name]`：删除远程仓库。**

**`git remote rename [oldName] [newName]`：修改仓库名。**

**`git remote set-url [name] [newURL]`：修改仓库对应的地址。**
也可以 rm 再 add，或直接修改`.git/config`配置。

**`git remote show [name]`：查看某个远程仓库的具体信息。**

`git remote`：查看所有远程仓库名。
**`git remote -v`：显示所有远程仓库的具体信息。**

如：

```
$ git remote -v
origin  https://github.com/SovietPower/MIT-6.824-Labs.git (fetch)
origin  https://github.com/SovietPower/MIT-6.824-Labs.git (push)
```



### 子模块

**git submodule**

`git submodule add <远程仓库URL> <本地路径>`：在指定路径创建并添加子模块。

子模块不会随当前仓库提交，其修改需要独立提交。

`vim .gitmodules` 可以查看当前仓库的子模块信息。该文件像 ignore 一样会被提交。

**子模块使用特定分支**

可以在 .gitmodules 里通过 `branch = xx` 为某个子模块指定分支。

`git submodule sync [--recursive]` 同步子模块到与当前 .gitmodules 一致。

**clone 子模块**

- clone 当前仓库时同时 clone 子模块：`git clone --recursive <仓库URL>`
- 初始化子模块：`git submodule init`、`git submodule update`。

**更新子模块**

同步到主仓库记录的特定 commit 或分支：`git submodule update [<子模块路径>]`。不指定子模块路径则更新所有。

可选参数：

- --init：初始化尚未初始化的 submodule。
- --recursive：递归处理嵌套的 submodule。
- --remote：更新到远程分支的最新 commit。

**删除子模块**

```sh
# 移除模块。{MOD_PATH}为模块目录，执行后可发现模块目录被清空
git submodule deinit {MOD_PATH}
# 删除.gitmodules中记录的模块信息（--cached选项清除.git/modules中的缓存）
git rm --cached {MOD_PATH}
# 提交更改到代码库，可观察到'.gitmodules'内容发生变更
git commit -am "Remove a submodule."
```

修改某模块 URL：修改 .gitmodules 中对应模块的 url 属性，再执行`git submodule sync`以将新的 URL 更新到文件 .git/config，然后 commit。







---

### 其它

**git describe**

`git describe [ref]`：返回离指定提交最近的一个标签，并输出标签之后到当前提交之间的提交信息。
ref 是任意引用或 commitID，默认为 HEAD。
输出结果为`<tag>_<numCommits>_g<hash>`：tag 表示离 ref 最近的标签， numCommits 是 ref 与 tag 之间有多少个提交记录， hash 为 ref 引用的提交记录的哈希值的前几位。如果 ref 提交记录上有 tag，则只输出 tag 的名字。

**git symbolic-ref**

[symbolic-ref](https://git-scm.com/docs/git-symbolic-ref) 读写或删除符号引用，比如 HEAD `git symbolic-ref HEAD`。

**git tag**

tag (标签) 是类似 branch 的引用/指针，指向一次提交，但不会像分支一样随提交而移动。
通常用于发布新的 release 版本。
tag 只是一个指向某次提交、可引用的标签，不能在上面进行修改提交。可通过`checkout tag`使 HEAD 指向 tag 所在的提交，此时 HEAD 会进入游离状态，如果要保留之后的修改需要创建新的分支。

`git tag <tagName> [commitID]`：创建一个永久指向指定提交的标签。
如果不指定 commitID，则使用 HEAD。可以使用`-m`附带注释信息。没有注释的 tag 称为轻量级 tag。

`git tag -d <tagName>...`：删除一个或多个 tag（--d 或 --delete 也可）。
`git tag <tagName> <commitID>`：在之前的某次提交位置，创建一个 tag。

`git tag`：列出版本库中的所有 tag。
`git tag -l <pattern>`：列出符合指定模式的 tag。
`git show <tagName>`：查看某个 tag 指向的提交的具体信息。

`git push <name> <tagName>`：推送指定 tag 到指定远程仓库。
该推送会在远程仓库新建一个 release（发布点？）。

`git push <name> --tags`：将本地版本库的所有 tag 推送到指定远程仓库。
`git push <name> -d <tagName>...`：删除指定远程仓库中的某个或某些 tag。





















---

## 其它

**游离状态** / **HEAD detached at refs/heads/... / HEAD is now at ... qq**

`git checkout`可以移动 head 指针，移动目标可以是分支，也可以是某一次的 commit 后的快照。
当指向 branch 时，分支提交后 HEAD 会和 branch 指针一起向后移动；当不指向 branch 时，则会处于 detached 状态。

```
$ cat .git/HEAD
ref: refs/heads/<branch name>  // 指向分支
cad0be9ceb89f474c39360c4de337d4a8194cab0 // 游离状态
```

通过`git checkout <commit id>`切换到过去的某一次提交后，head 将不处于任何分支、进入游离状态。
（`git checkout -d <branch>`删除一个未合并的分支？会删除失败，也会进入游离状态）
（或切换到一个远程的分支？不确定原因）

游离状态使我们能方便地切换到历史版本（只需要指定 commit id）。
但在游离状态的提交，会新建一个匿名分支提交（分支名为新的 commit id），所以该提交信息是无法保存的？如果此时切到别的分支，游离状态做出的提交就看不到了（从临时分支切换到其它分支后，临时分支会消失，它不与任何当前分支绑定）：`you are leaving 1 commit behind, not connected to
any of your branches`。所以不推荐在该状态进行提交，只用于实验。
换句话说，临时性分支上的改动不会影响原分支，实验完后可直接切换原分支。

如果要保留临时分支上（游离状态）的提交，可以新建一个永久分支保存下来：

```
// 如果已切换到其他分支（非游离状态），通过 commit id 创建
git branch <new-branch-name> <commitID>
// 如果还在游离状态，直接创建，然后切换过去。游离状态的更新会绑定到新分支
git checkout -b <new-branch-name>
```

然后回到其它分支，merge 创建的永久分支、提交，然后把创建的分支删除即可。

如果临时分支来自远程分支，那可以用`git push -u origin/branchName branchName`将其与远程分支关联。此时`git pull`应该不会有影响（Already up-to-date.）。

> You are in 'detached HEAD' state. You can look around, make experimental
> changes and commit them, and you can discard any commits you make in this
> state without impacting any branches by switching back to a branch.
>
> If you want to create a new branch to retain commits you create, you may
> do so (now or later) by using -c with the switch command. Example: `git switch -c <new-branch-name>`或`git checkout -b <new-branch-name>`。





---

## 使用问题

**create mode 100644 "1.md"**

因为 Linux 和 Windows 文件系统不一样的缘故，导致了拷贝或新建的文件权限发生了变化，而 git 默认会跟踪它。
配置`git config --add core.filemode false`来忽略。









---

## end

