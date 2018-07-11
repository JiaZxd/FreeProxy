# coding=utf-8
"""
端口代理
"""
from __future__ import unicode_literals

import requests

proxies = {
  "http": "http://180.180.216.219:8906",
  "https": "http://124.193.37.5:8888",
}


r = requests.get('http://www.cnki.net/', proxies=proxies)
print r