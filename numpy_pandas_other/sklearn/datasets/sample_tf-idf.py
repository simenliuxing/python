#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import os
import jieba
import sys
import string
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
reload(sys)
sys.setdefaultencoding('utf8')


# 获取文件列表（该目录下放着100份文档）
def get_file_list(path):
    file_list = []
    files = os.listdir(path)
    for f in files:
        file_list.append(f)
    return file_list, path


# 对文档进行分词处理
def fen_ci(filename, path):
    # 保存分词结果的目录
    s_file_path = './segfile'
    # 再新建
    if not os.path.exists(s_file_path):
        os.mkdir(s_file_path)

    # 读取文档
    with open(path+filename, 'r+') as f:
        file_list = f.read()

    # 对文档进行分词处理，采用默认模式
    seg_list = jieba.cut(file_list, cut_all=True)

    # 对空格，换行符进行处理
    result = []
    for seg in seg_list:
        # 默认为所有的空字符
        seg = ''.join(seg.split())
        if seg != '' and seg != '\n' and seg != '\n\n':
            result.append(seg)
    # 将分词后的结果用空格隔开，保存至本地。
    # 比如"我来到北京清华大学"，分词结果写入为："我 来到 北京 清华大学"
    f = open(s_file_path+'/'+filename, 'w+')
    f.write(' '.join(result))
    f.close()


# 读取100份已分词好的文档，进行TF-IDF计算
def tf_idf(file_list):
    path = './segfile/'
    # 存取100份文档的分词结果
    corpus = []
    for ff in file_list:
        f_name = path + ff
        with open(f_name, 'r+') as f:
            content = f.read()
        corpus.append(content)

    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tf_idf = transformer.fit_transform(vectorizer.fit_transform(corpus))

    # 所有文本的关键字
    word = vectorizer.get_feature_names()
    # 对应的tf_idf矩阵
    weight = tf_idf.toarray()

    s_file_path = './tfidffile'
    if not os.path.exists(s_file_path):
        os.mkdir(s_file_path)

    # 这里将每份文档词语的TF-IDF写入tfidffile文件夹中保存
    list_tfidf_fileame = []
    for i in range(len(weight)):
        list_tfidf_fileame.append(string.zfill(i, 5))
        print u"--------Writing tf-idf in ", i, u" file into ", s_file_path + '/' + string.zfill(i, 5), "--------"
        with open(s_file_path+'/'+string.zfill(i, 5), 'w+') as f:
            for j in range(len(word)):
                f.write(word[j]+'   '+str(weight[i][j])+'\n')

    return s_file_path, list_tfidf_fileame


# 提取分数最高的前5个关键词语
def get_top5word(path, filenames):
    for filename in filenames:
        list_top5 = []
        print('-------------', path+'/'+filename ,'-------------')
        with open(path + '/' + filename, 'r+') as f:
            while True:
                # 读取一个新闻中的没一条数据
                line = f.readline().replace('\n', '').replace('\r', '')
                lines = line.split('   ')
                # 组成一个tuple放到list中
                if len(lines) == 2:
                    lines = (lines[0], float(lines[1]))
                    list_top5.append(lines)
                if not line:
                    break
        # 排序并且获取前5
        print(str(sorted(list_top5, key=lambda t: t[1], reverse=True)[:5]).decode('string_escape'))


if __name__ == "__main__":
    (all_file, path) = get_file_list('./tf-idf_zh/')
    for ff in all_file:
        fen_ci(ff, path)
    s_file_path, list_tfidf_fileame = tf_idf(all_file)
    get_top5word(s_file_path, list_tfidf_fileame)
