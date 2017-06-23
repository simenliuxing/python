#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      积木盒子标的爬虫
"""
import pymysql.cursors
import time
import requests
import json
import sys
import collections
import random
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
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
source_from = "积木盒子"
# 详细信息的链接(项目列表)
detail_link_xiang = "https://box.jimu.com/Project/List"
# 详细信息的链接(债权转让列表列表)
detail_link_zai = "https://box.jimu.com/CreditAssign/List"
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


def parse_data(result, url_type):
    """数据的抽取

    :param result: 请求到的数据
    :param url_type: 请求的类型
    :return: :list集合
    :rtype:
    """
    # 一页的数据
    data_list = []
    soup = BeautifulSoup(result)
    tags = soup.find_all("div", class_="span3")
    for tag in tags:
        # 返回结果
        result = collections.OrderedDict()
        try:
            result['来源平台'] = source_from
            try:
                if "xiang" == url_type:
                    # 项目类型
                    result["项目类型"] = "普通项目"
                    # 标id
                    result["标id"] = tag.a["href"].split("=-")[1]
                if "zai" == url_type:
                    # 项目类型
                    result["项目类型"] = "债权转让"
                    # 标id
                    result["标id"] = tag.a["href"].split("Index/")[1]
            except Exception as e:
                print e
                result["标id"] = str(random.uniform(10, 20))

            div_tags = tag.a.div.find_all("div")
            # 标名称
            result["项目名称"] = div_tags[0].get_text() \
                .replace("\n", "") \
                .replace("\t", "") \
                .replace(" ", "") \
                .replace("\r", "")
            # 还款方式
            result["还款方式"] = div_tags[1].get_text() \
                .replace("\n", "") \
                .replace("\t", "") \
                .replace(" ", "") \
                .replace("\r", "")
            info = tag.a.div.p.get_text().replace("\n", "").replace("\t", "").replace(" ", "").replace("\r", "")
            if "%" in info and "/" in info:
                if len(info.split("%")) >= 1 and len(info.split("/")) >= 2:
                    # 项目进度
                    result['项目进度'] = info.split("%")[0] +"%"
                    # 项目总额
                    result['项目总额'] = info.split("/")[1]
                else:
                    # 项目进度
                    result['项目进度'] = ""
                    # 项目总额
                    result['项目总额'] = ""
            else:
                result['项目进度'] = "100%"
                if len(info.split("金额")) >= 1:
                    # 项目总额
                    result['项目总额'] = info.split("金额")[1]
                else:
                    # 项目总额
                    result['项目总额'] = ""
            if 15 == len(div_tags):
                # 年化收益
                result['年化收益'] = div_tags[8].get_text() \
                                     .replace("\n", "") \
                                     .replace("\t", "") \
                                     .replace(" ", "") \
                                     .replace("\r", "") + "%"
                duration = div_tags[13].get_text() \
                    .replace("\n", "") \
                    .replace("\t", "") \
                    .replace(" ", "") \
                    .replace("\r", "")
                if "天" in duration:
                    # 投资期限
                    result['投资期限'] = div_tags[12].get_text() \
                                         .replace("\n", "") \
                                         .replace("\t", "") \
                                         .replace(" ", "") \
                                         .replace("\r", "") + "天"
                else:
                    # 投资期限
                    result['投资期限'] = div_tags[12].get_text() \
                                         .replace("\n", "") \
                                         .replace("\t", "") \
                                         .replace(" ", "") \
                                         .replace("\r", "") + "个月"
            if 14 == len(div_tags):
                # 年化收益
                result['年化收益'] = div_tags[7].get_text() \
                                     .replace("\n", "") \
                                     .replace("\t", "") \
                                     .replace(" ", "") \
                                     .replace("\r", "") + "%"
                duration = div_tags[12].get_text() \
                    .replace("\n", "") \
                    .replace("\t", "") \
                    .replace(" ", "") \
                    .replace("\r", "")
                if "天" in duration:
                    # 投资期限
                    result['投资期限'] = div_tags[11].get_text() \
                                         .replace("\n", "") \
                                         .replace("\t", "") \
                                         .replace(" ", "") \
                                         .replace("\r", "") + "天"
                else:
                    # 投资期限
                    result['投资期限'] = div_tags[11].get_text() \
                                         .replace("\n", "") \
                                         .replace("\t", "") \
                                         .replace(" ", "") \
                                         .replace("\r", "") + "个月"

            data_list.append(result)
        except Exception as e:
            print("parse data exception", e)
            data_list.append(result)
            continue
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


def spider_wd(url, payload):
    """爬取数据(容错的方式爬取)

    :param url: 请求的链接
    :param payload: 请求的参数
    :return: :数据
    :rtype:
    """
    try:
        try:
            # 使用代理
            result = requests.get(url, headers=headers, timeout=10, params=payload, proxies=proxies).content
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            result = requests.get(url, headers=headers, timeout=10, params=payload).content
        return result
    except Exception as e:
        print("爬取失败", e)
        return 0


def re_spider_wd(url, payload):
    """爬取数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    :param payload: 请求的参数
    :return: :爬取到的数据
    :rtype:
    """
    result = spider_wd(url, payload)
    # 1.异常、2.结果不正确、3.结果失败。都需要重试
    # 如果没有获取到数据则重试多次
    if 0 == result:
        # 如果没有爬取成功则，重爬
        for num in range(1, 20):
            if 0 == result:
                print("reconnect "+str(num)+" times!!!")
                time.sleep(2)
                result = spider_wd(url, payload)
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
                sql = 'INSERT INTO ods_jmhz_project_info (id, from_platform, project_type, project_name, ' \
                      'project_amount, project_rate, project_duration, repayment_method, ' \
                      'project_speed, stat_time)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                # 批量插入,放到集合中
                msg_list = []
                for m in result['msg']:
                    bid = m["标id".decode("utf-8")]
                    # 如果数据库中没有记录，则插入
                    if 0 == cursor.execute("SELECT * FROM ods_jmhz_project_info WHERE id='"+bid+"'"):
                        msg_data = (m["标id".decode("utf-8")],
                                    m["来源平台".decode("utf-8")],
                                    m["项目类型".decode("utf-8")],
                                    m["项目名称".decode("utf-8")],
                                    m["项目总额".decode("utf-8")],
                                    m["年化收益".decode("utf-8")],
                                    m["投资期限".decode("utf-8")],
                                    m["还款方式".decode("utf-8")],
                                    m["项目进度".decode("utf-8")],
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


def re_spider_wd_pages_into_db(url, url_type):
    """爬取每一页的数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    :param url_type: 请求的参数
    """
    # 插入的数据计数器
    count = 0
    for p in range(1, 16):
        time.sleep(0.6)
        # 发送的参数
        if "xiang" == url_type:
            payload = {"category": "",
                       "rate": "",
                       "range": "",
                       "page": p,
                       "status": "",
                       "guarantee": ""
                       }
        if "zai" == url_type:
            payload = {"amount": "",
                       "repaymentCalcType": "",
                       "category": "",
                       "rate": "",
                       "days": "",
                       "page": p,
                       "orderIndex": "1",
                       "guarantee": ""
                       }
        # time.sleep(1)
        print("第"+str(p)+"页的数据：")
        result = re_spider_wd(url, payload)
        result = parse_data(result, url_type)
        flag = result
        result = package_data(result)
        count += insert_db(result)
        # 如果每页的元素个数小于12，则到了末页
        if len(flag) < 12:
            break
    print("总共插入："+str(count)+"条记录")


def start_spider():
    """
        开始爬虫
    """
    start_time = int(time.time())
    print("开始时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    re_spider_wd_pages_into_db(detail_link_xiang, "xiang")
    re_spider_wd_pages_into_db(detail_link_zai, "zai")
    print("结束时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    end_time = int(time.time())
    print("总共用时：" + str(end_time - start_time) + "秒")


if __name__ == '__main__':
    for n in range(1, 2):
        start_spider()

