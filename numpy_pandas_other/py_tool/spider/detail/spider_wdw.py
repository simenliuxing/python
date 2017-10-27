#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      微贷网标的爬虫
"""
import pymysql.cursors
import time
import requests
import json
import sys
import collections
from requests.exceptions import ProxyError
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# 请求头
headers = {
    "Host": "www.weidai.com.cn",
    "Referer": "https://www.weidai.com.cn/list/showApList.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
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
source_from = "微贷网"
# 还款方式
repaymentStyle = {"0": "月还息到期还本", "1": "等额本息"}
# 投资期限单位
durationTimeUnit = {"0": "天", "1": "个月"}
# 标的状态
status = {"OPENED": "投资中", "OOS": "已满标", "CONFIRMED": "还款中"}
# 详细信息的链接(优选计划)
detail_link_you = "https://www.weidai.com.cn/bid/showApDetail?hash="
# 详细信息的链接(散标)
detail_link_san = "https://www.weidai.com.cn/bid/showBidDetail?hash="
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


def parse_data(rest, project_type):
    """数据格式化

    :param rest: 请求到的数据
    :param project_type: 标的类型
    :return: :list集合
    :rtype:
    """
    # 一页的数据
    data_list = []
    if rest["success"]:
        # 具体数据
        rest = rest["data"]["data"]
        for data in rest:
            # 返回结果
            result = collections.OrderedDict()
            result['来源平台'] = source_from
            # hash
            result["hash"] = data["hash"]
            # 标id
            result["标id"] = data["bid"]
            # uid
            result["uid"] = data["uid"]
            # 标名称
            result["标名称"] = data["title"]
            # bizCategory
            result["bizCategory"] = data["bizCategory"]
            # bizProp
            result["bizProp"] = data["bizProp"]
            # 还款方式
            result['还款方式'] = repaymentStyle[str(data["repaymentStyle"])]
            # 项目总额
            result['项目总额'] = data["bidAmount"]
            # 已投金额
            result['已投金额'] = data["biddedAmount"]
            # 年化收益
            result['年化收益'] = data["annualizedRate"]
            # 投资期限
            result['投资期限'] = str(data["duration"]) + durationTimeUnit[data["durationTimeUnit"]]
            # 项目开始时间
            result['项目开始时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(data["openTime"]) / 1000))
            # 项目结束时间
            result['项目结束时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(data["closeTime"]) / 1000))
            # 项目状态
            result['项目状态'] = status[data["status"]]
            # 额外收入
            result['额外收入'] = data["additionalEarnings"]
            # 额外利率
            result['额外利率'] = data["additionalAnnualizedRate"]
            # tags
            result["tags"] = data["tags"]
            # 活动标签
            result["活动标签"] = data["activityTags"]
            # 最低投资金额
            result["最低投资金额"] = data["tenderMinAmount"]
            # 最高投资金额
            result["最高投资金额"] = data["tenderMaxAmount"]
            # 完成进度
            result["完成进度"] = data["completionRate"]
            # 剩余可投金额
            result["剩余可投金额"] = data["leftAmount"]
            # 详细信息
            if "you" == project_type:
                result["详细信息"] = detail_link_you + data["hash"]
            if "san" == project_type:
                result["详细信息"] = detail_link_san + data["hash"]
            # 追加到集合中
            data_list.append(result)
    return data_list


def spider_wd(url, payload, project_type):
    """请求数据

    :param url: 请求的链接
    :param payload: 请求的参数
    :param project_type: 标的类型
    :return: :格式化后的数据
    :rtype:
    """
    try:
        try:
            # 使用代理
            con = requests.get(url, headers=headers, timeout=20, params=payload, proxies=proxies)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            con = requests.get(url, headers=headers, timeout=20, params=payload)

        # 先直接获取首页的总量
        rest = json.loads(con.content)
        return parse_data(rest, project_type)
    except Exception as e:
        print("爬取失败", e)
        return 0


def re_spider_wd(url, payload, project_type):
    """爬取数据（处理超时异常,默认10次重试），并组装成json格式数据

    :param url: 请求的链接
    :param payload: 请求的参数
    :param project_type: 标的类型
    :return: :格式化后的json数据
    :rtype:
    """
    result = spider_wd(url, payload, project_type)
    # 如果没有获取到数据则重试多次
    if result == 0:
        # 如果没有爬取成功则，重爬
        for num in range(1, 10):
            print(num)
            time.sleep(1)
            if result == 0:
                result = spider_wd(url, payload, project_type)
            else:
                break
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


def re_spider_wd_pages(url, project_type):
    """爬取每一页的数据（处理超时异常,默认10次重试）

    :param url: 请求的链接
    :param project_type: 爬取的类型
    """
    try:
        # 使用代理
        con = requests.get(url, headers=headers, timeout=20, proxies=proxies)
    except ProxyError:
        print("ProxyError Exception ,use no proxies ")
        # 不使用代理
        con = requests.get(url, headers=headers, timeout=20)

    rest = json.loads(con.content)
    # 如果请求失败，则重复十次
    if not rest["success"]:
        for num in range(1, 10):
            time.sleep(1)
            if not rest["success"]:
                try:
                    # 使用代理
                    con = requests.get(url, headers=headers, timeout=20, proxies=proxies)
                except ProxyError:
                    print("ProxyError Exception ,use no proxies ")
                    # 不使用代理
                    con = requests.get(url, headers=headers, timeout=20)
                rest = json.loads(con.content)
            else:
                break
    # 成功之后，获取总的页数，一遍访问每一页
    if rest["success"]:
        pages = rest["data"]["count"]/rest["data"]["pageSize"]
        count = 0
        for p in range(0, pages):
            time.sleep(0.6)
            print("第" + str(p + 1) + "页的数据：")
            # 发送的参数
            # 优选计划
            if "you" == project_type:
                payload = {"type": 0, "periodType": 0, "page": p+1, "rows": 10}
                count += insert_db(re_spider_wd(url, payload, project_type))
            # 散标
            if "san" == project_type:
                payload = {"type": 0, "periodType": 0, "sort": 0, "page": p+1, "rows": 10}
                # 插入到数据库中
                count += insert_db(re_spider_wd(url, payload, project_type))
        print("总共插入："+str(count)+"条记录")


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
                sql = 'INSERT INTO ods_wdw_project_info (bid, from_platform, hash, uid, title, ' \
                      'bizCategory, bizProp, repaymentStyle, bidAmount, biddedAmount, ' \
                      'annualizedRate, duration, openTime, closeTime, status, ' \
                      'additionalEarnings, additionalAnnualizedRate, tags, activityTags, ' \
                      'tenderMinAmount, tenderMaxAmount, completionRate, leftAmount, bidUrl, stat_time)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
                      '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                # 批量插入,放到集合中
                msg_list = []
                for m in result['msg']:
                    bid = m["标id".decode("utf-8")]
                    # 如果数据库中没有记录，则插入
                    if 0 == cursor.execute("SELECT * FROM ods_wdw_project_info WHERE bid="+str(bid)+""):
                        msg_data = (m["标id".decode("utf-8")], m["来源平台".decode("utf-8")],
                                    m["hash".decode("utf-8")], m["uid".decode("utf-8")],
                                    m["标名称".decode("utf-8")], m["bizCategory".decode("utf-8")],
                                    m["bizProp".decode("utf-8")], m["还款方式".decode("utf-8")],
                                    m["项目总额".decode("utf-8")], m["已投金额".decode("utf-8")],
                                    m["年化收益".decode("utf-8")], m["投资期限".decode("utf-8")],
                                    m["项目开始时间".decode("utf-8")], m["项目结束时间".decode("utf-8")],
                                    m["项目状态".decode("utf-8")], m["额外收入".decode("utf-8")],
                                    m["额外利率".decode("utf-8")], m["tags".decode("utf-8")],
                                    str(m["活动标签".decode("utf-8")]).replace("u\'", "\'").decode("unicode-escape")  ,
                                    m["最低投资金额".decode("utf-8")],
                                    m["最高投资金额".decode("utf-8")], m["完成进度".decode("utf-8")],
                                    m["剩余可投金额".decode("utf-8")], m["详细信息".decode("utf-8")],
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


def start_spider():
    """
        开始爬虫
    """
    start_time = int(time.time())
    print("开始时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    # 1.优选计划
    link = "https://www.weidai.com.cn/list/assetPacketList"
    re_spider_wd_pages(link, "you")
    # 2.散标
    link2 = "https://www.weidai.com.cn/list/bidList"
    re_spider_wd_pages(link2, "san")
    print("结束时间：" + str(time.strftime("%Y-%m-%d %H:%M:%S")))
    end_time = int(time.time())
    print("总共用时：" + str(end_time - start_time) +"秒")


if __name__ == '__main__':
    start_spider()
