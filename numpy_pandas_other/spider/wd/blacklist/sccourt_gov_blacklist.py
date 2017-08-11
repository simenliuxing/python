#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      四川法院司法黑名单的爬取
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
# headers
headers = {
    'Cookie': 'JSESSIONID=8510701EE56D313AC32D04ACB1DB6E46',
    'Host': 'zxgk.sccourt.gov.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36'
}


# 数据解析
def parse_data(html):
    # 一页的数据
    data_list = []
    # 具体数据
    soup = BeautifulSoup(html, "lxml")
    users = soup.find_all("tr")
    for user in users:
        user_td = user.find_all('td')
        if len(user_td) == 9:
            # 返回结果
            result = collections.OrderedDict()
            result['姓名'] = user_td[1].get_text()
            result['证件号码'] = user_td[3].get_text()
            result['信息类型'] = user_td[4].get_text()
            result['执行案号'] = user_td[5].get_text()
            result['执行法院'] = user_td[7].get_text()
            # 追加到集合中
            data_list.append(result)
    return data_list


# 爬取数据
def spider_data(url, payload):
    try:
        try:
            # 使用代理
            res = requests.post(url, timeout=10, proxies=proxies, headers=headers, params=payload)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.post(url, timeout=10, headers=headers, params=payload)
        res.encoding = 'utf-8'
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
    # 遍历爬取每页的数据
    for page in range(1, 170):
        payload = {'xxlx': '1',
                   'currentPage': str(page),
                   'opt': 'getSxbzxrList',
                   'nd': '',
                   'fydm': '',
                   'dz': '',
                   'zh': '',
                   'bzxr': '',
                   'mhpp': '1'
                   }
        # 获取的html数据
        url = 'http://zxgk.sccourt.gov.cn/webapp/area/scsfgk/sfgk/zxxx/ajax.jsp'
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
        print("第:"+str(page)+"页写文件")
        print(result)
        parse_data_write_file(result)


# 数据的解析,写到文件中
def parse_data_write_file(msg):
    rest = json.loads(msg)
    users = rest["msg"]
    for user in users:
        try:
            with open('./sccourt_gov_blacklist.json', 'a') as f:
                user = json.dumps(user).decode("unicode-escape")
                f.write(user)
                f.write("\n")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
