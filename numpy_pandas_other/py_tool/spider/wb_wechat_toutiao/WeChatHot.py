#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import requests
import traceback
from bs4 import BeautifulSoup
import time as time_sleep
import json
import collections
from requests.exceptions import ProxyError
import pymysql.cursors


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
                                     '微信热点',
                                     time_sleep.strftime('%Y-%m-%d')))
            connection.commit()
    except Exception as e:
        print(e)
    finally:
        connection.close()

# 微信热门爬取
class WeChat:
        # # 将your cookie替换成自己的cookie
        cookie = {'Cookie':
                'IPLOC=CN3301; SUV=002023267AE0CFCD598D43ADECFBE034; CXID=A00A7198722F777A8DB09B116B627BB2; wuid=AAGlJtW6GgAAAAqGCmL9WwYAIAY=; LSTMV=381%2C143; LCLKINT=5320; usid=_5aKYfXoAHU8qgwR; ABTEST=1|1509087767|v1; JSESSIONID=aaa57Ac9EO3Sf-SSYtv8v; weixinIndexVisited=1; ad=mZllllllll2Bu$TPlllllVXTchGlllllWmR58yllllwlllll4Cxlw@@@@@@@@@@@; SUID=CDCFE07A620A860A599AADE0000E3F0B; sct=6; SNUID=10133CA6DBD9819E74CB365CDCB176D6'
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

        # 数据的解析,写到文件中
        def write_file(self, msg, path):
            try:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(msg)
                    f.write('\n')
            except Exception as e:
                print(e)

        # 获取微信热门文章
        def get_wx_remen(self, page):
                try:
                    url = 'http://weixin.sogou.com/'
                    # 下一页的数据
                    # url = 'http://weixin.sogou.com/pcindex/pc/pc_0/'+str(page)+'.html'
                    print(url)
                    html = self.re_spider_page_data(url)
                    soup = BeautifulSoup(html, "lxml")
                    feeds_div = soup.find('ul', class_='news-list').find_all('li')
                    for feed in feeds_div:
                        try:
                            time_sleep.sleep(5)
                            # 返回结果
                            result = collections.OrderedDict()
                            # 文章链接
                            feed_url = feed.find('div', class_='txt-box').h3.a['href']
                            html = self.re_spider_page_data(feed_url)
                            soup = BeautifulSoup(html, "lxml")
                            # 文章标题
                            feed_title = soup.find('h2', class_='rich_media_title').get_text().strip()
                            # 发表时间
                            feed_time = soup.find_all('em', class_='rich_media_meta rich_media_meta_text')[0].get_text().strip()
                            # 公众号
                            feed_gong = soup.find('a', class_='rich_media_meta rich_media_meta_link rich_media_meta_nickname').get_text().strip()
                            # 文章内容
                            feed_content = soup.find('div', class_='rich_media_content ').get_text().strip()
                            result['文章链接'] = feed_url
                            result['文章标题'] = feed_title
                            result['文章发布时间'] = feed_time
                            result['公众号'] = feed_gong
                            result['文章内容'] = feed_content
                            # 追加到集合中
                            print(json.dumps(result, ensure_ascii=False, indent=2))
                            # insert_db(json.dumps(result, ensure_ascii=False))
                            # self.write_file(json.dumps(result, ensure_ascii=False), 'wx_remen.json')
                        except Exception as e:
                            print("\033[0;31m Error: %s\033[0m" % e)
                            print("\033[0;31m 异常的url ：: %s\033[0m" % feed_url)
                except Exception as e:
                    print("Error: ", e)
                    traceback.print_exc()

        # 运行爬虫
        def start(self):
            try:
                for i in range(1, 2):
                    self.get_wx_remen(i)
                print("===========================================================================")
            except Exception as e:
                print("Error: ", e)


def main():
    try:
        wx = WeChat()  # 调用Weibo类，创建微博实例wb
        wx.start()  # 爬取微博信息
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()