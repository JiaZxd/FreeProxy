# coding=utf-8

"""
代理ip爬取配置文件，设置参数：
"""

import os

env = os.getenv('env', 'dev')
log_level = 'debug'
if env == 'dev':
    # 清容
    HOST = '110.184.160.230'  # 网络ip
    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = 27017
    DB = 'data'

    # log_level = 'debug'
elif env == 'production':
    # 节能大厦
    HOST = '218.89.222.253'  # 网络ip
    MONGO_HOST = '192.168.102.127'  # 数据库地址
    MONGO_PORT = 27017
    DB = 'data'

    # log_level = 'info'

# 已经写好的代理网站爬虫
PROXY_WEB = [
    'goubanjia', 'data5u',  'xici','qiyun',  'cn_proxy'
    #'proxydb',
]

#
TEST_WEBSITE = [
    {'name': 'cnki',
     'url': 'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=cpfd&dbname=cpfd9908&filename=dzxx200807001060',
     'headers': None},
    {'name': 'sipop', 'url': 'http://www.sipop.cn',
     'headers': None}

]
