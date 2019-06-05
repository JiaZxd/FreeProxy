# coding=utf-8
"""
proxy爬虫类，从代理网站爬取ip。
目前有三个网站：
    CNProxy：http://cn-proxy.com/
    GouBanJia：http://www.goubanjia.com/
    WuYou：http://www.data5u.com/
    Xici: http://www.xicidaili.com/nn
    QiYun http://www.qydaili.com/free/?page=1
"""
from __future__ import unicode_literals
import re

import base64
from .log import logging

import execjs
import requests
from requests.exceptions import ReadTimeout, ProxyError, ConnectTimeout
from lxml import etree

from .ip import Proxy as IP
from .utils import open_url


class ProxySpider(object):
    """
    ip网站爬虫基类,定义了公共的方法，子类重写部分
        打开代理网站,提取需要的ip,验证ip的延时,插入到数据库
        子类：解析文本
    """

    PROXY = None

    def __init__(self):
        self.ip = IP()
        self.source = ''  # 来源,网站链接
        # self._get_host()

    # 打开url
    def open(self, url, proxy=None, timeout=5):
        """
        get打开网站
        :param url:
        :param proxy: 代理ip
        :return:
        """
        res = open_url(url, proxy=proxy, timeout=timeout)
        return res

    # 从网页提取ip
    def extract_fields(self, res):
        raise Exception

    def save_ip(self, ips):
        """
        过滤ip，选出能够使用的ip
        :param ips:
        :return:
        """
        if isinstance(ips, list):
            ips = list(map(self.ip.validate_ip, ips))
        elif isinstance(ips, dict):
            ips = self.ip.validate_ip(ips)
        # print(ips)
        return ips

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
    # PROXY = {
    #     "http": "socks5://127.0.0.1:1080",
    #     'https': 'socks5://127.0.0.1:1080'
    # }
    name = 'cn_proxy'

    def __init__(self):
        super(CNProxy, self).__init__()
        self.source = 'https://cn-proxy.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//table[@class="sortable"]//tbody//tr')
        result = []
        for x in trs:
            ip = ''.join(x.xpath('.//td[1]/text()'))
            port = ''.join(x.xpath('.//td[2]/text()'))
            result.append(dict(ip=ip, port=str(port), name=self.name))
        return result


class GouBanJia(ProxySpider):
    """
    代理网站地址:http://www.goubanjia.com/
    """
    name = 'goubanjia'

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

            result.append(dict(ip=ip, port=str(port), name=self.name))

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
        result = int(''.join(_list)) / 8
        return result


class WuYou(ProxySpider):
    """
    代理网站地址:http://www.data5u.com/
    """
    name = 'wuyou'

    def __init__(self):
        super(WuYou, self).__init__()
        self.source = 'http://www.data5u.com'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//ul[@class="l2"]')
        result = []
        for x in trs:
            params = x.xpath('.//*[self::li]/text()')
            string = ''.join(params)
            if '透明' in string:
                continue
            _list = re.split('透明|高匿|匿名', string)
            _type = 'http'
            if 'https' in string:
                _type = 'https'
            ip = params[0]
            # 解码端口号,得到真正的端口
            _port = params[1]
            _class = ''.join(x.xpath('.//span[2]/li/@class')).split(' ')[-1]
            port = self.decode_port(_port, _class)
            # print "http://%s:%s" % (ip, port)

            result.append(dict(ip=ip, port=str(port), name=self.name))

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
        result = int(''.join(_list)) / 8
        return result


class Xici(ProxySpider):
    """
    西刺代理 http://www.xicidaili.com/nn
    """
    name = 'xici'

    def __init__(self):
        super(Xici, self).__init__()
        self.source = 'http://www.xicidaili.com/nn'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//table[@id="ip_list"]/tr')
        result = []
        for x in trs:
            # params = x.xpath('.//*[self::li]/text()')
            # string = ''.join(params)
            # if '透明' in string:
            #     continue
            # _list = re.split('透明|高匿|匿名', string)
            # _type = 'http'
            # if 'https' in string:
            #     _type = 'https'
            ip = ''.join(x.xpath('.//td[2]/text()'))
            # 解码端口号,得到真正的端口
            port = ''.join(x.xpath('.//td[3]/text()'))
            if ip and port:
                result.append(dict(ip=ip, port=str(port), name=self.name))
            # _class = ''.join(x.xpath('.//span[2]/li/@class')).split(' ')[-1]
            # port = self.decode_port(_port, _class)
            # print "http://%s:%s" % (ip, port)

        return result


