# coding=utf-8

from __future__ import unicode_literals
import base64
import requests
import time
from StringIO import StringIO
from PIL import Image
import pytesseract

from lxml import etree

# uin

uin = base64.b64encode('MzAxMDU0MDYwMQ==')

proxies = {
    "http": "http://112.25.6.30:80",
    "https": "http://112.25.6.30:80",
}


def get_url():
    req = requests.session()
    home_url = 'http://bizapi.cn/Home/LinkTransfer'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    res = req.get('http://bizapi.cn/Home/GetCaptchaImage')
    cracked_captcha(res)
    r = r.get(home_url, headers=headers)
    print(r.text)
    selector = etree.HTML(text=r.text)
    selector.xpath('//*[@id="codeImg"]')
    # 解析
    url = 'http://bizapi.cn/Home/LinkTransfer?type=1'
    params = {
        'url': 'https://mp.weixin.qq.com/s?src=11&timestamp=1543980601&ver=1283&signature=0wD3ij5dP9cs5hAXeHqb12I'
               '6CgxVu8HmadJhszmKuGKR*7OeQNvSFqmQLrJWMFotrTaZfz-Mf*AehcJIqB4q0ptsH-k3YZQeCaixYt3wbS0B5Ou3KglanosSYY6GnVHb&new=1',
        'code': ''
    }
    res = requests.post(url=url, params=params, headers=headers)

    # 验证码图片
    res = req.get('http://bizapi.cn/Home/GetCaptchaImage')
    print(res)


def convert_to_permanent_url(temp_url):
    pre_redirect_url = "".join([temp_url, "&uin=", uin])
    response = requests.head(pre_redirect_url)
    permanent_url = response.headers['Location']
    return permanent_url


import hashlib, random, string
from urllib import quote

# app_id = '2110320846'

"""腾讯ocr调用"""


def test_tecent():
    # 腾讯ocr使用（识别效果不好）
    with open('1.jpeg', 'rb') as f:
        strins = f.read()
    base64_data = base64.b64encode(strins)
    url = 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr'
    params = get_params(base64_data)
    res = requests.post(url, params)
    print(res)


def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    return m.hexdigest().upper()


def get_params(base64_data):
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = '2110320846'
    app_key = 'cO4C1hMqnmL5ixIr'
    params = {'app_id': app_id,
              'image': base64_data,
              'time_stamp': time_stamp,
              'nonce_str': nonce_str,
              }
    sign_before = ''
    # 要对key排序再拼接
    for key in sorted(params):
        # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
        sign_before += '{}={}&'.format(key, quote(params[key], safe=''))
    # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
    sign_before += 'app_key={}'.format(app_key)
    # 对字符串sign_before进行MD5运算，得到接口请求签名
    sign = curlmd5(sign_before)
    params['sign'] = sign
    return params


def down_img():
    proxies = {
        "http": "http://112.25.6.30:80",
        "https": "http://112.25.6.30:80",
    }
    for x in xrange(0, 100):
        res = requests.get('http://bizapi.cn/Home/GetCaptchaImage', proxies=proxies)
        file_name = '%s.jpeg' % x
        with open('img/%s' % file_name, 'wb') as f:
            f.write(res.content)
        # print(res.content)
        pass


"""tesseract使用"""


# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'


def cracked_captcha(response):
    # url_captcha = 'http://cx.cnca.cn/rjwcx/checkCode/rand.do?'
    # 获取英文验证码
    # captcha_image = self._requests_url(url=url_captcha, method='get', params={'d': time.time()})

    # 生成流
    # output = StringIO()
    # output.write(response.content)
    # output.seek(0)

    # 识别验证码
    image = Image.open('64.jpeg')  # 将图片转成为灰度图像
    image = covert_image(image)
    saveSmall(image, 'cfs/', cfs(image))
    text = pytesseract.image_to_string(image)
    print(text)
    value = ''
    if not text:  # 未识别出
        pass
    elif text[1] == 'x':
        value = (int('%s' % text[0]) * int('%s' % text[2]))
    elif text[1] == '-':
        value = (int('%s' % text[0]) - int('%s' % text[2]))
    elif text[1] == '+':
        value = (int('%s' % text[0]) + int('%s' % text[2]))
    return value
    pass


# 灰度处理
def covert_image(image):
    # 灰度化
    image = image.convert('L')  # 将图片转成为灰度图像
    # 二值化
    standard = 150  # 阀值， 将图片转为黑白
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    # image.save('covert.jpeg')
    return image

    # 二值化


from Queue import Queue

"""连通域分割"""


