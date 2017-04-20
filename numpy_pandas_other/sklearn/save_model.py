#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
'''
    保存模型
'''
from sklearn import svm
from sklearn import datasets

clf = svm.SVC()
iris = datasets.load_iris()
x,y = iris.data,iris.target
clf.fit(x,y)

# # 1.保存到pickle中
# import pickle
# with open('clf.pickle','wb') as f:
#     pickle.dump(clf,f)
#
# # 导出模型来测试
# with open('clf.pickle','rb') as f:
#     clf2 = pickle.load(f)
#     print(clf2.predict(x[0:1]))

# 2.sklearn中自己的方法
from sklearn.externals import joblib
# 保存
joblib.dump(clf,'clf.pkl')
# 读取
clf3 = joblib.load('clf.pkl')
print(clf3.predict(x[0:1]))
