#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import requests
import traceback
import time as time_sleep
import json
import collections
from requests.exceptions import ProxyError
import pymysql.cursors
from bs4 import BeautifulSoup


# 代理
proxies = {
  "HTTP": "http://110.73.6.231:8123",
  "HTTP": "http://111.155.116.215:8123",
  "HTTP": "http://115.46.67.255:8123",
  "HTTP": "http://111.155.116.211:8123",
  "HTTP": "http://110.73.2.178:8123",
  "HTTP": "http://182.88.134.110:8123",
  "HTTP": "http://110.73.6.124:8123",
  "HTTP": "http://116.226.90.12:808",
  "HTTPS": "https://221.229.44.14:808",
  "HTTPS": "https://114.230.234.223:808",
  "HTTPS": "https://218.108.107.70:909"
}

# 数据库配置
config = {
    'host': '172.16.34.48',
    'port': 3306,
    'user': 'bigdata_read',
    'password': 'bigdata_read',
    'db': 'cgjrRisk',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


# 写到mysql中
def insert_db(result):
    connection = pymysql.connect(**config)
    try:
        result = json.loads(result)
        with connection.cursor() as cursor:
            sql = 'INSERT INTO spider_redian (url, title, ' \
                      'time, content, source, spider_time)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (result['文章链接'],
                                     result['文章标题'],
                                     result['文章发布时间'],
                                     result['文章内容'],
                                     '百度热点',
                                     time_sleep.strftime('%Y-%m-%d')))
            connection.commit()
    except Exception as e:
        print(e)
    finally:
        connection.close()


# 百度热点爬取
class Baidu:
        # # 将your cookie替换成自己的cookie
        cookie = {'Cookie':
                'UM_distinctid=15f511687c7c7c-0895c079daf0f6-323f5c0f-1fa400-15f511687c8925; uuid="w:426b339bc89a4d52bf8c9716d8028f80"; _ba=BA0.2-20171025-51d9e-kJ1I27xlSdCAdz0lTKQY; sso_login_status=0; _ga=GA1.2.532277549.1508893939; tt_webid=6480649968964683278; WEATHER_CITY=%E5%8C%97%E4%BA%AC; utm_source=toutiao; __tasessionId=zrrss15m41509947045509; __user_from=toutiao; CNZZDATA1259612802=755582950-1508890750-https%253A%252F%252Fwww.google.co.jp%252F%7C1509943755; tt_webid=6480649968964683278'
                  }

        # 爬取数据
        def spider_data(self, url):
            try:
                try:
                    # 使用代理
                    res = requests.get(url, timeout=10, proxies=proxies)
                except ProxyError:
                    print("ProxyError Exception ,use no proxies ")
                    # 不使用代理
                    res = requests.get(url, timeout=10)
                res.encoding = 'utf-8'
                return res.content
            except Exception as e:
                print("爬取失败", e)
                return -1

        # 爬取每页的具体数据（处理超时异常,默认10次重试）
        def re_spider_page_data(self, url):
            # 如果没有爬取成功则，重爬
            for num in range(1, 10):
                html = self.spider_data(url)
                if html == -1:
                    time_sleep.sleep(5)
                    print(num + 1)
                    html = self.spider_data(url)
                else:
                    return html

        # 获取百度热点
        def get_db_toutiao(self):
                try:
                    url = 'http://top.baidu.com/buzz?b=1&fr=topbuzz_b341'
                    print(url)
                    html = self.re_spider_page_data(url)
                    soup = BeautifulSoup(html, "lxml")
                    feeds_div = soup.find_all('td', class_='keyword')
                    flag = 0
                    for feed in feeds_div:
                        try:
                            if flag == 10:
                                break
                            # 返回结果
                            result = collections.OrderedDict()
                            bd_context = feed.a.get_text().strip()
                            # 文章链接
                            feed_url = 'https://www.baidu.com/baidu?cl=3&tn=SE_baiduhomet8_jmjb7mjw&fr=top1000&wd='+bd_context
                            # 文章发布时间和作者
                            bd_time = time_sleep.strftime('%Y-%m-%d')
                            result['文章链接'] = feed_url
                            result['文章标题'] = bd_context
                            result['文章发布时间'] = bd_time
                            result['文章内容'] = bd_context
                            # 追加到集合中
                            print(json.dumps(result, ensure_ascii=False, indent=2))
                            # insert_db(json.dumps(result, ensure_ascii=False))
                            flag = flag + 1
                        except Exception as e:
                            print("Error: %s" % e)
                            print("异常的url ：: %s" % feed_url)
                except Exception as e:
                    print("Error: ", e)
                    traceback.print_exc()

        # 运行爬虫
        def start(self):
            try:
                print(time_sleep.strftime("%Y-%m-%d %H:%M:%S",
                                          time_sleep.localtime()) + ":  开始爬取>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                self.get_db_toutiao()
                print(time_sleep.strftime("%Y-%m-%d %H:%M:%S",
                                      time_sleep.localtime()) + ":  结束爬取>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            except Exception as e:
                print("Error: ", e)


def main():
    try:
        tt = Baidu()
        tt.start()
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()