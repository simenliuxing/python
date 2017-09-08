#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
      百度失信人黑名单的爬取
"""
from time import strftime,gmtime
import elasticsearch
import requests
import sys
import collections
import time
import json
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
# headers
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cookie': 'JSESSIONID=9CAA8C2BEE80C74B1952EFA9E69C4150; '
              'wafenterurl=L3NzZncvZnltaC8xNDUxL3p4Z2suaHRtP3N0PTAmcT0mc3hseD0xJmJ6e'
              'HJseD0xJmNvdXJ0X2lkPSZienhybWM9JnpqaG09JmFoPSZzdGFydENwcnE9JmVuZENwcnE9JnBhZ2U9Mw==; '
              '__utma=161156077.495504895.1501221471.1501221471.1501221471.1; '
              '__utmc=161156077; '
              '__utmz=161156077.1501221471.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
              'wafcookie=6638c7e043d4634e31fc03f98c44d6c6; '
              'wafverify=1ac90afbc1da7e6e86e4f07057416bcb; '
              'wzwsconfirm=7711ddd10a544f8efa642db4685e86e8; '
              'wzwstemplate=OA==; '
              'clientlanguage=zh_CN; '
              'JSESSIONID=0E40DC7D29A84A4528787317B590F218; '
              'ccpassport=601fd92b79652fe0489b52310512d73b; '
              'wzwschallenge=-1; '
              'wzwsvtime=1501226469',
    'Host': 'www.ahgyss.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://www.ahgyss.cn/ssfw/fymh/1451/zxgk.htm'
               '?st=0&q=&sxlx=&bzxrlx=&court_id=&bzxrmc=&zjhm=&ah=&startCprq=&endCprq=&page=11',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36'
}

# es链接地址
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


# es数据操作
class LoadElasticSearchTest(object):
    def __init__(self, index, doc_type):
        self.index = index
        self.doc_type = doc_type
        self.es_client = ElasticSearchClient.get_es_servers()

    # 如果返回结果>=1,这表明该黑名单已经存在了
    def search_data(self, id_card_no, name):
        return len(self.es_client.search(index="blacklist",
                                         body={"query": {"bool": {"filter": [{"term": {"ID_card_no": str(id_card_no)}},{ "term": { "name":  str(name) }}]}}})['hits']['hits'])

    def add_date(self, id, row_obj):
        """
        单条插入ES
        """
        resu = self.es_client.index(index=self.index, doc_type=self.doc_type, id=id, body=row_obj)
        return resu.get('created', '')


# 数据解析
def parse_data(html):
    # 一页的数据
    data_list = []
    # 具体数据
    rest = html["data"]
    rest = rest[0]["result"]
    if len(rest) > 0:
        try:
            for rs in rest:
                try:
                    result = collections.OrderedDict()
                    result['name'] = rs.get('iname', '')
                    result['ID_card_no'] = rs.get('cardNum', '')
                    id_card_no_pre = result.get('ID_card_no', '')
                    # 获取身份证，如果有
                    if id_card_no_pre:
                        result['ID_card_no_pre'] = id_card_no_pre[0: 6]
                    result['from_platform'] = rs.get('courtName', '')
                    result['case_code'] = rs.get('caseCode', '')
                    result['filing_time'] = rs.get('publishDate', '')
                    result['notes'] = rs.get('disruptTypeName', '')
                    result['involved_amt'] = rs.get('duty', '')
                    result['gender'] = rs.get('sexy', '')
                    result['address'] = rs.get('areaName', '')
                    data_list.append(result)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    return data_list


# 爬取数据
def spider_data(url):
    try:
        try:
            # 使用代理
            res = requests.get(url, timeout=10, proxies=proxies)
        except ProxyError:
            print("ProxyError Exception ,use no proxies ")
            # 不使用代理
            res = requests.get(url, timeout=10)
        res = res.content
        res = res[:-2]
        res = res[46:]
        return json.loads(res)
    except Exception as e:
        print("爬取失败", e)
        return -1


# 数据最终结果的封装
def package_data(result):
    # 结果数据的封装
    message = collections.OrderedDict()
    if len(result) == 0:
        message["statue_code"] = 0
        message["msg_size"] = 0
    else:
        message["statue_code"] = 1
        message["msg_size"] = len(result)
        message["msg"] = result
    return json.dumps(message).decode("unicode-escape")


# 数据的解析,写到elastic中
def parse_data_write_es(rest):
    users = rest["msg"]
    if len(users) > 0:
        load_es = LoadElasticSearchTest('blacklist', 'promise')
        insert_count = 0
        for user in users:
            try:
                id_card = user.get('ID_card_no', '')
                name = user.get('name', '')
                if id_card and name and len(id_card) >= 6 and (not is_chinese(id_card)):
                    from_platform = user.get('from_platform', '').strip()
                    name = user.get('name', '').strip()
                    ID_card_no = user.get('ID_card_no', '').strip()
                    ID_card_no_pre = user.get('ID_card_no_pre', '').strip()
                    phone_no = user.get('phone_no', '').strip()
                    qq = user.get('qq', '').strip()
                    gender = user.get('gender', '').strip()
                    address = user.get('address', '').strip()
                    involved_amt = user.get('involved_amt', '').strip()
                    filing_time = user.get('filing_time', '').strip()
                    case_code = user.get('case_code', '').strip()
                    notes = user.get('notes', '').strip()

                    id = str(id_card) + str(name)
                    action = '{"from_platform": \"'+from_platform+'\", ' \
                              '"name": \"'+name+'\", ' \
                              '"ID_card_no": \"'+ID_card_no+'\", ' \
                              '"ID_card_no_pre": \"'+ID_card_no_pre+'\", ' \
                              '"phone_no": \"'+phone_no+'\", ' \
                              '"qq": \"'+qq+'\", ' \
                              '"gender": \"'+gender+'\", ' \
                              '"address": \"'+address+'\", ' \
                              '"involved_amt": \"'+involved_amt+'\", ' \
                              '"filing_time": \"'+filing_time+'\", ' \
                              '"case_code": \"'+case_code+'\",' \
                              '"notes": \"'+notes+'\"}'

                    if load_es.add_date(id, action) == True:
                        insert_count += 1
            except Exception as e:
                print(e)
        print('该批次共插入 '+str(insert_count)+' 条数据')


# 爬取每页的具体数据（处理超时异常,默认10次重试）
def re_spider_page_data(url_list):
    count = 1
    for url in url_list:
        try:
            html = spider_data(url)
            # 如果没有获取到数据则重试多次
            if html == -1:
                # 如果没有爬取成功则，重爬
                for num in range(1, 10):
                    time.sleep(8)
                    print(num)
                    if html == -1:
                        html = spider_data(url)
                    else:
                        break
            # 解析数据
            result = parse_data(html)
            # 包装数据
            result = package_data(result)
            result = json.loads(result)
            print('第 ' + str(count) + ' 页爬取，共 '+str(len(result["msg"]))+' 条数据====>')
            parse_data_write_es(result)
            time.sleep(1)
            count += 1
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # 常用字
    # first_name_list = ['诚', '夫', '声', '冬', '奎', '扬', '双', '坤', '镇', '楚', '水', '铁', '喜', '之', '迪', '泰', '方', '同', '滨','邦',
    #                    '先', '聪', '朝', '善', '非', '恒', '晋', '汝', '丹', '为', '晨', '乃', '秀', '岩', '辰', '洋', '然', '厚', '灿','卓',
    #                    '轩', '帆', '若', '连', '勋', '祖', '锡', '吉', '崇', '钧', '田', '石', '奕', '发', '洲', '彪', '钢', '运', '伯','满',
    #                    '庭', '申', '湘', '皓', '承', '梓', '雪', '孟', '其', '潮', '冰', '怀', '鲁', '裕', '翰', '征', '谦', '航', '士','尧',
    #                    '标', '洁', '城', '寿', '枫', '革', '纯', '风', '化', '逸', '腾', '岳', '银', '鹤', '琳', '显', '焕', '来', '心','凤',
    #                    '睿', '勤', '延', '凌', '昊', '西', '羽', '百', '捷', '定', '琦', '圣', '佩', '麒', '虹', '如', '靖', '日', '咏','会',
    #                    '久', '昕', '黎', '桂', '玮', '燕', '可', '越', '彤', '雁', '孝', '宪', '萌', '颖', '艺', '夏', '桐', '月', '瑜','沛',
    #                    '杨', '钰', '兰', '怡', '灵', '淇', '美', '琪', '亦', '晶', '舒', '菁', '真', '涵', '爽', '雅', '爱', '依', '静','棋',
    #                    '宜', '男', '蔚', '芝', '菲', '露', '娜', '珊', '雯', '淑', '曼', '萍', '珠', '诗', '璇', '琴', '素', '梅', '玲','蕾',
    #                    '艳', '紫', '珍', '丽', '仪', '梦', '倩', '伊', '茜', '妍', '碧', '芬', '儿', '岚', '婷', '菊', '妮', '媛', '莲','娟'
    #                    ]
    first_name_list = [
        '蕊','薇','菁','梦','岚','苑','婕','馨','瑗','琰','韵','融','园','艺','咏','卿','聪','澜','纯',
        '爽','琬','茗','羽','希','宁','欣','飘','育','滢','馥','筠','柔','竹','霭','凝','晓','欢','霄',
        '伊','亚','宜','可','姬','舒','影','荔','枝','思','丽','芬','芳','燕','莺','媛','艳','珊','莎',
        '秀','娟','英','华','慧','巧','美','娜','静','淑','惠','珠','翠','雅','芝','玉','萍','红','月',
        '彩','春','菊','兰','凤','洁','梅','琳','素','云','莲','真','环','雪','荣','爱','妹','霞','香',
        '瑞','凡','佳','嘉','琼','勤','珍','贞','莉','桂','娣','叶','璧','璐','娅','琦','晶','妍','茜',
        '黛','青','倩','婷','姣','婉','娴','瑾','颖','露','瑶','怡','婵','雁','蓓','纨','仪','荷','丹',
        '蓉','眉','君','琴','毓','悦','昭','冰','枫','芸','菲','寒','锦','玲','秋','梁','栋','维','启',
        '盛','雄','琛','钧','冠','策','腾','楠','榕','风','航','弘','义','兴','良','飞','彬','富','和',
        '伟','刚','勇','毅','俊','峰','强','军','平','保','东','文','辉','力','明','永','健','世','广',
        '海','山','仁','波','宁','福','生','龙','元','全','国','胜','学','祥','才','发','武','新','利',
        '顺','信','子','杰','涛','昌','成','康','星','光','天','达','安','岩','中','茂','进','林','有',
        '诚','先','敬','震','振','壮','会','思','群','豪','心','邦','承','乐','绍','功','松','善','厚',
        '裕','河','哲','江','超','浩','亮','政','谦','亨','奇','固','之','轮','翰','朗','伯','宏','言',
        '克','伦','翔','旭','鹏','泽','晨','辰','士','以','建','家','致','树','炎','鸣','朋','斌','行',
        '时','泰','博','磊','民','友','志','清','坚','庆','若','德','彪'
    ]
    print('-----------------------start:'+str(strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+'-----------------------')
    for first_name in first_name_list:
        print('-------------------'+first_name+"-字：开始爬取-------------------")
        title = '失信被执行人名单'
        url_list = ['https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php' \
                    '?resource_id=6899'
                    '&query=' + title + ''
                    '&cardNum='
                    '&iname=' + first_name + ''
                    '&areaName='
                    '&ie=utf-8'
                    '&oe=utf-8'
                    '&format=json'
                    '&t=1504228484424'
                    '&cb=jQuery110203450799221787775_1504227514772'
                    '&_=1504227514784'
                    ]
        # 爬取姓氏的前30页
        for page_num in range(1, 30):
            url_list.append(
                        'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
                        '?resource_id=6899'
                        '&query=' + title + ''
                        '&cardNum='
                        '&iname=' + first_name + ''
                        '&areaName='
                        '&pn='+str(page_num*50)+''
                        '&rn=10'
                        '&ie=utf-8'
                        '&oe=utf-8'
                        '&format=json'
                        '&t=1504259202271'
                        '&cb=jQuery110205604198048294293_1504254835087'
                        '&_=1504254835152'
                        )
        re_spider_page_data(url_list)
    print('-----------------------end:' + str(strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '-----------------------')
