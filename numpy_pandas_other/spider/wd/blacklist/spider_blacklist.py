#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      今日头条黑名单的爬取
"""
from lxml import etree
import requests
import json
import sys
import collections
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


# 爬取今日头条搜索到的url
def spider_url():
    # 链接数据获取的偏移量
    offset = 0
    url = "https://www.toutiao.com/search_content/?offset=0&format=json" \
          "&keyword=%E5%A4%B1%E4%BF%A1%E6%9B%9D%E5%85%89%E5%8F%B0&autoload=true&count=20&cur_tab=1"
    try:
        # 返回结果
        link_list = []
        # 迭代所有的链接
        while True:
            # 先直接获取
            con = requests.get(url, timeout=10).content
            rest = json.loads(con)
            # 返回结果正确
            if "success" == rest["message"] and rest["return_count"] > 0:
                # 此处得到的是list
                rest = rest["data"]
                for r in rest:
                    if r.has_key("media_name") \
                            and r.has_key("title") \
                            and r.has_key("display_url") \
                            and r.has_key("media_creator_id") \
                            and 4082153852 == r["media_creator_id"]:
                        link_dict = collections.OrderedDict()
                        link_dict["来源平台"] = r["media_name"]
                        link_dict["事件信息"] = r["title"]
                        link_dict["具体信息地址"] = r["display_url"]
                        link_list.append(link_dict)
            else:
                break
            # 下一页数据
            offset += 20
            url = "https://www.toutiao.com/search_content/?" \
                  "offset=" + str(offset) + "&format=json&keyword=%E5%A4%B1%E4%BF%A1%E6%9B%9D%E5%85%89%E5%8F%B0&" \
                                            "autoload=true&count=20&cur_tab=1"

        # 返回结果
        return link_list
    except Exception as e:
        print("爬取失败", e)
        return -1


# 爬取今日头条搜索到的url,中的每页的具体数据
def spider_data(url):
    try:
        con = requests.get(url, timeout=10).content
        # xpath解析
        tree = etree.HTML(con)
        # 返回结果
        black_list = tree.xpath("//*[@id='article-main']/div[2]/p[position()>2 and position()<last()-3 ]/text()")
        user_list = []
        user_info = ""
        for b in black_list:
            if b[:1].isdigit():
                user_info = user_info[:-1]
                user_list.append(user_info)
                user_info = ""
            user_info = user_info + b + ","
        return user_list
    except Exception as e:
        print("爬取失败", e)
        return -1


# 爬取数据，并组装成json格式数据
def re_spider(result):
    # 如果没有获取到数据则重试多次
    if result != -1:
        # 结果数据的封装
        message = collections.OrderedDict()
        if result == -1:
            message['statue_code'] = 0
        else:
            message['statue_code'] = 1
            message['msg'] = result
        return json.dumps(message).decode('unicode-escape')


# 从url中爬取data
def spider_data_from_url():
    # 先获取搜索到的url
    rest_links = json.loads(re_spider(spider_url()))
    links = rest_links["msg"]
    # 最终结果的封装
    black_list_dict = collections.OrderedDict()
    black_list_list = []
    for link in links:
        link = link["具体信息地址".decode("utf-8")]
        # 然后获取搜索到的每个url数据
        format_list = json.loads(re_spider(spider_data(link)))["msg"]
        for form in format_list:
            if form:
                black_list_list.append(form)

    # 最终结果的封装
    black_list_dict['statue_code'] = 1
    black_list_dict['msg'] = black_list_list
    return json.dumps(black_list_dict).decode('unicode-escape')


if __name__ == '__main__':
    for n in range(1, 2):
        print spider_data_from_url()
