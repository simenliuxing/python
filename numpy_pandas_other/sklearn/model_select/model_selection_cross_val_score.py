#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn import datasets, svm
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import cross_val_predict

# 交叉验证计算得分
# digits = datasets.load_digits()
# X = digits.data
# y = digits.target
#
# svc = svm.SVC(kernel='linear')
# C_s = np.logspace(-10, 0, 10)
#
# scores = list()
# scores_std = list()
# for C in C_s:
#     svc.C = C
#     this_scores = cross_val_score(svc, X, y, n_jobs=1)
#     scores.append(np.mean(this_scores))
#     scores_std.append(np.std(this_scores))
#
# # Do the plotting
# plt.figure(1, figsize=(4, 3))
# plt.clf()
# plt.semilogx(C_s, scores)
# plt.semilogx(C_s, np.array(scores) + np.array(scores_std), 'b--')
# plt.semilogx(C_s, np.array(scores) - np.array(scores_std), 'b--')
# locs, labels = plt.yticks()
# plt.yticks(locs, list(map(lambda x: "%g" % x, locs)))
# plt.ylabel('CV score')
# plt.xlabel('Parameter C')
# plt.ylim(0, 1.1)
# plt.show()

# 对每个输入数据点产生交叉验证估计
lr = linear_model.LinearRegression()
boston = datasets.load_boston()
y = boston.target

# cross_val_predict returns an array of the same size as `y` where each entry
# is a prediction obtained by cross validation:
predicted = cross_val_predict(lr, boston.data, y, cv=10)

fig, ax = plt.subplots()
ax.scatter(y, predicted)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_xlabel('Measured')
ax.set_ylabel('Predicted')
plt.show()