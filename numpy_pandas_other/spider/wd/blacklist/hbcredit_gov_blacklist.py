#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      信用湖北黑名单的爬取
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
    'Cookie': 'JSESSIONID=7AE9CB13F23A1572D9674C1A8527DA7A; '
              '_gscu_1116912920=03299260e5f68q13; '
              '_gscs_1116912920=03299260s05yze13|pv:39; '
              '_gscbrs_1116912920=1; '
              '_trs_uv=5agv_675_j6ltkd9s; '
              '_trs_ua_s_1=jxd5_675_j6ltkd9r',
    'Host': 'www.hbcredit.gov.cn',
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
        users = soup.find_all('p', class_='xkgs_title')
        for user in users:
            # 返回结果
            result = collections.OrderedDict()
            try:
                user_info_url = user.a['href']
                user_info_url = 'http://www.hbcredit.gov.cn' + user_info_url
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
                user_soup_trs = user_soup.find_all("div", class_="display_con")[0].find_all("tr")
                tr_flag = 0
                for tr in user_soup_trs:
                    if 1 == tr_flag:
                        result['姓名'] = tr.find_all('td')[1].get_text(strip=True)
                    if 2 == tr_flag:
                        result['身份证号'] = tr.find_all('td')[1].get_text(strip=True)
                    if 3 == tr_flag:
                        result['处罚日期'] = tr.find_all('td')[1].get_text(strip=True)
                    if 4 == tr_flag:
                        result['处罚内容'] = tr.find_all('td')[1].get_text(strip=True)\
                            .replace('"', '')\
                            .replace('\n', '')\
                            .replace('\t', '')\
                            .replace('\r', '')
                    if 5 == tr_flag:
                        result['处罚机关'] = tr.find_all('td')[1].get_text(strip=True)
                    if 6 == tr_flag:
                        result['事项名称'] = tr.find_all('td')[1].get_text(strip=True)
                    if 7 == tr_flag:
                        result['来源单位'] = tr.find_all('td')[1].get_text(strip=True)
                    tr_flag += 1
                # 添加到集合中
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
    total_page = 287
    # 遍历爬取每页的数据
    for page in range(1, total_page):
        # 获取的html数据
        payload={
            'bt': '',
            'bmmc': '',
            'sxmc': '',
            'type': 'BlackList',
            'pageIndex': page
        }
        url = 'http://www.hbcredit.gov.cn/credithb/gkgs/list.html'
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
                with open('./hbcredit_blacklist.json', 'a') as f:
                    user = json.dumps(user).decode("unicode-escape")
                    f.write(user)
                    f.write("\n")
            except Exception as e:
                print(e)


if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data())

