# coding=utf-8
"""
验证保存的ip,更新ip的延时
"""
from __future__ import unicode_literals

from crawl_ip import create_spider, crawl_ip


def anonymous_test():
    ps = ProxySpider()
    ps.check_anonymous('123.58.10.6', 8080)
    pass


def wuyou_test():
    """
    测试无忧ip，爬取
    :return: 
    """
    crawl_ip(WuYou)


def xici_test():
    obj = create_spider('xici')
    crawl_ip(obj)


def qiyun_test():
    obj = create_spider('qiyun')
    crawl_ip(obj)


def proxydb_test():
    obj = create_spider('proxydb')
    crawl_ip(obj)


if __name__ == '__main__':
    proxydb_test()
