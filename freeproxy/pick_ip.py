# coding=utf-8
"""
从失败(status=-1)的ip中挑选出能用的ip
"""
from __future__ import unicode_literals
import sys
from threading import Thread

sys.path.append('/home/kxd/code-project/spider-publicnet/')
from freeproxy.models import Proxy, ProxySpider


class PickThread(Thread):
    """
    挑选ip的线程类
    """
    
if __name__ == '__main__':
    cursor = Proxy.select({'status': -1})
    ps = ProxySpider()
    ps.save_ip(list(cursor))
    pass