#!/usr/bin/env python
# -*- coding:utf-8 -*-


# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 默认figure
x = np.linspace(-1,1,50)
y = 2*x+1
# y = x**2
# plt.plot(x,y)
# plt.show()


# 一个figure
x = np.linspace(-3,3,50)
y1 = 2*x+1
y2 = x**2
# plt.figure()
# plt.plot(x,y1)

# 一个figure中的两条线，num = 3名称,figsize = (8,5)长宽
# plt.figure(num = 3,figsize = (8,5))
# plt.plot(x,y2)
# 线条的颜色，宽度，风格
# plt.plot(x,y1	,color = 'red',linewidth = 1.0,linestyle='--')



# plt.figure()
# plt.plot(x,y2)
# plt.plot(x,y1
# 	,color = 'red'
# 	,linewidth = 1.0
# 	,linestyle='--')
# # x取值范围
# plt.xlim((-1,2))
# # y取值范围
# plt.ylim((-2,3))
# # x,y轴的描述
# plt.xlabel('i am x')
# plt.ylabel('i am y')
# # 替换x,y刻度
# new_ticks = np.linspace(-1,2,5)
# plt.xticks(new_ticks)
# #plt.yticks([-2,-1.8,-1,1.22,3],
# #			['really bad','bad','nomal'
# #			,'good','really good'])
# # 替换字体
# plt.yticks([-2,-1.8,-1,1.22,3],
# 			[r'$really\ bad$'
# 			,r'$bad$'
# 			,r'$nomal$'
# 			,r'$good$'
# 			,r'$really\ good$'])
# # 获取图片边框，并相应的设置
# # gca = 'get current axis'
# ax = plt.gca()
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('red')
# # 指定x轴为顶部框，y轴为左部
# ax.xaxis.set_ticks_position('bottom')
# ax.yaxis.set_ticks_position('left')
# # 设置x轴原点为-1，y轴原点为0
# # data是指定位置，axes为百分比
# ax.spines['bottom'].set_position(('data',0))
# ax.spines['left'].set_position(('axes',0.5))

# 样图的设置，label='up'名称
# plt.plot(x,y2,label='up')
# plt.plot(x,y1
# 	,color = 'red'
# 	,linewidth = 1.0
# 	,linestyle='--'
# 	,label='down')
# # labels重命名   loc位置
# plt.legend(labels = ['aaa','bbb'] ,loc = 'best')
# plt.show()



x = np.linspace(-3,3,50)
y = 2*x + 1
plt.figure(num = 1,figsize=(8,5))
plt.plot(x,y,linewidth = 20)
ax = plt.gca()
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.spines['bottom'].set_position(('data',0))
ax.yaxis.set_ticks_position('left')
ax.spines['left'].set_position(('data',0))

x0 = 1
y0 = 2*x0 + 1

# plot是画的直线，scatter是画的点
plt.scatter(x0 , y0 , s = 50 , color = 'b')

# 画一条虚线，连接到x轴
plt.plot([x0,x0],[y0,0],'k--',lw = 2.5) 

# 添加标注,方法一
# plt.annotate(r'$2x+1=%s$' %y0,xy = (x0,y0),xycoords ='data',xytext=(+30,-30))
# 添加标注，方法二
plt.text(-3.7,3,r'$this\ is\ the\ some\ text.$',fontdict={'size':16,'color':'red'})

# 轴标注刻度能见度设置
for label in ax.get_xticklabels()+ax.get_yticklabels():
	label.set_fontsize(12)
	label.set_bbox(dict(facecolor = 'white',edgecolor = 'None' , alpha = 0.7))
plt.show()


