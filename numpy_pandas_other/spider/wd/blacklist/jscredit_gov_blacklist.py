#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      信用江苏黑名单的爬取
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
    'Cookie': 'ADMINCONSOLESESSION=DOfojmXJI6Z9WVj5RDeYn9X5o4MFmdi1aS0m6pr9BAJXmkGU0Ra7!1511183603; '
              '_gscu_240771025=026735364bkjby17; '
              '_gscs_240771025=t02845397s8y2s317|pv:30; '
              '_gscbrs_240771025=1',
    'Host': 'www.jscredit.gov.cn',
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
        users = soup.find(id='bmTable').find_all('tbody')[0].find_all('tr')
        for user in users:
            # 返回结果
            result = collections.OrderedDict()
            try:
                user_info = user.find_all('td')
                result['被执行人姓名'] = user_info[1].get_text(strip=True)
                result['身份证件号'] = user_info[2].get_text(strip=True)
                result['立案时间'] = user_info[3].get_text(strip=True)
                result['案号'] = user_info[4].get_text(strip=True)
                data_list.append(result)

                # onclick = user.find_all('td')[0].a['onclick']
                # onclick = onclick.split('","')[0].split('("')[1]
                # # 详细信息地址
                # url_detail = 'http://www.jscredit.gov.cn/creditInfo/webapp/cms/sfysxbzxr_sfysxbzxrDetail.htm?' \
                #              '&dataid='+onclick
                # user_info = spider_data(url_detail)
                # # 如果没有获取到数据则重试多次
                # if 'detailerror1.html' in user_info:
                #     # 如果没有爬取成功则，重爬
                #     for num in range(1, 10):
                #         time.sleep(0.5)
                #         print(num)
                #         if 'detailerror1.html' in user_info:
                #             user_info = spider_data(url_detail)
                #         else:
                #             break
                # # 二级链接下的详细信息
                # user_soup = BeautifulSoup(user_info, "lxml")
                # user_soup_trs = user_soup.find_all("table", class_="tab tab_tt")[0].find_all("tr")
                # for tr in user_soup_trs:
                #     tr_info = tr.get_text(strip=True)
                #     tr_info_array = tr_info.split(':')
                #     result[tr_info_array[0]] = tr_info_array[1]

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
def re_spider_page_data():
    total_page = 5471
    # 遍历爬取每页的数据
    for page in range(1, total_page):
        # 获取的html数据
        url = "http://www.jscredit.gov.cn/creditInfo/webapp/cms/sfysxbzxr_sfysxbzxrList.htm?dto.pageNo=" + str(page)
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
                with open('./jscredit_blacklist.json', 'a') as f:
                    user = json.dumps(user).decode("unicode-escape")
                    f.write(user)
                    f.write("\n")
            except Exception as e:
                print(e)


def json_mat():
    with open('./jscredit_blacklist.json', 'r') as f:
        for line in f:
            json_line = json.loads(line)
            if json_line[u'\u8eab\u4efd\u8bc1\u4ef6\u53f7']:
                with open('./jscredit_blacklist_new.json', 'a') as f:
                    user = json.dumps(json_line).decode("unicode-escape")
                    f.write(user)
                    f.write("\n")


if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())

