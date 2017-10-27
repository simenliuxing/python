#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      安徽省高级人民法院黑名单的爬取
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
    'Cookie': 'JSESSIONID=9CAA8C2BEE80C74B1952EFA9E69C4150; '
              'wafenterurl=L3NzZncvZnltaC8xNDUxL3p4Z2suaHRtP3N0PTAmcT0mc3hseD0xJmJ6e'
              'HJseD0xJmNvdXJ0X2lkPSZienhybWM9JnpqaG09JmFoPSZzdGFydENwcnE9JmVuZENwcnE9JnBhZ2U9Mw==; '
              '__utma=161156077.495504895.1501221471.1501221471.1501221471.1; '
              '__utmc=161156077; '
              '__utmz=161156077.1501221471.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
              'wafcookie=6638c7e043d4634e31fc03f98c44d6c6; '
              'wafverify=1ac90afbc1da7e6e86e4f07057416bcb; '
              'wzwsconfirm=7711ddd10a544f8efa642db4685e86e8; '
              'wzwstemplate=OA==; '
              'clientlanguage=zh_CN; '
              'JSESSIONID=0E40DC7D29A84A4528787317B590F218; '
              'ccpassport=601fd92b79652fe0489b52310512d73b; '
              'wzwschallenge=-1; '
              'wzwsvtime=1501226469',
    'Host': 'www.ahgyss.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://www.ahgyss.cn/ssfw/fymh/1451/zxgk.htm'
               '?st=0&q=&sxlx=&bzxrlx=&court_id=&bzxrmc=&zjhm=&ah=&startCprq=&endCprq=&page=11',
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
        users = soup.find_all('table', class_='table_01')[0].find_all('tr')
        for user in users:
            # 返回结果
            result = collections.OrderedDict()
            try:
                tr_user = user['onclick']
                url_user = tr_user.split('(')[1].replace('\'', '').replace(')', '').replace(';', '')
                # 详细信息地址
                url_detail = 'http://www.ahgyss.cn/ssfw/pub/zxgk/detail.htm?bh='+url_user+'&fy=1451'
                user_info = spider_data(url_detail)
                # 如果没有获取到数据则重试多次
                if user_info == -1:
                    # 如果没有爬取成功则，重爬
                    for num in range(1, 10):
                        time.sleep(0.5)
                        print(num)
                        if user_info == -1:
                            user_info = spider_data(url_detail)
                        else:
                            break
                # 二级链接下的详细信息
                user_soup = BeautifulSoup(user_info, "lxml")
                user_soup_trs = user_soup.find_all("table", class_="table_01 table_02")[0].find_all("tr")
                flag = 1
                for tr in user_soup_trs:
                    if flag != 1:
                        tr_info = tr.get_text(strip=True)
                        tr_info_array = tr_info.split('：')
                        result[tr_info_array[0]] = tr_info_array[1]
                    flag += 1
                # 追加到集合中
                if flag != 1:
                    data_list.append(result)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return data_list


# 爬取数据
def spider_data(url):
    try:
        try:
            # 使用代理
            res = requests.get(url, timeout=10, proxies=proxies, headers=headers)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.get(url, timeout=10, headers=headers)
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
def re_spider_page_data(url_type):
    # 有案件
    if 'A' == url_type:
        total_page = 795
    # 失信
    if 'S' == url_type:
        total_page = 1885
    # 遍历爬取每页的数据
    for page in range(1, total_page):
        # 获取的html数据
        # 有案件
        if 'A' == url_type:
            url = "http://www.ahgyss.cn/ssfw/fymh/1451/zxgk.htm" \
                  "?st=0&q=&sxlx=1&bzxrlx=1&court_id=&bzxrmc=&zjhm=&ah=&startCprq=&endCprq=&page=" + str(page)
        # 失信
        if 'S' == url_type:
            url = "http://www.ahgyss.cn/ssfw/fymh/1451/zxgk.htm" \
                  "?st=0&q=&sxlx=5&bzxrlx=1&court_id=&bzxrmc=&zjhm=&ah=&startCprq=&endCprq=&page=" + str(page)
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
        # 解析数据
        result = parse_data(html)
        # 包装数据
        result = package_data(result)
        # 有案件
        if 'A' == url_type:
            print("有案件人员，第:" + str(page) + "页写文件")
        # 失信
        if 'S' == url_type:
            print("失信人员，第:" + str(page) + "页写文件")
        print(result)
        parse_data_write_file(result)
        time.sleep(0.5)


# 数据的解析,写到文件中
def parse_data_write_file(msg):
    rest = json.loads(msg)
    if rest.has_key('msg'):
        users = rest["msg"]
        for user in users:
            try:
                with open('./ahgyss_blacklist.json', 'a') as f:
                    user = json.dumps(user).decode("unicode-escape")
                    f.write(user)
                    f.write("\n")
            except Exception as e:
                print(e)

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data('A'))
        print(re_spider_page_data('S'))
