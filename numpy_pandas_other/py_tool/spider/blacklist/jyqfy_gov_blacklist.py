#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      德阳市旌阳区黑名单的爬取
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
    'Cookie': 'ASPSESSIONIDAASSBTTT=KPDFOMEDNFJPJDLFLHEOELOG; '
              'ASPSESSIONIDQCDRDDST=JPNNGMPDHBGCDBBGHNLNAIEP; '
              'ASPSESSIONIDSQBRQTTR=PPCHIBGABCAGKICHLICPPCCA; '
              'safedog-flow-item=; '
              '_gscu_1136629196=00970718o2b0dr19; '
              '_gscs_1136629196=t01126027wk16td75|pv:6; '
              '_gscbrs_1136629196=1',
    'Host': 'www.jyqfy.gov.cn',
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
    users = soup.find_all("ul", class_="N_list")[0].find_all('li')
    for user in users:
        try:
            # 返回结果
            result = collections.OrderedDict()
            a_href = user.find_all("a")[0]['href']
            # url地址
            cq_url = 'http://www.jyqfy.gov.cn'+a_href
            # 获取二级链接
            user_info = spider_data(cq_url)
            # 二级链接下的详细信息
            # 如果没有获取到数据则重试多次
            if user_info == -1:
                # 如果没有爬取成功则，重爬
                for num in range(1, 10):
                    time.sleep(0.5)
                    print(num)
                    if user_info == -1:
                        user_info = spider_data(cq_url)
                    else:
                        break
            user_soup = BeautifulSoup(user_info, "lxml")
            user_soup_p = user_soup.find_all("div", class_="info_content")[0].find_all('p')
            flag = 1
            for p in user_soup_p:
                try:
                    if 1 != flag:
                        user_info = p.get_text().replace("\n", "") \
                            .replace("\t", "") \
                            .replace("\r", "") \
                            .strip()
                        user_info_array = user_info.split("：")
                        if len(user_info_array) >= 2:
                            result[user_info_array[0].replace("\n", "").replace("\t", "").replace("\r", "").strip()] = \
                                user_info_array[1].replace("\n", "").replace("\t", "").replace("\r", "").strip()
                        flag += 1
                except Exception as e:
                    print('small,,,,', e)
            # 追加到集合中
            if 1 != flag:
                data_list.append(result)
        except Exception as e:
            print('big,,,,', e)
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
            res = requests.get(url, headers=headers, timeout=10)
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
    # return json.dumps(message, indent=2).decode("unicode-escape")
    return json.dumps(message).decode("unicode-escape")


# 爬取每页的具体数据（处理超时异常,默认10次重试）
def re_spider_page_data():
    tatal_page = 3
    # 遍历爬取每页的数据
    for page in range(1, tatal_page):
        # 获取的html数据
        url = 'http://www.jyqfy.gov.cn/list/?12_'+str(page)+'.html'
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
        # print(result)
        parse_data_write_file(result)


# 数据的解析,写到文件中
def parse_data_write_file(msg):
    rest = json.loads(msg)
    users = rest["msg"]
    for user in users:
        try:
            with open('./jyqfy_gov_blacklist.json', 'a') as f:
                user = json.dumps(user).decode("unicode-escape")
                f.write(user)
                f.write("\n")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
