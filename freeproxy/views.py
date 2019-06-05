# coding=utf-8
"""
执行ip爬虫方法：
    1.crawl_website:获取新ip
    2.repick_ip：失败ip中重新检索
    3.validate_ip：检测成功ip
"""

from __future__ import unicode_literals
import sys, os

root_dir = os.path.abspath(__file__).split('freeproxy')[0]
sys.path.append(root_dir)
# sys.path.append('/home/kxd/code-project/spider-publicnet/publicnet')
# from models import CNProxy, GouBanJia, ProxySpider, WuYou, Xici,FreeSite
from freeproxy.models import create_spider, Proxy, ProxySpider
from freeproxy.settings import PROXY_WEB


def crawl_website(web=''):
    """
    从网站爬取新的ip
    :return:
    """
    for x in PROXY_WEB:
        spider = create_spider(x)
        try:
            # 打开代理ip网站
            res = spider.open(spider.source, proxy=spider.PROXY)
            # 获取ip列表
            try:
                ips = spider.extract_fields(res)
            except Exception as e:
                spider.logger.error('爬虫网站：%s，提取ip错误' % x)
                continue
            # 过滤不可用的ip
            a = spider.save_ip(ips)
        except Exception as e:
            print('Error website:%s' % x)
            raise e


def repick_ip():
    """
    从数据库失败ip中挑选成功ip
    :return:
    """
    cursor = Proxy.select({'status': -1})
    ps = ProxySpider()
    ps.save_ip(list(cursor))
    pass


def validate_ip():
    """
    验证数据库中的成功ip
    :return:
    """
    cursor = Proxy.select({'status': 1})
    ps = ProxySpider()
    ps.save_ip(list(cursor))
    pass


if __name__ == '__main__':

    while True:
        validate_ip()
        repick_ip()
        crawl_website()

        # time.sleep(50)
    # crawl_ip(GouBanJia)
    # crawl_ip(CNProxy)
    # crawl_ip(WuYou)
    # crawl_ip(Xici)
