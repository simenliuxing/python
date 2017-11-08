#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import os
import re
import requests
import sys
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from lxml import etree
import time as time_sleep
import json
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

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


# p2p平台注册校验
class P2P:
    def __init__(self, path):
        self.path = path  # 文件保存路径
        self.ppd = False
        self.wdw = False
        self.aqj = False
        self.tdw = False
        self.ydw = False
        self.xylc = False
        self.yld = False
        self.trjr = False

    # 拍拍贷
    def ppd_register(self, phone):
        try:
            ppd_url = 'https://ac.ppdai.com/registercheck?callback=jQuery17108959717728378076_1509584615885&name=mobilePhone&value='+str(phone)+'&_=1509584726062'
            ppd_html = requests.get(ppd_url, proxies=proxies, timeout=3).content
            ppd_html_json = json.loads(ppd_html[41:][:-1])
            if ppd_html_json['Code'] == 1:
                self.ppd = False
            else:
                self.ppd = True
        except Exception as e:
            print('ppd error:', phone)

    # 微贷网
    def wdw_register(self, phone):
        try:
            # headers
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Content-Length': '42',
                'Cookie':
                    'UM_distinctid=15dd09662a614d-0977e52b24136a-323f5c0f-1fa400-15dd09662a7af8; gr_user_id=f6bf063c-0217-426e-87d9-92a46655f122; _uab_collina=150244310321496229359104; aliyungf_tc=AQAAAGw2bVcn0gIAy8/geoKbMwqiyHmu; acw_tc=AQAAAFBWGl+FbgMAy8/geoxYhGxT0wkx; route=fe730935a4f8fcc6ba142f2669a549fe; CNZZDATA1256511929=1669338562-1502441445-https%253A%252F%252Fwww.weidai.com.cn%252F%7C1508918547; Hm_lvt_6f8af5890dcd62a8bd38a1e06fa72039=1508304782,1509357571; Hm_lpvt_6f8af5890dcd62a8bd38a1e06fa72039=1509357571; JSESSIONID=010231717BD5C6B4C471DCB2BAC4BDBB; u_asec=099%23KAFEW7EKE3bEhGTLEEEEEpEQz0yFD6V3DcaYC6NTDciIW6z3Du9ID6z1DNQTEE7EERpClYFETKxqAjHhE7Eht3BlluZdBEFE13iSEJ8BAXZbsYFET%2FyZTEwMgcGTE1LSt3llsyaSt3iS1wJP%2F3fTt37MlXZddqLStTLtsyaGQ3iSh3nP%2F3wYAYFEM7Ekb%2FWdCwUQrjDt9235rAXsbYaRPfGBbyXZ3MeWNi8CbsNtiOJkPR4Wb4Qt%2Fq%2BZ6L7WadWvv0XBrsr3323hPwpGPwZprtMBbiXBYoCVCL8XUTzul%2Fp1ryXWcMURW2Y280LUE7TxEqhiEFyPRJfr2T4IcuV%2BMJK41ISAzZjDfJcy1hWcqHGt06Mqm%2FQ%2BfkfrvHbzukj26HA38ZeL2h0Yffro5RT2qHAo1DN7VmGt0HU6mCXGkLjo3f7TEEiStEE7; gr_session_id_9e499063616a9fe6=2169f9e8-62fc-4107-9e75-9ed887a04633'
                ,
                'Host': 'www.weidai.com.cn',
                'Origin': 'https://www.weidai.com.cn',
                'Referer': 'https://www.weidai.com.cn/regs/register.html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            wdw_url = 'https://www.weidai.com.cn/regs/authUserExist'
            param = {
                'mobile': str(phone),
                'net4': '0.9496613830221385'
            }
            wdw_html = requests.post(wdw_url, proxies=proxies, data=param, headers=headers, timeout=3).content
            wdw_html_json = json.loads(wdw_html)
            if wdw_html_json['success'] == False:
                self.wdw = True
            else:
                self.wdw = False
        except Exception as e:
            print('wdw error:', phone)

    # 爱钱进
    def aqj_register(self, phone):
        try:
            aqj_url = 'https://www.iqianjin.com/user/checkMobile'
            param = {
                'mobile': str(phone),
                'name': str(phone)
            }
            aqj_html = requests.post(aqj_url, proxies=proxies, data=param, timeout=3).content
            aqj_html_json = json.loads(aqj_html)
            if aqj_html_json['success'] == False:
                self.aqj = True
            else:
                self.aqj = False
        except Exception as e:
            print('aqj error:', phone)

    # 团贷网
    def tdw_register(self, phone):
        try:
            # headers
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.8',
                'content-length': '18',
                'content-type': 'application/x-www-form-urlencoded;charset = UTF - 8',
                'Cookie':
                '_jzqx=1.1505878524.1505878524.1.jzqsr=wdzj%2Ecom|jzqct=/p2phongbao/front/s-activity-detail.-; acw_tc=AQAAAGx9IAb9iAcAy8/gepfeEeoKj1Y1; _jzqa=1.1712910740852378000.1505878524.1507877777.1508383003.3; _jzqc=1; _jzqy=1.1507877777.1508383003.1.jzqsr=baidu|jzqct=%E5%9B%A2%E8%B4%B7%E7%BD%91.-; td_visitorId=870f0f69-743f-3450-8207-1bfab88c3fec; _td_st=1509584822948; JSESSIONID=oLlzwqsv7WtnKKTOLPkM8w4lo9cwBoJW0MJGv1aC; tuandainame=Ws2WRuOavUsFRPlauzkFVg%3D%3D; tuandai005=967tuK%2B0Z%2BdASHtGAbje0f4wxhSUhJ31fQpfU9H4FrpzX3lNfEAeIA%3D%3D; td_visitorId=870f0f69-743f-3450-8207-1bfab88c3fec; td_exit_flag=1; Hm_lvt_e5885737885060b19f50ba5ed78c9802=1507877812; Hm_lpvt_e5885737885060b19f50ba5ed78c9802=1509585221'
                ,
                'Origin': 'https://www.tdw.cn',
                'Referer': 'https://www.tdw.cn/user/Register.aspx',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest'
            }
            tdw_url = 'https://www.tdw.cn/user/checkPhone'
            param = {
                'sPhone': str(phone)
            }
            tdw_html = requests.post(tdw_url, proxies=proxies, data=param, headers=headers, timeout=3).content
            tdw_html_json = json.loads(tdw_html)
            if tdw_html_json['code'] == 1:
                self.tdw = True
            else:
                self.tdw = False
        except Exception as e:
            print('tdw error:', phone)

    # 宜贷网
    def ydw_register(self, phone):
        try:
            ydw_url = 'https://www.yidai.com/user/checkphone/?phone='+str(phone)
            ydw_html = requests.get(ydw_url, proxies=proxies, timeout=3).content
            ydw_html = ydw_html.decode()
            ydw_html = ydw_html.strip()
            if '1' in ydw_html:
                self.ydw = True
            else:
                self.ydw = False
        except Exception as e:
            print('ydw error:', phone)

    # 小盈理财
    def xylc_register(self, phone):
        try:
            xylc_url = 'https://www.xiaoying.com/user/apiCheckMobile'
            param = {
                'mobile': str(phone),
                '_fromAjax_': '1',
                '_csrfToken_': 'd41d8cd98f00b204e9800998ecf8427e'
            }
            xylc_html = requests.post(xylc_url, proxies=proxies, data=param, timeout=3).content
            xylc_html_json = json.loads(xylc_html)
            if xylc_html_json['ret'] == -1000:
                self.xylc = True
            else:
                self.xylc = False
        except Exception as e:
            print('xylc error:', phone)

    # 翼龙贷
    def yld_register(self, phone):
        try:
            # headers
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'content-length': '18',
                'content-type': 'application/x-www-form-urlencoded;charset = UTF - 8',
                'Cookie':
                      'register_record_regist_sign="https://www.eloancn.com/"; _ga=GA1.2.463219826.1509585998; _gid=GA1.2.346762924.1509585998; _gat=1; Hm_lvt_6d141314e7cea7d4950e6b57c4d67420=1509585998; Hm_lpvt_6d141314e7cea7d4950e6b57c4d67420=1509585998; sid=0abbf7f8-f870-4eab-95ab-f6e156310817; __ads_session=CVHmhN9x/whEv+I7ywA='
                ,
                'Host': 'user.eloancn.com',
                'Origin': 'http://user.eloancn.com',
                'Referer': 'http://user.eloancn.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest'
            }
            yld_url = 'http://user.eloancn.com/userbaseinfo/register/checkMobile'
            param = {
                'mobile': str(phone)
            }
            yld_html = requests.post(yld_url, proxies=proxies, data=param, headers=headers, timeout=3).content
            yld_html_json = json.loads(yld_html)
            if yld_html_json['state'] == 'OK':
                self.yld = False
            else:
                self.yld = True
        except Exception as e:
            print('yld error:', phone)

    # 泰然金融
    def trjr_register(self, phone):
        try:
            trjr_url = 'http://passport.trc.com/proxy/account/user/phone/exist/' + str(phone)
            trjr_html = requests.get(trjr_url, proxies=proxies, timeout=3).content
            trjr_html_json = json.loads(trjr_html)
            if trjr_html_json['have'] == True:
                self.trjr = True
            else:
                self.trjr = False
        except Exception as e:
            print('trjr error:', phone)

    # p2p注册校验
    def p2p_register(self, phone):
        self.ppd_register(phone)
        register_phone = ''
        if self.ppd:
            register_phone = '拍拍贷' + '\t'

        self.wdw_register(phone)
        if self.wdw:
            register_phone = register_phone + '微贷网' + '\t'

        self.aqj_register(phone)
        if self.aqj:
            register_phone = register_phone + '爱钱进' + '\t'

        self.tdw_register(phone)
        if self.tdw:
            register_phone = register_phone + '团贷网' + '\t'

        self.ydw_register(phone)
        if self.ydw:
            register_phone = register_phone + '宜贷网' + '\t'

        self.xylc_register(phone)
        if self.xylc:
            register_phone = register_phone + '小盈理财' + '\t'

        self.yld_register(phone)
        if self.yld:
            register_phone = register_phone + '翼龙贷' + '\t'

        self.trjr_register(phone)
        if self.trjr:
            register_phone = register_phone + '泰然金融' + '\t'

        if self.ppd or self.wdw or self.aqj or self.tdw or self.ydw or self.xylc or self.yld or self.trjr:
            register_phone = phone + '\t' + register_phone
            with open(self.path, 'a') as f:
                f.write(register_phone)
                f.write('\n')
                print(phone+':在 '+register_phone+'  注册')
        else:
            print(phone+'   未注册')


