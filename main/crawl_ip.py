# coding=utf-8
"""
爬取新的代理ip, 目前从两个代理网站获取ip

"""

from __future__ import unicode_literals

from model import CNProxy, GouBanJia, ProxySpider


def crawl_ip(model):
    obj = model()
    if isinstance(obj, ProxySpider):
        # obj.logger.info('123')
        res = obj.open(obj.url, proxy=obj.PROXY)
        ips = obj.extract_fields(res)
        obj.validate_ip(ips)


if __name__ == '__main__':
    crawl_ip(GouBanJia)
    crawl_ip(CNProxy)






