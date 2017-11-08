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
                                     '微博热点',
                                     time_sleep.strftime('%Y-%m-%d')))
            connection.commit()
    except Exception as e:
        print(e)
    finally:
        connection.close()

class Weibo:
        # # 将your cookie替换成自己的cookie
        cookie = {'Cookie':
                'SINAGLOBAL=2375035684357.2964.1502788001389; _s_tentry=blog.csdn.net; Apache=4880734666771.718.1503724416842; ULV=1503724417469:2:2:1:4880734666771.718.1503724416842:1502788001816; YF-V5-G0=a906819fa00f96cf7912e89aa1628751; YF-Page-G0=c81c3ead2c8078295a6f198a334a5e82; YF-Ugrow-G0=57484c7c1ded49566c905773d5d00f82; TC-V5-G0=40eeee30be4a1418bde327baf365fcc0; UM_distinctid=15f294d93fe909-06177db9c2cac3-323f5c0f-1fa400-15f294d93ffd34; login_sid_t=7336ca34f04f1c17579bb10b8bdfc863; appkey=; WB_register_version=b81eb8e02b10d728; user_active=201710271600; user_unver=bb426661b6cda5efe95e3ad53d271583; wb_timefeed_6394930693=1; WBtopGlobal_register_version=b81eb8e02b10d728; SCF=AmoPOYQKcM--VgFvuLaVWH6gWxTEeET2UXf5r9HP_AJlNanoiUckb_C0PN893lKs4BgjhX-oe9x3bXbkTDMlxt0.; SUHB=0XD1AuNWZiFkFV; un=l492341344@163.com; SUB=_2AkMuo0stdcNxrAVSkfwcz2vkZY5H-jyddiLbAn7uJhMyAxgv7g81qSW6ma3lZOl0IL17wCnlfJhkdpDqUw..; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WFTnruZG6SceBYiNqx.DkoF5JpV2J7X1Kz0Sh20Shx5eKq0TJSadBtt; cross_origin_proto=SSL; WBStorage=54efc81d62ba349e|undefined; UOR=ent.ifeng.com,widget.weibo.com,login.sina.com.cn'
                  }

        # 爬取数据
        def spider_data(self, url):
            try:
                try:
                    # 使用代理
                    res = requests.get(url, timeout=10, cookies=self.cookie, proxies=proxies)
                except ProxyError:
                    print("ProxyError Exception ,use no proxies ")
                    # 不使用代理
                    res = requests.get(url, timeout=10, cookies=self.cookie)
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

        # 获取微博头条标题
        def get_wb_toutiao(self, page):
                try:
                    #毫秒值
                    t = time_sleep.time()
                    nowTime = lambda: int(round(t * 1000))
                    # url = 'https://d.weibo.com/p/aj/discover/loading?ajwvr=6&id=623751_1&uid=6394930693&page='+str(page)+'&__rnd='+str(nowTime())
                    url = 'https://weibo.com/a/aj/transform/loadingmoreunlogin' \
                          '?ajwvr=6' \
                          '&category=1760' \
                          '&page='+str(page)+'' \
                          '&lefnav=0' \
                          '&__rnd='+str(nowTime())
                    print(url)
                    html = self.re_spider_page_data(url)
                    html = html.decode("utf-8")
                    html = json.loads(html)
                    html = html['data']
                    soup = BeautifulSoup(html, "lxml")
                    feeds_div = soup.find_all('div', 'UG_list_b')
                    for feed in feeds_div:
                        try:
                            time_sleep.sleep(2)
                            # 返回结果
                            # 文章链接
                            result = collections.OrderedDict()
                            feed_url = feed.find('h3', class_='list_title_b').a['href']
                            # 文章标题
                            wb_title = feed.find('h3', class_='list_title_b').a.get_text().strip()
                            # 文章发布时间
                            wb_time = feed.find('div', class_='subinfo_box clearfix').find_all('span', class_='subinfo S_txt2')[1].get_text().strip()
                            # 文章内容
                            wb_content = wb_title
                            result['文章链接'] = feed_url
                            result['文章标题'] = wb_title
                            result['文章发布时间'] = wb_time
                            result['文章内容'] = wb_content
                            # 追加到集合中
                            print(json.dumps(result, ensure_ascii=False, indent=2))
                            # insert_db(json.dumps(result, ensure_ascii=False))
                            # self.write_file(json.dumps(result, ensure_ascii=False), 'wb_toutiao.json')
                        except Exception as e:
                            print("\033[0;31m Error: %s\033[0m" % e)
                            print("\033[0;31m 异常的url ：: %s\033[0m" % feed_url)
                except Exception as e:
                    print("Error: ", e)
                    traceback.print_exc()

        # 获取微博热门
        def get_wb_remen(self, page):
            try:
                # 毫秒值
                t = time_sleep.time()
                nowTime = lambda: int(round(t * 1000))
                url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist' \
                      '?ajwvr=6' \
                      '&domain=102803_ctg1_1760_-_ctg1_1760' \
                      '&pagebar='+str(page-1) + \
                      '&tab=home' \
                      '&current_page='+str(page)+ \
                      '&pre_page=1' \
                      '&page=1' \
                      '&pl_name=Pl_Core_NewMixFeed__3' \
                      '&id=102803_ctg1_1760_-_ctg1_1760' \
                      '&script_uri=/' \
                      '&feed_type=1' \
                      '&domain_op=102803_ctg1_1760_-_ctg1_1760' \
                      '&__rnd='+str(nowTime())
                print(url)
                html = self.re_spider_page_data(url)
                html.decode("utf-8")
                html = json.loads(html)
                html = html['data']
                soup = BeautifulSoup(html, "lxml")
                feeds_div = soup.find_all('div', 'WB_cardwrap WB_feed_type S_bg2 WB_feed_vipcover WB_feed_like')
                for feed in feeds_div:
                    try:
                        # 返回结果
                        result = collections.OrderedDict()
                        # 微博链接
                        wb_url = feed.find('div', class_='WB_from S_txt2').a['href']
                        # 微博博主
                        wb_info = feed.find('div', class_='WB_info').get_text().strip()
                        # 发布时间
                        wb_time = feed.find('div', class_='WB_from S_txt2').get_text().strip()
                        # 微博内容
                        wb_content = feed.find('div', class_='WB_text W_f14').get_text().strip()

                        # 转发次数
                        wb_pat = feed.find('ul', class_='WB_row_line WB_row_r4 clearfix S_line2').find_all('li')
                        wb_pos = wb_pat[1].get_text().strip().replace(' ', '')
                        # 评论次数
                        wb_arrow = wb_pat[2].get_text().strip().replace(' ', '')
                        # 点赞次数
                        wb_thumbs = wb_pat[3].get_text().strip().replace('ñ', '')
                        result['博主链接'] = wb_url
                        result['微博博主'] = wb_info
                        result['发布时间'] = wb_time
                        result['微博内容'] = wb_content
                        result['转发次数'] = wb_pos
                        result['评论次数'] = wb_arrow
                        result['点赞次数'] = wb_thumbs
                        # 追加到集合中
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                        self.write_file(json.dumps(result, ensure_ascii=False), 'wb_remen.json')
                    except Exception as e:
                        print("\033[0;31m Error: %s\033[0m" % e)

            except Exception as e:
                print("Error: ", e)
                traceback.print_exc()

        # 运行爬虫
        def start(self):
            try:
                print(time_sleep.strftime("%Y-%m-%d %H:%M:%S",time_sleep.localtime()) + ":开始爬取>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                for i in range(1, 4):
                    self.get_wb_toutiao(i)
                    time_sleep.sleep(5)
                print("===========================================================================")
            except Exception as e:
                print("Error: ", e)


def main():
    try:
        wb = Weibo()  # 调用Weibo类，创建微博实例wb
        wb.start()  # 爬取微博信息
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()