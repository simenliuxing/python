#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      鑫合汇标的爬虫
"""
from bs4 import BeautifulSoup
import pymysql.cursors
import time
import requests
import json
import sys
import collections
from lxml import etree
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
# 还款方式
repay_type = {
    "2": "按月付息",
    "1": "到期还本付息",
    "4": "气球贷",
    "3": "等额本息"
                 }
# 平台名称
source_from = "鑫合汇"
# 链接(日益升)
detail_link_ri = "https://www.xinhehui.com/Financing/Invest/ajaxplist" \
                 "?c=2&sort_id=&sort=&order=&bid_st=0&show_new=0&time_limit=0&b_type=&p="
# 链接(月益升)
detail_link_yue = "https://www.xinhehui.com/Financing/Invest/ajaxplist" \
                  "?c=3&sort_id=&sort=&order=&bid_st=0&show_new=0&time_limit=0&b_type=&p="
# 链接(速兑通)
detail_link_su = "https://www.xinhehui.com/Financing/Invest/ajaxplist" \
                 "?c=6&sort_id=&sort=Array&order=Array&bid_st=0&show_new=0&time_limit=0&b_type=&p="
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


def parse_data(result_data):
    """数据的抽取

    :param result_data: 请求到的数据
    :return: :list集合
    :rtype:
    """
    # 一页的数据
    data_list = []
    soup = BeautifulSoup(result_data.replace("\n", ""))
    tags = soup.find_all("div", class_="proListBox modplist-bywf proListBox_bd clearfix")
    if len(tags) == 0:
        tags = soup.find_all("div", class_="proListBox modplist-bywf proListBox_bd clearfix proListBox-disable ")
    for tag in tags:
        # 追加到集合中
        try:
            # 返回结果
            result = collections.OrderedDict()
            result['来源平台'] = source_from
            # 标id
            result["标id"] = tag.div.h4.a['href'].split("id=")[1]
            # 标名称
            result["项目名称"] = tag.div.h4.a.get_text()
            # 年华收益
            spans = tag.div.div.find_all("span")
            if len(spans) == 11:
                result['年化收益'] = spans[0].div.get_text()
                # 投资期限
                result['项目期限'] = spans[6].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("项目期限")[1]
                # 还款方式
                result['还款方式'] = spans[8].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("还款方式")[1]
                # 起投金额
                result['起投金额'] = spans[10].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("起投金额(元)")[1]
            else:
                result['年化收益'] = spans[0].div.get_text()
                # 投资期限
                result['项目期限'] = spans[3].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("项目期限")[1]
                # 还款方式
                result['还款方式'] = spans[5].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("还款方式")[1]
                # 起投金额
                result['起投金额'] = spans[7].get_text().replace("\n", "").replace("\t", "").replace(" ", "").split("起投金额(元)")[1]
            # 计算总额
            total_left = tag.find_all("div")
            total_left = total_left[4].get_text()\
                .replace("\n", "")\
                .replace("\t", "")\
                .replace(" ", "")\
                .replace("剩余", "")\
                .replace(",", "")\
                .replace("立即投资", "")
            if ".00" in total_left:
                # 剩余金额
                result['剩余金额'] = total_left.split(".00")[0]
                # 完成进度
                result['项目进度'] = total_left.split(".00")[1]
            else:
                # 剩余金额
                result['剩余金额'] = ""
                # 完成进度
                result['项目进度'] = total_left
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
    :param payload: 请求的参数
    :return: :数据
    :rtype:
    """
    try:
        try:
            # 使用代理
            result = requests.get(url, timeout=10, proxies=proxies).content
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            result = requests.get(url, timeout=10).content
        return result
    except Exception as e:
        print("爬取失败", e)
        return 0


def re_spider_wd(url):
    """爬取数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    :param payload: 请求的参数
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
                sql = 'INSERT INTO ods_xhh_project_info (id, from_platform, project_name, ' \
                      'project_rate, project_duration, repayment_method, unit_amount, ' \
                      'left_amount, project_speed, stat_time)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                # 批量插入,放到集合中
                msg_list = []
                for m in result['msg']:
                    bid = m["标id".decode("utf-8")]
                    # 如果数据库中没有记录，则插入
                    if 0 == cursor.execute("SELECT * FROM ods_xhh_project_info WHERE id='"+bid+"'"):
                        msg_data = (m["标id".decode("utf-8")],
                                    m["来源平台".decode("utf-8")],
                                    m["项目名称".decode("utf-8")],
                                    m["年化收益".decode("utf-8")],
                                    m["项目期限".decode("utf-8")],
                                    m["还款方式".decode("utf-8")],
                                    m["起投金额".decode("utf-8")],
                                    m["剩余金额".decode("utf-8")],
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


def re_spider_wd_pages_into_db(url):
    """爬取每一页的数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    """
    # 插入的总的条数
    count = 0
    # 获取数据
    # result = re_spider_wd(url+str(1))
    # 得到总的页码
    # soup = BeautifulSoup(result)
    # pages_div = soup.find_all("div", class_="page pageWraper")
    # pages_a = pages_div[0].find_all("a")[4]
    # pages = int(pages_a.get_text())
    for p in range(1, 6):
        # time.sleep(0.5)
        url_parameter = url + str(p)
        print("第"+str(p)+"页的数据：")
        result = re_spider_wd(url_parameter)
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
    re_spider_wd_pages_into_db(detail_link_ri)
    re_spider_wd_pages_into_db(detail_link_yue)
    re_spider_wd_pages_into_db(detail_link_su)
    print("结束时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    end_time = int(time.time())
    print("总共用时：" + str(end_time - start_time) + "秒")


if __name__ == '__main__':
    for n in range(1, 2):
        start_spider()
