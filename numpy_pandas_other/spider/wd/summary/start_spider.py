#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import json
import os
from multiprocessing import Pool

import pymysql.cursors

import spider_mdtx
import spider_aqj
import spider_jmhz
import spider_ppd
import spider_tdw
import spider_wdw
import spider_xhh
import spider_xnzx
import spider_xsjf
import spider_ydw


# 进程池多进程爬取
def multi_pool_start():
    pool = Pool(4)
    pool.apply_async(insert_db, (spider_aqj.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_ppd.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_tdw.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_wdw.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_xsjf.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_ydw.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_xnzx.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_jmhz.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_mdtx.re_spider_wd(),))
    pool.apply_async(insert_db, (spider_xhh.re_spider_wd(),))
    pool.close()
    pool.join()


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
        if result['statue_code'] != 0:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO ods_wd_total_info (platform, total_sum, ' \
                      'earn_total, not_earn_total, today_total, total_account, stat_date)' \
                      ' VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (result['msg']['来源平台'.decode("utf-8")],
                                     result['msg']['投资总额'.decode("utf-8")],
                                     result['msg']['已赚取'.decode("utf-8")],
                                     result['msg']['待赚取'.decode("utf-8")],
                                     result['msg']['今日成交额'.decode("utf-8")],
                                     result['msg']['注册用户数'.decode("utf-8")],
                                     result['msg']['日期'.decode("utf-8")]))
                connection.commit()
    finally:
        connection.close()


# 写到文件中
def write_dis(result):
    result = json.loads(result)
    if result['statue_code'] != 0:
        with open('./wd.txt', 'a') as f:
            # 如果文件存在，则新写入的数据换一行
            if os.path.isfile('./wd.txt'):
                f.write('\n')
            f.write(result['msg']['来源平台'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['投资总额'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['已赚取'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['待赚取'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['今日成交额'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['注册用户数'.decode("utf-8")])
            f.write('\t')
            f.write(result['msg']['日期'.decode("utf-8")])

if __name__ == '__main__':
    multi_pool_start()
