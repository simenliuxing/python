#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      小牛在线数据爬虫
"""

import time
import requests
from lxml import etree
import json
import sys
import collections
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }


# 爬取数据
def spider_wd():
    try:
        # 先直接获取
        url = 'https://www.xiaoniu88.com/portal/platform/index'
        con = requests.get(url, headers=headers, timeout=10).content

        # xpath解析
        tree = etree.HTML(con)
        # 返回结果
        result = collections.OrderedDict()
        result['来源平台'] = '小牛在线'

        # 总投资额
        total_sum = tree.xpath('//em[2]')[0].xpath('string(.)').split(' )')[1]
        result['投资总额'] = total_sum

        # 已赚取
        result['已赚取'] = ''

        # 待赚取
        result['待赚取'] = ''

        # 今日成交额
        result['今日成交额'] = ''

        # 总注册用户数
        total_count = tree.xpath('//em[1]')[0].xpath('string(.)').split(')')[1]
        result['注册用户数'] = total_count

        # 数据日期
        result['日期'] = time.strftime('%Y-%m-%d')

        return result
    except Exception as e:
        print("爬取失败", e)
        return -1


# 爬取数据（处理超时异常,默认10次重试），并组装成json格式数据
def re_spider_wd():
    result = spider_wd()
    # 如果没有获取到数据则重试多次
    if result == -1:
        # 如果没有爬取成功则，重爬
        for num in range(1, 10):
            time.sleep(0.5)
            if result == -1:
                result = spider_wd()
            else:
                break

    # 结果数据的封装
    message = collections.OrderedDict()
    if result == -1:
        message['statue_code'] = 0
    else:
        message['statue_code'] = 1
        message['msg'] = result
    return json.dumps(message).decode('unicode-escape')

if __name__ == '__main__':
    for n in range(1, 200):
        print(n)
        print(re_spider_wd())


