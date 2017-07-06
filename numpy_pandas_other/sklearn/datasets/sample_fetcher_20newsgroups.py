#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

"""
    20组新闻文件数据集api用法详解
"""
from sklearn.datasets import get_data_home
from sklearn.datasets import fetch_20newsgroups
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import fetch_20newsgroups_vectorized

# 下载数据的默认路径
print(get_data_home())
newsgroups_train = fetch_20newsgroups()
# 输出目标变量target的names
pprint(list(newsgroups_train.target_names))
print(newsgroups_train.filenames.shape)
print(newsgroups_train.target.shape)
print(newsgroups_train.target[:10])
print('-'*50)

# 只选择两个类型的新闻
cats = ['alt.atheism', 'sci.space']
newsgroups_train = fetch_20newsgroups(subset='train', categories=cats)
print(list(newsgroups_train.target_names))
print(list(newsgroups_train.filenames.shape))
print(list(newsgroups_train.target.shape))
print(list(newsgroups_train.target[:10]))
print('-'*50)

# 选择四个类型的新闻
categories = ['alt.atheism', 'talk.religion.misc',
              'comp.graphics', 'sci.space']
newsgroups_train = fetch_20newsgroups(subset='train', categories=categories)
# 将新闻的内容（都是英文单词）变成TF-IDF的一元模型向量
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(newsgroups_train.data)
print(vectors.shape)
print('-'*50)

# 直接加载向量化后的数据
newsgroups_train = fetch_20newsgroups_vectorized(subset='train')
from sklearn.datasets import fetch_lfw_people

