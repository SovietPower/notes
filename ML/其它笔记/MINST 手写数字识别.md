# MINST 手写数字识别
-----
[TOC]

-----
## 数据处理
数据即 MINST 数据集，使用默认的划分：60000 个训练数据、10000 个测试数据。

**规范化**
导入时利用官方提供的 0.1307, 0.3081 可直接对数据进行零均值规范化：
```python
trainDataSet = torchvision.datasets.MNIST('../data/',
	train = True,
	download = False,
	transform = torchvision.transforms.Compose([
		torchvision.transforms.ToTensor(),
		torchvision.transforms.Normalize(
			(0.1307,), (0.3081,)),
	]))

testDataSet = torchvision.datasets.MNIST('../data/',
	train = False,
	download = False,
	transform = torchvision.transforms.Compose([
		torchvision.transforms.ToTensor(),
		torchvision.transforms.Normalize(
			(0.1307,), (0.3081,)),
	]))
```

<!-- ![](规范化1.jpg) -->
![](规范化2.png)
![](规范化3.png)

**去歪斜**
`deskew()`通过使用其二阶矩对数字进行去歪斜：通过两个中心矩的比值 (mu11/mu02) 计算偏斜的度量，将偏斜用于计算仿射变换，从而消除数字的偏斜。

```python
def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        return img.copy()
    skew = m['mu11'] / m['mu02']
    M = np.float32([[1, skew, -0.5 * SIZE_IMAGE * skew], [0, 1, 0]])
    img = cv2.warpAffine(img, M, (SIZE_IMAGE, SIZE_IMAGE), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)

    return img
```
下面两行展示了处理前后的图片：

![](20221221131718.png)

在 KNN 中使用该预处理，正确率从 97.05% 提高到了 97.99%。

**使用高级描述符**
上述情况下使用的是原始像素值作为特征描述符。一种常见的方法是使用更高级的描述符，比如 定向梯度直方图 (Histogram of Oriented Gradients, HOG) 作为图像特征用以提高算法准确率。
特征描述符是图像的一种表示，它通过提取描述基本特征（如形状、颜色或纹理等）的有用信息来简化图像。通常，特征描述符将图像转换为长度为 n 的特征向量，HOG 是一种用于计算机视觉的流行特征描述符。

通过 cv2 定义 HOG 描述符并转换数据：
```python
def get_hog(imageSize):
	hog = cv2.HOGDescriptor((imageSize, imageSize), (8, 8), (4, 4), (8, 8), 9, 1, -1, 0, 0.2, 1, 64, True)
	return hog

hog = get_hog(imageSize)
for img in trainData:
	hog_descriptors.append(hog.compute(img)) # hog.compute 会将28*28像素输入转为1*324
hog_descriptors = np.squeeze(hog_descriptors) # 60000*324

trainData = hog_descriptors
knn.fit(trainData, trainLabel)
```

在 KNN 中使用该预处理，正确率从 97.05% 提高到了 97.92%。

与`deskew()`一起使用，KNN 正确率可提高到 98.36%。

（CNN 中没用这两个处理，数据类型不太对没解决）

-----
## CNN
### LeNet5
> http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf

早期的卷积神经网络，包括 卷积-池化(subsample)-卷积-池化-全连接-全连接-全连接 7层。
最初用的激活函数是 sigmoid，使用平均池化，现在一般是用 relu 和最大池化。

**实现**
```python
class LeNet5(nn.Module):
	def __init__(self):
		super(LeNet5, self).__init__()
		self.net = nn.Sequential(
			nn.Conv2d(1, 6, 5, padding=2), # 1*28*28 -> 6*28*28
			nn.MaxPool2d(2), # 6*14*14
			nn.ReLU(),

			nn.Conv2d(6, 16, 5), # 16*10*10
			nn.MaxPool2d(2), # 16*5*5
			nn.ReLU(),

			nn.Conv2d(16, 120, 5), # 120*1*1
			nn.ReLU(),

			nn.Flatten(),
			nn.Linear(120, 84),
			nn.ReLU(),
			nn.Linear(84, 10),
		)
	def forward(self, x):
		return self.net(x)
```

**测试**

![](LeNet5_new.png)

```
train: time used: 0m 26s
Test after epoch 1: Loss: 0.0598, Accuracy: 9817/10000 (98.2)
train: time used: 0m 25s
Test after epoch 2: Loss: 0.0430, Accuracy: 9856/10000 (98.6)
train: time used: 0m 25s
Test after epoch 3: Loss: 0.0356, Accuracy: 9886/10000 (98.9)
```

