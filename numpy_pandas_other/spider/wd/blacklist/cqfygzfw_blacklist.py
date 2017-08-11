#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      重庆法院黑名单的爬取
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
    users = soup.find_all("table", class_="table_ys")[0].find_all('tr')
    for user in users:
        try:
            # 返回结果
            result = collections.OrderedDict()
            a_href = user.find_all("td")[0].a['href']
            a_href = a_href.split('(')[1].replace('\'', '').replace(')', '')
            # url地址
            cq_url = 'http://www.cqfygzfw.com/court/gg_loadGsbg.shtml?gsbg.id='+a_href+'&gsbg.lx=3'
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
            user_soup_tr = user_soup.find_all("tr", class_="tr_color")
            flag = 1
            for user_tr in user_soup_tr:
                try:
                    # 过滤掉企业
                    if len(user_soup_tr) == 5:
                        user_tds = user_tr.find_all('td')
                        if 1 == flag:
                            result['案件字号'] = user_tds[1].get_text()
                            result['法院'] = user_tds[3].get_text()
                        if 2 == flag:
                            result['立案日期'] = user_tds[1].get_text()
                        if 3 == flag:
                            result['姓名'] = user_tds[1].get_text()
                            result['性别'] = user_tds[3].get_text()
                        if 4 == flag:
                            result['民族'] = user_tds[1].get_text()
                            result['身份证号码'] = user_tds[3].get_text()
                        if 5 == flag:
                            result['单位名称'] = user_tds[1].get_text()
                        flag += 1
                except Exception as e:
                    print('small,,,,', e)
            # 追加到集合中,过滤掉企业
            if len(user_soup_tr) == 5:
                data_list.append(result)
        except Exception as e:
            print('big,,,,', e)
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
    tatal_page = 9039
    # 遍历爬取每页的数据
    for page in range(1, tatal_page):
        # 获取的html数据
        url = 'http://www.cqfygzfw.com/court/gg_listgsbgmore.shtml?gsbg.lx=3&page='+str(page)
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
        parse_data_write_file(result)


# 数据的解析,写到文件中
def parse_data_write_file(msg):
    rest = json.loads(msg)
    users = rest["msg"]
    for user in users:
        try:
            with open('./cqfygzfw_blacklist.json', 'a') as f:
                user = json.dumps(user).decode("unicode-escape")
                f.write(user)
                f.write("\n")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())
