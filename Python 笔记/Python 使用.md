# Python 使用

---

[TOC]



---





---

## 安装

**从源码安装 3.10**

```sh
# 安装依赖工具
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel make
# 下载 Python 3.10 源码包
wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
tar xzf Python-3.10.0.tgz
cd Python-3.10.0
# 编译安装
./configure --enable-optimizations
make -j $(nproc)        # 使用多核加速编译
sudo make altinstall    # 使用 altinstall 避免覆盖系统默认 Python
# 验证（使用 python3.10 即可调用）
python3.10 --version
```













---

## end





