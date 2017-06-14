#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      团贷网数据爬虫
"""

import time
import requests
from bs4 import BeautifulSoup
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
        # 先直接获取
        url = 'https://www.tdw.cn/'
        con = requests.get(url, timeout=10).content
        soup = BeautifulSoup(con, "lxml")

        # 如果之获取到<meta，则之获取到了缓存，则需要拿里面的参数重新获取
        if con.startswith('<meta'):
            # 获取缓存参数
            req = soup._most_recent_element.attrs['content']
            new_url = req.split('0; url=/')[1]
            # 组拼新的url
            url += new_url
            # 重新请求
            con = requests.get(url, timeout=10).content

        # xpath解析
        tree = etree.HTML(con)
        # 返回结果
        result = collections.OrderedDict()
        result['来源平台'] = '团贷网'

        # 总投资额
        total_sum1 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[2]/dl/dd/div[1]/span[1]/@data-to")[0]
        total_sum2 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[2]/dl/dd/div[1]/text()")
        total_sum3 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[2]/dl/dd/div[1]/span[2]/@data-to")[0]
        if len(total_sum2) > 2:
            result['投资总额'] = total_sum1 + total_sum2[1] + total_sum3 + total_sum2[2]
        else:
            result['投资总额'] = total_sum1+'亿'+total_sum3+'万元'

        # 已赚取
        earn_sum1 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[1]/span[2]/@data-to")[0]
        earn_sum2 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[1]/text()")
        earn_sum3 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[1]/span[3]/@data-to")[0]
        if len(earn_sum2) > 2:
            result['已赚取'] = earn_sum1 + earn_sum2[1] + earn_sum3 + earn_sum2[2] + '元'
        else:
            result['已赚取'] = earn_sum1 + '亿' + earn_sum3 + '万元'

        # 待赚取
        not_earn_sum1 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[2]/span[2]/@data-to")[0]
        not_earn_sum2 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[2]/text()")
        not_earn_sum3 = tree.xpath("/html/body/div[5]/div[2]/div[1]/div[3]/dl/dd/div[2]/span[3]/@data-to")[0]
        if len(not_earn_sum2) > 2:
            result['待赚取'] = not_earn_sum1 + not_earn_sum2[1] + not_earn_sum3 + not_earn_sum2[2] + '元'
        else:
            result['待赚取'] = not_earn_sum1 + '亿' + not_earn_sum3 + '万元'

        # 今日成交额
        today_sum = round(float(tree.xpath("/html/body/div[5]/div[2]/div[1]/div[4]/dl/dd/div[2]/span[2]/@data-to")[0])/10000, 4)
        result['今日成交额'] = str(today_sum) + '万元'

        # 总注册用户数
        result['注册用户数'] = ''

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
    print(re_spider_wd())


