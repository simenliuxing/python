#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      宜贷网数据爬虫,该平台是T+1形式的数据，只能获取前一天的数据
"""

import datetime
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


# 爬取数据
def spider_wd():
    try:
        # 先直接获取首页的总量
        url = 'https://www.yidai.com/'
        con = requests.get(url, timeout=10).content

        # 获取已赚取收益、待赚取收益
        url_earn = 'https://www.yidai.com/offten/index/'
        con_earn = requests.get(url_earn, timeout=10).content
        tree_earn = etree.HTML(con_earn)
        earn_sum = tree_earn.xpath('//*[@id="js-tzsy"]/ul[2]/li[3]/ul/li[1]/p/em/text()')[0]
        not_earn_sum = tree_earn.xpath('//*[@id="js-tzsy"]/ul[2]/li[3]/ul/li[2]/p/em/text()')[0]

        # xpath解析
        tree = etree.HTML(con)
        # 返回结果
        result = collections.OrderedDict()
        result['来源平台'] = '宜贷网'

        # 总投资额
        total_sum = tree.xpath('/html/body/div[1]/div[2]/div[2]/div/dl[2]/dd/p/text()')[0]
        result['投资总额'] = total_sum

        # 已赚取
        # 亿部分
        earn_sum = float(earn_sum.strip('￥').replace(',', ''))/100000000
        result['已赚取'] = str(earn_sum) + '亿元'

        # 待赚取
        # 亿部分
        not_earn_sum = float(not_earn_sum.strip('￥').replace(',', ''))/100000000
        result['待赚取'] = str(not_earn_sum) + '亿元'

        # 今日成交额
        today_sum = tree.xpath('/html/body/div[1]/div[2]/div[2]/div/dl[4]/dd/p/text()')[0]
        result['今日成交额'] = today_sum

        # 总注册用户数
        result['注册用户数'] = ''

        # 数据日期
        result['日期'] = str(get_yesterday())

        return result
    except Exception as e:
        print("爬取失败", e)
        return -1


def get_yesterday():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    return yesterday


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
        print(re_spider_wd())


