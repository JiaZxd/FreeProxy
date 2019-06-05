# coding=utf-8

from __future__ import unicode_literals
import re
from freeproxy.models.log import logging
from datetime import datetime

import requests
from lxml import etree
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from a import HOST,MONGO_HOST,MONGO_PORT,DB


client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db_crawler = client[DB]
# db_crawler.authenticate('kxd', '1234abcd!')


class Proxy(object):
    """
    创建类,ip池,保存代理ip的信息,期刊从中获取代理ip
    """
    def __init__(self):
        self.ip = ''  # ip地址
        self.port = ''  # 端口
        self.add_time = ''  # 添加时间
        self.update_time = ''  # 更新时间(每次更新,会得到新的延时)
        # self.source = ''  # 获取网站
        self.status = 1  # 代理状态, 1可用, -1不可用, 0延时高
        self.delay = 10.0  # 延时
        self.anonymous = ''  # 匿名度
        self.type = ''  # ip请求类型

    # 保存到数据库
    def insert(self, **kwargs):
        self.add_time = datetime.now()
        self.update_time = datetime.now()
        if kwargs:
            self.ip = kwargs.get(b'ip', '')
            self.port = kwargs.get(b'port', '')
            # self.source = kwargs.get(b'source', '')
            self.delay = kwargs.get(b'delay', 10)
            self.anonymous = kwargs.get(b'anonymous', '')
            self.type = kwargs.get(b'type', '')
        required_fields = [b'ip', b'port']
        for key in required_fields:
            if not self.__dict__[key]:
                raise KeyError('%s Error:must value' % key)
        try:
            _id = db_crawler.proxy.insert(self.__dict__)
        except DuplicateKeyError as e:
            # 更新代理ip更新时间
            cur = db_crawler.proxy.find_one({'ip': self.ip, 'port': self.port})
            delay = (cur['delay'] + self.delay)/2
            _id = self.update(cur['_id'], update_time=datetime.now(), delay=delay, status=1, anonymous=self.anonymous
                              ,type=self.type)
        return _id

    def update(self, _id, **kwargs):
        result = db_crawler.proxy.update({'_id': _id}, {'$set': kwargs})
        return result

    def delete(self):
        pass

    @classmethod
    def select(cls, query, dtype='cursor'):
        cur = db_crawler.proxy.find(query)
        return cur

    # 修改代理ip状态
    def update_proxy_status(self, ip, port, status):
        result = ''
        if not ip or not port:
            raise KeyError('Value not " "')
        cur = db_crawler.proxy.find_one({'ip': ip, 'port': port})
        now = datetime.now()
        if cur:
            cha = (now - cur['add_time']).days
        # if :
        #     db_crawler.proxy.remove({'_id': cur['_id']})
        if cur and status == -1 and cha > 3:  # 判断ip的添加时间，超过3天的删除
            db_crawler.proxy.remove({'_id': cur['_id']})
        elif cur:
            result = self.update(cur['_id'], status=status, update_time=datetime.now())
        return result


