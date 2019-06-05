# coding=utf-8
"""
端口代理
"""
from __future__ import unicode_literals

import requests
from datetime import datetime

import execjs
#
# js = ""
# execjs.eval()



proxies = {
    "http": "http://103.238.225.77:8888",
    "https": "https://103.238.225.77:8888",

    # "http": "socks5://127.0.0.1:1080",
    # 'https': 'socks5://127.0.0.1:1080'
}

a = ['高匿', '透明']
s = datetime.now()

res = requests.get('http://pv.sohu.com/cityjson?ie=utf-8', proxies=proxies)
print(res.text)
# 检索匿名度
res = requests.get('http://www.xxorg.com/tools/checkproxy/', proxies=proxies, timeout=5)
# res = requests.get('http://www.xxorg.com/tools/checkproxy/')
print(res.text)
# 访问知网主页
r = requests.get('http://www.cnki.net/', proxies=proxies, timeout=5)
if '知网' in r.content.decode('utf-8'):
    print('cnki success')

# 访问详情页
r = requests.get('http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=cpfd&dbname=cpfd9908&filename=dzxx200807001060', proxies=proxies)
if '知网' in r.content.decode('utf-8'):
    print('cnki success')
# wechat_detail = 'https://mp.weixin.qq.com/s?src=11&timestamp=1545197401&ver=1283&signature=0wD3ij5dP9cs5hAXeHqb1' \
#                 '2I6CgxVu8HmadJhszmKuGI1ZN-RUr*veiaszltr*kTh1-Ra*lK3FHAv-*FWVpOaGy8CERPTx4ZJq9eBqz83mBZ3mMc8CFSIP20nHDTbp**O&new=1'
# res_wechat = requests.get(wechat_detail, proxies=proxies)

# if '从微信打开验证身份' in res_wechat.text:
#   print('从微信打开验证身份')
# r = requests.get('http://www.baidu.com', proxies=proxies)

e = datetime.now()
print(e - s)

# print r.text
