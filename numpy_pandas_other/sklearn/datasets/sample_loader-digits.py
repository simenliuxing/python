#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
"""
    手写数字的数据集
"""
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt
import numpy as np
digits = load_digits()
print(digits.data[0])
print(digits.images[0])
print(np.all(digits.images.reshape((1797L, 64)) == digits.data))
# 设置画布
fig = plt.figure(figsize=(6, 6))
fig.subplots_adjust(left=0,
                    right=1,
                    bottom=0,
                    top=1,
                    hspace=0.05,
                    wspace=0)
# 绘制数字，每张图像8x8像素点
for i in range(64):
    ax = fig.add_subplot(8, 8, i + 1, xticks=[], yticks=[])
    ax.imshow(digits.images[i], cmap=plt.cm.binary, interpolation='nearest')
    # 用目标值标记图像
    ax.text(0, 7, str(digits.target[i]))
plt.show()
