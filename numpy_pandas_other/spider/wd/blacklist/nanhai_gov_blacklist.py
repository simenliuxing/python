#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      佛山市南海区黑名单的爬取
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
    'Cache-Control': 'max-age=0',
    'Cookie': 'JSESSIONID=6640865B3E7DFAFF9233A461296950E5; '
              'yunsuo_session_verify=b1b5db69a4584b3cef484e503323a297; '
              '_gscu_339891467=00972756a759fc83; '
              '_gscs_339891467=t01061989deqquy10|pv:4; '
              '_gscbrs_339891467=1',
    'Host': 'fayuan.nanhai.gov.cn',
    'Proxy-Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
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
        users = soup.find_all('div', class_='courtbig')[0].find_all('tr')
        for user in users:
            # 详细信息地址
            url_detail = 'http://fayuan.nanhai.gov.cn/cms/sites/nhfayuan/'
            # 返回结果
            result = collections.OrderedDict()
            try:
                tds = user.find_all("td")
                url_user = tds[0].a['href']
                url_user_detail = url_detail + url_user
                user_info = spider_data(url_user_detail)
                # 如果没有获取到数据则重试多次
                if user_info == -1:
                    # 如果没有爬取成功则，重爬
                    for num in range(1, 10):
                        time.sleep(0.5)
                        print(num)
                        if user_info == -1:
                            user_info = spider_data(url_user_detail)
                        else:
                            break
                # 二级链接下的详细信息
                user_soup = BeautifulSoup(user_info, "lxml")
                user_soup_trs = user_soup.find_all("div", class_="tab01_md")[0].find_all("tr")
                for tr in user_soup_trs:
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
def spider_data(url):
    try:
        try:
            # 使用代理
            res = requests.get(url, timeout=10, headers=headers, proxies=proxies)
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
def re_spider_page_data():
    total_page = 114
    # 遍历爬取每页的数据
    for page in range(1, total_page):
        # 获取的html数据
        url = "http://fayuan.nanhai.gov.cn/cms/sites/nhfayuan/court_list.jsp?type=1&page="+str(page)+""
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
        print("第:"+str(page)+"页写文件")
        print(result)
        with open('./nanhai_gov_blacklist.json', 'a') as f:
            f.write(result)
            f.write("\n")

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
