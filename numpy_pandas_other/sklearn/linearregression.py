#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
'''
    线性回归分类
'''
from sklearn import datasets
from sklearn.linear_model import LinearRegression

loaded_data = datasets.load_boston()
data_X = loaded_data.data
data_Y = loaded_data.target

model = LinearRegression()
model.fit(data_X,data_Y)

# print (model.predict(data_X[:4,:]))
# x轴的参数
# print(model.coef_) # y = 0.1x+0.3
# y轴的焦点
# print(model.intercept_)
# modle的参数
# print (model.get_params())
# 用data_x预测，然后和data_y对比的打分情况(数据的精确度)
print (model.score(data_X,data_Y))