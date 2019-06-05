# coding=utf-8

from __future__ import unicode_literals

import socks
import socket,requests


import urllib2
from sockshandler import SocksiPyHandler

opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 1080))
x = opener.open("http://www.google.com/")
print x.read()

socks.set_default_proxy(socks.SOCKS5, "localhost", port=1080)
socket.socket = socks.socksocket

headers = {
    'user-agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; fi-FI) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16'
}
r_google=requests.get('https://www.google.com', headers=headers, allow_redirects=False, verify=False,)
print r_google