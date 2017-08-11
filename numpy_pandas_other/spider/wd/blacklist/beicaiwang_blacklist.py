#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      贝才网黑名单的爬取
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
    'Cookie': '__qc_wId=769; '
              'pgv_pvid=2647345061; '
              'Asessionid=BBMEYPSuo7SB3Rh7RKa6SQ$$; '
              'JSESSIONID=6927DCCD824BBB98E919265C8F19B603; '
              'flashadv=true; '
              'Hm_lvt_c081b0d069f993c94291e40cb636375b=1500610413; '
              'Hm_lpvt_c081b0d069f993c94291e40cb636375b=1501062720',
    'Host': 'www.thebetterchinese.com',
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
    users = soup.find_all("div", class_="detention_all")
    for user in users:
        try:
            # 贝才的官网url
            url_home = 'http://www.thebetterchinese.com'
            # 返回结果
            result = collections.OrderedDict()
            a_tag = user.find_all('a')[1]['href']
            url_home = url_home + a_tag
            # 获取二级链接
            user_info = spider_data(url_home, None)
            # 二级链接下的详细信息
            user_soup = BeautifulSoup(user_info, "lxml")
            user_soup_ul_li = user_soup.find_all("ul", class_="etention_ytg")[0].find_all("li")
            for li in user_soup_ul_li:
                try:
                    li_info = li.get_text(strip=True)
                    li_info_array = li_info.split('：')
                    result[li_info_array[0]] = li_info_array[1]
                except Exception as e:
                    print(e)
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
            res = requests.post(url, timeout=10, headers=headers, proxies=proxies, params=payload)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.post(url, timeout=10, headers=headers, params=payload)
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
    # total_page = re_spider_total_page()
    if 'L' == url_type:
        total_page = 24
    if 'P' == url_type:
        total_page = 16
    # 遍历爬取每页的数据
    for page in range(0, total_page):
        payload = {"pageNo": str(page+1),
                   "pageSize": "10"
                   }
        # 获取的html数据
        if 'L' == url_type:
            url = "http://www.thebetterchinese.com/Blacklist/Lai.mvc"
        if 'P' == url_type:
            url = "http://www.thebetterchinese.com/Blacklist/Pian.mvc"
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
        if 'L' == url_type:
            print("老赖，第:"+str(page)+"页写文件")
        if 'P' == url_type:
            print("骗子，第:" + str(page) + "页写文件")
        # print(result)
        with open('./beicaiwang_blacklist.json', 'a') as f:
            f.write(result)
            f.write("\n")

if __name__ == '__main__':
    for n in range(1, 2):
        print(re_spider_page_data('L'))
        print(re_spider_page_data('P'))
