# coding=utf-8

from __future__ import unicode_literals
import re
from log import logging
from datetime import datetime

import requests
from lxml import etree
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

host = '192.168.102.130'
client = MongoClient(host=host)
db_crawler = client.crawler
db_crawler.authenticate('kxd', '1234abcd!')


class Proxy(object):
    """
    创建类,ip池,保存代理ip的信息,期刊从中获取代理ip
    """
    def __init__(self):
        self.ip = ''  # ip地址
        self.port = ''  # 端口
        self.add_time = ''  # 添加时间
        self.update_time = ''  # 更新时间(每次更新,会得到新的延时)
        self.source = ''  # 获取网站
        self.status = 1  # 代理状态, 1可用, -1不可用, 0延时高
        self.delay = 10.0  # 延时

    # 保存到数据库
    def insert(self, **kwargs):
        self.add_time = datetime.now()
        self.update_time = datetime.now()
        if kwargs:
            self.ip = kwargs.get(b'ip', '')
            self.port = kwargs.get(b'port', '')
            self.source = kwargs.get(b'source', '')
            self.delay = kwargs.get(b'delay', 10)

        for key, value in self.__dict__.items():
            if not value:
                raise KeyError('%s Error:must value' % key)
        try:
            _id = db_crawler.proxy.insert(self.__dict__)
        except DuplicateKeyError as e:
            # 更新代理ip更新时间
            cur = db_crawler.proxy.find_one({'ip': self.ip, 'port': self.port})
            _id = self.update(cur['_id'], update_time=datetime.now(), delay=self.delay, status=1)
        return _id

    def update(self, _id, **kwargs):
        result = db_crawler.proxy.update({'_id': _id}, {'$set': kwargs})
        return result

    def delete(self):
        pass

    def select(self):
        pass

    # 修改代理ip状态
    def update_proxy_status(self, ip, proxy, status):
        result = ''
        if not ip or not proxy:
            raise KeyError('Value not " "')
        cur = db_crawler.proxy.find_one({'ip': ip, 'port': proxy})
        if cur:
            result = self.update(cur['_id'], status=status, update_time=datetime.now())
        return result


class ProxySpider(object):
    """
    代理网站爬虫,打开代理网站,提取需要的ip,验证ip的延时,插入到数据库
    """

    PROXY = None

    def __init__(self):
        self.proxy = Proxy()
        self.url = ''

    # 打开url
    def open(self, url, proxy=None):
        # url = 'http://cn-proxy.com/'
        headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        }
        try:
            if proxy:

                if not isinstance(proxy, dict):
                    raise Exception
                res = requests.get(url=url, headers=headers, proxies=proxy, timeout=10)
            else:
                res = requests.get(url=url, headers=headers)

        except Exception as e:
            self.logger.exception('Connect failed')
        return res

    # 从网页提取ip
    def extract_fields(self, res):
        raise Exception

    # 检查ip地址
    def validate_ip(self, proxies):
        if not isinstance(proxies, list):
            raise Exception
        for p in proxies:
            ip = p['ip']
            port = p['port']
            proxies = {
                "http": "http://%s:%s" % (ip, port),
                "https": "http://%s:%s" % (ip, port),
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
                if res.status_code == 200 and (res.elapsed.microseconds / 1000000.0 < 3):
                    # 响应时间
                    delay = res.elapsed.microseconds / 1000000.0
                    self.logger.info('%s:%s delay:%s' % (ip, port, delay))
                    _id = self.proxy.insert(ip=ip, port=port, source=self.url, delay=delay)
                # elif res.elapsed.microseconds / 1000000.0 > 3:  # 延时高
                #     self.proxy.update_proxy_status(ip, port, 0)
                # elif res.status_code == 200:
                #     self.proxy.update_proxy_status(ip, port, 1)
                else:
                    self.logger.info('%s:%s failed' % (ip, port))
                    self.proxy.update_proxy_status(ip, port, -1)
        pass

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
        self.url = 'http://cn-proxy.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//div[1]/div[2]/div[1]/div[2]/div/div/div[4]/table/tbody/tr')
        result = []
        for x in trs:
            ip = ''.join(x.xpath('.//td[1]/text()'))
            port = ''.join(x.xpath('.//td[2]/text()'))
            # print "http://%s:%s" % (ip, port)
            result.append(dict(ip=ip, port=port))
            # 验证访问cnki
        return result


class GouBanJia(ProxySpider):
    """
    代理网站地址:http://www.goubanjia.com/
    """
    def __init__(self):
        super(GouBanJia, self).__init__()
        self.url = 'http://www.goubanjia.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//table[@class="table table-hover"]/tbody/tr')
        result = []
        for x in trs:
            string = ''.join(x.xpath('.//*[not(self::p)]/text()'))
            _list = re.split('透明|高匿|匿名', string)

            ip = _list[0].split(':')[0]
            # 解码端口号,得到真正的端口
            _port = _list[0].split(':')[1]
            _class = ''.join(x.xpath('.//td[1]/span[last()]/@class')).split(' ')[-1]
            port = self.decode_port(_port, _class)
            # print "http://%s:%s" % (ip, port)
            result.append(dict(ip=ip, port=port))

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

