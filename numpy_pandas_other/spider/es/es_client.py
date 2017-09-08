#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import elasticsearch
from elasticsearch.helpers import bulk
import json
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class ElasticSearchClient(object):
    @classmethod
    def get_es_servers(cls):
        hosts = [
            {"host": "172.16.39.55", "port": 9200},
            {"host": "172.16.39.56", "port": 9200},
            {"host": "172.16.39.57", "port": 9200}
        ]
        es = elasticsearch.Elasticsearch(
            hosts,
            sniff_on_start=True,
            sniff_on_connection_fail=True,
            sniffer_timeout=6000,
            http_auth=('elastic', 'cgtz@bigdata')
        )
        return es


def is_chinese(s):
    """
    判断是否有中文
    :return:
    """
    for ch in s.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


class LoadElasticSearch(object):
    def __init__(self, index, doc_type):
        self.index = index
        self.doc_type = doc_type
        self.es_client = ElasticSearchClient.get_es_servers()
        self.set_mapping()

    def set_mapping(self):
        """
        设置mapping
        """
        mapping = {
            self.doc_type: {
                "properties": {
                    "from_platform": {
                        "type": "string",
                        "index": "no"
                    },
                    "name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "ID_card_no": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "ID_card_no_pre": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "phone_no": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "qq": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "gender": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "address": {
                        "type": "string",
                        "analyzer": "ik_smart"
                    },
                    "involved_amt": {
                        "type": "string",
                        "index": "no"
                    },
                    "filing_time": {
                        "type": "string",
                        "index": "no"
                    },
                    "case_code": {
                        "type": "string",
                        "analyzer": "ik_smart"
                    },
                    "notes": {
                        "type": "string",
                        "analyzer": "ik_smart"
                    }
                }
            }
        }
        if not self.es_client.indices.exists(index=self.index):
            # 创建Index和mapping
            self.es_client.indices.create(index=self.index)
            self.es_client.indices.put_mapping(index=self.index,
                                               doc_type=self.doc_type,
                                               body=mapping)
        else:
            print(self.index + ' exist')

    def add_date(self, row_obj):
        """
        单条插入ES
        """
        _id = row_obj.get("_id", 1)
        row_obj.pop("_id")
        self.es_client.index(index=self.index, doc_type=self.doc_type, body=row_obj, id=_id)

    # 如果返回结果>=1,这表明该黑名单已经存在了
    def search_data(self, id_card_no, name):
        return len(self.es_client.search(index="blacklist",
                                         body={"query": {"bool": {"filter": [{"term": {"ID_card_no": str(id_card_no)}},
                                                                             {"term": {"name": str(name)}}]}}})['hits'][
                       'hits'])

    def add_date_bulk(self, row_obj_list):
        """
        批量插入ES
        """
        load_data = []
        i = 1
        bulk_num = 2000  # 2000条为一批
        for row_obj in row_obj_list:
            id_card = row_obj.get('ID_card_no', '')
            name = row_obj.get('name', '')
            if id_card and name and len(id_card) >= 6 and (not is_chinese(id_card)):
                action = {
                    "_index": self.index,
                    "_type": self.doc_type,
                    "_id":str(id_card)+str(name),
                    "_source": {
                        'from_platform': row_obj.get('from_platform', '').strip(),
                        'name': row_obj.get('name', '').strip(),
                        'ID_card_no': row_obj.get('ID_card_no', '').strip(),
                        'ID_card_no_pre': row_obj.get('ID_card_no_pre', '').strip(),
                        'phone_no': row_obj.get('phone_no', '').strip(),
                        'qq': row_obj.get('qq', '').strip(),
                        'gender': row_obj.get('gender', '').strip(),
                        'address': row_obj.get('address', '').strip(),
                        'involved_amt': row_obj.get('involved_amt', '').strip(),
                        'filing_time': row_obj.get('filing_time', '').strip(),
                        'case_code': row_obj.get('case_code', '').strip(),
                        'notes': row_obj.get('notes', '').strip(),
                    }
                }
                load_data.append(action)
                i += 1
                # 批量处理
                if len(load_data) == bulk_num:
                    print '插入', i / bulk_num, '批数据'
                    print len(load_data)
                    success, failed = bulk(self.es_client, load_data, index=self.index, raise_on_error=True)
                    del load_data[0:len(load_data)]
                    print success, failed

        if len(load_data) > 0:
            success, failed = bulk(self.es_client, load_data, index=self.index, raise_on_error=True)
            del load_data[0:len(load_data)]
            print success, failed

    def update_by_id(self, row_obj):
        """
        根据给定的_id,更新ES文档
        :return:
        """
        _id = row_obj.get("_id", 1)
        row_obj.pop("_id")
        self.es_client.update(index=self.index, doc_type=self.doc_type, body={"doc": row_obj}, id=_id)

    def delete_by_id(self, _id):
        """
        根据给定的id,删除文档
        :return:
        """
        self.es_client.delete(index=self.index, doc_type=self.doc_type, id=_id)

    @staticmethod
    def jiedaibao_parse_insert():
        row_obj_list = []
        with open('./jiedaibaoyuqi_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '借贷宝'.decode("utf-8")
                temp_data['involved_amt'] = json_line['逾期金额'.decode("utf-8")]
                temp_data['name'] = json_line['借贷宝姓名'.decode("utf-8")]
                temp_data['address'] = json_line['身份证住址'.decode("utf-8")]
                temp_data['filing_time'] = json_line['逾期时间'.decode("utf-8")]
                temp_data['ID_card_no'] = json_line['身份证号码'.decode("utf-8")]
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                temp_data['phone_no'] = json_line['借贷宝账号'.decode("utf-8")]
                temp_data['qq'] = json_line['QQ号码'.decode("utf-8")]
                temp_data['notes'] = json_line['说明'.decode("utf-8")]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def jyqfy_gov_parse_insert():
        row_obj_list = []
        with open('./jyqfy_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '德阳市旌阳区政府'.decode("utf-8")
                temp_data['name'] = json_line.get('失信被执行人'.decode("utf-8"), '')
                temp_data['filing_time'] = json_line.get('立案日期'.decode("utf-8"), '')
                temp_data['ID_card_no'] = json_line.get('证件号码'.decode("utf-8"), '')
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                temp_data['case_code'] = json_line.get('案号'.decode("utf-8"), '')
                temp_data['notes'] = json_line.get('信息类型'.decode("utf-8"), '')
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def beicaiwang_parse_insert():
        row_obj_list = []
        with open('./beicaiwang_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '贝才网'.decode("utf-8")
                temp_data['qq'] = json_line.get('QQ'.decode("utf-8"), '')
                temp_data['address'] = json_line.get('家庭住址'.decode("utf-8"), '')
                temp_data['involved_amt'] = json_line.get('逾期金额'.decode("utf-8"), '')
                temp_data['address'] = json_line.get('身份证地址'.decode("utf-8"), '')
                temp_data['gender'] = json_line.get('性别'.decode("utf-8"), '')
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '')
                temp_data['ID_card_no'] = json_line.get('身份证号码'.decode("utf-8"), '')
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def hbfy_gov_parse_insert():
        row_obj_list = []
        with open('./hbfy_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '武汉市黄陂区法院'.decode("utf-8")
                temp_data['name'] = json_line.get('被执行人'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('依据文书'.decode("utf-8"), '')
                temp_data['address'] = json_line.get('住所地'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def kaikaidai_parse_insert():
        row_obj_list = []
        with open('./kaikaidai_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '开开贷'.decode("utf-8")
                temp_data['name'] = json_line.get('真实姓名'.decode("utf-8"), '').strip()
                temp_data['phone_no'] = json_line.get('手机'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('逾期待还总额'.decode("utf-8"), '').strip()
                temp_data['qq'] = json_line.get('E_mail'.decode("utf-8"), '').strip()
                temp_data['address'] = json_line.get('地址'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def sccourt_gov_parse_insert():
        row_obj_list = []
        with open('./sccourt_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '四川法院司法'.decode("utf-8")
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('执行案号'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('证件号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def xinyongheimingdan_parse_insert():
        row_obj_list = []
        with open('./xinyongheimingdan_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '信用黑名单网'.decode("utf-8")
                temp_data['phone_no'] = json_line.get('电话'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('金额'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('状态'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def nanhai_gov_parse_insert():
        row_obj_list = []
        with open('./nanhai_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '佛山市南海区法院'.decode("utf-8")
                temp_data['involved_amt'] = json_line.get('未履行义务内容（万元）'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('执行案号'.decode("utf-8"), '').strip()
                temp_data['filing_time'] = json_line.get('立案时间'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def dailianmeng_parse_insert():
        row_obj_list = []
        with open('./dailianmeng_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '贷联盟网'.decode("utf-8")
                temp_data['phone_no'] = json_line.get('手机号'.decode("utf-8"), '').strip()
                temp_data['qq'] = json_line.get('邮箱地址'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('未还/罚息'.decode("utf-8"), '').strip()
                temp_data['filing_time'] = json_line.get('借款时间'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def luchengqu_parse_insert():
        row_obj_list = []
        with open('./luchengqu_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '鹿城区法院'.decode("utf-8")
                temp_data['case_code'] = json_line.get('案件字号'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('案由'.decode("utf-8"), '').strip()
                temp_data['address'] = json_line.get('地址'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('执行标的额'.decode("utf-8"), '').strip()
                temp_data['gender'] = json_line.get('性别'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def jscredit_parse_insert():
        row_obj_list = []
        with open('./jscredit_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '信用江苏'.decode("utf-8")
                temp_data['name'] = json_line.get('被执行人姓名'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('案号'.decode("utf-8"), '').strip()
                temp_data['filing_time'] = json_line.get('立案时间'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证件号'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def hbcredit_parse_insert():
        row_obj_list = []
        with open('./hbcredit_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '信用湖北'.decode("utf-8")
                temp_data['case_code'] = json_line.get('处罚内容'.decode("utf-8"), '').strip()
                temp_data['filing_time'] = json_line.get('处罚日期'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('事项名称'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def cqfygzfw_parse_insert():
        row_obj_list = []
        with open('./cqfygzfw_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '重庆法院'.decode("utf-8")
                temp_data['filing_time'] = json_line.get('立案日期'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('案件字号'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['gender'] = json_line.get('性别'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('身份证号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def nbcredit_gov_parse_insert():
        row_obj_list = []
        with open('./nbcredit_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '信用宁波'.decode("utf-8")
                temp_data['filing_time'] = json_line.get('立案时间'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('案号'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('被执行人姓名'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('失信被执行人行为具体情形'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('居民身份证号'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def zjsfgkw_parse_insert(i):
        row_obj_list = []
        with open('./zjsfgkw_blacklist_'+str(i), 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '浙江司法公开网'.decode("utf-8")
                temp_data['filing_time'] = json_line.get('立案日期'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('案号'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('未执行金额'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('姓名'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('执行案由'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('证件号码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def anxifayuan_gov_parse_insert():
        row_obj_list = []
        with open('./anxifayuan_blacklist', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = line.split('\t')
                if 8 == len(json_line):
                    temp_data['from_platform'] = '安溪法院'.decode("utf-8")
                    temp_data['filing_time'] = json_line[7].strip().decode("utf-8")
                    temp_data['case_code'] = json_line[5].strip().decode("utf-8")
                    temp_data['name'] = json_line[0].strip().decode("utf-8")
                    temp_data['notes'] = json_line[4].strip().decode("utf-8")
                    temp_data['ID_card_no'] = json_line[1].strip().decode("utf-8")
                    id_card_no_pre = temp_data.get('ID_card_no', None)
                    # 获取身份证，如果有
                    if id_card_no_pre:
                        temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                    row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def gzcourt_gov_parse_insert():
        row_obj_list = []
        with open('./gzcourt_gov_blacklist.json', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                json_line = json.loads(line)
                temp_data['from_platform'] = '广州审判网'.decode("utf-8")
                temp_data['address'] = json_line.get('执行法院'.decode("utf-8"), '').strip()
                temp_data['involved_amt'] = json_line.get('执行标的（万元）'.decode("utf-8"), '').strip()
                temp_data['case_code'] = json_line.get('执行案号'.decode("utf-8"), '').strip()
                temp_data['name'] = json_line.get('被执行人姓名（名称）'.decode("utf-8"), '').strip()
                temp_data['notes'] = json_line.get('失信情形'.decode("utf-8"), '').strip()
                temp_data['ID_card_no'] = json_line.get('被执行人身份证号码或组织机构代码'.decode("utf-8"), '').strip()
                id_card_no_pre = temp_data.get('ID_card_no', None)
                # 获取身份证，如果有
                if id_card_no_pre:
                    temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                row_obj_list.append(temp_data)
        return row_obj_list

    @staticmethod
    def user_id_black_parse_insert():
        row_obj_list = []
        with open('./user_id_black.txt', 'r') as f:
            for line in f:
                temp_data = write_obj.copy()
                line = line.split('\t')
                if len(line) == 7:
                    temp_data['name'] = line[1].strip()
                    temp_data['address'] = line[3].strip()
                    temp_data['phone_no'] = line[4].strip()
                    temp_data['from_platform'] = line[6].strip()
                    temp_data['ID_card_no'] = line[2].strip()
                    id_card_no_pre = temp_data.get('ID_card_no', None)
                    # 获取身份证，如果有
                    if id_card_no_pre:
                        temp_data['ID_card_no_pre'] = id_card_no_pre[0: 6]
                    row_obj_list.append(temp_data)
        return row_obj_list


if __name__ == '__main__':
    write_obj = {
        # 来源平台
        'from_platform': '',
        # 姓名
        "name": '',
        # 身份证
        "ID_card_no": '',
        # 身份证前缀六位
        "ID_card_no_pre": '',
        # 电话号码
        "phone_no": '',
        # QQ号码/E_mail/微信号
        'qq': '',
        # 性别
        'gender': '',
        # 地址
        'address': '',
        # 涉案金额
        'involved_amt': '',
        # 立案时间/逾期时间
        'filing_time': '',
        # 案号
        'case_code': '',
        # 备注
        'notes': ''
    }
    load_es = LoadElasticSearch('blacklist', 'promise')

    # 批量插入数据测试
    # print('--------jiedaibao_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.jiedaibao_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('--------jyqfy_gov_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.jyqfy_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('--------beicaiwang_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.beicaiwang_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('--------hbfy_gov_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.hbfy_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('---------kaikaidai_parse_insert----------')
    # row_obj_list = LoadElasticSearch.kaikaidai_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('--------sccourt_gov_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.sccourt_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('---------xinyongheimingdan_parse_insert----------')
    # row_obj_list = LoadElasticSearch.xinyongheimingdan_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('--------nanhai_gov_parse_insert-----------')
    # row_obj_list = LoadElasticSearch.nanhai_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('---------dailianmeng_parse_insert----------')
    # row_obj_list = LoadElasticSearch.dailianmeng_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('---------luchengqu_parse_insert----------')
    # row_obj_list = LoadElasticSearch.luchengqu_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('----------jscredit_parse_insert---------')
    # row_obj_list = LoadElasticSearch.jscredit_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('----------hbcredit_parse_insert---------')
    # row_obj_list = LoadElasticSearch.hbcredit_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('----------cqfygzfw_parse_insert---------')
    # row_obj_list = LoadElasticSearch.cqfygzfw_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    #
    # print('----------nbcredit_gov_parse_insert---------')
    # row_obj_list = LoadElasticSearch.nbcredit_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)
    # for i in range(1, 12):
    #     print('----------zjsfgkw'+str(i)+'_parse_insert ---------')
    #     row_obj_list = LoadElasticSearch.zjsfgkw_parse_insert(i)
    #     load_es.add_date_bulk(row_obj_list)
    #
    # print('----------gzcourt_gov_parse_insert---------')
    # row_obj_list = LoadElasticSearch.gzcourt_gov_parse_insert()
    # load_es.add_date_bulk(row_obj_list)

    print('----------user_id_black_parse_insert---------')
    row_obj_list = LoadElasticSearch.user_id_black_parse_insert()
    load_es.add_date_bulk(row_obj_list)