#!/usr/bin/env python
# -*- coding:utf-8 -*-

# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec

# # 大图中画小图
# fig = plt.figure()
# x = [1,2,3,4,5,6,7]
# y = [1,3,4,2,5,8,6]
# # 添加一个axes:子图
# left,bottom,width,height = 0.1,0.1,0.8,0.8
# ax1 = fig.add_axes([left,bottom,width,height])
# ax1.plot(x,y,'r')
# ax1.set_xlabel('x')
# ax1.set_ylabel('y')
# ax1.set_title('title')
# # 添加一个axes:子图
# left,bottom,width,height = 0.2,0.6,0.25,0.25
# ax2 = fig.add_axes([left,bottom,width,height])
# ax2.plot(y,x,'b')
# ax2.set_xlabel('x')
# ax2.set_ylabel('y')
# ax2.set_title('title inside 1')
# # 添加一个axes:子图
# plt.axes([0.6,0.2,0.25,0.25])
# plt.plot(y[::-1],x,'g')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.show()



# 主次坐标轴
# x = np.arange(0,10,0.1)
# y1 = 0.05*x**2
# y2 = -1*y1
# fig,ax1 = plt.subplots()
# # 将ax2对着过来
# ax2 = ax1.twinx()
# ax1.plot(x,y1,'g-')
# ax1.set_xlabel('X data')
# ax1.set_ylabel('Y1',color = 'g')
# ax2.plot(x,y2,'b--')
# ax2.set_ylabel('Y2',color = 'b')
# plt.show()



# 画动画
from matplotlib import animation
fig,ax = plt.subplots()
x = np.arange(0,2*np.pi,0.01)
# line,:表示列表的第一位
line, = ax.plot(x,np.sin(x))

def animate(i):
	line.set_ydata(np.sin(x+i/10))
	return line,

def init():
	line.set_ydata(np.sin(x))
	return line,

ani = animation.FuncAnimation(
	fig = fig
	,func = animate
	,frames = 100
	,init_func = init
	,interval = 20
	,blit = True)
plt.show()