-----

### ResNet

残差神经网络，会将前面某一层的输出直接跳过多层输入到后面的某个数据层，即后面特征层的内容会有一部分由前面的某一层线性贡献，以缓解深度增加带来的梯度消失问题。

主要有下面两种残差结构(building block)，即一般的跨层连接只跨2~3层。
左边用于较浅的网络，右边可用于很深的网络，使用1\*1的卷积降维和升维以降低参数量（称为 bottleneck design）。

![](20221207231251.png)

使用了 Batch Normalization，可缓解梯度消失问题，加快收敛，一定程度防止过拟合。
> 随着网络的深度增加，每层特征值分布会逐渐的向激活函数的输出区间的上下两端（激活函数饱和区间）靠近，这样继续下去就会导致梯度消失。BN就是通过方法将该层特征值分布重新拉回标准正态分布，特征值将落在激活函数对于输入较为敏感的区间，输入的小变化可导致损失函数较大的变化，使得梯度变大，避免梯度消失，同时也可加快收敛。

结构：

![](20221207233634.png)

**实现**
同下面的 VGG，输入大小会不匹配，所以用了一个卷积层填充：`self.conv0 = nn.Conv2d(1, 3, 1, 1, 98)`。
代码见文件。

**测试**
ResNet18 比 VGG 和 GoogLeNet 快一点点。

![](ResNet.png)

```
Test after epoch 1: Loss: 0.0395, Accuracy: 9866/10000 (98.7)
Test after epoch 2: Loss: 0.0253, Accuracy: 9912/10000 (99.1)
Test after epoch 3: Loss: 0.0252, Accuracy: 9916/10000 (99.2)
```

-----

### VGG16

VGG16为13个3\*3卷积层，5个最大池化层，3个全连接层。
VGG19则多了3个3\*3卷积层。

![](20221207224943.png)

**实现**
VGG 的输入是$3*224*224$的，即RGB 3通道的$224*244$像素图。
但 MINST 的数据是$1*28*28$的，因为不方便修改，所以改了网络来保证输入大小合适：将第一层`nn.Conv2d(3, 64, kernel_size=3, padding=1)`改为`nn.Conv2d(1, 64, kernel_size=3, padding=1)`，然后删除了前三部分的池化。
（但好像并不对）

```python
class VGG16(nn.Module):
	def __init__(self, num_classes=10):
		super(VGG16,self).__init__()
		self.net = nn.Sequential(
			nn.Conv2d(1, 64, kernel_size=3, padding=1), # 64*28*28
			# nn.Conv2d(3, 64, kernel_size=3, padding=1), # 64*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(64, 64, kernel_size=3, padding=1), # 64*28*28
			nn.ReLU(inplace=True),
			# nn.MaxPool2d(2, 2),

			nn.Conv2d(64, 128, kernel_size=3, padding=1), # 128*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(128,  128,  kernel_size=3,  padding=1), # 128*28*28
			nn.ReLU(inplace=True),
			# nn.MaxPool2d(2, 2),

			nn.Conv2d(128, 256, kernel_size=3, padding=1), # 256*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(256, 256, kernel_size=3, padding=1), # 256*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(256, 256, kernel_size=3, padding=1), # 256*28*28
			nn.ReLU(inplace=True),
			# nn.MaxPool2d(2, 2),

			nn.Conv2d(256, 512, kernel_size=3, padding=1), # 512*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(512, 512, kernel_size=3, padding=1), # 512*28*28
			nn.ReLU(inplace=True),
			nn.Conv2d(512, 512, kernel_size=3, padding=1), # 512*28*28
			nn.ReLU(inplace=True),
			nn.MaxPool2d(2, 2), # 512*14*14

			nn.Conv2d(512, 512, kernel_size=3, padding=1), # 512*14*14
			nn.ReLU(inplace=True),
			nn.Conv2d(512, 512, kernel_size=3, padding=1), # 512*14*14
			nn.ReLU(inplace=True),
			nn.Conv2d(512, 512, kernel_size=3, padding=1), # 512*14*14
			nn.ReLU(inplace=True),
			nn.MaxPool2d(2, 2), # 512*7*7

			nn.Flatten(),
			nn.Linear(512*7*7, 4096),
			nn.ReLU(inplace=True),
			nn.Dropout(),

			nn.Linear(4096, 4096),
			nn.ReLU(True),
			nn.Dropout(),

			nn.Linear(4096, num_classes)
		)
	def forward(self, x):
		return self.net(x)

```

