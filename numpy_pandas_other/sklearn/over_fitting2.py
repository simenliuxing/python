#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
过拟合问题
"""
__author__='liuxing'
# 可视化过程
from sklearn.learning_curve import validation_curve
# 数字
from sklearn.datasets import load_digits
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import numpy as np

digits = load_digits()
X = digits.data
Y = digits.target
# train_loss，test_loss误差值
param_range = np.logspace(-6,-2.3,5)
train_loss,test_loss = validation_curve(
    SVC()
    ,X
    ,Y
    ,param_name='gamma'
    ,param_range=param_range
    # 分成10组
    ,cv = 10
    # 方差值(对比误差值)
    ,scoring='mean_squared_error'
    # 记录点的位置
)
# 平均值误差
train_loss_mean = -np.mean(train_loss,axis=1)
test_loss_mean = -np.mean(test_loss,axis=1)
plt.plot(
    param_range
    ,train_loss_mean
    ,'o-'
    ,color = 'r'
    ,label='Training'
)
plt.plot(
    param_range
    ,test_loss_mean
    ,'o-'
    ,color = 'g'
    ,label='Cross-validation'
)
plt.xlabel('gamma')
plt.ylabel('Loss')
plt.legend(loc = 'best')
plt.show()