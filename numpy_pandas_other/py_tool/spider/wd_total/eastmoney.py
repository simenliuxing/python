#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      东方财富货币供应量爬取
"""
from bs4 import BeautifulSoup
import requests
import sys
import collections
import time
import json
from requests.exceptions import ProxyError
import pymysql.cursors
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# 代理
proxies = {
  "HTTPS": "https://114.230.234.223:808",
  "HTTP": "http://110.73.6.124:8123",
  "HTTPS": "https://221.229.44.14:808",
  "HTTP": "http://116.226.90.12:808",
  "HTTPS": "https://218.108.107.70:909"
}
# 数据库配置
config = {
    'host': '172.16.34.48',
    'port': 3306,
    'user': 'bigdata_read',
    'password': 'bigdata_read',
    'db': 'cgjrRisk',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


# 数据解析
def parse_data(html):
    # 一页的数据
    data_list = []
    # 具体数据
    soup = BeautifulSoup(html, "lxml")
    users = soup.find(id='tb').find_all('tr')
    try:
        for user in users:
            user_td = user.find_all('td')
            if len(user_td) == 10:
                # 返回结果
                result = collections.OrderedDict()
                result['月份'] = user_td[0].get_text().strip()
                result['M2-数量（亿元）'] = user_td[1].get_text().strip()
                result['M2-同比增长'] = user_td[2].get_text().strip()
                result['M2-环比增长'] = user_td[3].get_text().strip()
                result['M1-数量（亿元）'] = user_td[4].get_text().strip()
                result['M1-同比增长'] = user_td[5].get_text().strip()
                result['M1-环比增长'] = user_td[6].get_text().strip()
                result['M0-数量（亿元）'] = user_td[7].get_text().strip()
                result['M0-同比增长'] = user_td[8].get_text().strip()
                result['M0-环比增长'] = user_td[9].get_text().strip()
                result['日期'] = time.strftime('%Y-%m-%d')
                # 追加到集合中
                data_list.append(result)
    except Exception as e:
        print(e)
    return data_list


# 爬取数据
def spider_data(url):
    try:
        try:
            # 使用代理
            res = requests.get(url, timeout=10, proxies=proxies)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.get(url, timeout=10)
        res.encoding = 'gb2312'
        return res.text
    except Exception as e:
        print("爬取失败", e)
        return -1


# 数据最终结果的封装
def package_data(result):
    # 结果数据的封装
    message = collections.OrderedDict()
    if len(result) == 0:
        message["statue_code"] = 0
        message["msg_size"] = 0
    else:
        message["statue_code"] = 1
        message["msg_size"] = len(result)
        message["msg"] = result
    return json.dumps(message).decode("unicode-escape")


# 爬取每页的具体数据（处理超时异常,默认10次重试）
def re_spider_page_data():
    # 遍历爬取每页的数据
    for page in range(1, 7):
        # 获取的html数据
        url = 'http://data.eastmoney.com/cjsj/moneysupply.aspx?p='+str(page)
        html = spider_data(url)
        # 如果没有获取到数据则重试多次
        if html == -1:
            # 如果没有爬取成功则，重爬
            for num in range(1, 10):
                time.sleep(0.5)
                print(num)
                if html == -1:
                    html = spider_data(url)
                else:
                    break

        if html != -1:
            # 解析数据
            result = parse_data(html)
            # 包装数据
            result = package_data(result)
            print('第'+str(page)+'页写数据库')
            insert_db(result)
            time.sleep(2)


# 写到mysql中
def insert_db(result):
    connection = pymysql.connect(**config)
    try:
        result = json.loads(result)
        if result['statue_code'] != 0:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO eastmoney_currency_supply (month, m2_amount, ' \
                      'm2_same_growth, m2_ratio_growth, m1_amount, m1_same_growth, ' \
                      'm1_ratio_growth, m0_amount, m0_same_growth, m0_ratio_growth, ' \
                      'spider_date)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                result = result['msg']
                for res in result:
                    cursor.execute(sql, (res['月份'.decode("utf-8")],
                                         res['M2-数量（亿元）'.decode("utf-8")],
                                         res['M2-同比增长'.decode("utf-8")],
                                         res['M2-环比增长'.decode("utf-8")],
                                         res['M1-数量（亿元）'.decode("utf-8")],
                                         res['M1-同比增长'.decode("utf-8")],
                                         res['M1-环比增长'.decode("utf-8")],
                                         res['M0-数量（亿元）'.decode("utf-8")],
                                         res['M0-同比增长'.decode("utf-8")],
                                         res['M0-环比增长'.decode("utf-8")],
                                         res['日期'.decode("utf-8")]))
                connection.commit()
    finally:
        connection.close()

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
