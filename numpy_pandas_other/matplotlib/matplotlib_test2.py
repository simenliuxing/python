#!/usr/bin/env python
# -*- coding:utf-8 -*-

# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 散点图
# n = 1024
# X = np.random.normal(0,1,n)
# Y = np.random.normal(0,1,n)
# # 颜色设置
# T = np.arctan2(Y,X)
# plt.scatter(X,Y,s = 75 , c=T , alpha = 0.5 , )
# plt.xlim((-1.5,1.5))
# plt.ylim((-1.5,1.5))
# # 替换x,y刻度，不要刻度
# plt.xticks(())
# plt.yticks(())



# 柱状图
# n = 12
# X = np.arange(n) 
# Y1 = (1 - X/float(n))*np.random.uniform(0.5,1.0,n)
# Y2 = (1 - X/float(n))*np.random.uniform(0.5,1.0,n)
# # facecolor = '#9999ff'主题颜色，edgecolor = 'white'边框颜色
# plt.bar(X,+Y1,facecolor = '#9999ff',edgecolor = 'white')
# plt.bar(X,-Y2,facecolor = '#ff9999',edgecolor = 'white')
# # 添加标签
# for x,y in zip(X,Y1):
# 	# x,y+0.15位置偏移  '%.2f' % y原始值  ha:对齐方式
# 	plt.text(x,y+0.15,'%.2f' % y,ha='center',va = 'bottom')
# for x,y in zip(X,Y2):
# 	# 位置偏移 ha:对齐方式
# 	plt.text(x,-y-0.05,-y,ha='center',va = 'top')
# plt.xlim(-0.5,n)
# # plt.xticks(())
# plt.ylim(-1.25,1.25)
# plt.yticks(())



# 画等高线
# 计算高度的函数
def f(x,y):
	return (1-x/2+x**5+y**3)*np.exp(-x**2 -y**2)
n = 256
x = np.linspace(-3,3,n)
y = np.linspace(-3,3,n)
# 定义网格
X,Y = np.meshgrid(x,y)
# 定义contour:等高线的颜色
# X,Y,f(X,Y):x,y,z三个坐标轴，cmap:f(X,Y)高度对应的颜色,8等高线分类10
plt.contourf(X,Y,f(X,Y),8,alpha = 0.75,cmap=plt.cm.hot)
# 画等高线圈圈
C = plt.contour(X,Y,f(X,Y),8,colors = 'black',linewidth = 0.5)
# 画标注C：画在哪里，inline：位置，fontsize：字大小
plt.clabel(C,inline = True,fontsize = 10)
plt.xticks(())
plt.yticks(())
plt.show()