# 号码爬取
class Phone:
    def __init__(self, p2p):
        # 移动号段
        self.yidong = ['139', '138', '137', '136', '135', '134', '147', '150', '151', '152', '157', '158', '159', '178',
                       '182', '183', '184', '187', '188']
        # 联通号段
        self.liantong = ['130', '131', '132', '155', '156', '185', '186', '145', '176']
        # 电信号段
        self.dianxin = ['133', '153', '177', '173', '180', '181', '189']
        # p2p注册对象
        self.p2p = p2p
        # 地区
        self.area_argv = p2p.path

    # 获取号段地区
    def get_haoduan_area(self, haoduan):
        try:
            # 一页的数据
            data_list = []
            url = 'http://www.jihaoba.com/haoduan/%s/%s.htm' %(haoduan, self.area_argv)
            html = requests.get(url, proxies=proxies, timeout=3).content
            soup = BeautifulSoup(html, "lxml")
            phones = soup.find_all('ul', class_='hd-city')[1]
            phones = phones.find_all('li', 'hd-city01')
            for phone in phones:
                data_list.append(phone.a.get_text(strip=True))
            return data_list
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 通过地区爬取号码
    def diqv(self):
        print('======'+self.area_argv+'  地区======')
        for haoduan in self.yidong:
            haoduan_area = self.get_haoduan_area(haoduan)
            for area in haoduan_area:
                for i in range(0000, 10000):
                    suffix_len = str(i).__len__()
                    if suffix_len < 4:
                        suffix_need = 4 - suffix_len
                        number = area + '0' * suffix_need + str(i)
                    else:
                        number = area + str(i)
                    self.p2p.p2p_register(number)

        for haoduan in self.liantong:
            haoduan_area = self.get_haoduan_area(haoduan)
            for area in haoduan_area:
                for i in range(0000, 10000):
                    suffix_len = str(i).__len__()
                    if suffix_len < 4:
                        suffix_need = 4 - suffix_len
                        number = area + '0' * suffix_need + str(i)
                    else:
                        number = area + str(i)
                    self.p2p.p2p_register(number)

        for haoduan in self.dianxin:
            haoduan_area = self.get_haoduan_area(haoduan)
            for area in haoduan_area:
                for i in range(0000, 10000):
                    suffix_len = str(i).__len__()
                    if suffix_len < 4:
                        suffix_need = 4 - suffix_len
                        number = area + '0' * suffix_need + str(i)
                    else:
                        number = area + str(i)
                    self.p2p.p2p_register(number)

    def start(self):
        self.diqv()


if __name__ == '__main__':
    # p2p.p2p_register('15866548865')
    # p2p.p2p_register('15866668888')
    # p2p.p2p_register('15986988965')
    # p2p.p2p_register('15968846255')

    area_argv = 'hangzhou'
    # area_argv = 'shanghai'
    # area_argv = 'beijing'
    # area_argv = 'shenzhen'
    # area_argv = 'guangzhou'


    # area_argv = 'wuhan'
    # area_argv = 'chengdu'
    # area_argv = 'zhengzhou'
    # area_argv = 'sjz'
    # area_argv = 'nanjing'

    # area_argv = sys.argv[1]
    p2p = P2P(area_argv)
    phone = Phone(p2p)
    phone.start()


