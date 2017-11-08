#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import os
import re
import requests
import sys
import traceback
from datetime import datetime
from datetime import timedelta
from lxml import etree
import time as time_sleep


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

class Weibo:
        # # 将your cookie替换成自己的cookie
        cookie = {'Cookie':'SINAGLOBAL=2375035684357.2964.1502788001389; _s_tentry=blog.csdn.net; Apache=4880734666771.718.1503724416842; ULV=1503724417469:2:2:1:4880734666771.718.1503724416842:1502788001816; UM_distinctid=15f294d93fe909-06177db9c2cac3-323f5c0f-1fa400-15f294d93ffd34; login_sid_t=7336ca34f04f1c17579bb10b8bdfc863; appkey=; user_active=201710271600; user_unver=bb426661b6cda5efe95e3ad53d271583; YF-Page-G0=ab26db581320127b3a3450a0429cde69; cross_origin_proto=SSL; UOR=ent.ifeng.com,widget.weibo.com,login.sina.com.cn; SCF=AmoPOYQKcM--VgFvuLaVWH6gWxTEeET2UXf5r9HP_AJleQiRTiUovAmP4mq1rJLMm34cxmT_qEdLK6eTiG9hWyA.; SUB=_2A250_RZTDeThGeBN4lYY8y7Kwj-IHXVXiwCbrDV8PUNbmtBeLUTYkW-CRQmPNEM1uWJk4DlaDALlz9PGHQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTnruZG6SceBYiNqx.DkoF5JpX5K2hUgL.Foq01KB4e05c1Ke2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM4eh.7eon7eoBR; SUHB=0oU4kOehwfT7o_; ALF=1510121667; SSOLoginState=1509516803; un=l492341344@163.com; wvr=6'}

        # Weibo类初始化
        def  __init__(self, user_id, filter=0):
            self.user_id = user_id  # 用户id，即需要我们输入的数字，如昵称为“Dear-迪丽热巴”的id为1669879400
            self.filter = filter  # 取值范围为0、1，程序默认值为0，代表要爬取用户的全部微博，1代表只爬取用户的原创微博
            self.username = ''  # 用户名，如“Dear-迪丽热巴”
            self.weibo_num = 0  # 用户全部微博数
            self.weibo_num2 = 0  # 爬取到的微博数
            self.following = 0  # 用户关注数
            self.followers = 0  # 用户粉丝数
            self.weibo_content = []  # 微博内容
            self.publish_time = []  # 微博发布时间
            self.up_num = []  # 微博对应的点赞数
            self.retweet_num = []  # 微博对应的转发数
            self.comment_num = []  # 微博对应的评论数

        # 获取用户昵称
        def get_username(self):
                try:
                    url = 'https://weibo.cn/%s' % (self.user_id)
                    html = requests.get(url, cookies = self.cookie, proxies=proxies).content
                    selector = etree.HTML(html)
                    username = selector.xpath('//title/text()')[0]
                    self.username = username[:-3]
                    print('用户名: ' + self.username)
                except Exception as e:
                    print("Error: ", e)
                    traceback.print_exc()

        # 获取用户微博数、关注数、粉丝数
        def get_user_info(self):
            try:
                url = 'https://weibo.cn/%s' %(self.user_id)
                html = requests.get(url, cookies=self.cookie, proxies=proxies).content
                selector = etree.HTML(html)
                pattern = r"\d+\.?\d*"

                # 微博数量
                str_wb = selector.xpath(
                    "//div[@class='tip2']/span[@class='tc']/text()")[0]
                guid = re.findall(pattern, str_wb, re.S | re.M)
                for value in guid:
                    num_wb = int(value)
                    break
                self.weibo_num = num_wb
                print('微博数: ' + str(self.weibo_num))

                # 关注数
                str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
                guid = re.findall(pattern, str_gz, re.M)
                self.following = int(guid[0])
                print('关注数: ' + str(self.following))

                # 粉丝数
                str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
                guid = re.findall(pattern, str_fs, re.M)
                self.followers = int(guid[0])
                print ('粉丝数: ' + str(self.followers))
            except Exception as e:
                print("Error: ", e)
                traceback.print_exc()

        # 获取用户微博内容及对应的发布时间、点赞数、转发数、评论数
        def get_weibo_info(self):
            try:
                url = "https://weibo.cn/%s?filter=%d&page=1" % (
                    self.user_id, self.filter)
                html = requests.get(url, cookies=self.cookie, proxies=proxies).content
                selector = etree.HTML(html)
                if selector.xpath("//input[@name='mp']") == []:
                    page_num = 1
                else:
                    page_num = (int)(selector.xpath(
                        "//input[@name='mp']")[0].attrib["value"])
                pattern = r"\d+\.?\d*"
                for page in range(1, page_num + 1):
                    url2 = "https://weibo.cn/%s?filter=%d&page=%d" % (
                        self.user_id, self.filter, page)
                    html2 = requests.get(url2, cookies=self.cookie, proxies=proxies).content
                    selector2 = etree.HTML(html2)
                    info = selector2.xpath("//div[@class='c']")
                    if len(info) > 3:
                        for i in range(0, len(info) - 2):
                            # 微博内容
                            str_t = info[i].xpath("div/span[@class='ctt']")
                            weibo_content = str_t[0].xpath("string(.)").encode(
                                sys.stdout.encoding, "ignore").decode(
                                sys.stdout.encoding)
                            self.weibo_content.append(weibo_content)
                            print("微博内容：" + weibo_content)

                            # 微博发布时间
                            str_time = info[i].xpath("div/span[@class='ct']")
                            str_time = str_time[0].xpath("string(.)").encode(
                                sys.stdout.encoding, "ignore").decode(
                                sys.stdout.encoding)
                            publish_time = str_time.split('来自')[0]
                            if "刚刚" in publish_time:
                                publish_time = datetime.now().strftime(
                                    '%Y-%m-%d %H:%M')
                            elif "分钟" in publish_time:
                                minute = publish_time[:publish_time.find("分钟")]
                                minute = timedelta(minutes=int(minute))
                                publish_time = (
                                    datetime.now() - minute).strftime(
                                    "%Y-%m-%d %H:%M")
                            elif "今天" in publish_time:
                                today = datetime.now().strftime("%Y-%m-%d")
                                time = publish_time[3:]
                                publish_time = today + " " + time
                            elif "月" in publish_time:
                                year = datetime.now().strftime("%Y")
                                month = publish_time[0:2]
                                day = publish_time[3:5]
                                time = publish_time[7:12]
                                publish_time = (
                                    year + "-" + month + "-" + day + " " + time)
                            else:
                                publish_time = publish_time[:16]
                            self.publish_time.append(publish_time)
                            print("微博发布时间：" + publish_time)

                            # 点赞数
                            str_zan = info[i].xpath("div/a/text()")[-4]
                            guid = re.findall(pattern, str_zan, re.M)
                            up_num = int(guid[0])
                            self.up_num.append(up_num)
                            print("点赞数: " + str(up_num))

                            # 转发数
                            retweet = info[i].xpath("div/a/text()")[-3]
                            guid = re.findall(pattern, retweet, re.M)
                            retweet_num = int(guid[0])
                            self.retweet_num.append(retweet_num)
                            print("转发数: " + str(retweet_num))

                            # 评论数
                            comment = info[i].xpath("div/a/text()")[-2]
                            guid = re.findall(pattern, comment, re.M)
                            comment_num = int(guid[0])
                            self.comment_num.append(comment_num)
                            print("评论数: " + str(comment_num))
                            self.weibo_num2 += 1
                            print('')
                            time_sleep.sleep(2)

                if not self.filter:
                    print("共" + str(self.weibo_num2) + "条微博")
                else:
                    print("共" + str(self.weibo_num) + "条微博，其中" + str(self.weibo_num2) + "条为原创微博")
            except Exception as e:
                print("Error: ", e)
                traceback.print_exc()

        # 将爬取的信息写入文件
        def write_txt(self):
            try:
                if self.filter:
                    result_header = "\n\n原创微博内容：\n"
                else:
                    result_header = "\n\n微博内容：\n"
                result = ("用户信息\n用户昵称：" + self.username +
                          "\n用户id：" + str(self.user_id) +
                          "\n微博数：" + str(self.weibo_num) +
                          "\n关注数：" + str(self.following) +
                          "\n粉丝数：" + str(self.followers) +
                          result_header
                          )
                for i in range(1, self.weibo_num2 + 1):
                    text = (str(i) + ":" + self.weibo_content[i - 1] + "\n" +
                            "发布时间：" + self.publish_time[i - 1] + "\n" +
                            "点赞数：" + str(self.up_num[i - 1]) +
                            "	 转发数：" + str(self.retweet_num[i - 1]) +
                            "	 评论数：" + str(self.comment_num[i - 1]) + "\n\n"
                            )
                    result = result + text
                file_dir = os.path.split(os.path.realpath(__file__))[
                               0] + os.sep + "weibo"
                if not os.path.isdir(file_dir):
                    os.mkdir(file_dir)
                file_path = file_dir + os.sep + "%s" % self.user_id + ".txt"
                f = open(file_path, "wb")
                f.write(result.encode(sys.stdout.encoding))
                f.close()
                print("微博写入文件完毕，保存路径:" + file_path)
            except Exception as e:
                print("Error: ", e)
                traceback.print_exc()

        # 运行爬虫
        def start(self):
            try:
                self.get_username()
                print('')
                self.get_user_info()
                print('')
                self.get_weibo_info()
                # self.write_txt()
                print("信息抓取完毕")
                print("===========================================================================")
            except Exception as e:
                print("Error: ", e)


def main():
    try:
        # 使用实例,输入一个用户id，所有信息都会存储在wb实例中
        user_id = '6182236310'  # 可以改成任意合法的用户id（爬虫的微博id除外）
        filter = 0  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
        wb = Weibo(user_id, filter)  # 调用Weibo类，创建微博实例wb
        wb.start()  # 爬取微博信息
        print("用户名：" + wb.username)
        print("全部微博数：" + str(wb.weibo_num))
        print("关注数：" + str(wb.following))
        print("粉丝数：" + str(wb.followers))
        print("最新一条原创微博为：" + wb.weibo_content[0])
        print("最新一条原创微博发布时间：" + wb.publish_time[0])
        print("最新一条原创微博获得的点赞数：" + str(wb.up_num[0]))
        print("最新一条原创微博获得的转发数：" + str(wb.retweet_num[0]))
        print("最新一条原创微博获得的评论数：" + str(wb.comment_num[0]))
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()