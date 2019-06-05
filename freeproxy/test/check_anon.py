# coding=utf-8
"""
检测匿名度
"""
import requests

# 搜狐
url1 = 'http://pv.sohu.com/cityjson?ie=utf-8'

# 站长工具
url2 = 'http://www.xxorg.com/tools/checkproxy/'

proxy = {
    'http:': '182.108.44.47:808',
    'https': '182.108.44.47:808'
}

res = requests.get(url1, proxies=proxy)
print(res.text)








