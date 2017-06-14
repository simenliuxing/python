#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      微贷网数据爬虫
"""

import time
import requests
import json
import sys
import collections
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

headers = {
    "Referer": "https://www.weidai.com.cn/sys/platformDataInfo.html",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }


# 爬取数据
def spider_wd():
    try:
        # 先直接获取首页的总量
        url = 'https://www.weidai.com.cn/indexSummaryTrade'
        con = requests.get(url, headers=headers, timeout=10)
        rest = json.loads(con.content)

        # 返回结果
        result = collections.OrderedDict()
        result['来源平台'] = '微贷网'

        # 总投资额
        total_sum = rest['data']['totalTradeAmount']/100000000
        result['投资总额'] = str(total_sum) + '亿元'

        # 已赚取
        earn_sum = rest['data']['earning']/100000000
        result['已赚取'] = str(earn_sum) + '亿元'

        # 待赚取
        result['待赚取'] = ''

        # 今日成交额
        today_sum = rest['data']['dayTradeAmount']/10000
        result['今日成交额'] = str(today_sum) + '万元'

        # 总注册用户数
        total_count = float(rest['data']['tenders']) / 10000
        result['注册用户数'] = str(total_count) + '万'

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
    # print(re_spider_wdw())
    for n in range(1, 2):
        print(re_spider_wd())


