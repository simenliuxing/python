#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
'''
    SKLearn模型选择之超参数优化方法
'''
import numpy as np
from time import time
from scipy.stats import randint as sp_randint
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


# 随机采样式超参数优化方法