# 切割
def cfs(img):
    """传入二值化后的图片进行连通域分割"""
    pixdata = img.load()
    w, h = img.size
    visited = set()
    q = Queue()
    offset = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cuts = []
    for x in range(w):
        for y in range(h):
            x_axis = []
            # y_axis = []
            if pixdata[x, y] == 0 and (x, y) not in visited:
                q.put((x, y))
                visited.add((x, y))
            while not q.empty():
                x_p, y_p = q.get()
                for x_offset, y_offset in offset:
                    x_c, y_c = x_p + x_offset, y_p + y_offset
                    if (x_c, y_c) in visited:
                        continue
                    visited.add((x_c, y_c))
                    try:
                        if pixdata[x_c, y_c] == 0:
                            q.put((x_c, y_c))
                            x_axis.append(x_c)
                            # y_axis.append(y_c)
                    except:
                        pass
            if x_axis:
                min_x, max_x = min(x_axis), max(x_axis)
                if max_x - min_x > 3:
                    # 宽度小于3的认为是噪点，根据需要修改
                    cuts.append((min_x, max_x + 1))
    return cuts


def saveSmall(img, outDir, cuts):
    w, h = img.size
    pixdata = img.load()
    for i, item in enumerate(cuts):
        box = (item[0], 0, item[1], h)
        img.crop(box).save(outDir + str(i) + ".png")


# img = Image.open('out/51.png')
import numpy as np

import cv2


def getPoint(x, y, data, subdata=None):
    a = [0, -1, 0, 1, 0, -2, 0, 2, 0, -3, 0, 3, 0, -4, 0, 4, 0, -5, 0, 5]
    b = [1, 0, -1, 0, 2, 0, -2, 0, 3, 0, -3, 0, 4, 0, -4, 0, 5, 0, -5, 0]
    width, height = data.shape
    if subdata is None:
        subdata = []
    if x > 5 and y < height - 5 and y > 5 and x < width - 5:
        for i in range(20):
            if data[x + a[i]][y + b[i]] == 1:
                subdata.append((x + a[i], y + b[i]))
                data[x + a[i]][y + b[i]] = 2
                getPoint(x + a[i], y + b[i], data, subdata)
    subdata.append((x, y))



def getcell(data):
    list1 = []
    index = 0
    flag = True
    for y in range(data.shape[1]):
        for x in range(data.shape[0]):
            if data[x][y] == 1:
                if list1:
                    for i in range(len(list1)):
                        if (x, y) in list1[i]:
                            flag = False
                if not flag:
                    continue
                list1.append([])
                getPoint(x, y, data, list1[index])  # 调用流水算法
                index += 1
            else:
                continue

    for index in range(len(list1)):
        l = list1[index][0][0]
        t = list1[index][0][1]
        r = list1[index][0][0]
        b = list1[index][0][1]
        for i in list1[index]:
            x = i[0]
            y = i[1]
            l = min(l, x)
            t = min(t, y)
            r = max(r, x)
            b = max(b, y)
        w = r - l + 1
        h = b - t + 1
        if w * h < 8:  # 去除小色块
            continue
        img0 = np.zeros([w, h])  # 创建全0矩阵
        for x, y in list1[index]:
            img0[x - l][y - t] = 1
        img0[img0 < 1] = 255
        img1 = Image.fromarray(img0)
        img1 = img1.convert('RGB')
        img1.save('img2/' + str(index) + '.png')

"""水滴"""
from itertools import groupby

def binarizing(img,threshold):
    """传入image对象进行灰度、二值处理"""
    img = img.convert("L") # 转灰度
    pixdata = img.load()
    w, h = img.size
    # 遍历所有像素，大于阈值的为黑色
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    return img

def vertical(img):
    """传入二值化后的图片进行垂直投影"""
    pixdata = img.load()
    w,h = img.size
    result = []
    for x in range(w):
        black = 0
        for y in range(h):
            if pixdata[x,y] == 0:
                black += 1
        result.append(black)
    return result

def get_start_x(hist_width):
    """根据图片垂直投影的结果来确定起点
       hist_width中间值 前后取4个值 再这范围内取最小值
    """
    mid = len(hist_width) // 2 # 注意py3 除法和py2不同
    temp = hist_width[mid-4:mid+5]
    return mid - 4 + temp.index(min(temp))

def get_nearby_pix_value(img_pix,x,y,j):
    """获取临近5个点像素数据"""
    if j == 1:
        return 0 if img_pix[x-1,y+1] == 0 else 1
    elif j ==2:
        return 0 if img_pix[x,y+1] == 0 else 1
    elif j ==3:
        return 0 if img_pix[x+1,y+1] == 0 else 1
    elif j ==4:
        return 0 if img_pix[x+1,y] == 0 else 1
    elif j ==5:
        return 0 if img_pix[x-1,y] == 0 else 1
    else:
        raise Exception("get_nearby_pix_value error")


