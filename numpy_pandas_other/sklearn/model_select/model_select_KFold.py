#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import numpy as np
from sklearn.model_selection import KFold
from sklearn.model_selection import GroupKFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import LeavePOut
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import ShuffleSplit
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 2, 3, 4, 5, 6])
# # 两折划分
# kf = KFold(n_splits=3)
# print(kf.get_n_splits(X))
#
# for train_index, test_index in kf.split(X):
#     print("Train Index:", train_index, ", Test Index:", test_index)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]
#     # print(X_train, X_test, y_train, y_test)

# GroupKFold分组
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 2, 3, 4, 5, 6])
# groups = np.array([1, 2, 3, 4, 5, 6])
# groups_kfold = GroupKFold(n_splits=3)
# groups_kfold.get_n_splits(X, y, groups)
# print(groups_kfold)
#
# for train_index, test_index in groups_kfold.split(X, y, groups):
#     print("Train Index:", train_index, ", Test Index:", test_index)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]
#     # print(X_train, X_test, y_train, y_test)

# KFold分层划分(训练集、测试集数据比例与原始集合比例保持一致)
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 1, 1, 2, 2, 2])
# # n_splits=3必须小于最小的y中的某类的个数
# skf = StratifiedKFold(n_splits=3)
# skf.get_n_splits(X, y)
# print(skf)
#
# for train_index, test_index in skf.split(X, y):
#     print("Train Index:", train_index, ", Test Index:", test_index)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]

# 留P法
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 2, 3, 4, 5, 6])
# lpo = LeavePOut(p=3)
# lpo.get_n_splits(X)
# print(lpo)
# for train_index, test_index in lpo.split(X, y):
#     print("Train Index:", train_index, ", Test Index:", test_index)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]


# 留1法
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 2, 3, 4, 5, 6])
# lpo = LeaveOneOut()
# lpo.get_n_splits(X)
# print(lpo)
# for train_index, test_index in lpo.split(X, y):
#     print("Train Index:", train_index, ", Test Index:", test_index)
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]


# 随机划分
# X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
# y = np.array([1, 2, 1, 2, 1, 2])
# rs = ShuffleSplit(n_splits=3, test_size=.25, random_state=0)
# rs.get_n_splits(X)
# print(rs)
# for train_index, test_index in rs.split(X, y):
#     print("Train Index:", train_index, ", Test Index:", test_index)
# print("="*60)
# rs = ShuffleSplit(n_splits=3, train_size=0.5, test_size=.25, random_state=0)
# for train_index, test_index in rs.split(X, y):
#     print("Train Index:", train_index, ", Test Index:", test_index)


# 分层随机划分
X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
y = np.array([1, 2, 1, 2, 1, 2])
rs = StratifiedShuffleSplit(n_splits=3, test_size=0.5, random_state=0)
rs.get_n_splits(X)
print(rs)
for train_index, test_index in rs.split(X, y):
    print("Train Index:", train_index, ", Test Index:", test_index)
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
