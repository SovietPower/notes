# Matplotlib

-----
[TOC]

-----
## 笔记
> 文档：https://matplotlib.org/stable
> 
> https://www.runoob.com/matplotlib/matplotlib-pyplot.html

### 概念
**axes**
轴域，是一个有限制的绘画区域，基本与`subplot`等同。

**subplot**
`subplot`是对创建`axes`功能的包装，非常方便，但自由度也更低。

**figure**
一个画布，或者一整张图，可以包含一个或多个`axes`。

### 基本命令
**import matplotlib.pyplot as plt**

**plt.show()**
调用后，会关闭本来的`figure`（所以保存`figure`等需在`show`之前进行）。

**plt.xlim(), ylim()**
`plt.xlim(left, right)`
设置 x 轴的范围。
用`xlim(left=..)`或`xlim(right=..)`设置某一个范围。
`l, r = xlim()`  返回当前的范围。

例：
`plt.xlim（X.min()* 1.1, X.max()* 1.1`
`plt.ylim（Y.min()* 1.1, Y.max()* 1.1）`

**plt.xticks(), yticks()**
> https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.xticks.html

`plt.xticks(_ticks=None_, _labels=None_, _**kwargs_)`
更新或返回 x/y 轴上的标签及位置。

例：
`plt.xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])` 设置5个要显示的标签位置（显示为数字）。
`plt.xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi], [r'$-\pi$', r'$-\pi/2$', r'$0$', r'$+\pi/2$', r'$+\pi$'])` 设置5个标签的位置及显示内容（使用 `r'..$..$'`+LaTeX 表示）。

**plt.xlabel(), ylabel()**
`plt.xlabel(text, loc='center')`
设置坐标轴整体标签。

**plt.figure()**
> https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.figure.html

创建新图像，或激活一个已有图像。（不太清楚用处）
可设置图像的基本参数，如图片标识符 num，大小 figsize，分辨率 dpi，背景色 facecolor，是否清除原图像（如果存在）clear 等。


### 其它命令
**plt.subplot()**
`plt.subplot(n, m, id)`
将整个绘图区域分成 n 行和 m 列，并切换到第 id 个区域（之后`plt.func`的更新，如`plt.title()`，都更新该区域）。
`plt.show()`时绘画所有区域。
`plt.suptitle()`给整个图加标题。

当`n,m,id`都只有一位时，可使用一个三位数表示。
例：
```
plt.subplot(234) # 分成2*3格，切换到区域4
plt.subplot(231)
plt.show() # 会显示区域1,4（其它区域没有，不显示）
```

**plt.subplots()**
> https://www.runoob.com/matplotlib/matplotlib-subplots.html

`plt.subplots(nrows=1, ncols=1, *, sharex=False, sharey=False, squeeze=True)`
返回 `(Figure fig, axes.Axes[] axs)`。
`fig` 控制整个图，`axs`中的每个`ax`控制各自的绘画内容。

例：
```python
x = np.linspace(0, 2*np.pi, 400)  
y = np.sin(x**2)
# 两个子图
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)  
ax1.plot(x, y)  
ax1.set_title('Sharing Y axis')  
ax2.scatter(x, y)
f.show()

# 四个子图
fig, axs = plt.subplots(2, 2, subplot_kw=dict(projection="polar"))  
axs[0, 0].plot(x, y)  
axs[1, 1].scatter(x, y)
fig.show()
```
**plt.legend()**
> https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.legend.html

`plt.legend(loc="best", ...)`
添加图例。图例内容为每条曲线的 label。

例：
```
plt.plot(X, C, color="blue", linewidth=2.5, linestyle="-", label="cosine")
plt.plot(X, S, color="red", linewidth=2.5, linestyle="-", label="sine")
plt.legend(loc='upper left', frameon=False)
```

**plt.savefig()**
> https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.savefig.html

`plt.savefig(fname, format=None, .∝.)`
保存当前图片。
`fname` 为要保存的文件名（带路径，不带扩展名），扩展名由`format`指定，如`'png', 'pdf', 'svg'`，默认为`png`。

例：
`plt.savefig(os.path.join(os.path.dirname(__file__), "figures/fig1"))`