**测试**
未测试。
卷积层和参数量太多但电脑性能不行，batch size 调到4也很慢，训练一次可能至少要1小时。
尝试过用 GPU，会出现 CUDA out of memory 的问题，但 free 的部分(>1G)是非常够分配的，pytorch 不分配，也没解决。
`CUDA out of memory. Tried to allocate 20.00 MiB (GPU 0; 4.00 GiB total capacity; 680.81 MiB already allocated; 2.01 GiB free; 698.00 MiB reserved in total by PyTorch)`

-----
### GoogLeNet

使用 inception 模块，将一个输入分成多个分支进行不同的处理，然后再将不同的处理结果进行拼接，组成最后的多尺度融合输出结构。
分支中使用了1\*1的卷积层来降低输入维度，减少参数，以减少大核卷积的代价。
inception 可以更高效的利用计算资源，在相同的计算量下提取到更多的特征，但不会使网络过深，带来梯度消失等问题。

此外增加了两个辅助分类器，用来辅助训练。但实际测试时只使用主分类器。

**实现**
GoogLeNet 的输入也是$3*224*224$的，所以将下面 卷积-池化-卷积-池化 改成了3个卷积层，以使第5层的输入符合$192*28*28$的大小。

![](20221207210226.png)

训练时与其它模型略有不同：损失的计算方式为$loss_{main}+0.3*(loss_{1}+loss_{2})$，使用该损失更新网络。

代码见文件。
（但改的好像也不对）

**测试**
未测试。
同VGG，参数量太多，跑了一段时间也没完成一次训练。

-----

### 其它

最早参考的两种非常简单的网络，但在本问题中正确率还是很高。

```python
class CNN0(nn.Module):
	def __init__(self):
		super(CNN0, self).__init__()
		self.net = nn.Sequential(
			# 1.
			# nn.Conv2d(1, 10, 5), # 1*28*28 -> 10*24*24
			# nn.MaxPool2d(2), # 10*12*12
			# nn.ReLU(),

			# nn.Conv2d(10, 20, 5), # 20*8*8
			# nn.Dropout2d(),
			# nn.MaxPool2d(2), # 20*4*4
			# nn.ReLU(),

			# nn.Flatten(),
			# nn.Linear(320, 50),
			# nn.ReLU(),
			# nn.Dropout(),
			# nn.Linear(50, 10),

			# 2.
			nn.Conv2d(1, 28, 3, 1, 1), # 1*28*28 -> 28*28*28
			nn.Conv2d(28, 64, 3, 1, 1), # 64*28*28
			nn.MaxPool2d(2), # 64*14*14

			nn.Conv2d(64, 64, 3, 1, 1), # 64*14*14
			nn.Conv2d(64, 64, 3, 1, 1), # 64*14*14
			nn.MaxPool2d(2), # 64*7*7

			nn.Flatten(),
			nn.Linear(3136, 10),
		)
	def forward(self, x):
		return self.net(x)
```

**测试**
多次使用卷积层、扩展到更高的维度，效果一般会更好，也会更慢。

![](CNN0.png)

```
train: time used: 1m 55s
Test after epoch 1: Loss: 0.0691, Accuracy: 9787/10000 (97.9)
train: time used: 1m 56s
Test after epoch 2: Loss: 0.0492, Accuracy: 9840/10000 (98.4)
train: time used: 1m 56s
Test after epoch 3: Loss: 0.0503, Accuracy: 9825/10000 (98.2)
```

-----
## KNN

对每个输入，找到与它最近的 k 个样本点，然后选择出现最多的标签（或其它投票方式）。

**实现**
对每次询问，找最近的 k 个距离，可以维护 k 个最小值，或者全计算然后 sort。
因为是求$x^2 + y^2 - 2xy$，所以也可以用矩阵批量算所有测试数据的该式的值，效率要远高于每次单独计算。

