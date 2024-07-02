# Folly 编译
Tags: 实习 2022.7 华为

------------
[TOC]

------------
> https://github.com/facebook/folly

------------
## 编译
```
mkdir build_ && cd build_
cmake .. -Wno-dev
make install
```

安装了的依赖：
```
boost (scon)
DoubleConversion (setuptools, python38, libffi-devel)
gflags
glog
libevent
openSSL (perl-IPC-Cmd, perl-Pod-Html)
fmt
```

还会提示有没找到的，但已经可以 build install。

**Cmake error: Could NOT find Boost (missing: Boost_INCLUDE_DIR)**<br>
**安装 boost**<br>
按照这里重新安装：https://www.boost.org/doc/libs/1_78_0/more/getting_started/unix-variants.html#link-your-program-to-a-boost-library

```
# 下载解压
tar --bzip2 -xf boost_1_77_0.tar.bz2
# 安装
./bootstrap.sh
./b2 install
```

**New Boost version may have incorrect or missing dependencies and imported targets**<br>
boost 的版本比 cmake 新，可忽略。

**Could NOT find DoubleConversion (missing: DOUBLE_CONVERSION_LIBRARY DOUBLE_CONVERSION_INCLUDE_DIR)**<br>
**安装 DoubleConversion**<br>
在 https://github.com/google/double-conversion 下载解压，`scons install`。<br>
官方推荐的`scons install`好像不行。还是要`cmake -DBUILD_SHARED_LIBS=ON .`、`make`、`make install`。

**make: scons: Command not found**<br>
**安装 scons**<br>
官方推荐直接用 pip 安装，但是连不了。<br>
在 https://scons.org/pages/download.html 下载解压，目录下运行`python3 setup.py install`。<br>

**distutils.errors.DistutilsOptionError: Unsupported distribution option section: [options.data_files]**<br>
好像是因为`setuptools`版本太旧。官方还是推荐直接用 pip 安装。<br>
在 https://pypi.org/project/setuptools/#files 下载解压，目录外运行`python3 -m pip install setuptools-63.2.0.tar.gz`。

**SyntaxError: future feature annotations is not defined**<br>
Python 版本低，要至少 3.7。<br>
在 https://www.python.org/downloads/source/ 下载解压，目录中`./configure`、`make`、`make install`。

然后`setuptools`还是安装不了，网络问题。<br>
但上面安装 Python 的时候好像也更新了 pip, setuptools（虽然版本依然很低），`python3 setup.py`换成了下面的报错。

**ModuleNotFoundError: No module named '\_ctypes'**<br>
```
# 安装centos缺少的库
yum install libffi-devel
# 重新安装python
yum install python38
```

**Could NOT find gflags (missing: LIBGFLAGS_LIBRARY LIBGFLAGS_INCLUDE_DIR)**<br>
在 https://github.com/gflags/gflags 下载解压，`mkdir build && cd build`、`cmake ..`、`make`、`make install`。

进行`cmake -DBUILD_SHARED_LIBS=ON ..`，然后重新`make`、`make install`，可生成`.so`动态链接库。

**Could NOT find Glog (missing: GLOG_LIBRARY GLOG_INCLUDE_DIR)**<br>
按照 https://github.com/google/glog#cmake 下载安装。

同上，也要`cmake -DBUILD_SHARED_LIBS=ON ... .`重新安装，得到`.so`。

**安装glog时 /usr/bin/ld: final link failed: Nonrepresentable section on output
collect2: error: ld returned 1 exit status**<br>
编译时需要加`-fPIC`。如果是`cmake`，就在`CMakeList.txt`中加`add_compile_options(-fPIC)`。<br>
注意提示的都是`gflags_xxx.cc.o`的问题，不是改`glog`的`CMakeList.txt`，要改`gflags`的然后重新`make`。

**Could NOT find libevent.**<br>
**安装libevent**<br>
https://github.com/libevent/libevent#cmake-unix

**Could NOT find OpenSSL, try to set the path to OpenSSL root folder in the system variable OPENSSL_ROOT_DIR (missing: OPENSSL_CRYPTO_LIBRARY OPENSSL_INCLUDE_DIR)**<br>
按照 https://github.com/openssl/openssl/blob/master/INSTALL.md#building-openssl 进行。<br>
可能需要先安装：`yum -y install perl-IPC-Cmd`、`yum -y install perl-Pod-Html`。

**Target "follybenchmark" links to target "fmt::fmt" but the target was not found.  Perhaps a find_package() call is missing for an IMPORTED target, or an ALIAS target is missing?**<br>
**安装fmt**<br>
https://fmt.dev/latest/usage.html ，同样`cmake ..`、`make`、`make install`。

**error while loading shared libraries: libglog.so.1: cannot open shared object file: No such file or directory**<br>
**error while loading shared libraries: libgflags.so.2.2: cannot open shared object file: No such file or directory**<br>
两个安装的时候，分别装到了`/usr/local/lib64`和`/usr/local/lib`。<br>
要在配置文件里添加这两个路径到动态库搜索路径：
```
# ~/.bashrc
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib64:/usr/local/lib
```

**测试**<br>
```cpp
#include <folly/concurrency/ConcurrentHashMap.h>
#include <string>
#include <iostream>

class Student
{
public:
    Student(std::string name, int id, std::string email)
        : m_name(name), m_id(id), m_email(email)
    {}

    void printSelf() const
    {
        std::cout << "name: " << m_name << " "
            << "id: " << m_id << " "
            << "email: " << m_email << std::endl;
    }

private:
    std::string m_name;
    int m_id;
    std::string m_email;
};

int main()
{
	folly::ConcurrentHashMap<std::string, Student> students;
    students.insert("Tom", Student("Tom", 1, "tom@gmail.com"));
    students.insert("Lilly", Student("Lilly", 2, "lilly@gmail.com"));

    for (const auto& st : students)
        st.second.printSelf();

    return 0;
}
```

```
[root@ds-pallasdb-ecs-guoxiaobo Temp]# g++ a.cpp -o a -lfolly -lglog -lgflags -lpthread -ldl -ldouble-conversion -lfmt
[root@ds-pallasdb-ecs-guoxiaobo Temp]# ./a
name: Tom id: 1 email: tom@gmail.com
name: Lilly id: 2 email: lilly@gmail.com
```


```
-- Up-to-date: /usr/local/include/folly/io/async/test/UndelayedDestruction.h
-- Up-to-date: /usr/local/include/folly/io/async/test/Util.h
-- Up-to-date: /usr/local/include/folly/synchronization/test/Semaphore.h
-- Up-to-date: /usr/local/include/folly/test/DeterministicSchedule.h
-- Up-to-date: /usr/local/include/folly/test/JsonTestUtil.h
-- Up-to-date: /usr/local/include/folly/test/TestUtils.h
-- Installing: /usr/local/include/folly/folly-config.h
-- Installing: /usr/local/lib/cmake/folly/folly-config.cmake
-- Old export file "/usr/local/lib/cmake/folly/folly-targets.cmake" will be replaced.  Removing files [/usr/local/lib/cmake/folly/folly-targets-noconfig.cmake].
-- Installing: /usr/local/lib/cmake/folly/folly-targets.cmake
-- Installing: /usr/local/lib/cmake/folly/folly-targets-noconfig.cmake
-- Installing: /usr/local/lib/pkgconfig/libfolly.pc
-- Installing: /usr/local/lib/libfollybenchmark.a
```





