#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      宜贷网标的爬虫
"""
import pymysql.cursors
import time
import requests
import json
import sys
import collections
from bs4 import BeautifulSoup
from lxml import etree
from requests.exceptions import ProxyError
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# 请求头
headers = {
    "Cookie": "PHPSESSID = 55fcc0b25ee58743b1c3dc67cb7e8a92; "
              "Hm_lvt_8e0b98ef5dbcad55cb6284bf790594e0 = 1496732879, 1496733205, 1496890061, 1498007897; "
              "Hm_lpvt_8e0b98ef5dbcad55cb6284bf790594e0 = 1498013275",
    "Host": "www.yidai.com",
    "Referer": "https://www.yidai.com/invest/index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Upgrade-Insecure-Requests": "1"
    }
# 代理
proxies = {
  "HTTPS": "https://114.230.234.223:808",
  "HTTP": "http://110.73.6.124:8123",
  "HTTPS": "https://221.229.44.14:808",
  "HTTP": "http://116.226.90.12:808",
  "HTTPS": "https://218.108.107.70:909"
}

# 平台名称
source_from = "宜贷网"
# 详细信息的链接
detail_link_san = "https://www.yidai.com/invest/index.html"
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


def parse_data(result):
    """数据的抽取

    :param result: 请求到的数据
    :return: :list集合
    :rtype:
    """
    # 一页的数据
    data_list = []
    soup = BeautifulSoup(result)
    tags = soup.find_all("div", class_="item")
    for tag in tags:
        try:
            # 返回结果
            result = collections.OrderedDict()
            result['来源平台'] = source_from
            tag = tag.find_all("li")
            # 标id
            result["标id"] = tag[0].find_all("a")[1]['href'].split("invest/")[1].split(".")[0]
            # 标名称
            result["标名称"] = tag[0].find_all("a")[1]['title'].decode('utf-8')
            # 项目总额
            result['项目总额'] = float(tag[1].get_text().replace("元", "").replace(",", ""))
            # 年化收益
            rate = tag[2].span.text.replace("\n", "").replace("\t", "").replace(" ", "").replace("\r", "")
            rate = rate.split("%")
            result['年化收益'] = rate[0]+"%"
            if len(rate) > 2:
                # 加息
                result['加息'] = rate[1]+"%"
            else:
                # 加息
                result['加息'] = ""
            # 投资期限
            result['投资期限'] = tag[3].get_text().replace("\n", "").replace("\t", "").replace(" ", "").replace("\r", "")
            # 还款方式
            result['还款方式'] = tag[4].get_text()
            # 完成进度
            result["完成进度"] = tag[5].div.span.get_text()
            # 项目开始时间
            result['项目开始时间'] = tag[6].span.get_text().split("：")[1]
            # 追加到集合中
            data_list.append(result)
        except Exception as e:
            print("parse data exception", e)
    return data_list


def package_data(result):
    """数据最终结果的封装
    """
    # 结果数据的封装
    message = collections.OrderedDict()
    if result == 0:
        message["statue_code"] = 0
        message["msg_size"] = 0
    else:
        message["statue_code"] = 1
        message["msg_size"] = len(result)
        message["msg"] = result
    return json.dumps(message).decode("unicode-escape")


def spider_wd(url):
    """爬取数据(容错的方式爬取)

    :param url: 请求的链接
    :return: :数据
    :rtype:
    """
    try:
        try:
            # 使用代理
            result = requests.get(url, headers=headers, timeout=20, proxies=proxies).content
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            result = requests.get(url, headers=headers, timeout=20).content
        return result
    except Exception as e:
        print("爬取失败", e)
        return 0


def re_spider_wd(url):
    """爬取数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    :return: :爬取到的数据
    :rtype:
    """
    result = spider_wd(url)
    # 1.异常、2.结果不正确、3.结果失败。都需要重试
    # 如果没有获取到数据则重试多次
    if 0 == result:
        # 如果没有爬取成功则，重爬
        for num in range(1, 20):
            if 0 == result:
                print("reconnect "+str(num)+" times!!!")
                time.sleep(2)
                result = spider_wd(url)
            else:
                break
    return result


def insert_db(result):
    """
    写到mysql中
    """
    # 插入的记录数
    insert_count = 0
    connection = pymysql.connect(**config)
    try:
        result = json.loads(result)
        if result['statue_code'] != 0:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO ods_ydw_project_info (id, from_platform, project_name, ' \
                      'project_amount, project_rate, raise_rate, project_duration, repayment_method, ' \
                      'project_speed, start_time, stat_time)' \
                      ' VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                # 批量插入,放到集合中
                msg_list = []
                for m in result['msg']:
                    bid = m["标id".decode("utf-8")]
                    # 如果数据库中没有记录，则插入
                    if 0 == cursor.execute("SELECT * FROM ods_ydw_project_info WHERE id='"+bid+"'"):
                        msg_data = (m["标id".decode("utf-8")],
                                    m["来源平台".decode("utf-8")],
                                    m["标名称".decode("utf-8")],
                                    m["项目总额".decode("utf-8")],
                                    m["年化收益".decode("utf-8")],
                                    m["加息".decode("utf-8")],
                                    m["投资期限".decode("utf-8")],
                                    m["还款方式".decode("utf-8")],
                                    m["完成进度".decode("utf-8")],
                                    m["项目开始时间".decode("utf-8")],
                                    time.strftime("%Y-%m-%d %H:%M:%S")
                                    )
                        msg_list.append(msg_data)
                        insert_count += 1
                print("该批次插入了："+str(len(msg_list))+"条记录！\n")
                cursor.executemany(sql, msg_list)
                connection.commit()
        return insert_count
    except Exception as e:
        print("插入数据库失败，",e)
        return insert_count
    finally:
        connection.close()


def re_spider_wd_pages_into_db(url):
    """爬取每一页的数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    """
    # 获取数据
    result = re_spider_wd(url)
    # 解析得到总的页数
    tree = etree.HTML(result)
    # 得到总的页数
    total_pages = tree.xpath("/html/body/div[1]/div[2]/div[3]/div[2]/div[2]/span/em/text()")[0]
    pages = int(filter(str.isdigit, str(total_pages.decode('utf-8'))))
    # 成功之后，获取总的页数，一遍访问每一页
    if pages > 0:
        count = 0
        # 只需要爬取前50页
        for p in range(0, 50):
            time.sleep(1)
            # 发送的参数
            page = str(p+1)
            print("第"+page+"页的数据：")
            result = re_spider_wd(url+"?page="+page)
            result = parse_data(result)
            result = package_data(result)
            count += insert_db(result)
        print("总共插入："+str(count)+"条记录")


def start_spider():
    """
        开始爬虫
    """
    start_time = int(time.time())
    print("开始时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    re_spider_wd_pages_into_db(detail_link_san)
    print("结束时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    end_time = int(time.time())
    print("总共用时：" + str(end_time - start_time) + "秒")


if __name__ == '__main__':
    for n in range(1, 2):
        start_spider()