def get_end_route(img,start_x,height):
    """获取滴水路径"""
    left_limit = 0
    right_limit = img.size[0] - 1
    end_route = []
    cur_p = (start_x,0)
    last_p = cur_p
    end_route.append(cur_p)

    while cur_p[1] < (height-1):
        sum_n = 0
        max_w = 0
        next_x = cur_p[0]
        next_y = cur_p[1]
        pix_img = img.load()
        for i in range(1,6):
            cur_w = get_nearby_pix_value(pix_img,cur_p[0],cur_p[1],i) * (6-i)
            sum_n += cur_w
            if max_w < cur_w:
                max_w = cur_w
        if sum_n == 0:
            # 如果全黑则看惯性
            max_w = 4
        if sum_n == 15:
            max_w = 6

        if max_w == 1:
            next_x = cur_p[0] - 1
            next_y = cur_p[1]
        elif max_w == 2:
            next_x = cur_p[0] + 1
            next_y = cur_p[1]
        elif max_w == 3:
            next_x = cur_p[0] + 1
            next_y = cur_p[1] + 1
        elif max_w == 5:
            next_x = cur_p[0] - 1
            next_y = cur_p[1] + 1
        elif max_w == 6:
            next_x = cur_p[0]
            next_y = cur_p[1] + 1
        elif max_w == 4:
            if next_x > last_p[0]:
                # 向右
                next_x = cur_p[0] + 1
                next_y = cur_p[1] + 1
            if next_x < last_p[0]:
                next_x = cur_p[0]
                next_y = cur_p[1] + 1
            if sum_n == 0:
                next_x = cur_p[0]
                next_y = cur_p[1] + 1
        else:
            raise Exception("get end route error")

        if last_p[0] == next_x and last_p[1] == next_y:
            if next_x < cur_p[0]:
                max_w = 5
                next_x = cur_p[0] + 1
                next_y = cur_p[1] + 1
            else:
                max_w = 3
                next_x = cur_p[0] - 1
                next_y = cur_p[1] + 1
        last_p = cur_p

        if next_x > right_limit:
            next_x = right_limit
            next_y = cur_p[1] + 1
        if next_x < left_limit:
            next_x = left_limit
            next_y = cur_p[1] + 1
        cur_p = (next_x,next_y)
        end_route.append(cur_p)
    return end_route

def get_split_seq(projection_x):
    split_seq = []
    start_x = 0
    length = 0
    for pos_x, val in enumerate(projection_x):
        if val == 0 and length == 0:
            continue
        elif val == 0 and length != 0:
            split_seq.append([start_x, length])
            length = 0
        elif val == 1:
            if length == 0:
                start_x = pos_x
            length += 1
        else:
            raise Exception('generating split sequence occurs error')
    # 循环结束时如果length不为0，说明还有一部分需要append
    if length != 0:
        split_seq.append([start_x, length])
    return split_seq


def do_split(source_image, starts, filter_ends):
    """
    具体实行切割
    : param starts: 每一行的起始点 tuple of list
    : param ends: 每一行的终止点
    """
    left = starts[0][0]
    top = starts[0][1]
    right = filter_ends[0][0]
    bottom = filter_ends[0][1]
    pixdata = source_image.load()
    for i in range(len(starts)):
        left = min(starts[i][0], left)
        top = min(starts[i][1], top)
        right = max(filter_ends[i][0], right)
        bottom = max(filter_ends[i][1], bottom)
    width = right - left + 1
    height = bottom - top + 1
    image = Image.new('RGB', (width, height), (255,255,255))
    for i in range(height):
        start = starts[i]
        end = filter_ends[i]
        for x in range(start[0], end[0]+1):
            if pixdata[x,start[1]] == 0:
                image.putpixel((x - left, start[1] - top), (0,0,0))
    return image

def drop_fall(img):
    """滴水分割"""
    width, height = img.size
    # 1 二值化
    b_img = binarizing(img,200)
    # 2 垂直投影
    hist_width = vertical(b_img)
    # 3 获取起点
    start_x = get_start_x(hist_width)

    # 4 开始滴水算法
    start_route = []
    for y in range(height):
        start_route.append((0, y))

    end_route = get_end_route(img,start_x,height)
    filter_end_route = [max(list(k)) for _,k in groupby(end_route,lambda x:x[1])] # 注意这里groupby
    img1 = do_split(img,start_route,filter_end_route)
    img1.save('cuts-d-1.png')

    start_route = list(map(lambda x : (x[0]+1,x[1]),filter_end_route)) # python3中map不返回list需要自己转换
    end_route = []
    for y in range(height):
        end_route.append((width-1,y))
    img2 = do_split(img,start_route,end_route)
    img2.save('cuts-d-2.png')


if __name__ == '__main__':
    p = Image.open("cuts-2.png")
    drop_fall(p)

    # down_img()
    # covert_image()
    # filename = 'test'
    # data = cv2.imread(filename, 2)
    # allimg = getcell(data)
    # test_tecent()
    # cracked_captcha('')
