#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
"""
================================
识别手写数字
================================

显示如何使用scikit学习来识别图像的示例
手写数字。

"""
print(__doc__)
import matplotlib.pyplot as plt
from sklearn import datasets, svm, metrics

# The digits dataset
digits = datasets.load_digits()
# print(digits.images)
# print(digits.target)
# print(list(zip(digits.images,digits.target)[0:1]))
image_and_labels = list(zip(digits.images,digits.target))
for index,(image,label) in enumerate(image_and_labels[:4]):
    plt.subplot(2, 4, index + 1)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Training: %i' % label)
plt.show()
