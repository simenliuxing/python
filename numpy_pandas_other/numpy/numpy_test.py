#-*- coding:utf-8 -*-
import numpy as np
# 创建
array = np.array([[1,2,3],[2,3,4]])
a = np.array([2,23,4],dtype=np.float)
b = np.zeros((3,4))
c = np.ones((3,4))
d = np.empty((2,2))
e = np.arange(12).reshape((4,3))
f = np.linspace(1,10,20).reshape((4,5))

# 操作
a = np.array([10,20,30,40])
b = np.arange(4)
c = b ** 3
c = b - a
c = 10*np.sin(a)
c = b < 3
a = np.array([[1,1]
			,[0,1]])
b = np.arange(4).reshape((2,2))
c = a.dot(b)
a = np.random.random((2,4))
# axis=1 row,axis=0 colnum
c = a.sum(axis=1)
c = a.min()
c = a.max()
a = np.arange(14,2,-1).reshape((3,4))
# 最大，最小索引
c = np.argmin(a) 
c = np.argmax(a) 
# 平均值
c = a.mean()
c = np.average(a)
c = np.median(a)
# 累加
c = a.cumsum()
c = np.diff(a)
c = np.nonzero(a)
# 左到有递增排序
c = np.sort(a)
# 翻转
c = np.transpose(a)
c = a.T
c = (a.T.dot(a))
# 大于9变成9,小于5变成5,其他不变
c = np.clip(a,5,9)
c = np.mean(a,axis=0)
# print(c)

# 索引
a = np.arange(3, 15).reshape((3, 4))
c = a[2]
c = a[1, 1]
c = a[1][1]
c = a[2, :]
c = a[:, 1]
c = a[1, 1:3]
# for row in a:
# 	print row

# for colnum in a.T:
# 	print colnum

# print a.flatten()

for item in a.flat:
	# print item
	pass


# 合并
a = np.array([1,1,1])
b = np.array([2,2,2])
# 向下合并
c = np.vstack((a,b))
# 左右合并
c = np.hstack((a,b))
# 行列转换
c = a[:,np.newaxis]
d = b[:,np.newaxis]
# print np.vstack((c,d))
# print np.hstack((c,d))
# 多个合并,axis = 0上下合并,axis = 1左右合并
c = np.concatenate((c,d,d),axis = 1)
# print c

# 分割
a = np.arange(12).reshape((3,4))
c = np.split(a,2,axis=1)
c = np.split(a,3,axis=0)
# 不均等分割
c = np.array_split(a,3,axis=1)
# 横向分割
c = np.vsplit(a,3)
# 纵向分割
c = np.hsplit(a,2)
# print c


# 深浅复制
a = np.arange(4)
b = a
c = a
d = b
a[0] = 23
d[1:3] = 44
# print b
# print c
# print a is b
b = a.copy()
a[3] = 99
print(a)
print(b)