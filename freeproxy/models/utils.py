# coding=utf-8

import logging

import requests
from requests.exceptions import Timeout, ReadTimeout, ConnectTimeout,ProxyError

logger = logging.getLogger('utils')


def open_url(url, proxy=None, timeout=5):
    """
    get打开网站
    :param url:
    :param proxy: 代理ip
    :param timeout: 请求时间
    :return:
    """
    # url = 'http://cn-proxy.com/'
    res = False  # 结果

    headers = {
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    }
    if not proxy:
        proxy = dict()
    str_proxy = ''.join(proxy.values())  # 代理ip字符串
    try:
        res = requests.get(url=url, headers=headers, proxies=proxy, timeout=timeout)
    except (ReadTimeout, ConnectTimeout) as e:
        logger.debug('%s，访问超时！' % str_proxy)
    except ProxyError as e:
        logger.debug('%s，代理ip不能使用！' % str_proxy)
    except Exception as e:
        logger.exception(e)
    else:
        if res.status_code != 200:
            logger.exception('%s，响应码:%s！' % (str_proxy, res.status_code))
            res = False
    return res
