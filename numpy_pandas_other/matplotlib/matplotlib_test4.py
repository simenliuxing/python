#!/usr/bin/env python
# -*- coding:utf-8 -*-

# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# # 一个figure画多个小图
# plt.figure()
# # 第一个小图,分成两行两列
# plt.subplot(2,2,1)
# plt.plot([0,1],[0,1])

# # 第二个小图,分成两行两列
# plt.subplot(2,2,2)
# plt.plot([0,1],[0,2])

# # 第二个小图,分成两行两列
# plt.subplot(2,2,3)
# plt.plot([0,1],[0,3])

# # 第二个小图,分成两行两列
# plt.subplot(2,2,4)
# plt.plot([0,1],[0,4])


# # 一个figure画多个小图
# plt.figure()
# # 第一个小图,分成两行两列
# plt.subplot(2,1,1)
# plt.plot([0,1],[0,1])

# # 第二个小图,分成两行两列
# plt.subplot(2,3,4)
# plt.plot([0,1],[0,2])

# # 第二个小图,分成两行两列
# plt.subplot(2,3,5)
# plt.plot([0,1],[0,3])

# # 第二个小图,分成两行两列
# plt.subplot(2,3,6)
# plt.plot([0,1],[0,4])


# # 画多个图的subplot2grid方式
# import matplotlib.gridspec as gridspec
# plt.figure()
# # (3,3):3行3列，(0,0):图一从第0行0列开始
# ax1 = plt.subplot2grid((3,3),(0,0),colspan = 3)
# ax1.plot([1,2],[1,2])
# ax1.set_title('ax1_one')
# ax2 = plt.subplot2grid((3,3),(1,0),colspan = 2)
# ax3 = plt.subplot2grid((3,3),(1,2),rowspan = 2)
# ax4 = plt.subplot2grid((3,3),(2,0))
# ax4 = plt.subplot2grid((3,3),(2,1))



# 画多个图的GridSpec方式
import matplotlib.gridspec as gridspec
plt.figure()
# 3行3列
gs = gridspec.GridSpec(3,3)
ax1 = plt.subplot(gs[0,:])
ax1.scatter([1,2],[1,2])
ax2 = plt.subplot(gs[1,:2])
ax3 = plt.subplot(gs[1:,2])
ax4 = plt.subplot(gs[-1,0])
ax5 = plt.subplot(gs[-1,-2])
plt.show()



# 画多个图的GridSpec方式
# 2行2列