```python
def KNN3(trainData, trainLabel, testData, testLabel, K):
	'''
	使用矩阵运算一次性计算测试结果。
	$O(nm\log n)$
	'''
	startTime = time.time()
	m = testData.size(0)
	n = trainData.size(0)

	# 计算 x^2, y^2 并扩展成相同大小相加
	xx = (testData**2).sum(dim=1, keepdim=True).expand(m, n)
	yy = (trainData**2).sum(dim=1, keepdim=True).expand(n, m).transpose(0, 1)
	# 计算 x^2 + y^2 - 2xy
	distance = xx + yy - 2*testData.matmul(trainData.transpose(0, 1))
	# 对每行进行排序
	idsArray = distance.argsort(dim=-1)

	i, correct = 0, 0
	for ids in idsArray:
		correct += np.bincount(np.array([trainLabel[id] for id in ids[:K]])).argmax() == testLabel[i]

		i += 1

	total = len(testData)
	print('Accuracy: %d/%d (%.2f%%)' % (correct, total, 100.*correct/total))

	timeUsed = time.time() - startTime
	print('time used: %.0fm %.0fs' % (timeUsed//60, timeUsed%60))

	return correct, total, timeUsed
```

sklearn 也提供了 K 近邻的 API：

```python
def KNNstd(trainDataSet, testDataSet, K):
	'''
	使用 sklearn.neighbors.KNeighborsClassifier。
	'''
	startTime = time.time()

	# 需要用 numpy.array 作为输入
	trainData = trainDataSet.data.numpy()
	trainLabel = trainDataSet.targets.numpy()

	testData = testDataSet.data.numpy()
	testLabel = testDataSet.targets.numpy()

	# 将原来的三维60000*28*28输入 转为二维60000*784
	trainData = np.reshape(trainData, (60000, 784))
	testData = np.reshape(testData, (10000, 784))

	knn = KNeighborsClassifier(n_neighbors=K)
	knn.fit(trainData, trainLabel)
	acc = knn.score(testData, testLabel)
	print('Accuracy: (%.2f%%)' % (100.*acc))

	timeUsed = time.time() - startTime
	print('time used: %.0fm %.0fs' % (timeUsed//60, timeUsed%60))

```

**测试**
**K 的取值对结果的影响：**
```
K: 1
Accuracy: (96.91%)
time used: 0m 15s
K: 2
Accuracy: (96.27%)
time used: 0m 16s
K: 3
Accuracy: (97.05%)
time used: 0m 18s
K: 4
Accuracy: (96.82%)
time used: 0m 19s
K: 5
Accuracy: (96.88%)
time used: 0m 19s
K: 6
Accuracy: (96.77%)
time used: 0m 19s
K: 7
Accuracy: (96.94%)
time used: 0m 19s
K: 10
Accuracy: (96.65%)
time used: 0m 19s
```

可见 K 较小时正确率更高，不过直接 K=1 不会比其它值低多少。

**K 取 3 时：**
使用 3000 个样本，测试 1000 个数据结果：
```
# KNN3
Accuracy: 890/1000 (89.00%)
time used: 0m 0s
```

使用完整数据集（60000 个样本、10000 个测试数据）：
```
# KNN3
Accuracy: 9705/10000 (97.05%)
time used: 0m 26s

# KNNstd (sklearn.neighbors.KNeighborsClassifier)
Accuracy: (97.05%)
time used: 0m 18s
```

可见两个算法完全一致，但 sklearn 的实现方式和效率要好很多。

使用`deskew()`和 HOG 描述符预处理数据后的结果：
```
# KNNstd (sklearn.neighbors.KNeighborsClassifier)
Accuracy: (98.36%)
time used: 0m 20s
```

-----
## SVM

<!-- **核函数** -->

<!-- > 无论是在高维空间的线性支持向量机求解过程中，还是在最终得到的线性判别函数中，除了类别标签以外，我们并没有用到原始空间中的样本$x(i)$映射到高维空间中的像$y(i)$，我们用到的只是高维空间中两个向量的内积。换句话说，如果我们能够不经过原始特征空间到高维特征空间的映射过程，就能够计算出两个低维空间的向量在高维空间中的内积，就可以实现非线性支持向量机求解的目标。
>
> 核函数是这样一类函数，它的输入是低维空间中的两个向量，输出是这两个向量经过同一个映射到另一个空间以后的内积。换句话说，使用核函数，可以在低维空间中直接计算某一些高维空间中的向量内积，而无需进行向量从低维空间到高维空间的映射变换。
>
> 使用核函数以后，我们就可以假定在低维原始特征空间中的一个非线性分类问题，映射到某个高维空间变成了一个线性可分的问题(虽然我们并不知道究竟是怎么映射的)。然后我们就可以进行线性支持向量机的求解了。求解过程中需要用到样本集中样本之间的内积，就用核函数来计算，最后得到的高维空间中的线性判别函数，也用同样的核函数代入，就得到了低维空间中的判别函数。
>
> 最后一个问题就是：如何选择核函数？ 遗憾的是，无论是核函数的形式还是参数，都没有确定的选择方法，只能依靠经验来试。这里面深层次的问题是，我们并不知道一个低维空间中的非线性分类问题，映射到多高的维度、如何映射才能变成一个线性可分的问题。甚至是不是永远都无法变成一个线性可分的问题。所以，核函数方法只是提供给我们一种可能，如果可以通过广义线性化来解决某一个非线性分类问题，那么这个问题的求解过程中，可以通过与所需的映射相一致的某个核函数方便地计算在高维空间中的向量内积，从而方便地得出分类器训练结果。如果我们试来试去都没有找到支持向量机的解，我们也无法确定是没找到合适的核函数，还是该问题本身就没有线性分类器的解。
> ![](20221221155002.png) -->

