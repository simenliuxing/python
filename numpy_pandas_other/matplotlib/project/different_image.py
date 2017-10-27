#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

from pylab import *
import numpy as np
# 普通图
# n = 256
# X = np.linspace(-np.pi,np.pi,n,endpoint=True)
# Y = np.sin(2*X)
#
# plot(X, Y+2, color='blue', alpha=1.00)
# plot(X, Y-2, color='blue', alpha=1.00)
# show()

#　散点图
# n = 102
# X = np.random.normal(0,1,n)
# Y = np.random.normal(0,1,n)
# scatter(X, Y)
# show()


# 条形图
# n = 12
# X = np.arange(n)
# Y1 = (1-X/float(n)) * np.random.uniform(0.5,1.0,n)
# Y2 = (1-X/float(n)) * np.random.uniform(0.5,1.0,n)
# bar(X, +Y1, facecolor='#9999ff', edgecolor='white')
# bar(X, -Y2, facecolor='#ff9999', edgecolor='white')
# for x,y in zip(X,Y1):
#     text(x, y+0.05, '%.2f' % y, ha='center', va= 'bottom')
# for x,y in zip(X,Y2):
#     text(x, -y-0.15, '%.2f' % y, ha='center', va= 'bottom')
# ylim(-1.25,+1.25)
# show()


# 等高线图
# def f(x, y):
#     return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
# n = 256
# x = np.linspace(-3, 3, n)
# y = np.linspace(-3, 3, n)
# X,Y = np.meshgrid(x,y)
#
# contourf(X, Y, f(X,Y), 8, alpha=.75, cmap='jet')
# C = contour(X, Y, f(X,Y), 8, colors='black', linewidth=.5)
# show()

# 灰度图
# def f(x,y):
#     return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
# n = 20
# x = np.linspace(-3,3,4*n)
# y = np.linspace(-3,3,3*n)
# X,Y = np.meshgrid(x,y)
# imshow(f(X,Y))
# show()


# 饼状图
# n = 20
# # Z = np.random.uniform(0, 1, n)
# Z = np.arange(n)
# pie(Z)
# show()

# 量场图
# n = 8
# X,Y = np.mgrid[0:n,0:n]
# print(X)
# print(Y)
# quiver(X,Y)
# show()

# 网格
# axes = gca()
# axes.set_xlim(0,4)
# axes.set_ylim(0,3)
# axes.set_xticklabels([])
# axes.set_yticklabels([])
# show()

# 多重网格
# subplot(2,2,1)
# subplot(2,2,2)
# subplot(2,2,3)
# subplot(2,2,4)
# show()

# 极轴图
# axes([0,0,1,1])
# N = 20
# theta = np.arange(0.0, 2*np.pi, 2*np.pi/N)
# radii = 10*np.random.rand(N)
# width = np.pi/4*np.random.rand(N)
# bars = bar(theta, radii, width=width, bottom=0.0)
# for r,bar in zip(radii, bars):
#     bar.set_facecolor( cm.jet(r/10.))
#     bar.set_alpha(0.5)
# show()


# 3D 图
from mpl_toolkits.mplot3d import Axes3D

fig = figure()
ax = Axes3D(fig)
X = np.arange(-4, 4, 0.25)
Y = np.arange(-4, 4, 0.25)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)

ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='hot')

show()