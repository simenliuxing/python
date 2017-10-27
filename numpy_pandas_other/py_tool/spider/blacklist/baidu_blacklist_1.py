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
    # first_name_list = ['李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
    #                    '徐', '孙', '朱', '马', '胡', '郭', '林', '何', '高', '梁',
    #                    '郑', '罗', '宋', '谢', '唐', '韩', '曹', '许', '邓', '萧',
    #                    '冯', '曾', '程', '蔡', '彭', '潘', '袁', '於', '董', '余',
    #                    '苏', '叶', '吕', '魏', '蒋', '田', '杜', '丁', '沈', '姜',
    #                    '范', '江', '傅', '钟', '卢', '汪', '戴', '崔', '任', '陆',
    #                    '廖', '姚', '方', '金', '邱', '夏', '谭', '韦', '贾', '邹',
    #                    '石', '熊', '孟', '秦', '阎', '薛', '侯', '雷', '白', '龙',
    #                    '段', '郝', '孔', '邵', '史', '毛', '常', '万', '顾', '赖',
    #                    '钱', '施', '牛', '洪', '龚', '文', '庞', '樊', '兰', '殷',
    #                    '颜', '倪', '严', '牛', '温', '芦', '季', '俞', '章', '鲁',
    #                    '葛', '伍', '韦', '申', '尤', '毕', '聂', '丛', '焦', '向',
    #                    '柳', '邢', '路', '岳', '齐', '沿', '梅', '莫', '庄', '辛',
    #                    '管', '祝', '左', '涂', '谷', '祁', '时', '舒', '耿', '牟',
    #                    '卜', '路', '詹', '关', '苗', '凌', '费', '纪', '靳', '盛',
    #                    '童', '欧', '甄', '项', '曲', '成', '游', '阳', '裴', '席',
    #                    '卫', '查', '屈', '鲍', '位', '覃', '霍', '翁', '隋', '植',
    #                    '甘', '景', '薄', '单', '包', '司', '柏', '宁', '柯', '阮',
    #                    '施', '陶', '洪', '翟', '安', '武', '康', '贺', '严', '尹',
    #                    '桂', '闵', '欧阳', '解', '强', '柴', '华', '车', '冉', '房'
    #                    ]
    first_name_list = [
        '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫',
        '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许', '何', '吕', '施', '张',
        '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻',
        '柏', '水', '窦', '章', '云', '苏', '潘', '葛', '奚', '范', '彭', '郎',
        '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
        '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤',
        '滕', '殷', '罗', '毕', '郝', '邬', '安', '常', '乐', '于', '时', '傅',
        '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄',
        '和', '穆', '萧', '尹', '姚', '邵', '湛', '汪', '祁', '毛', '禹', '狄',
        '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
        '熊', '纪', '舒', '屈', '项', '祝', '董', '梁', '杜', '阮', '蓝', '闵',
        '席', '季', '麻', '强', '贾', '路', '娄', '危', '江', '童', '颜', '郭',
        '梅', '盛', '林', '刁', '锺', '徐', '邱', '骆', '高', '夏', '蔡', '田',
        '樊', '胡', '凌', '霍', '虞', '万', '支', '柯', '昝', '管', '卢', '莫',
        '经', '房', '裘', '缪', '干', '解', '应', '宗', '丁', '宣', '贲', '邓',
        '郁', '单', '杭', '洪', '包', '诸', '左', '石', '崔', '吉', '钮', '龚',
        '程', '嵇', '邢', '滑', '裴', '陆', '荣', '翁', '荀', '羊', '於', '惠',
        '甄', '麴', '家', '封', '芮', '羿', '储', '靳', '汲', '邴', '糜', '松',
        '井', '段', '富', '巫', '乌', '焦', '巴', '弓', '牧', '隗', '山', '谷',
        '车', '侯', '宓', '蓬', '全', '郗', '班', '仰', '秋', '仲', '伊', '宫',
        '宁', '仇', '栾', '暴', '甘', '钭', '历', '戎', '祖', '武', '符', '刘',
        '景', '詹', '束', '龙', '叶', '幸', '司', '韶', '郜', '黎', '蓟', '溥',
        '印', '宿', '白', '怀', '蒲', '邰', '从', '鄂', '索', '咸', '籍', '赖',
        '卓', '蔺', '屠', '蒙', '池', '乔', '阳', '郁', '胥', '能', '苍', '双',
        '闻', '莘', '党', '翟', '谭', '贡', '劳', '逄', '姬', '申', '扶', '堵',
        '冉', '宰', '郦', '雍', '却', '璩', '桑', '桂', '濮', '牛', '寿', '通',
        '边', '扈', '燕', '冀', '僪', '浦', '尚', '农', '温', '别', '庄', '晏',
        '柴', '瞿', '阎', '充', '慕', '连', '茹', '习', '宦', '艾', '鱼', '容',
        '向', '古', '易', '慎', '戈', '廖', '庾', '终', '暨', '居', '衡', '步',
        '都', '耿', '满', '弘', '匡', '国', '文', '寇', '广', '禄', '阙', '东',
        '欧', '殳', '沃', '利', '蔚', '越', '夔', '隆', '师', '巩', '厍', '聂',
        '晁', '勾', '敖', '融', '冷', '訾', '辛', '阚', '那', '简', '饶', '空',
        '曾', '毋', '沙', '乜', '养', '鞠', '须', '丰', '巢', '关', '蒯', '相',
        '查', '后', '荆', '红', '游', '竺', '权', '逮', '盍', '益', '桓', '公',
        '寸', '贰', '皇', '侨', '彤', '竭', '端', '赫', '实', '甫', '集', '象',
        '翠', '狂', '辟', '典', '良', '函', '芒', '苦', '其', '京', '中', '夕',
        '税', '荤', '靖', '绪', '愈', '硕', '牢', '买', '但', '巧', '枚', '撒',
        '泰', '秘', '亥', '绍', '以', '壬', '森', '斋', '释', '奕', '姒', '朋',
        '求', '羽', '用', '占', '真', '穰', '翦', '闾', '漆', '贵', '代', '贯',
        '旁', '崇', '栋', '告', '休', '褒', '谏', '锐', '皋', '闳', '在', '歧',
        '禾', '示', '是', '委', '钊', '频', '嬴', '呼', '大', '威', '昂', '律',
        '冒', '保', '系', '抄', '定', '化', '莱', '校', '么', '抗', '祢', '綦',
        '悟', '宏', '功', '庚', '务', '敏', '捷', '拱', '兆', '丑', '丙', '畅',
        '苟', '随', '类', '卯', '俟', '友', '答', '乙', '允', '甲', '留', '尾',
        '佼', '玄', '乘', '裔', '延', '植', '环', '矫', '赛', '昔', '侍', '度',
        '旷', '遇', '偶', '前', '由', '咎', '塞', '敛', '受', '泷', '袭', '衅',
        '叔', '圣', '御', '夫', '仆', '镇', '藩', '邸', '府', '掌', '首', '员',
        '焉', '戏', '可', '智', '尔', '凭', '悉', '进', '笃', '厚', '仁', '业',
        '肇', '资', '合', '仍', '九', '衷', '哀', '刑', '俎', '仵', '圭', '夷',
        '徭', '蛮', '汗', '孛', '乾', '帖', '罕', '洛', '淦', '洋', '邶', '郸',
        '郯', '邗', '邛', '剑', '虢', '隋', '蒿', '茆', '菅', '苌', '树', '桐',
        '锁', '钟', '机', '盘', '铎', '斛', '玉', '线', '针', '箕', '庹', '绳',
        '磨', '蒉', '瓮', '弭', '刀', '疏', '牵', '浑', '恽', '势', '世', '仝',
        '同', '蚁', '止', '戢', '睢', '冼', '种', '涂', '肖', '己', '泣', '潜',
        '卷', '脱', '谬', '蹉', '赧', '浮', '顿', '说', '次', '错', '念', '夙',
        '斯', '完', '丹', '表', '聊', '源', '姓', '吾', '寻', '展', '出', '不',
        '户', '闭', '才', '无', '书', '学', '愚', '本', '性', '雪', '霜', '烟',
        '寒', '少', '字', '桥', '板', '斐', '独', '千', '诗', '嘉', '扬', '善',
        '揭', '祈', '析', '赤', '紫', '青', '柔', '刚', '奇', '拜', '佛', '陀',
        '弥', '阿', '素', '长', '僧', '隐', '仙', '隽', '宇', '祭', '酒', '淡',
        '塔', '琦', '闪', '始', '星', '南', '天', '接', '波', '碧', '速', '禚',
        '腾', '潮', '镜', '似', '澄', '潭', '謇', '纵', '渠', '奈', '风', '春',
        '濯', '沐', '茂', '英', '兰', '檀', '藤', '枝', '检', '生', '折', '登',
        '驹', '骑', '貊', '虎', '肥', '鹿', '雀', '野', '禽', '飞', '节', '宜',
        '鲜', '粟', '栗', '豆', '帛', '官', '布', '衣', '藏', '宝', '钞', '银',
        '门', '盈', '庆', '喜', '及', '普', '建', '营', '巨', '望', '希', '道',
        '载', '声', '漫', '犁', '力', '贸', '勤', '革', '改', '兴', '亓', '睦',
        '修', '信', '闽', '北', '守', '坚', '勇', '汉', '练', '尉', '士', '旅',
        '五', '令', '将', '旗', '军', '行', '奉', '敬', '恭', '仪', '母', '堂',
        '丘', '义', '礼', '慈', '孝', '理', '伦', '卿', '问', '永', '辉', '位',
        '让', '尧', '依', '犹', '介', '承', '市', '所', '苑', '杞', '剧', '第',
        '零', '谌', '招', '续', '达', '忻', '六', '鄞', '战', '迟', '候', '宛',
        '励', '粘', '萨', '邝', '覃', '辜', '初', '楼', '城', '区', '局', '台',
        '原', '考', '妫', '纳', '泉', '老', '清', '德', '卑', '过', '麦', '曲',
        '竹', '百', '福', '言', '第五', '佟', '爱', '年', '笪', '谯', '哈', '墨',
        '富察', '费莫', '蹇', '称', '诺', '来', '多', '繁', '戊', '朴', '回', '毓',
        '鲜于', '锺离', '盖', '逯', '库', '郏', '逢', '阴', '薄', '厉', '稽', '闾丘',
        '南宫', '赏', '伯', '佴', '佘', '牟', '商', '西门', '东门', '左丘', '梁丘', '琴',
        '公良', '段干', '开', '光', '操', '瑞', '眭', '泥', '运', '摩', '伟', '铁', '迮',
        '后', '况', '亢', '缑', '帅', '微生', '羊舌', '海', '归', '呼延', '南门', '东郭',
        '百里', '钦', '鄢', '汝', '法', '闫', '楚', '晋', '谷梁', '宰父', '夹谷', '拓跋',
        '钟离', '宇文', '长孙', '慕容', '司徒', '司空', '召', '有', '舜', '叶赫那拉', '丛', '岳',
        '壤驷', '乐正', '漆雕', '公西', '巫马', '端木', '颛孙', '子车', '督', '仉', '司寇', '亓官',
        '澹台', '公冶', '宗政', '濮阳', '淳于', '单于', '太叔', '申屠', '公孙', '仲孙', '轩辕', '令狐',
        '万俟', '司马', '上官', '欧阳', '夏侯', '诸葛', '闻人', '东方', '赫连', '皇甫', '尉迟', '公羊',
        '乌雅', '范姜', '碧鲁', '张廖', '张简', '图门', '太史', '公叔', '乌孙', '完颜', '马佳', '佟佳',
        '之', '章佳', '那拉', '冠', '宾', '香', '果', '依尔根觉罗', '依尔觉罗', '萨嘛喇', '赫舍里', '额尔德特',
        '萨克达', '钮祜禄', '他塔喇', '喜塔腊', '讷殷富察', '叶赫那兰', '库雅喇', '瓜尔佳', '舒穆禄', '爱新觉罗', '索绰络', '纳喇'
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
        for page_num in range(0, 50):
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
