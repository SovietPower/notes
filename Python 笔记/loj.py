# -*- coding: utf-8 -*-
import math

# https://www.cnblogs.com/xxoy/p/python_read.html
# 本质：读入到函数的一个静态变量中，每次返回一个数（类似fread()）
def read():
    def get_numbers():
        try:#防止奇怪的东西出现
            read.s = input().split()
            read.s_len = len(read.s)
            if(read.s_len==0):get_numbers()#空行就继续
            read.cnt=0
            return 1#可以正常读
        except:#如果读到文件尾就不读了
            return 0
    if not hasattr(read, 'cnt'):
        if not get_numbers():return 0
    if read.cnt==read.s_len:
        if not get_numbers():return 0
    read.cnt+=1#下一个
    return int(read.s[read.cnt-1])#用eval,整数与小数通用，改成int或许会更快一点

def FP(x, k):
	t=1
	while k:
		if k&1: t=t*x%mod
		x=x*x%mod
		k>>=1
	return t

mod=998244353
K=int(math.sqrt(mod)+1)

x, T= read(), read()
xk=FP(x,K)
cnt=mod//K

A=[0]*cnt
B=[0]*K
A[0]=1
B[0]=1
for i in range(1,cnt):
	A[i]=A[i-1]*xk%mod
for i in range(1,K):
	B[i]=B[i-1]*x%mod

for i in range(T):
	n=read()
	print(A[n//K]*B[n%K]%mod, end=" ")









