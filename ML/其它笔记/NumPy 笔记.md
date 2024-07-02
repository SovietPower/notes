# NumPy 笔记

-----
[TOC]

-----
## 笔记
> 文档：https://numpy.org/doc/stable/reference/index.html#reference

**axis 轴，transpose**
> https://zhuanlan.zhihu.com/p/30960190

strides 指同一轴上，每次跳过索引的数量。
对二维矩阵，axis=0 即行，axis=1 即列。

**linspace()**
`np.linspace(start, end, num=50, endpoint=true)`
生成 $[start, end]$ 内的等差数列形成的一维数组，共`num`个，公差为`(end-start)/num`。
元素类型为 float64。
`endpoint=false`时，结果不包括末端点。

**arange()**
`np.arange(start=0, end, step=1)`
生成 $[start, end)$ 内的等差数列形成的一维数组，公差为`step`。
如果结果为整数，元素类型为 int，否则为 float64。

例：
`plt.plot(np.arange(len(A)), A, label="ada")` 绘制序列A（横坐标为$[0,len(A))$）。










