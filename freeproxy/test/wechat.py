# coding=utf-8
"""
端口代理
"""
from __future__ import unicode_literals

import requests
from datetime import datetime

# proxies = {
#   "http": "http://163.43.30.69:60088",
#   "https": "http://163.43.30.69:60088",
# }
proxies = {
  "http": "http://221.239.108.36:80",
  "https": "http://221.239.108.36:80",
}
# proxies = {
#   "http": "http://140.205.222.3:80",
#   "https": "http://140.205.222.3:80",
# }

a = ['高匿', '透明', ]
s = datetime.now()

r = requests.get('http://weixin.sogou.com/', proxies=proxies)
# r = requests.get('http://www.baidu.com', proxies=proxies)
e = datetime.now()
print(e-s)
#article_url = 'https://mp.weixin.qq.com/s?src=11&timestamp=1537342201&ver=1131&signature=iu2OC0H-NkJhmmG7I1gaKdyqloRUCIJrjPRLEx-KTgUaKrsqQftJmTAc3Z8xvDl7sZQ0lgi0agYBCuHoxawoff8igFvWsFUz7EKS1u9QNInBsVlvE9SKRNxcfKO19XdR&new=1'

article_url = 'http://weixin.sogou.com/weixin?p=42341200&query=%E6%BF%80%E5%85%89&type=2&ie=utf8'
headers = {
            'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8',
            'Accept - Encoding': 'gzip, deflate, sdch',
            'Accept - Language': 'zh - CN, zh;q = 0.8',
            # Connection:keep - alive
            # 'Host': 'weixin.sogou.com
            'user-agent': "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Mobile Safari/537.36",
            'Referer': article_url
        }
res = requests.get(article_url, headers=headers, proxies=proxies)
print(res.content)
print(res.url)
# print r.text

