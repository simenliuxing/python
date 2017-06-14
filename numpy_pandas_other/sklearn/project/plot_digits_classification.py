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
    # 不显示坐标尺寸
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Training: %i' % label)

# plt.show()
# 要对这些数据应用分类器，我们需要对图像进行平铺 ＃将数据转换成一个（samples，feature）矩阵：
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# 创建分类器：支持向量分类器
classifier = svm.SVC(gamma=0.001)

# 我们学习上半部分数字的数字
classifier.fit(data[:n_samples/2],digits.target[:n_samples/2])

# 预测下半部分
expected = digits.target[n_samples / 2:]
predicted = classifier.predict(data[n_samples / 2:])

print("Classification report for classifier %s:\n%s\n"
      % (classifier,metrics.classification_report(expected,predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

images_and_predictions = list(zip(digits.images[n_samples / 2:], predicted))
for index, (image, prediction) in enumerate(images_and_predictions[:4]):
    plt.subplot(2, 4, index + 5)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Prediction: %i' % prediction)

plt.show()