#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.datasets.samples_generator import make_classification
from sklearn.datasets.samples_generator import make_moons
# # 指定每个cluster的中心
# centers = [[1, 1], [-1, -1], [1, -1]]
# # 每个cluster的标准差
# cluster_std = 0.3
# X, labels = make_blobs(n_samples=200, centers=centers,
#                        n_features=2, cluster_std=cluster_std,
#                        random_state=0)
# print('X.shape:', X.shape)
# print('labels:', set(labels))
#
# # 将二维点集绘制出来
# # set去重
# unique_labels = set(labels)
# colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
# for k, col in zip(unique_labels, colors):
#     # 此处用array直接和一个数值比较，会得到True\False
#     # 然后可以从array中的True就可以获取，array中的值
#     X_k = X[labels == k]
#     plt.plot(X_k[:, 0], X_k[:, 1], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=14)
# plt.title('dataset by make_blob()')
# plt.show()


# make_classification数据集
# n_clusters_per_class点集，数据集的中心点个数
X, labels = make_classification(n_samples=200, n_features=2,
                                n_redundant=0, n_informative=2,
                                random_state=1, n_clusters_per_class=2
                                )
# ############数据加噪声#########
# # 它是伪随机数产生器的种子
# rng = np.random.RandomState(2)
# # 200行2列的0到1上的均匀分布数据,然后加入到X的range中
# # print(rng.uniform(size=X.shape))
# X += 2 * rng.uniform(size=X.shape)
#
# # 将二维点集绘制出来
# unique_labels = set(labels)
# colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
# for k, col in zip(unique_labels, colors):
#     X_k = X[labels == k]
#     plt.plot(X_k[:, 0], X_k[:, 1], 'o', markerfacecolor=col,
#                  markeredgecolor='k', markersize=14)
# plt.title('dataset by make_blob()')
# plt.show()

# make_moons数据集
X, labels = make_moons(n_samples=200, shuffle=True,
                       noise=0.3, random_state=0)
print(X.shape)
print(set(labels))
# 将二维点集绘制出来
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    X_k = X[labels == k]
    plt.plot(X_k[:, 0], X_k[:, 1], 'o', markerfacecolor=col,
            markeredgecolor='k', markersize=14)
plt.title('dataset by make_blob()')
plt.show()