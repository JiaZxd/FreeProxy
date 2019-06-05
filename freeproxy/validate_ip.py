# coding=utf-8
"""
验证保存的ip,更新ip的延时
"""
from __future__ import unicode_literals
import sys
sys.path.append('/home/kxd/code-project/spider-publicnet/')
from freeproxy.models import Proxy, ProxySpider
# from freeproxy.settings import PROXY_WEB

if __name__ == '__main__':
    cursor = Proxy.select({'status': 1})
    ps = ProxySpider()
    ps.save_ip(list(cursor))
    pass