**优点**
有严格的数学理论支持；可处理高维数据；小数量样本数据集表现好。

**缺点**
难监控和可视化；需要选择合适的参数和核；样本量和支持向量的个数对效率的影响很大（不过好像有复杂度更好的算法和分布式应用）。

**实现**
直接用的 `sklearn.svm.SVC()`、`sklearn.svm.LinearSVC()` 和 `cv2.ml.SVM_create()`。

SVM 中常用的参数（以 sklearn 为例）：
```
C：错误项的惩罚系数，默认为1.0。c越大，对分错样本的惩罚程度越大，在训练样本中准确率越高，但泛化能力越低。
kernel：核函数，默认为'rbf'（径像核函数/高斯核）。其它可选值：'linear'（线性核函数）、'poly'（多项式核函数）、'sigmod'（sigmod核函数）、'precomputed'。
gamma：'rbf'、'poly'和'sigmoid'的核系数。默认为'auto'（样本特征数的倒数）或'scale'（1/(n_features*X.var())）。
tol：停止训练的误差精度，默认为0.001。
max_iter：最大迭代次数，默认为-1（不受限制）（LinearSVC中是1000）。
```

C 和 γ 的取值依赖于数据集，所以需枚举找到合适的参数值：

![](SVM.png)

由图知，γ 较小、C 值较大时，准确率更高（图中橙绿红线基本重合）。
所以可取 C=10, γ=0.1。

**测试**
```
# 数据经过预处理
cv2.ml.SVM_create() with C=10, gamma=0.10：
Accuracy: 99.25%
time used: 0m 19s

# 修改C和γ后跑不出来，所以使用默认值 C=1，gamma='scale'
sklearn.svm.SVC()：
Accuracy: (97.92%)
time used: 4m 39s

sklearn.svm.LinearSVC(dual=False)：
Accuracy: (86.10%)
time used: 1m 59s
```

该问题中 SVM 可达到 99.25% 的正确率。

-----
<br>
<br>
<br>


## 总结

|模型|正确率|大概用时|
|-|-|-|
|LeNet5|$98.9\%$|1m 15s|
|ResNet18|$99.2\%$|(比较长)|
|VGG|-|-|
|GoogLeNet|-|-|
|其它CNN|$98.4\%$|5m 47s|
|KNN|$98.36\%$|0m 20s|
|SVM|$99.25\%$|0m 19s|

**正确率**
正确率都很高，复杂的神经网络和 SVM 正确率最高。

问题比较简单，结果也差距不大，应该很难说某算法有明显优势。

**效率**
SVM 和 KNN 模型相对简单，没有复杂训练过程，所以效率远比神经网络高。

**实现难度/模型复杂度**
SVM 和 KNN 有实现好的 API，只需要调整参数，但参数的影响很大、不确定性强。
神经网络需要定义每一层，扩展性更强，但是要自己写；计算量和正确率和网络层数有关，可以根据需要调整？还可以比较容易地直接应用到其它问题？

-----
所有代码见文件。

**测试方式：**
进入`DigitalRecognition\CNN/KNN/SVM`子目录下，
CNN：对于除`GoogLeNet`外的模型，直接修改`main.py`中的`model`字符串值，然后运行`main.py`；对于`GoogLeNet`，直接运行`GoogLeNet.py`（因为测试方式略有不同）。
KNN, SVM：运行文件即可。

使用的第三方库：`cv2, numpy, torch, sklearn`。

