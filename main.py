#!/usr/bin/python3.7.0
# -*- coding: utf-8 -*-
import argparse
import base64
import json
import re
import time
from datetime import datetime, timedelta
import cv2
import numpy as np
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from python.capature import sign
from python.enc import enc
import psutil
import aiohttp
import asyncio


# 计算验证码的滑动距离
def identify_gap(bg, tp):
    '''
    bg: 背景图片
    tp: 缺口图片
    out:输出图片
    '''
    bg, tp = asyncio.run(async_fetch_img(bg, tp))
    # 读取背景图片和缺口图片
    bg_img = cv2.imdecode(np.frombuffer(bg, np.uint8), cv2.IMREAD_COLOR)  # 背景图片
    tp_img = cut_slide(tp)
    # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)
    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    # 绘制方框
    tl = max_loc  # 左上角点的坐标
    # 返回缺口的X坐标
    return tl[0]


# 获取当前的时间
def get_formatted_datetime():
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


async def async_fetch(session: aiohttp.ClientSession, url):
    async with session.get(url) as res:
        return await res.content.read()


# 异步获取图片的方法
async def async_fetch_img(back_url, slide_url):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(async_fetch(session, i)) for i in [back_url, slide_url]]
        return await asyncio.gather(*tasks)


# 加密函数
def encryptByAES(message):
    key = "u2oh6Vu^HWe4_AES"
    iv = key.encode('utf-8')
    aeskey = key.encode('utf-8')
    secretData = message.encode('utf-8')
    cipher = AES.new(aeskey, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(secretData, AES.block_size))
    ciphertext = base64.b64encode(encrypted).decode('utf-8')
    return ciphertext


def get_param_dict():
    def parse_key_value_pair(pair):
        key, value = pair.split('=')
        return key, value

    parser = argparse.ArgumentParser()
    # 解析键值对参数
    parser.add_argument('key_value_pairs', nargs='+', type=parse_key_value_pair, help='键值对参数')
    args = parser.parse_args()
    # 将键值对参数存储在字典中
    params = dict(args.key_value_pairs)
    return params


def cut_slide(slide):
    # 解码图像数据为NumPy数组
    slider_array = np.frombuffer(slide, np.uint8)
    # 将NumPy数组解码为OpenCV图像格式
    slider_image = cv2.imdecode(slider_array, cv2.IMREAD_UNCHANGED)
    # 提取滑块部分
    slider_part = slider_image[:, :, :3]  # 提取RGB通道，忽略Alpha通道
    # 创建掩膜
    mask = slider_image[:, :, 3]  # Alpha通道作为掩膜
    # 将掩膜中的非零值设为255
    mask[mask != 0] = 255
    # 查找滑块部分的边界框
    x, y, w, h = cv2.boundingRect(mask)
    # 裁剪滑块图像
    cropped_image = slider_part[y:y + h, x:x + w]
    return cropped_image


