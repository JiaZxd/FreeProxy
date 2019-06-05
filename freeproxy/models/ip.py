# coding=utf-8
"""
代理ip类：
    1.对ip数据库操作
    2.对代理ip的检测
"""
import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from .mongo_helper import db_crawler
from .utils import open_url
from freeproxy.settings import TEST_WEBSITE


class Proxy(object):
    """
    ip池,保存代理ip的信息,期刊从中获取代理ip
    """

    def __init__(self):
        self.ip = ''  # ip地址
        self.port = ''  # 端口
        self.add_time = ''  # 添加时间
        self.update_time = ''  # 更新时间(每次更新,会得到新的延时)
        self.status = -1  # 代理状态, 1可用, -1不可用, 0延时高
        self.delay = 10.0  # 延时
        self.anonymous = ''  # ip代理类型（透明|匿名|高匿）
        # self.type = ''  # ip请求类型
        self.method = []  # ip请求类型(重新命名)

        self.website = ''  # 来源网站
        self.success = 0  # 验证成功次数
        self.failed = 0  # 验证失败次数

        self.test_web = []

    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)

    # 验证ip
    def validate_ip(self, proxy):
        """
        检查ip是否可用，是否能打开cnki网页（ip主要用于爬取文献）。
        三个步骤：
            1.匿名度（只保存匿名/高匿）
            2.测试需求的网页（cnki、sipop）
            3.插入数据库
        :param proxy:[], eg: [{ip:'', port:'', }]
        :return:
        """
        if not isinstance(proxy, dict):
            raise Exception
        try:
            ip = proxy['ip']
            port = int(float(proxy['port']))
            website = proxy.get('name', '')
        except KeyError as e:
            return ''
        ip_port = '%s:%s' % (ip, port)

        # 1.检查匿名度
        anonymous = '透明'
        http_method = []
        try:
            anonymous, http_method = self.check_anonymous(ip, port)
        except Exception as e:
            self.logger.exception('validate anonymous failed：{0}:{1}'.format(ip, port))

        # 2.测试要通过的网页
        test_web = []
        if anonymous != '透明' and len(http_method) > 0:
            _method = http_method[0]
            proxies = {
                _method: "{method}://{ip}:{port}".format(method=_method, ip=ip, port=port),
            }
            try:
                test_web = self._test_website(proxies)
            except Exception as e:
                self.logger.info('open cnki failed：{0}:{1}'.format(ip, port))

        # 3.插入数据库
        if len(test_web) > 0:  # 通过测试网站
            proxy = Proxy()
            proxy.ip = ip
            proxy.port = port
            proxy.test_web = test_web
            proxy.anonymous = anonymous
            proxy.method = http_method
            proxy.website = website

            _id = proxy.insert()
            self.logger.info('%s:%s 保存数据库' % (ip, port))
            return ip_port
        else:
            self.failed_proxy(ip, port, -1)

    # 检查匿名度
    def check_anonymous(self, ip, port):
        """
        检查ip匿名度,判断ip透明|匿名|高匿
        :param ip:
        :param port:
        :return:
        """

        methods = ('http', 'https')

        anonymous_arr = []
        use_methods = []

        host = self._get_host()  # 获取当前外网ip
        for me in methods:
            proxies = {
                me: "{type}://{ip}:{port}".format(type=me, ip=ip, port=port),
            }

            string = self._get_host(proxy=proxies)
            if not string:
                continue
            # selector = etree.HTML(text=res.text)
            # string = res.text
            # 匿名度判断
            if host in string:
                value = '透明'
            elif 'unknown' in string or '使用高匿名代理' in string:
                value = '高匿'
            elif ip in string or '普通匿名代理服务器' in string:
                value = '匿名'
            else:
                value = '透明'
                print('外网ip：%s，代理ipo：%s，协议：%s' % (host, string, me))
                # raise Exception()

            if value != '透明':
                use_methods.append(me)
                anonymous_arr.append(value)

        if len(anonymous_arr) > 0:
            anonymous = anonymous_arr.pop()
        else:
            anonymous = '透明'

        return anonymous, use_methods

    # 能否打开测试网站
    def _test_website(self, proxies):
        """
        验证ip要打开的网站
        :return:
        """
        result = dict()
        for web in TEST_WEBSITE:
            delay = -1
            name = web['name']
            url = web['url']

            try:
                # 打开cnki延时
                res = open_url(url, proxy=proxies)
            except Exception as e:
                raise Exception
            else:
                if not res:
                    # result[name] = False
                    continue

                if res.status_code == 200 and (res.elapsed.total_seconds() < 1.3):
                    #and string in res.content.decode('utf-8')
                    # 匿名度
                    delay = res.elapsed.total_seconds()  # 响应时间
                result[name] = delay

        return result

    # 获得所在网络ip地址
    def _get_host(self, proxy=None):

        res1 = open_url('http://pv.sohu.com/cityjson?ie=utf-8', proxy=proxy)
        # res2 = open_url('http://www.xxorg.com/tools/checkproxy/', proxy=proxy)

        if res1:
            string = res1.text.strip(';').split('=')[1]

            # 比较两个获取的ip是否一致
            host = eval(string)['cip']
        else:
            host = ''
        return host

    """数据库操作"""

    # 保存到数据库
    def insert(self):
        self.add_time = datetime.now()
        self.update_time = datetime.now()
        self.success += 1

        required_fields = ['ip', 'port', 'anonymous', 'delay']
        for key in required_fields:
            if not self.__dict__[key]:
                raise KeyError('%s Error:must value' % key)
        try:
            _id = db_crawler.proxy.insert(self.__dict__)
        except DuplicateKeyError as e:
            # 更新代理ip更新时间
            cur = db_crawler.proxy.find_one({'ip': self.ip, 'port': self.port})
            delay = (cur['delay'] + self.delay) / 2
            success = cur['success'] + 1
            params = {
                'update_time': datetime.now(),
                'delay': delay,
                'status': 1,
                'anonymous': self.anonymous,
                'method': self.method,
                'success': success
            }
            _id = self.update(cur['_id'], params)
        return _id

    def update(self, _id, _dict):
        result = db_crawler.proxy.update({'_id': _id}, {'$set': _dict})
        return result

    def delete(self):
        pass

    @classmethod
    def select(cls, query, dtype='cursor', sort=None):
        """
        
        :param query: 
        :param dtype: 
        :param sort: 
        :return: 
        """
        cur = db_crawler.proxy.find(query)  # .sort([('_id',-1)])
        if sort:
            cur = cur.sort(sort)
        return cur

    # 处理不可用的ip
    def failed_proxy(self, ip, port, status):
        """

        :return:
        """
        status = -1
        result = ''
        if not ip or not port:
            raise KeyError('Value not " "')
        cur = db_crawler.proxy.find_one({'ip': ip, 'port': port})
        # now = datetime.now()
        if cur:
            # cha = (now - cur['add_time']).days
            failed = cur['failed'] + 1
            success = cur['success']
            # 成功比率，小于80%的删除
            ratio = float(cur['success']) / (failed + cur['success']) * 100

            if status == -1 and failed > 50 and ratio < 75:
                db_crawler.proxy.remove({'_id': cur['_id']})
            elif cur:
                params = {
                    'status': status,
                    'update_time': datetime.now(),
                    'failed': failed
                }
                result = self.update(cur['_id'], params)
        return result


if __name__ == '__main__':
    pass
