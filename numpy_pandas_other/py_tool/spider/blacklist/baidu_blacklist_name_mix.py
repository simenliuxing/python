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
    first_name_list = ['李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                       '徐', '孙', '朱', '马', '胡', '郭', '林', '何', '高', '梁',
                       '郑', '罗', '宋', '谢', '唐', '韩', '曹', '许', '邓', '萧',
                       '冯', '曾', '程', '蔡', '彭', '潘', '袁', '於', '董', '余',
                       '苏', '叶', '吕', '魏', '蒋', '田', '杜', '丁', '沈', '姜',
                       '范', '江', '傅', '钟', '卢', '汪', '戴', '崔', '任', '陆',
                       '廖', '姚', '方', '金', '邱', '夏', '谭', '韦', '贾', '邹',
                       '石', '熊', '孟', '秦', '阎', '薛', '侯', '雷', '白', '龙',
                       '段', '郝', '孔', '邵', '史', '毛', '常', '万', '顾', '赖',
                       '钱', '施', '牛', '洪', '龚', '文', '庞', '樊', '兰', '殷',
                       '颜', '倪', '严', '牛', '温', '芦', '季', '俞', '章', '鲁',
                       '葛', '伍', '韦', '申', '尤', '毕', '聂', '丛', '焦', '向',
                       '柳', '邢', '路', '岳', '齐', '沿', '梅', '莫', '庄', '辛',
                       '管', '祝', '左', '涂', '谷', '祁', '时', '舒', '耿', '牟',
                       '卜', '路', '詹', '关', '苗', '凌', '费', '纪', '靳', '盛',
                       '童', '欧', '甄', '项', '曲', '成', '游', '阳', '裴', '席',
                       '卫', '查', '屈', '鲍', '位', '覃', '霍', '翁', '隋', '植',
                       '甘', '景', '薄', '单', '包', '司', '柏', '宁', '柯', '阮',
                       '施', '陶', '洪', '翟', '安', '武', '康', '贺', '严', '尹',
                       '桂', '闵', '欧阳', '解', '强', '柴', '华', '车', '冉', '房'
                       ]
    first_name_list2 = [
        '的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到', '时', '大', '地', '为', '子', '中',
        '你', '说', '生', '国', '年', '着', '就', '那', '和', '要',
        '她', '出', '也', '得', '里', '后', '自', '以', '会', '家', '可', '下', '而', '过', '天', '去', '能', '对', '小', '多', '然', '于',
        '心', '学', '么', '之', '都', '好', '看', '起', '发', '当',
        '没', '成', '只', '如', '事', '把', '还', '用', '第', '样', '道', '想', '作', '种', '开', '美', '总', '从', '无', '情', '己', '面',
        '最', '女', '但', '现', '前', '些', '所', '同', '日', '手',
        '又', '行', '意', '动', '方', '期', '它', '头', '经', '长', '儿', '回', '位', '分', '爱', '老', '因', '很', '给', '名', '法', '间',
        '斯', '知', '世', '什', '两', '次', '使', '身', '者', '被',
        '高', '已', '亲', '其', '进', '此', '话', '常', '与', '活', '正', '感', '见', '明', '问', '力', '理', '尔', '点', '文', '几', '定',
        '本', '公', '特', '做', '外', '孩', '相', '西', '果', '走',
        '将', '月', '十', '实', '向', '声', '车', '全', '信', '重', '三', '机', '工', '物', '气', '每', '并', '别', '真', '打', '太', '新',
        '比', '才', '便', '夫', '再', '书', '部', '水', '像', '眼',
        '等', '体', '却', '加', '电', '主', '界', '门', '利', '海', '受', '听', '表', '德', '少', '克', '代', '员', '许', '稜', '先', '口',
        '由', '死', '安', '写', '性', '马', '光', '白', '或', '住',
        '难', '望', '教', '命', '花', '结', '乐', '色', '更', '拉', '东', '神', '记', '处', '让', '母', '父', '应', '直', '字', '场', '帄',
        '报', '友', '关', '放', '至', '张', '认', '接', '告', '入',
        '笑', '内', '英', '军', '候', '民', '岁', '往', '何', '度', '山', '觉', '路', '带', '万', '男', '边', '风', '解', '叫', '任', '金',
        '快', '原', '吃', '妈', '变', '通', '师', '立', '象', '数',
        '四', '失', '满', '战', '远', '格', '士', '音', '轻', '目', '条', '呢', '病', '始', '达', '深', '完', '今', '提', '求', '清', '王',
        '化', '空', '业', '思', '切', '怎', '非', '找', '片', '罗',
        '钱', '紶', '吗', '语', '元', '喜', '曾', '离', '飞', '科', '言', '干', '流', '欢', '约', '各', '即', '指', '合', '反', '题', '必',
        '该', '论', '交', '终', '林', '请', '医', '晚', '制', '球',
        '决', '窢', '传', '画', '保', '读', '运', '及', '则', '房', '早', '院', '量', '苦', '火', '布', '品', '近', '坐', '产', '答', '星',
        '精', '视', '五', '连', '司', '巴', '奇', '管', '类', '未',
        '朋', '且', '婚', '台', '夜', '青', '北', '队', '久', '乎', '越', '观', '落', '尽', '形', '影', '红', '爸', '百', '令', '周', '吧',
        '识', '步', '希', '亚', '术', '留', '市', '半', '热', '送',
        '兴', '造', '谈', '容', '极', '随', '演', '收', '首', '根', '讲', '整', '式', '取', '照', '办', '强', '石', '古', '华', '諣', '拿',
        '计', '您', '装', '似', '足', '双', '妻', '尼', '转', '诉',
        '米', '称', '丽', '客', '南', '领', '节', '衣', '站', '黑', '刻', '统', '断', '福', '城', '故', '历', '惊', '脸', '选', '包', '紧',
        '争', '另', '建', '维', '绝', '树', '系', '伤', '示', '愿',
        '持', '千', '史', '谁', '准', '联', '妇', '纪', '基', '买', '志', '静', '阿', '诗', '独', '复', '痛', '消', '社', '算', '算', '义',
        '竟', '确', '酒', '需', '单', '治', '卡', '幸', '兰', '念',
        '举', '仅', '钟', '怕', '共', '毛', '句', '息', '功', '官', '待', '究', '跟', '穿', '室', '易', '游', '程', '号', '居', '考', '突',
        '皮', '哪', '费', '倒', '价', '图', '具', '刚', '脑', '永',
        '歌', '响', '商', '礼', '细', '专', '黄', '块', '脚', '味', '灵', '改', '据', '般', '破', '引', '食', '仍', '存', '众', '注', '笔',
        '甚', '某', '沉', '血', '备', '习', '校', '默', '务', '土',
        '微', '娘', '须', '试', '怀', '料', '调', '广', '蜖', '苏', '显', '赛', '查', '密', '议', '底', '列', '富', '梦', '错', '座', '参',
        '八', '除', '跑', '亮', '假', '印', '设', '线', '温', '虽',
        '掉', '京', '初', '养', '香', '停', '际', '致', '阳', '纸', '李', '纳', '验', '助', '激', '够', '严', '证', '帝', '饭', '忘', '趣',
        '支', '春', '集', '丈', '木', '研', '班', '普', '导', '顿',
        '睡', '展', '跳', '获', '艺', '六', '波', '察', '群', '皇', '段', '急', '庭', '创', '区', '奥', '器', '谢', '弟', '店', '否', '害',
        '草', '排', '背', '止', '组', '州', '朝', '封', '睛', '板',
        '角', '况', '曲', '馆', '育', '忙', '质', '河', '续', '哥', '呼', '若', '推', '境', '遇', '雨', '标', '姐', '充', '围', '案', '伦',
        '护', '冷', '警', '贝', '著', '雪', '索', '剧', '啊', '船',
        '险', '烟', '依', '斗', '值', '帮', '汉', '慢', '佛', '肯', '闻', '唱', '沙', '局', '伯', '族', '低', '玩', '资', '屋', '击', '速',
        '顾', '泪', '洲', '团', '圣', '旁', '堂', '兵', '七', '露',
        '园', '牛', '哭', '旅', '街', '劳', '型', '烈', '姑', '陈', '莫', '鱼', '异', '抱', '宝', '权', '鲁', '简', '态', '级', '票', '怪',
        '寻', '杀', '律', '胜', '份', '汽', '右', '洋', '范', '床',
        '舞', '秘', '午', '登', '楼', '贵', '吸', '责', '例', '追', '较', '职', '属', '渐', '左', '录', '丝', '牙', '党', '继', '托', '赶',
        '章', '智', '冲', '叶', '胡', '吉', '卖', '坚', '喝', '肉',
        '遗', '救', '修', '松', '临', '藏', '担', '戏', '善', '卫', '药', '悲', '敢', '靠', '伊', '村', '戴', '词', '森', '耳', '差', '短',
        '祖', '云', '规', '窗', '散', '迷', '油', '旧', '适', '乡',
        '架', '恩', '投', '弹', '铁', '博', '雷', '府', '压', '超', '负', '勒', '杂', '醒', '洗', '采', '毫', '嘴', '毕', '九', '冰', '既',
        '状', '乱', '景', '席', '珍', '童', '顶', '派', '素', '脱',
        '农', '疑', '练', '野', '按', '犯', '拍', '征', '坏', '骨', '余', '承', '置', '臓', '彩', '灯', '巨', '琴', '免', '环', '姆', '暗',
        '换', '技', '翻', '束', '增', '忍', '餐', '洛', '塞', '缺',
        '忆', '判', '欧', '层', '付', '阵', '玛', '批', '岛', '项', '狗', '休', '懂', '武', '革', '良', '恶', '恋', '委', '拥', '娜', '妙',
        '探', '呀', '营', '退', '摇', '弄', '桌', '熟', '诺', '宣',
        '银', '势', '奖', '宫', '忽', '套', '康', '供', '优', '课', '鸟', '喊', '降', '夏', '困', '刘', '罪', '亡', '鞋', '健', '模', '败',
        '伴', '守', '挥', '鲜', '财', '孤', '枪', '禁', '恐', '伙',
        '杰', '迹', '妹', '藸', '遍', '盖', '副', '坦', '牌', '江', '顺', '秋', '萨', '菜', '划', '授', '归', '浪', '听', '凡', '预', '奶',
        '雄', '升', '碃', '编', '典', '袋', '莱', '含', '盛', '济',
        '蒙', '棋', '端', '腿', '招', '释', '介', '烧', '误'
    ]

    print('-----------------------start:' + str(strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '-----------------------')
    for first_name in first_name_list:
        for last_name in first_name_list2:
            print('-------------------'+first_name+''+last_name+"-姓氏：开始爬取-------------------")
            title = '失信被执行人名单'
            url_list = ['https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php' \
                        '?resource_id=6899'
                        '&query=' + title + ''
                        '&cardNum='
                        '&iname=' + first_name+''+last_name+ ''
                        '&areaName='
                        '&ie=utf-8'
                        '&oe=utf-8'
                        '&format=json'
                        '&t=1504228484424'
                        '&cb=jQuery110203450799221787775_1504227514772'
                        '&_=1504227514784'
                        ]
            # 爬取姓氏的前50页
            for page_num in range(0, 15):
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
