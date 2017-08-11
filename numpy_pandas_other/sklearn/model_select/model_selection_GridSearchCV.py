#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
'''
    SKLearn模型选择之超参数优化方法
'''
import numpy as np
from time import time
import scipytest
from scipytest.stats import randint as sp_randint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm, datasets
from sklearn.model_selection import GridSearchCV
# iris = datasets.load_iris()
# # 定义参数网格：2*3=6个参数组合
# parameters = {'kernel':('rbf', 'linear'), 'C':[1, 5, 10]}
# svr = svm.SVC()
# clf = GridSearchCV(svr, parameters)
# # print(clf)
# clf.fit(iris.data, iris.target)
# # sorted(clf.cv_results_.keys())
# print(clf.best_estimator_)


# ------------随机采样式超参数优化方法---------------
# 用于报告超参数搜索的最好结果的函数
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")

# 获得数据：手写字符分类
digits = load_digits()
X, y = digits.data, digits.target
# 构建一个分类器   随机森林中的20棵树
clf = RandomForestClassifier(n_estimators=20)
print "-------以下是随机采样超参数优化方法---------"
# 设置想要优化的超参数以及他们的取值分布
param_dist = {"max_depth": [3, None],
              "max_features": sp_randint(1, 11),
              "min_samples_split": sp_randint(2, 11),
              "min_samples_leaf": sp_randint(1, 11),
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]}
# 开启超参数空间的随机搜索
# 最大迭代次数
n_iter_search = 20
random_search = RandomizedSearchCV(clf,
                                   param_distributions=param_dist,
                                   n_iter=n_iter_search
                                   )
start = time()
random_search.fit(X, y)
print("RandomizedSearchCV took %.2f seconds for %d candidates"
      " parameter settings." % ((time() - start), n_iter_search))
report(random_search.cv_results_)


print "------以下是网格搜索超参数优化方法--------"
param_grid = {"max_depth": [3, None],
              "max_features": [1, 3, 10],
              "min_samples_split": [2, 3, 10],
              "min_samples_leaf": [1, 3, 10],
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]}

# run grid search
grid_search = GridSearchCV(clf, param_grid=param_grid)
start = time()
grid_search.fit(X, y)
print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
      % (time() - start, len(grid_search.cv_results_['params'])))
report(grid_search.cv_results_)