class ProxySpider(object):
    """
    代理网站爬虫,打开代理网站,提取需要的ip,验证ip的延时,插入到数据库
    """

    PROXY = None

    def __init__(self):
        self.proxy = Proxy()
        self.source = ''  # 来源,网站链接

    # 打开url
    def open(self, url, proxy=None):
        """
        get打开网站
        :param url:
        :param proxy: 代理ip
        :return:
        """
        # url = 'http://cn-proxy.com/'
        res = ''
        headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        }
        # try:
        if proxy:

            if not isinstance(proxy, dict):
                raise Exception
            res = requests.get(url=url, headers=headers, proxies=proxy, timeout=3)
        else:
            res = requests.get(url=url, headers=headers)
        # except Exception as e:
        #     self.logger.exception('Connect failed')
        return res

    # 从网页提取ip
    def extract_fields(self, res):
        raise Exception

    # 检查ip地址
    def validate_ip(self, proxy):
        """
        检查ip是否可用，是否能打开cnki网页（ip主要用于爬取文献）
        :param proxies:ip数组, [{ip:'', port:'', }]
        :return:
        """
        if not isinstance(proxy, dict):
            raise Exception
        # for p in proxies:
        ip = proxy['ip']
        port = proxy['port']
        _type = proxy.get('type', '')
        proxies = {
            _type:"{type}://{ip}:{port}".format(type=_type, ip=ip, port=port),
        }
        self.proxy = Proxy()
        try:
            # 打开cnki延时
            res = self.open('http://www.cnki.net/', proxy=proxies)
            # 打开google延时
        except Exception as e:
            # raise
            self.logger.info('%s:%s failed' % (ip, port))
            self.proxy.update_proxy_status(ip, port, -1)
        else:
            # 保存
            string = '中国知网'
            try:
                if res.status_code == 200 and (res.elapsed.total_seconds() < 1.3) and string in res.content.decode(
                        'utf-8'):
                    # 匿名度
                    try:
                        anonymous = self.check_anonymous(ip, port)
                    except:
                        anonymous = '透明'
                    delay = res.elapsed.total_seconds()  # 响应时间
                    self.logger.info('%s:%s delay:%s' % (ip, port, delay))
                    _id = self.proxy.insert(ip=ip, port=port, delay=delay, anonymous=anonymous, type=type)
                else:
                    self.logger.info('%s:%s failed' % (ip, port))
                    self.proxy.update_proxy_status(ip, port, -1)
            except:
                self.proxy.update_proxy_status(ip, port, -1)



    # 检查ip匿名度
    def check_anonymous(self, ip, port):
        proxy = '{ip}:{port}'.format(ip=ip, port=port)
        proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        }
        res = self.open('http://www.xxorg.com/tools/checkproxy/', proxies)
        selector = etree.HTML(text=res.text)

        string = res.text
        # 匿名度判断
        if HOST in string:
            value = '透明'
        elif 'unknown' in string or '没有使用代理或者使用高匿名代理' in string:
            value = '高匿'
        elif ip in string or '普通匿名代理服务器' in string:
            value = '匿名'
        else:
            raise Exception('cant define ip anonymous {0}'.format(proxy))
        return value


    def save(self):
        raise Exception

    @property
    def logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        return logging.LoggerAdapter(logger, {'spider': self.__class__.__name__})


class CNProxy(ProxySpider):
    """
    http://cn-proxy.com/网站, 需要翻墙才能访问, 本地用了shadowsocks
    """
    PROXY = {
        "http": "socks5://127.0.0.1:1080",
        'https': 'socks5://127.0.0.1:1080'
    }

    def __init__(self):
        super(CNProxy, self).__init__()
        self.source = 'http://cn-proxy.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//div[1]/div[2]/div[1]/div[2]/div/div/div[4]/table/tbody/tr')
        result = []
        for x in trs:
            ip = ''.join(x.xpath('.//td[1]/text()'))
            port = ''.join(x.xpath('.//td[2]/text()'))
            # print "http://%s:%s" % (ip, port)
            result.append(dict(ip=ip, port=str(port)))
            # 验证访问cnki
        return result


class GouBanJia(ProxySpider):
    """
    代理网站地址:http://www.goubanjia.com/
    """
    def __init__(self):
        super(GouBanJia, self).__init__()
        self.source = 'http://www.goubanjia.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//table[@class="table table-hover"]/tbody/tr')
        result = []
        for x in trs:
            string = ''.join(x.xpath('.//*[not(self::p)]/text()'))
            if '透明' in string:
                continue
            _list = re.split('透明|高匿|匿名', string)
            _type = 'http'
            if 'https' in string:
                _type = 'https'
            ip = _list[0].split(':')[0]
            # 解码端口号,得到真正的端口
            _port = _list[0].split(':')[1]
            _class = ''.join(x.xpath('.//td[1]/span[last()]/@class')).split(' ')[-1]
            port = self.decode_port(_port, _class)
            # print "http://%s:%s" % (ip, port)
            
            result.append(dict(ip=ip, port=str(port), type=_type))

        return result

    def decode_port(self, _port, _class):
        """
        端口的class中包含端口的信息,解码
        :param _port:
        :param _class:
        :return:
        """
        temp = 'ABCDEFGHIZ'
        _list = []
        for x in _class:
            s = temp.index(x)
            _list.append(str(s))
        result = int(''.join(_list))/8
        return result

