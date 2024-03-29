import asyncio
import json
import re
import time

import aiohttp
import cv2
import numpy as np
import requests
import utils
from sign.captcha import captcha_key_and_token
from sign.enc import enc
import logging


# 异步加载数据
async def async_fetch(url):
    global async_session
    async with async_session.get(url) as res:
        return await res.content.read()


# 计算验证码的滑动距离
async def slide_distance(bg, tp):
    """
    计算滑动验证码的距离
    :param bg: 背景图的url
    :param tp: 滑块图的url
    :return: 计算得到的滑动距离
    """

    def cut_slide(slide):
        slider_array = np.frombuffer(slide, np.uint8)
        slider_image = cv2.imdecode(slider_array, cv2.IMREAD_UNCHANGED)
        slider_part = slider_image[:, :, :3]
        mask = slider_image[:, :, 3]
        mask[mask != 0] = 255
        x, y, w, h = cv2.boundingRect(mask)
        cropped_image = slider_part[y:y + h, x:x + w]
        return cropped_image

    tasks = [asyncio.create_task(async_fetch(i)) for i in [bg, tp]]
    bg, tp = await asyncio.gather(*tasks)
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


class CX:
    # 实例化请传入手机号和密码
    def __init__(self, phonenums, password):
        self.retry_cnt = 10
        self.user_name = utils.encryptByAES(phonenums)
        self.pwd = utils.encryptByAES(password)
        self.deptIdEnc = None
        self.deptId = None
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57",
        }
        self.login()  # 第一步 必须
        self.get_fidEnc()  # 第二步 必须
        self.phone = phonenums
        self.status = {
            0: '待履约',
            1: '学习中',
            2: '已履约',
            3: '暂离中',
            5: '被监督中',
            7: '已取消',
        }
        self.token_pattern = re.compile("token = '(.*?)'")
        self.page_token_pattern = re.compile(r"'&pageToken=' \+ '(.*)'}")
        self.today, self.tomorrow = utils.get_today_and_tomorrow()

    def login(self):
        data = {
            'fid': -1,
            'uname': self.user_name,
            'password': self.pwd,
            'refer': 'http%3A%2F%2Fi.chaoxing.com',
            't': 'true',
            'forbidotherlogin': 0,
            'validate': '',
            'doubleFactorLogin': 0,
            'independentId': 0
        }
        self.session.post('http://passport2.chaoxing.com/fanyalogin', data=data)

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

    def get_my_seat_id(self):
        """
        获取当前预约中的第一次预约的座位id
        :return: 座位id
        """
        # 注意 老版本的系统需要将url中的seat改为seatengine
        data = self.session.get(url="https://reserve.chaoxing.com/data/apps/seat/index").json()
        ids = [i["id"] for i in data["data"]["curReserves"]]
        return ids[0]

        # 获得预约的列表

    def get_submit_list(self):
        """
        获取当前预约的列表
        :return:
        """
        data = self.session.get("https://reserve.chaoxing.com/data/apps/seat/index").json()["data"]["curReserves"]
        return data

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
            "_": utils.get_time_stamp()
        }
        response = self.session.get(
            f'https://captcha.chaoxing.com/captcha/check/verification/result', params=params, headers=headers)
        text = response.text.replace('jQuery33105878581853212221_1698141785783(', "").replace(')', "")
        # 解析出验证签名
        data = json.loads(text)
        return json.loads(data["extraData"])['validate']

    def get_page_token(self):
        """
        获取pageToken
        :return: 解析得到的pageToken
        """
        url = 'https://office.chaoxing.com/front/apps/seat/list?'f'deptIdEnc={self.deptIdEnc}'
        response = self.session.get(url=url)
        page_token = self.page_token_pattern.findall(response.text)[0]
        return page_token

    async def get_submit_token(self, page_token):
        """
        获取提交座位预约时的token
        :param page_token: 页面token
        :return: token
        """
        url = f"https://reserve.chaoxing.com/front/third/apps/seat/select?id=5933&day={self.today}&backLevel=2&pageToken={page_token}"
        referer = 'https://office.chaoxing.com/front/apps/seat/list?'f'deptIdEnc={self.deptIdEnc}'
        headers = {
            "referer": referer
        }
        async with async_session.get(url=url, headers=headers) as res:
            text = await res.text()
            return self.token_pattern.findall(text)[0]

    async def get_slide_captcha_data(self, page_token):
        """
        获取验证码的相关数据
        :param page_token:
        :return:
        """
        url = "https://captcha.chaoxing.com/captcha/get/verification/image"
        t = utils.get_time_stamp()
        capture_key, token = captcha_key_and_token(t)
        referer = f"https://reserve.chaoxing.com/front/third/apps/seat/select?id=5933&day={self.today}&backLevel=2&pageToken={page_token}"
        # 参数
        params = {
            "callback": "jQuery33105878581853212221_1698141785783",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "version": "1.1.14",
            "captchaKey": capture_key,
            "token": token,
            "referer": referer,
            "_": t
        }
        async with async_session.get(url=url, params=params) as res:
            text = await res.text()
            data = text.replace("jQuery33105878581853212221_1698141785783(",
                                ")").replace(")", "")
            data = json.loads(data)
            captcha_token = data["token"]
            bg = data["imageVerificationVo"]["shadeImage"]
            tp = data["imageVerificationVo"]["cutoutImage"]
            return captcha_token, bg, tp

    def get_captcha_sign(self, token, x):
        headers = {
            "Referer": "https://reserve.chaoxing.com/"
        }
        params = {
            "callback": "jQuery33105878581853212221_1698141785783",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "token": token,
            "textClickArr": json.dumps([{"x": x}]),
            "coordinate": json.dumps([]),
            "runEnv": "10",
            "version": "1.1.14",
            "_": utils.get_time_stamp()
        }
        response = self.session.get(
            f'https://captcha.chaoxing.com/captcha/check/verification/result', params=params, headers=headers)
        text = response.text.replace('jQuery33105878581853212221_1698141785783(', "").replace(')', "")
        # 解析出验证签名
        data = json.loads(text)
        return json.loads(data["extraData"])['validate']

    async def submit_reserve_seat(self, start_time, end_time, retry_cnt=0):
        global params
        """
        生成座位预约所必须的参数信息
        :param start_time: 开启的时间
        :param end_time: 结束的时间
        :return: 返回的预约结果
        """
        # 1.获取pageToken
        page_token = self.get_page_token()
        # # 2.根据page_token去访问页面获得submit_token
        # submit_token = await self.get_submit_token(page_token)
        # # 3.获取验证码的数据
        # captcha_token, bg, tp = await self.get_slide_captcha_data(page_token)
        # 2,3可并行操作，修改为并行
        tasks = [
            asyncio.create_task(self.get_submit_token(page_token)),
            asyncio.create_task(self.get_slide_captcha_data(page_token))
        ]
        submit_token, (captcha_token, bg, tp) = await asyncio.gather(*tasks)
        # 4.根据验证码的数据计算滑动距离
        x = await slide_distance(bg, tp)
        # 5.获取滑动验证码的校验信息
        captcha_sign = self.get_captcha_sign(captcha_token, x)
        # 提交座位请求
        url = "https://reserve.chaoxing.com/data/apps/seat/submit"
        referer = ""
        headers = {
            "Referer": referer,
        }
        submit_params = {
            "roomId": params["room_id"],
            "startTime": start_time,
            "endTime": end_time,
            "day": self.tomorrow,
            "seatNum": params["seat_id"],
            "captcha": captcha_sign,
            "token": submit_token
        }
        submit_params["enc"] = enc(submit_params)
        data = self.session.get(url=url, params=submit_params, headers=headers).json()
        # 判断当前的请求
        if data.get("msg", "") == "非法请求" and retry_cnt < self.retry_cnt:
            logging.info(f"服务器未到预约时间发生错误！")
            return self.submit_reserve_seat(start_time, end_time, retry_cnt + 1)
        else:
            return data

    # 预提交，加速后面的速度
    async def pre_submit(self):
        await self.submit_reserve_seat("08:00", "12:00")

    async def submit(self):
        """
        座位预约逻辑
        :return:
        """
        # 预提交逻辑
        t_start = time.time()
        await self.pre_submit()
        t_end = time.time()
        logging.info(f"预抢座已完成,耗时{t_end - t_start}秒")
        # 开始延迟，等待抢座
        utils.delay(int(params["hour"]), 30)
        logging.info("延时结束开始抢座")
        # 真正提交逻辑
        time_list = [("08:00", "12:00"), ("12:00", "16:00"), ("16:00", "20:00"), ("20:00", "22:00")]
        t_start = time.time()
        for start_time, end_time in time_list:
            result = await self.submit_reserve_seat(start_time, end_time)
            logging.info(
                f"手机号{self.phone},房间号{params['room_id']},座位{params['seat_id']},起始时间{start_time},结束时间{end_time},预约日期{self.tomorrow},预约结果{result.get('msg', '成功')}")
        t_end = time.time()
        logging.info(f"手机号{self.phone},预约耗费{t_end - t_start}秒")

    def submit_sign(self, seat_id=None):
        if seat_id is None:
            seat_id = self.get_my_seat_id()
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/sign?'
                                        f'id={seat_id}')
        logging.info(f"签到信息{response.text}")

    # 退座
    def signback(self, seat_id=None):
        if seat_id is None:
            seat_id = self.get_my_seat_id()
        response = self.session.get(url='https://office.chaoxing.com/data/apps/seat/signback?'
                                        f'id={seat_id}')
        print(response.json())

    async def sign(self):
        # 获取当前的预约结果，判断是否需要签到
        cur_submit = self.get_submit_list()
        # 如果没有签到信息
        if len(cur_submit) == 0:
            logging.info(f"手机号{self.phone},你当前还没有预约信息！")
            return
        # 第一个为当前的数据
        now = cur_submit[0]
        # 判断当前是否到签到时间
        if utils.get_time_stamp() - now["startTime"] > -15 * 60 * 1000:
            if now["status"] != 1:
                # 不是就绪的逻辑，则直接进行签到
                logging.info(f"手机号{self.phone},当前状态:{self.status.get(now['status'], '未知状态')},将为您签到")
                self.submit_sign(now["id"])
            else:
                # 已经签到，查看当前是否还有下一个预约
                if len(cur_submit) == 1:
                    logging.info(f"手机号{self.phone},你已签到无需签到")
                    return
                # 查看结束时间与当前的差值是否在15分钟内
                if -15 * 60 * 1000 < now['endTime'] - utils.get_time_stamp() < 15 * 60 * 1000:
                    logging.info(f"手机号{self.phone},距离下一个位置的签到时间不足15分钟，将签退签到下一个")
                    # 退座
                    self.signback(now["id"])
                    # 进行下一个签到
                    self.submit_sign(cur_submit[1]['id'])
                # 状态既没有是其他的，也没有距离下次签到时间小于15分钟
                else:
                    # 无需进行签到
                    logging.info(f"手机号{self.phone},当前已签到,且距离下个座位签到时间大于15分钟,无需签到")
        else:
            logging.info(f":手机号{self.phone},当前还未到签到时间")


async def main():
    global params
    # 配置日志记录
    t_start = time.time()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    params = utils.get_param_dict()
    logging.info(f"当前执行的操作为：{params['type']}")
    # 实例化对象
    cx = CX(params["user_name"], params["password"])
    action = {
        "submit": cx.submit,
        "sign": cx.sign
    }
    global async_session
    async with aiohttp.ClientSession(cookies=cx.session.cookies) as async_session:
        # 触发动作
        await action[params["type"]]()
    t_end = time.time()
    logging.info(f"本次运行耗时{t_end - t_start}秒，脚本执行结束")


if __name__ == '__main__':
    async_session = None
    params = None
    asyncio.run(main())
