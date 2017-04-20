#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

"""
交叉验证,寻找最佳模型
"""
__author__='liuxing'
from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.neighbors import KNeighborsClassifier

iris = datasets.load_iris()
iris_X = iris.data
iris_Y = iris.target

from sklearn.cross_validation import cross_val_score
import matplotlib.pyplot as plt
k_range = range(1,31)
k_scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    # 训练数据、测试数据均匀分10次   分类
    scores = cross_val_score(knn,iris_X,iris_Y,cv=10,scoring='accuracy')
    # 线性回归
    loss = -cross_val_score(knn,iris_X,iris_Y,cv=10,scoring='mean_squared_error')
    k_scores.append(loss.mean())

plt.plot(k_range,k_scores)
plt.xlabel('Value of K for KNN')
plt.ylabel('Cross-Validated Accuracy')
plt.show()