class QiYun(ProxySpider):
    """
    旗云代理 http://www.qydaili.com/free/?page=1
    """
    name = 'qiyun'

    def __init__(self):
        super(QiYun, self).__init__()
        self.source = 'http://www.qydaili.com/free/?page=1'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//div[@class="container"]/table/tbody/tr')
        result = []
        for x in trs:

            ip = ''.join(x.xpath('.//td[1]/text()'))
            # 解码端口号,得到真正的端口
            port = ''.join(x.xpath('.//td[2]/text()'))
            if ip and port:
                result.append(dict(ip=ip, port=str(port), name=self.name))
        return result


class ProxyDB(ProxySpider):
    """
    ProxyDB http://proxydb.net/?protocol=http&protocol=https&country=CN
    """
    name = 'proxydb'

    def __init__(self):
        super(ProxyDB, self).__init__()
        self.source = 'http://proxydb.net/?protocol=http&anonlvl=2&' \
                      'anonlvl=3&anonlvl=4&min_uptime=75&max_response_time=5&exclude_gateway=1&country=CN'

    def extract_fields(self, res):
        selector = etree.HTML(text=res.text)
        # r = requests.get(url='http://www.baidu.com/')
        trs = selector.xpath('//div[@class="table-responsive"]/table/tbody/tr')
        result = []
        attrib = selector.xpath('//div[@class="container-fluid"]/div[1]')[0].attrib
        key = filter(lambda x: 'data' in x, attrib)[0]
        compute_port = int(attrib[key])

        for x in trs:
            js_str = ''.join(x.xpath('.//td[1]//script/text()'))
            # 得到ip
            ip_1 = execjs.eval(js_str.split(';')[0].split('=')[1])
            string = js_str.split(';')[1].split('=')[1]
            base64_code = re.search('(?<=atob\().*?\.', string).group().strip('.')
            ip_2 = base64.b64decode(eval(base64_code))
            ip = ip_1 + ip_2

            # 解码端口号,得到真正的端口
            port_str = js_str.split(';')[2].split('=')[1]
            string = re.search('\([0-9]{2,4}', port_str).group().strip('(')
            port = int(string) + compute_port
            if ip and port:
                result.append(dict(ip=ip, port=str(port), name=self.name))
        return result


# 废弃
class FreeSite(ProxySpider):
    """
    免费ip https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt
    大部分不能用
    """

    def __init__(self):
        super(FreeSite, self).__init__()
        self.source = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt'

    def extract_fields(self, res):
        text = res.text
        ip_port_str_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', text.decode('utf-8'))
        result = []
        for ip_port in ip_port_str_list:

            ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_port).group(0)
            port = re.search(r':(\d{2,5})', ip_port).group(1)

            if ip and port:
                result.append(dict(ip=ip, port=str(port), type=''))

        # for x in trs:
        #     # params = x.xpath('.//*[self::li]/text()')
        #     # string = ''.join(params)
        #     # if '透明' in string:
        #     #     continue
        #     # _list = re.split('透明|高匿|匿名', string)
        #     # _type = 'http'
        #     # if 'https' in string:
        #     #     _type = 'https'
        #     ip = ''.join(x.xpath('.//td[2]/text()'))
        #     # 解码端口号,得到真正的端口
        #     port = ''.join(x.xpath('.//td[3]/text()'))
        #     if ip and port:
        #         result.append(dict(ip=ip, port=str(port), type=''))
        #     # _class = ''.join(x.xpath('.//span[2]/li/@class')).split(' ')[-1]
        #     # port = self.decode_port(_port, _class)
        #     # print "http://%s:%s" % (ip, port)

        return result


def create_spider(name):
    try:
        mappings = {'goubanjia': GouBanJia, 'cn_proxy': CNProxy, 'data5u': WuYou, 'xici': Xici, 'qiyun': QiYun,
                    'proxydb': ProxyDB}
        obj = mappings[name]()
    except KeyError as e:
        raise KeyError('Dont exist spider%s' % name)
    except Exception as e:
        raise
    return obj
