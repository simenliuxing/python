#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

"""
    skleanr的数据集
"""
from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt

iris = load_iris()
# 形状
# print(iris.keys())
n_samples, n_features = iris.data.shape
shape = iris.data.shape
# print("number of shape:", shape)
# print("number of samples:", n_samples)
# print("number of features:", n_features)

# 第一朵花的数据
# print(iris.data[0])

# 三种花
# print(iris.target)

# 打印属性名和种类个数
# print(iris.target_names)
print(np.bincount(iris.target))

# 柱状图
# x_index = 2
# colors = ['blue', 'red', 'green']
# for label, color in zip(range(len(iris.target_names)), colors):
#     plt.hist(iris.data[iris.target == label, x_index],
#              label=iris.target_names[label],
#              color=color)
# # petal width 作为x标签
# plt.xlabel(iris.feature_names[x_index])
# # labels重命名
# plt.legend(loc="upper right")
# plt.show()

# 散点图
x_index = 1
y_index = 3
colors = ['blue', 'red', 'green']
for label, color in zip(range(len(iris.target_names)), colors):
    plt.scatter(iris.data[iris.target == label, x_index],
                iris.data[iris.target == label, y_index],
                label=iris.target_names[label],
                c=color)
plt.xlabel(iris.feature_names[x_index])
plt.ylabel(iris.feature_names[y_index])
plt.legend(loc="best")
plt.show()
