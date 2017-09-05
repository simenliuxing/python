#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      信用宁波黑名单的爬取
"""
from bs4 import BeautifulSoup
from lxml import etree
import requests
import sys
import collections
import time
import json
from requests.exceptions import ProxyError
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


# 数据解析
def parse_data(html):
    # 一页的数据
    data_list = []
    # 具体数据
    soup = BeautifulSoup(html, "lxml")
    try:
        users = soup.find_all("table", class_="sj_table")[0].find_all("tr")
        for user in users:
                # 贝才的官网url
                url_home = 'http://nbcredit.gov.cn/nbggxyww/bzxr/getDetail?unid='
                # 返回结果
                result = collections.OrderedDict()
                try:
                    a_tag = user.find_all('a')[0]['onclick']
                    a_tag = a_tag.split('(')[1].replace('\'', '').replace(')', '')
                    url_home = url_home + a_tag
                    # 获取二级链接
                    user_info = spider_data(url_home, None)
                    # 二级链接下的详细信息
                    user_soup = BeautifulSoup(user_info, "lxml")
                    user_soup_table_tr = user_soup.find_all("table", class_="ts_table")[0].find_all("tr")
                    for tr in user_soup_table_tr:
                        tr_info = tr.get_text(strip=True)
                        tr_info_array = tr_info.split('：')
                        result[tr_info_array[0]] = tr_info_array[1]
                    # 追加到集合中
                    data_list.append(result)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    return data_list


# 爬取数据
def spider_data(url, payload):
    try:
        try:
            # 使用代理
            if None == payload:
                res = requests.get(url, timeout=10, proxies=proxies)
            else:
                res = requests.post(url, timeout=10, proxies=proxies, params=payload)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            if None == payload:
                res = requests.get(url, timeout=10)
            else:
                res = requests.post(url, timeout=10, params=payload)
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
    # return json.dumps(message, indent=2).decode("unicode-escape")


# 爬取每页的具体数据（处理超时异常,默认10次重试）
def re_spider_page_data():
    # total_page = 7487
    # 遍历爬取每页的数据
    for page in range(1, 2000):
        payload = {"xm": "",
                   "mc": "",
                   "pageIndexfr": "1",
                   "pageIndex": str(page),
                   "zxrlx": "zrr"
                   }
        # 获取的html数据
        url = "http://nbcredit.gov.cn/nbggxyww/bzxr/list"
        html = spider_data(url, payload)
        # 如果没有获取到数据则重试多次
        if html == -1:
            # 如果没有爬取成功则，重爬
            for num in range(1, 10):
                time.sleep(0.5)
                print(num)
                if html == -1:
                    html = spider_data(url, payload)
                else:
                    break
        # 解析数据
        result = parse_data(html)
        # 包装数据
        result = package_data(result)
        print("第:" + str(page) + "页写文件")
        print(result)
        with open('./nbcredit_gov_blacklist.json', 'a') as f:
            f.write(result)
            f.write("\n")

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
