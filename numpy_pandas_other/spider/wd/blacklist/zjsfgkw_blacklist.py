#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      浙江司法公开网黑名单的爬取
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
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Content-Length': '98',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '__jsluid=bbf36f191a12afc596e220e6f58942b0; '
              '_gscu_274171321=01146704cs0imj89; '
              '_gscbrs_274171321=1; '
              'Hm_lvt_c4cb5f597b36c5db42909a369cbaab8e=1501146705; '
              'Hm_lpvt_c4cb5f597b36c5db42909a369cbaab8e=1501381648',
    'Host': 'www.zjsfgkw.cn',
    'Origin': 'http://www.zjsfgkw.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://www.zjsfgkw.cn/Execute/CreditPersonal',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


# 数据解析
def parse_data(html):
    # 一页的数据
    data_list = []
    # 具体数据
    try:
        users = json.loads(html)['informationmodels']
        for user in users:
            # 返回结果
            result = collections.OrderedDict()
            result['姓名'] = user['ReallyName']
            result['证件号码'] = user['CredentialsNumber']
            result['曝光日期'] = user['BGRQ']
            result['地址'] = user['Address']
            result['执行依据'] = user['ZXYJ']
            result['案号'] = user['AH']
            result['执行案由'] = user['ZXAY']
            result['执行法院'] = user['ZXFY']
            result['未执行金额'] = user['WZXJE']
            result['立案日期'] = user['LARQ']
            result['标的金额'] = user['ZXJE']
            # 追加到集合中
            data_list.append(result)
    except Exception as e:
        print(e)
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
            res = requests.post(url, timeout=10, params=payload, headers=headers)
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
    for page in range(1, 324984):
        payload = {'PageNo':  str(page),
                   'PageSize': '5',
                   'ReallyName': '',
                   'CredentialsNumber': '',
                   'AH': '',
                   'ZXFY': '全部',
                   'StartLARQ': '',
                   'EndLARQ': ''
                   }
        # 获取的html数据
        url = 'http://www.zjsfgkw.cn/Execute/CreditPersonal'
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
        if html != -1:
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
            with open('./zjsfgkw_blacklist.json', 'a') as f:
                user = json.dumps(user).decode("unicode-escape")
                f.write(user)
                f.write("\n")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
