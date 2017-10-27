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
                                        body={"query": {"bool": {"filter": [{"term": {"ID_card_no": str(id_card_no)}},{ "term": { "name":  str(name) }}]}}})['hits']['hits'] )

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

                    id = str(id_card)+str(name)
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
    # 前200大姓氏
    first_name_list = [
        '张伟', '王伟', '王芳', '李伟', '李娜', '张敏', '李静', '王静', '刘伟', '王秀英', '张丽', '李秀英', '王丽', '张静', '张秀英',
        '李强', '王敏', '李敏', '王磊', '刘洋', '王艳', '王勇', '李军', '张勇', '李杰', '张杰', '张磊', '王强', '李娟', '王军', '张艳',
        '张涛', '王涛', '李艳', '王超', '李明', '李勇', '王娟', '刘杰', '刘敏', '李霞', '李丽', '张军', '王杰', '张强', '王秀兰', '王刚',
        '王平', '刘芳', '张燕', '刘艳', '刘军', '李平', '王辉', '王燕', '陈静', '刘勇', '李玲', '李桂英', '王丹', '李刚', '李丹', '李萍',
        '王鹏', '刘涛', '陈伟', '张华', '刘静', '李涛', '王桂英', '张秀兰', '李红', '李超', '刘丽', '张桂英', '王玉兰', '李燕', '张鹏',
        '李秀兰', '张超', '王玲', '张玲', '李华', '王飞', '张玉兰', '王桂兰', '王英', '刘强', '陈秀英', '李英', '李辉', '李梅', '陈勇',
        '王鑫', '李芳', '张桂兰', '李波', '杨勇', '王霞', '李桂兰', '王斌', '李鹏', '张平', '张莉', '张辉', '张宇', '刘娟', '李斌', '王浩',
        '陈杰', '王凯', '陈丽', '陈敏', '王秀珍', '李玉兰', '刘秀英', '王萍', '王萍', '张波', '刘桂英', '杨秀英', '张英', '杨丽', '张健',
        '李俊', '李莉', '王波', '张红', '刘丹', '李鑫', '王莉', '杨静', '刘超', '张娟', '杨帆', '刘燕', '刘英', '李雪', '李秀珍', '张鑫',
        '王健', '刘玉兰', '刘辉', '刘波', '张浩', '张明', '陈燕', '张霞', '陈艳', '杨杰', '王帅', '李慧', '王雪', '杨军', '张旭', '刘刚',
        '王华', '杨敏', '王宁', '李宁', '王俊', '刘桂兰', '刘斌', '张萍', '王婷', '陈涛', '王玉梅', '王娜', '张斌', '陈龙', '李林', '王玉珍',
        '张凤英', '王红', '李凤英', '杨洋', '李婷', '张俊', '王林', '陈英', '陈军', '刘霞', '陈浩', '张凯', '王晶', '陈芳', '张婷', '杨涛',
        '杨波', '陈红', '刘欢', '王玉英', '陈娟', '陈刚', '王慧', '张颖', '张林', '张娜', '张玉梅', '王凤英', '张玉英', '李红梅', '刘佳',
        '刘磊', '张倩', '刘鹏', '王旭', '张雪', '李阳', '张秀珍', '王梅', '王建华', '李玉梅', '王颖', '刘平', '杨梅', '李飞', '王亮', '李磊',
        '李建华', '王宇', '陈玲', '张建华', '刘鑫', '王倩', '张帅', '李健', '陈林', '李洋', '陈强', '赵静', '王成', '张玉珍', '陈超', '陈亮',
        '刘娜', '王琴', '张兰英', '张慧', '刘畅', '李倩', '杨艳', '张亮', '张建', '李云', '张琴', '王兰英', '李玉珍', '刘萍', '陈桂英', '刘颖',
        '杨超', '张梅', '陈平', '王建', '刘红', '赵伟', '张云', '张宁', '杨林', '张洁', '高峰', '王建国', '杨阳', '陈华', '杨华', '王建军',
        '杨柳', '刘阳', '王淑珍', '杨芳', '李春梅', '刘俊', '王海燕', '刘玲', '陈晨', '王欢', '李冬梅', '张龙', '陈波', '陈磊', '王云', '王峰',
        '王秀荣', '王瑞', '李琴', '李桂珍', '陈鹏', '王莹', '刘飞', '王秀云', '陈明', '王桂荣', '李浩', '王志强', '张丹', '李峰', '张红梅',
        '刘凤英', '李玉英', '王秀梅', '李佳', '王丽娟', '陈辉', '张婷婷', '张芳', '王婷婷', '王玉华', '张建国', '李兰英', '王桂珍', '李秀梅',
        '陈玉兰', '陈霞', '刘凯', '张玉华', '刘玉梅', '刘华', '李兵', '张雷', '王东', '李建军', '刘玉珍', '王琳', '李建国', '李颖', '杨伟',
        '李桂荣', '王龙', '刘婷', '陈秀兰', '张建军', '李秀荣', '刘明', '周敏', '张秀梅', '李雪梅', '黄伟', '张海燕', '王淑兰', '李志强',
        '杨磊', '李晶', '李婷婷', '张秀荣', '刘建华', '王丽丽', '赵敏', '陈云', '李海燕', '张桂荣', '张晶', '刘莉', '李凯', '张玉', '张峰',
        '刘秀兰', '张志强', '李龙', '李秀云', '李秀芳', '李帅', '李欣', '刘云', '张丽丽', '李洁', '张秀云', '王淑英', '王春梅', '王红梅',
        '陈斌', '李玉华', '李桂芳', '张莹', '陈飞', '王博', '刘浩', '黄秀英', '刘玉英', '李淑珍', '黄勇', '周伟', '王秀芳', '王丽华', '王丹丹',
        '李彬', '王桂香', '王坤', '刘慧', '李想', '张瑞', '张桂珍', '王淑华', '刘帅', '张飞', '张秀芳', '王洋', '陈洁', '张桂芳', '张丽娟', '王荣',
        '吴秀英', '杨明', '李桂香', '马丽', '刘倩', '杨秀兰', '杨玲', '王秀华', '杨平', '王彬', '李亮', '李荣', '李桂芝', '李琳', '李岩', '李建',
        '王兵', '王桂芳', '王明', '陈梅', '张春梅', '李杨', '王岩', '王冬梅', '刘峰', '李秀华', '李丹丹', '杨雪', '刘玉华', '马秀英', '张丽华',
        '张淑珍', '李小红', '张博', '王欣', '王桂芝', '赵丽', '张秀华', '张琳', '黄敏', '杨娟', '王金凤', '周杰', '王雷', '陈建华', '刘梅', '杨桂英',
        '李淑英', '陈玉英', '杨秀珍', '孙秀英', '赵军', '赵勇', '刘兵', '杨斌', '李文', '陈琳', '陈萍', '孙伟', '张利', '陈俊', '张楠', '刘桂珍', '刘宇',
        '刘建军', '张淑英', '李红霞', '赵秀英', '李博', '王利', '张荣', '张帆', '王建平', '张桂芝', '张瑜', '周勇', '张坤', '徐伟', '王桂花', '刘琴',
        '周静', '徐敏', '刘婷婷', '徐静', '杨红', '王璐', '张淑兰', '张文', '杨燕', '陈桂兰', '周丽', '李淑华', '陈鑫', '马超', '刘建国', '李桂花',
        '王凤兰', '李淑兰', '陈秀珍', '李红霞', '赵秀英', '李博', '王利', '张荣', '张帆', '王建平', '张桂芝', '张瑜', '周勇', '张坤', '徐伟', '王桂花',
        '刘琴', '周静', '徐敏', '刘婷婷', '徐静', '杨红', '王璐', '张淑兰', '张文', '杨燕', '陈桂兰', '周丽', '李淑华', '陈鑫', '马超', '刘建国',
        '李桂花', '王凤兰', '李淑兰', '陈秀珍'
    ]

    print('-----------------------start:' + str(strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '-----------------------')
    for first_name in first_name_list:
        print('-------------------'+first_name+"-姓氏：开始爬取-------------------")
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
        # 爬取姓氏的前50页
        for page_num in range(0, 100):
            url_list.append(
                        'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
                        '?resource_id=6899'
                        '&query=' + title + ''
                        '&cardNum='
                        '&iname=' + first_name + ''
                        '&areaName='
                        '&pn='+str(page_num*10)+''
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
