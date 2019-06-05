# coding=utf-8
"""
爬取新的代理ip, 目前从两个代理网站获取ip
"""

from __future__ import unicode_literals
import sys,os
root_dir = os.path.abspath(__file__).split('freeproxy')[0]
sys.path.append(root_dir)
# sys.path.append('/home/kxd/code-project/spider-publicnet/publicnet')
# from models import CNProxy, GouBanJia, ProxySpider, WuYou, Xici,FreeSite
from freeproxy.models import create_spider
from freeproxy.settings import PROXY_WEB


def crawl_ip(_obj):

    # 打开代理ip网站
    res = _obj.open(_obj.source, proxy=_obj.PROXY)
    # 获取ip列表

    ips = _obj.extract_fields(res)
    # 过滤不可用的ip
    a = _obj.save_ip(ips)
    # for x in a:
    #     if x:
    #         print (x)


if __name__ == '__main__':
    # spider = create_spider('cn_proxy')
    # crawl_ip(spider)
    for x in PROXY_WEB:
        spider = create_spider(x)
        try:
            crawl_ip(spider)
        except Exception as e:
            print('Error website:%s' % x)
            raise e
    # crawl_ip(GouBanJia)
    # crawl_ip(CNProxy)
    # crawl_ip(WuYou)




