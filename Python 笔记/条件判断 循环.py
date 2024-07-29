# -*- coding: utf-8 -*-

'条件判断'
# 三目运算符：exp1 if condition else exp2
a=1
b=2
mx = a if a>b else b
print(mx)
print("a大于b") if a>b else print("a小于b")


# if elif else
x = 3

if not x<3: print("opt 1") # 若只有一行，可不换行

if x>=3:
	print("opt 1")
	print("opt 2...")

if x==4:
	print("opt 1")
elif x==5: # 不是else if
	print("opt 2")
else:
	print("opt 3")


x = [1]
if x: # 将x转为bool判断
	print("Yes!")
# 只要是空/为0的对象，都是False（如None，False，0, 0.0, 0j, '', "", [], (), {}）；其余非空/不为0的为True。

# 注意str与int无法直接比较，需自行转换int
a = input("Input something\n")
b = 3
# if a>b: # Error
if int(a)>b:
	print("a>b!")


'循环'
sum = 0
arr = [1, 3, 5, 7, 9]

# for in 循环。会依次枚举list或tuple中的每个元素
for x in arr:
	sum += x
for x in (10, 10):
	sum += x
print(sum)

# range(x) 可生成[0,x)的序列 0,1,2,...,x-1，可用于for in
# range(l,r) 可生成[l,r)的序列l,l+1,...,r-1，同样可用于for in
# range(l,r,step) 可生成[l,r)的序列l,l+step,l+step*2...，同样可用于for in。step可为负，此时为递减数列，且需保证l>=r。
# 注：range生成的就是一个range对象，表示一个不可变的数字序列。一个range对象只占用固定且较小的内存（无论范围多大，因为只有几个参数），是可迭代对象（但不是生成器、迭代器）。用list才转为完整序列。
for x in range(3):
	print(x)
for x in range(2,3):
	print(x)
# list()可将生成的序列转为list
print(list(range(2, 5))) # [2, 3, 4]


print("while:")
# while循环，同C
n = 9
sum = 0
while n>0:
	sum += n
	n -= 2
print(sum)


print("break:")
# break，同C
n = 10
while n>0:
	n-=2
	if n<5: break
	print(n)

for x in range(0,5):
	if x>1:
		print(x)
		break


print("continue:")
# continue，同C
n = 10
sum = 0
while n>0:
	n-=1
	if n%2: continue
	sum+=n
print(sum)













