#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

def is_chinese(s):
    for ch in s.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

print is_chinese('（身份证号码：441827197708046011）')
print is_chinese('（：441827197708046011）')


def format():
    str = ''
    with open('xxxxx', 'r') as f:
        for line in f:
            str = str + '\',\''+line.strip()
    return str
print format()