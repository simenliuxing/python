#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

'''
    通过搜狗新闻语料用word2Vec训练中文模型   查找相似词语
    数据地址：http://www.sogou.com/labs/resource/ca.php
'''
import jieba
from gensim.models import word2vec
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def fenci():
    f1 =open("./word2vec/corpus.txt")
    f2 =open("./word2vec/corpus_fenci.txt", 'a')
    lines =f1.readlines()  # 读取全部内容
    for line in lines:
        line = line.replace('\t', '').replace('\n', '').replace(' ', '')
        seg_list = jieba.cut(line, cut_all=False)
        f2.write(" ".join(seg_list))
    f1.close()
    f2.close()


def word2vec_test():
    # 主程序
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(u"./word2vec/corpus_fenci.txt")  # 加载语料
    model = word2vec.Word2Vec(sentences, size=200)  # 训练skip-gram模型，默认window=5

    print model
    # 计算两个词的相似度/相关程度
    try:
        y1 = model.similarity(u"湖人", u"科比")
    except KeyError:
        y1 = 0
    print u"【湖人】和【科比】的相似度为：", y1
    print"-----\n"

    # 计算某个词的相关词列表
    y2 = model.most_similar(u"科比", topn=20)  # 20个最相关的
    print u"和【科比】最相关的词有：\n"
    for item in y2:
        print item[0], item[1]
    print"-----\n"

    # 寻找对应关系
    # print u"现在 我 宣布"
    # y3 = model.most_similar([u'现在', u'我'], [u'宣布'], topn=3)
    # for item in y3:
    #     print item[0], item[1]
    # print"----\n"

    # 寻找不合群的词
    # y4 = model.doesnt_match(u"炸药 犯罪 走私 并".split())
    # print u"不合群的词：", y4
    # print"-----\n"



    # 保存模型，以便重用
    model.save(u"./word2vec/w2v.model")
    # 对应的加载方式
    # model_2 =word2vec.Word2Vec.load("text8.model")

    # 以一种c语言可以解析的形式存储词向量
    # model.save_word2vec_format(u"书评.model.bin", binary=True)
    # 对应的加载方式
    # model_3 =word2vec.Word2Vec.load_word2vec_format("text8.model.bin",binary=True)

if __name__ == '__main__':
    fenci()
    word2vec_test()
