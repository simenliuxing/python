#!/usr/bin/env python
# -*- coding:utf-8 -*-

# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 图像数据
# a = np.array([0.313,0.365,0.423
# 			,0.365,0.439,0.525
# 			,0.423,0.525,0.651]).reshape(3,3)
# # 展示图片,interpolation = 'nearest'：图片边框模糊程度
# plt.imshow(a,interpolation ='nearest',cmap = 'bone',origin = 'lower')
# # 图片注解shrink = 0.9:压缩为90%
# plt.colorbar(shrink = 0.9)
# plt.xticks(())
# plt.yticks(())


# 3D图像数据
fig = plt.figure()
# 加一个3D坐标轴
ax = Axes3D(fig)
X = np.arange(-4,4,0.25)
Y = np.arange(-4,4,0.25)
# x,y作为底面的网格
X,Y = np.meshgrid(X,Y)
# z的高度值
R = np.sqrt(X ** 2 + Y ** 2)
Z = np.sin(R)
# 画3D图像rstride,cstride:上线,左右的跨度
ax.plot_surface(X,Y,Z,rstride = 1,cstride = 1,cmap = plt.get_cmap('rainbow'))
# 画等高线zdir = 'z':映射到z轴,offset = -2:压缩到比0点高低多少
ax.contourf(X,Y,Z,zdir = 'z',offset = -3,cmap = 'rainbow')
# 设置等高线的范围
ax.set_zlim(-2,2)
plt.show()