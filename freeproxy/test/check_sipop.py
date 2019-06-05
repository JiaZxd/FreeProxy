# coding=utf-8
"""
检测匿名度
"""
import requests

# 搜狐
url1 = 'http://www.sipop.cn/patent-interface-search/patentDetail/queryAuditInfo?applicationDocNum=CN200420061132.7'


proxy = {
    'http:': '182.108.44.47:808',
    'https': '182.108.44.47:808'
}
headers = {
    'referer': 'http://www.sipop.cn/module/gate/patentSearch/domesticDetail.html'
}

res = requests.get(url1, headers=headers, proxies=proxy)
if res.status_code == 200:
    pass
print(res.text)