class CX:
    # 实例化请传入手机号和密码
    def __init__(self, phonenums, password):
        self.acc = phonenums
        self.pwd = password
        self.deptIdEnc = None
        self.deptId = None
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57",
        }
        self.login()  # 第一步 必须
        self.get_fidEnc()  # 第二步 必须
        self.phone = phonenums

    # 获取cookies
    def login(self):
        c_url = 'https://passport2.chaoxing.com/mlogin?' \
                'loginType=1&' \
                'newversion=true&fid=&' \
                'refer=http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Findex'
        self.session.get(c_url).cookies.get_dict()
        data = {
            'fid': -1,
            'uname': encryptByAES(self.acc),
            'password': encryptByAES(self.pwd),
            'refer': 'http%3A%2F%2Fi.chaoxing.com',
            't': 'true',
            'forbidotherlogin': 0,
            'validate': '',
            'doubleFactorLogin': 0,
            'independentId': 0
        }
        self.session.post('http://passport2.chaoxing.com/fanyalogin', data=data)
        s_url = 'https://office.chaoxing.com/front/third/apps/seat/index'
        self.session.get(s_url)

    # 获取学校id
    def get_fidEnc(self):
        # data = {
        #     'searchName': '',
        #     '_t': self.get_date()
        # }
        # res = self.session.post(url='https://i.chaoxing.com/base/cacheUserOrg', data=data)
        # print(res.json()["site"][0]['schoolname'], res.json()["site"][1]['schoolname'])  # 默认显示单位的前两个名称如果是多个单位请自行修改
        # for index in res.json()["site"]:
        #     fid = index['fid']
        #     res = self.session.get(url='https://uc.chaoxing.com/mobileSet/homePage?'
        #                                f'fid={fid}')
        #     selector = etree.HTML(res.text)
        #     mappid = selector.xpath(
        #         '/html/body/div[1]/div[3]/ul/li[1]/@onclick')  # ☆ 注意 这一步可能需要调整 否则不能正常获取到mappid 每个学校不一样此处就没有用RE ☆
        #     if mappid:
        #         self.mappid = mappid[0].split('(')[1].split(',')[0]
        # self.incode = self.session.cookies.get_dict()['wfwIncode']
        # url = f'https://v1.chaoxing.com/mobile/openRecentApp?incode={self.incode}&mappId={self.mappid}'
        # res = self.session.get(url=url, allow_redirects=False)
        # # 每个学校的deptIdEnc值是固定的，如果是为只为你的学校提供服务请直接将deptIdEnc保存！不需要再执行get_fidEnc()方法了
        # self.deptIdEnc = re.compile("fidEnc%3D(.*?)%").findall(res.headers['Location'])[0]
        # # 获全部预约记录
        return "64fc0d61619aa141"

    # 签到
    def sign(self):
        # 注意 老版本的系统需要将url中的seat改为seatengine
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/sign?'
                                        f'id={self.get_my_seat_id()}')
        print(f"{get_formatted_datetime()}:签到信息{response.text}")

    # 暂离
    def leave(self):
        # 注意 老版本的系统需要将url中的seat改为seatengine
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/leave?'
                                        f'id={self.get_my_seat_id()}')
        print(response.json())

    # 退座
    def signback(self):
        # 注意 老版本的系统需要将url中的seat改为seatengine
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/signback?'
                                        f'id={self.get_my_seat_id()}')
        print(response.json())

    # 取消
    def cancel(self):
        # 注意 老版本的系统需要将url中的seat改为seatengine
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/cancel?'
                                        f'id={self.get_my_seat_id()}')
        print(response.json())

    # 时间戳转换1
    @classmethod
    def t_time(cls, timestamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(str(timestamp)[0:10])))

    # 时间戳转换2
    @classmethod
    def t_second(cls, timestamp):
        if timestamp:
            m, s = divmod(int(str(timestamp)[0:-3]), 60)
            h, m = divmod(m, 60)
            if m:
                if h:
                    return str(h) + "时" + str(m) + "分" + str(s) + "秒"
                return str(m) + "分" + str(s) + "秒"
            return str(s) + "秒"
        return "0秒"

    def get_capture(self, url):
        t = int(time.time() * 1000)
        capture_key, token = sign(t)
        # 参数
        params = {
            "callback": "jQuery33105878581853212221_1698141785783",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "version": "1.1.14",
            "captchaKey": capture_key,
            "token": token,
            "referer": url,
            "_": t
        }
        response = self.session.get("https://captcha.chaoxing.com/captcha/get/verification/image", params=params)
        data = response.text.replace("jQuery33105878581853212221_1698141785783(", "").replace(")", "")
        return json.loads(data)

    # 预约座位 需要自己修改
    def submit(self, room_id, seat_num):
        # 获取今天的日期
        today = datetime.now().date()
        # 获取明天的日期
        tomorrow = today + timedelta(days=1)
        # 格式化日期为 "yyyy-MM-dd" 格式
        today = today.strftime("%Y-%m-%d")
        tomorrow = tomorrow.strftime("%Y-%m-%d")
        time_list = [("08:00", "12:00"), ("12:00", "16:00"), ("16:00", "20:00"), ("20:00", "22:00")]
        index_url = 'https://office.chaoxing.com/front/apps/seat/list?'f'deptIdEnc={self.deptIdEnc}'
        for start, end in time_list:
            # 重试请求
            for i in range(3):
                # 提交步骤
                result = self.submit_step(today, tomorrow, room_id, seat_num, start, end, index_url)
                print(
                    f"{get_formatted_datetime()}:手机号{self.phone},房间号{room_id},座位{seat_num},起始时间{start},结束时间{end},预约日期{tomorrow},预约结果{result},请求次数{i}")
                if result['success']:
                    break

    def submit_step(self, today, tomorrow, room_id, seat_num, start, end, index_url):
        # 注意 老版本的系统需要将url中的seat改为seatengine且不需要第一步获取list。有可能需要提供seatId的值
        # 获取token
        response = self.session.get(url=index_url)
        pageToken = re.compile(r"'&pageToken=' \+ '(.*)'}").findall(response.text)[0]
        referer = f"https://reserve.chaoxing.com/front/third/apps/seat/select?id=5933&day={today}&backLevel=2&pageToken={pageToken}"
        token = self.get_token(referer, index_url)
        # 获取图片验证码
        capture_data = self.get_capture(referer)
        # 校验图片的token
        verify_token = capture_data["token"]
        # 背景图
        shade_image_url = capture_data["imageVerificationVo"]["shadeImage"]
        # 缺块图
        cut_out_image_url = capture_data["imageVerificationVo"]["cutoutImage"]
        # 滑动的距离
        d = identify_gap(shade_image_url, cut_out_image_url)
        # 提交中的一个参数
        captcha = self.verify_capture(verify_token, d)
        result = self.appoint_seat(captcha, token, referer, start, end, tomorrow, room_id, seat_num)
        return result

    # 验证图片验证码
    def verify_capture(self, token, d):
        headers = {
            "Referer": "https://reserve.chaoxing.com/"
        }
        params = {
            "callback": "jQuery33105878581853212221_1698141785783",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "token": token,
            "textClickArr": json.dumps([{"x": d}]),
            "coordinate": json.dumps([]),
            "runEnv": "10",
            "version": "1.1.14",
            "_": int(time.time() * 1000)
        }
        response = self.session.get(
            f'https://captcha.chaoxing.com/captcha/check/verification/result', params=params, headers=headers)
        text = response.text.replace('jQuery33105878581853212221_1698141785783(', "").replace(')', "")
        # 解析出验证签名
        data = json.loads(text)
        return json.loads(data["extraData"])['validate']

    def distance(self, background_url, slider_url):
        response_background = self.session.get(background_url)
        response_slider = self.session.get(slider_url)
        background_image = cv2.imdecode(np.frombuffer(response_background.content, np.uint8), cv2.IMREAD_GRAYSCALE)
        slider_image = cv2.imdecode(np.frombuffer(response_slider.content, np.uint8), cv2.IMREAD_GRAYSCALE)
        # 使用模板匹配找到缺口在背景图中的位置
        result = cv2.matchTemplate(background_image, slider_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        slider_width = slider_image.shape[1]  # 缺口图的宽度
        # 计算滑动距离
        slider_distance = max_loc[0] + slider_width / 2  # 滑块中心点在背景图中的位置
        return slider_distance

    # 预约座位的接口
    def appoint_seat(self, captcha, token, referer, start, end, tommorow, room_id, seat_num):
        headers = {
            "Referer": referer,
        }
        params = {
            "roomId": room_id,
            "startTime": start,
            "endTime": end,
            "day": tommorow,
            "seatNum": seat_num,
            "captcha": captcha,
            "token": token
        }
        params["enc"] = enc(params)
        response = self.session.get("https://reserve.chaoxing.com/data/apps/seat/submit", params=params,
                                    headers=headers)
        return response.text

    def get_token(self, url, referer):
        headers = {
            "referer": referer
        }
        response = self.session.get(url, headers=headers)
        res = re.compile("token = '(.*?)'").findall(response.text)[0]
        return res

    # 标准时间转换
    @classmethod
    def get_date(cls):
        return time.strftime('%a %b %d %Y %I:%M:%S GMT+0800 ', time.localtime(time.time())) + '(中国标准时间)'

    # 获取到最近一次预约座位ID 默认的取消 签到 暂离都是默认这个 请自行发挥
    def get_my_seat_id(self):
        # 注意 老版本的系统需要将url中的seat改为seatengine
        data = self.session.get(url="https://reserve.chaoxing.com/data/apps/seat/index").json()
        ids = [i["id"] for i in data["data"]["curReserves"]]
        return ids[0]

    # 监督别人的座位
    def supervise(self, id):
        response = self.session.get(f"https://office.chaoxing.com/data/apps/seat/supervise?id={id}&objectId=")
        return response


if __name__ == '__main__':
    # room_id 5933
    # seat_id 10
    start = time.time()
    pid = psutil.Process().pid
    psutil.Process(pid).nice(-20)
    params = get_param_dict()
    print(f"{get_formatted_datetime()}:脚本开始执行,执行的操作类型为:{params['type']}")
    cx = CX(params['user_name'], params["password"])
    if params["type"] == "submit":
        retry_cnt = 0
        try:
            cx.submit(params["room_id"], params["seat_id"])
        except Exception as e:
            retry_cnt += 1
            print(f"{get_formatted_datetime()}:发生错误，错误信息{e.args},重试次数{retry_cnt}")
            if retry_cnt < 10:
                cx.submit(params["room_id"], params["seat_id"])
            else:
                exit()
    elif params['type'] == "sign":
        cx.sign()
    end = time.time()
    print(f"{get_formatted_datetime()}:本次运行耗时{end - start}秒，脚本执行结束")
