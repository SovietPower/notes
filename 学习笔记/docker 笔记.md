# docker 笔记

---

[TOC]





---

## 命令

**容器 ID**

容器 ID (container id) 是一个由 Docker 生成的64位十六进制字符串哈希值。使用时可以只用不冲突的前几位。



### 常用命令

```bash
# --- 启动容器
# 交互式 + 伪终端
docker run -it <image> /bin/bash
# 进入 gpu 环境容器
docker run -it --name=<name> --gpus=all --ipc=host <image> bash
# 启动一个长期运行的容器。tail -f /dev/null 让容器后台空转，不退出
docker run -d --name dev --gpus=all --ipc=host -v $(pwd):/workspace <image> \
	tail -f /dev/null

# --- 进入容器
docker exec -it <container> /bin/bash

# --- 修改/创建新容器
docker commit dev dev_trtllm:v1

# --- 管理容器
docker stop dev
docker rm dev

# 导出
docker save -o my-env.tar my-env:v1
# --- 转移到另一台机器 ---
# 导入
docker load -i my-env.tar
# 运行
docker run -it my-env:v1 /bin/bash
```







### 基本

**docker run**

创建并启动容器。

参数：

- --rm：容器退出后自动删除。这样创建的容器无法保存（除了 -v 挂载直接修改 host）。
- --name：为创建的容器指定名字，可代替容器 ID 启动。
- -v / --volume <host_dir>:<container_dir>：挂载卷，将宿主机的目录映射到容器内。
- -p / --publish <host_port>:<container_port>：将容器的端口映射到宿主机。
- -d / --detach：后台运行容器，不占用当前终端，类似 &。
- -e / --env NAME=VAL：设置环境变量。
- --shm-size：设置共享内存。
- --cpus、--memory：限制 cpu 或内存。
- --gpus：指定 gpu。

其它常用参数：

- --ulimit memlock=-1 --ulimit stack=67108864
- --network host：Host 网络模式，让容器不再拥有独立的网络命名空间，直接共用宿主机的网络栈。
  网络性能比 -p 更高（少了一层 NAT 转发），但隔离性差（容器能看到宿主机的所有网络接口）。

> 不配置 -p, --network 时，容器内的端口只能被容器自己访问。

**docker exec**

`docker exec -it <容器ID> /bin/bash`：进入一个正在运行 (up) 的容器。

`docker exec <容器ID> <command>`：不需要进入 shell，在运行中的容器执行单条命令。
如：`docker exec container_1 python /home/a.py`。

**docker commit**

`docker commit <容器ID> <新镜像名>:<标签>`：将一个正在运行或已停止的容器的当前状态保存为新的镜像。

> commit 不会清理缓存，可能导致镜像非常大。可手动在 commit 前清理：
>
> - `yum clean all`
> - `rm -rf ~/.cache/pip`
> - `apt-get clean`
> - `rm -rf /var/lib/apt/lists/*`
>
> 建议先 docker stop 再 commit，以免有正在运行的进程或内存数据未落盘，导致文件丢失或不一致。





### 容器管理

`docker ps`：查看运行中的容器。
参数：

- -a：包括已停止的所有容器。
- -s：显示各个容器的大小。

> 已停止的容器仍会占磁盘。
> `docker container prune`清理所有已停止的容器。

`docker inspect/start/restart/stop/kill/rm <容器id>`：查看/启动/重启/停止(SIGTERM)/强制停止(SIGKILL)/删除容器。

> 通过 docker run 启动的容器是主进程，在 exit / ctrl d 退出容器时会默认 stop 变为 exited。
> 通过 docker exec 启动的容器仅是一个子进程，在退出容器时不会 stop。
>
> 已退出的容器，需要 start 再 exec 进入。再在 exec 中退出不会结束容器。

`docker attach <容器id>`：连接到主进程终端。

> 注意，attach 不建议通过 Ctrl D 退出，会导致主进程退出。
> 应该 Ctrl P + Ctrl Q（逃逸序列），会从 attach 状态 detach，不影响容器在后台运行。
> 可通过`--detach-keys`定义逃逸序列。

`docker logs -f <容器id>`：查看容器日志（输出）。

> `docker logs --tail all <容器 ID> | less`：分页查看所有日志。



### 镜像管理

`docker images`：列出本地镜像。

`docker pull nvcr.io/nvidia/tensorrt-llm/release:1.3.0rc6`：拉取镜像。 

`docker rmi <镜像ID>`：删除镜像 (必须先删除使用该镜像的容器)。





### 导入导出

`docker save -o my-env.tar my-env:v1`：导出容器

`docker load -i my-env.tar`：导入容器。









---

## b





---

## end







