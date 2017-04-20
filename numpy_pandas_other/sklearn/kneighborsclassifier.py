#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KNeighborsClassifier test module
"""
__author__='liuxing'
from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.neighbors import KNeighborsClassifier

#花的数据集
iris = datasets.load_iris()
#花的属性
iris_X = iris.data
#花的类别 0 ，1,2三个类别
iris_Y = iris.target
# print(iris_X[:2,:])
# print (iris_Y)
# 训练数据，测试数据7:3
X_train,X_test,Y_train,Y_test = train_test_split(iris_X,iris_Y,test_size=0.3)
# print (y_train)
# k紧邻分类
knn = KNeighborsClassifier()
# 训练
knn.fit(X_train,Y_train)
print (knn.predict(X_test))
print (Y_test)