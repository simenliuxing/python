#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

'''
    数据标准化后的--支持向量机分类
'''
from sklearn import preprocessing
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.datasets.samples_generator import make_classification
from sklearn.svm import SVC
import matplotlib.pyplot as plt

# a = np.array([[10,2.7,3.6],
#               [-100,5,-2],
#               [120,20,40]],dtype=np.float64)
# print (a)
# 使得数据范围差不多，使得机器学习效果更好
# print(preprocessing.scale(a))

# 生成数据
X,Y = make_classification(n_samples=300 #300data
                          ,n_features=2 #属性
                          ,n_redundant=0 #
                          ,n_informative=2
                          ,random_state=22 #随机产生
                          ,n_clusters_per_class=1
                          ,scale=100
                          )
X = preprocessing.scale(X)
X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.3)
clf = SVC()
clf.fit(X_train,Y_train)
print(clf.score(X_test,Y_test))
# plt.scatter(X[:,0],X[:,1],c = Y)
# plt.show()
