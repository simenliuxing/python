#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      信用黑龙江黑名单的爬取
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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cookie': 'JSESSIONID=O__yv4Q492F_txcrmWjtrj41eUEUMZMJFwlc4AoU9leQRbuugtnp!-787394411; '
              '_gscu_983897279=03017691dk8uug14; '
              '_gscs_983897279=03017691z2oy1t14|pv:17; '
              '_gscbrs_983897279=1',
    'Host': 'www.hljcredit.gov.cn',
    'Proxy-Connection': 'keep-alive',
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
    try:
        users = soup.find_all('table', class_='list_2_tab')[0].find_all('tr')
        count = 0
        for user in users:
            if 0 != count:
                # 返回结果
                result = collections.OrderedDict()
                try:
                    user_info = user.find_all('td')
                    user_info_url = user_info[1].a['href']
                    user_info_url = 'http://www.hljcredit.gov.cn/' + user_info_url
                    user_info = spider_data(user_info_url, '')
                    # 如果没有获取到数据则重试多次
                    if -1 == user_info:
                        # 如果没有爬取成功则，重爬
                        for num in range(1, 10):
                            time.sleep(0.5)
                            print(num)
                            if -1 == user_info:
                                user_info = spider_data(user_info_url, '')
                            else:
                                break
                    # 二级链接下的详细信息
                    user_soup = BeautifulSoup(user_info, "lxml")
                    user_soup_trs = user_soup.find_all("table", class_="for_letter")[0].find_all("tr")
                    for tr in user_soup_trs:
                        tr_info = tr.get_text(strip=True)
                        tr_info_array = tr_info.split('：')
                        if tr_info_array[0] not in result:
                            result[tr_info_array[0]] = tr_info_array[1]
                    # 添加到集合中
                    data_list.append(result)
                except Exception as e:
                    print(e)
            count += 1
    except Exception as e:
        print(e)
    return data_list


# 爬取数据
def spider_data(url, payload):
    try:
        try:
            # 使用代理
            res = requests.post(url, timeout=10, proxies=proxies, params=payload, headers=headers)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.post(url, timeout=10, headers=headers, params=payload)
        res.encoding = 'UTF-8'
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
    total_page = 489343
    # 遍历爬取每页的数据
    for page in range(1, total_page):
        # 获取的html数据
        payload={
            'proselect': '',
            'cityselect': '',
            'disselect': '',
            'curPageNO': page
        }
        url = 'http://www.hljcredit.gov.cn/WebCreditQueryService.do?gssearch&type=sxbzxr&detail=true&sxbzxrmc='
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
        parse_data_write_file(result)
        # time.sleep(0.5)


# 数据的解析,写到文件中
def parse_data_write_file(msg):
    rest = json.loads(msg)
    if rest.has_key('msg'):
        users = rest["msg"]
        for user in users:
            try:
                with open('./hljcredit_blacklist.json', 'a') as f:
                    user = json.dumps(user).decode("unicode-escape")
                    f.write(user)
                    f.write("\n")
            except Exception as e:
                print(e)


if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())

