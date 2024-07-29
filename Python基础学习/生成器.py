# -*- coding: utf-8 -*-

# 生成器(generator)：类似列表生成式，但每次执行只生成一个元素（数列生成器），内存占用少
# 生成器是一种更简洁好用的迭代器。

# 通过将列表生成式的[]换为()，可得到生成器
l = [x*x for x in range(10)] # list
g = (x*x for x in range(10)) # generator
print(l, "\n", g)

# 通过next(x)获得generator x的下一个返回值，用于逐个输出
# 当计算完最后一个元素时，再调用next()会出错：StopIteration
print(next(g), next(g), next(g)) # 0 1 4

# generator也是可迭代对象，也可以用for迭代输出（更常用）。注意也是从当前执行位置开始迭代
g = (x*x for x in range(10))
next(g) # 0
next(g) # 1
for x in g:
	print(x, end=" ") # 4 9 16 25 36 49 64 81
print()

# 通过含yield的函数，也可以生成generator
# 对于一个生成数字的函数，将要生成的数x写为yield x，可得到生成x的generator
# 如生成Fibonacci数列的前n项函数，将print(b)改为yield(b)或yield b（类似return b），可得到生成Fibonacci数列的前n项的generator
# yield后可加任意类型、任意多个数值。元素数>1时会返回tuple。

# 对于generator函数，第一次调用时从头开始执行，遇到yield x时返回x，再次执行时从上次返回的yield语句处继续执行。彻底执行完后才会return，此时再次执行会有StopIteration错误。
# 如果generator函数永远不会return，那么就得到一个无穷数列；如果在执行过程中return，则直接抛出StopIteration，终止迭代。
def fib(n): # 普通函数
	x, a, b = 0, 0, 1
	while x<n:
		print(b)
		a, b = b, a+b
		x += 1
	return "Done!"
print(fib(5))

def fib(n): # generator函数
	x, a, b = 0, 0, 1
	while x<n:
		yield(b) # yield b
		a, b = b, a+b
		x += 1
	print("AlmostDone!")
	return "Done!"

# 注意每次调用fib(n)都会生成新的generator
print(next(fib(5))) # 1
for x in fib(5): # 1 1 2 3 5 AlmostDone!
	print(x, end=" ")

# 但使用变量赋值一个fib(n)，就可以保持旧的generator
g = fib(5) # g是一个generator
print(next(g)) # 1
for x in g: # 1 2 3 5 AlmostDone!
	print(x, end=" ")

# 可以发现，for迭代调用generator函数，无法得到其返回值。若要得到返回值，需用next()直到捕获StopIteration错误，返回值包含在StopIteration的value中。
# 使用捕获错误，得到StopIteration
g=fib(5)
while True:
	try:
		x=next(g)
		print(x, end=" ")
	except StopIteration as e:
		print("Gererator return value:", e.value)
		break
# 1 1 2 3 5 AlmostDone!
# Gererator return value: Done!




