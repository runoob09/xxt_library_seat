import asyncio
import json
import random
import time

import cv2
import numpy as np

from chaoxing import Chaoxing
from model.param import param
from sign.enc import enc
from utils import time_utils, system_utils


class NewChaoxing(Chaoxing):
    def __init__(self, p: param):
        super().__init__(p)
        self.async_session = None
        self.list_room_url = "https://reserve.chaoxing.com/data/apps/seat/room/list"

    def list_room(self):
        return super().get_room_id_list(url=self.list_room_url)

    async def get_submit_token(self, page_token):
        """
                获取提交座位预约时的token
                :param page_token: 页面token
                :return: token
                """
        url = f"https://reserve.chaoxing.com/front/third/apps/seat/select?id={self.p.get_room_id()}&day={self.today}&backLevel=2&pageToken={page_token}&deptIdEnc={self.deptIdEnc}"
        referer = 'https://office.chaoxing.com/front/apps/seat/list?'f'deptIdEnc={self.deptIdEnc}'
        headers = {
            "referer": referer
        }
        async with self.async_session.get(url=url, headers=headers) as res:
            text = await res.text()
            return self.token_pattern.findall(text)[0], str(res.url)

    async def slide_distance(self, bg, tp):
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

        tasks = [asyncio.create_task(self.__async_fetch__(i)) for i in [bg, tp]]
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

    async def reserve_seat(self, start_time, end_time, retry_cnt=0, is_retry=True):
        data = None
        # 1.获取pageToken
        page_token = await self.get_page_token()
        # 2.获取提交token
        submit_token, referer = await self.get_submit_token(page_token)
        # 判断是否需要验证码
        if not self.p.use_captcha:
            data = self.__reserve_with_no_captcha__(start_time, end_time, referer, submit_token)
        else:
            # 3.获取验证码
            captcha_token, bg, tp = await self.get_slide_captcha_data(page_token)
            # 4.计算滑动距离
            distance = await self.slide_distance(bg, tp)
            # 5.获取验证签名
            validate = self.get_captcha_sign(captcha_token, distance)
            # 提交本次座位预约请求
            data = self.__reserve_with_captcha__(start_time, end_time, referer, submit_token, validate)
            # 判断当前的请求
        if data.get("msg", "") == "非法预约" and retry_cnt < self.retry_cnt and is_retry:
            self.logger.info(
                f"开始时间:{start_time},结束时间:{end_time},服务器未到预约时间发生错误！重试次数:{retry_cnt}")
            return await self.reserve_seat(start_time, end_time, retry_cnt=retry_cnt + 1)
        else:
            return data

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
            "_": time_utils.get_time_stamp()
        }
        response = self.session.get(
            f'https://captcha.chaoxing.com/captcha/check/verification/result', params=params, headers=headers)
        text = response.text.replace('jQuery33105878581853212221_1698141785783(', "").replace(')', "")
        # 解析出验证签名
        data = json.loads(text)
        return json.loads(data["extraData"])['validate']

    def __reserve_with_no_captcha__(self, start_time, end_time, referer, submit_token):
        # 不需要验证码直接发送请求
        url = "https://reserve.chaoxing.com/data/apps/seat/submit"
        headers = {
            "Referer": referer
        }
        print(headers)
        p = {
            "deptIdEnc": self.deptIdEnc,
            "roomId": self.p.get_room_id(),
            "startTime": start_time,
            "endTime": end_time,
            "day": self.reserve_day,
            "captcha": "",
            "seatNum": self.p.get_seat_num(),
            "token": submit_token
        }
        print(p)
        data = self.session.get(url, params=p, headers=headers).json()
        return data

    def __reserve_with_captcha__(self, start_time, end_time, referer, submit_token, captcha_sign):
        # 提交座位请求
        url = "https://reserve.chaoxing.com/data/apps/seat/submit"
        headers = {
            "Referer": referer,
        }
        submit_params = {
            "roomId": self.p.room_id,
            "startTime": start_time,
            "endTime": end_time,
            "day": self.reserve_day,
            "seatNum": self.p.seat_num,
            "captcha": captcha_sign,
            "token": submit_token
        }
        submit_params["enc"] = enc(submit_params)
        data = self.session.get(url=url, params=submit_params, headers=headers).json()
        return data

    async def submit(self):
        """
        预约指定时间段的逻辑
        :return:
        """
        # 预提交逻辑
        t_start = time.time()
        await self.pre_submit()
        t_end = time.time()
        self.logger.info(f"预抢座已完成,耗时{t_end - t_start}秒")
        # 开始延迟，等待抢座
        system_utils.delay(self.p.time_delay, 30)
        self.logger.info("延时结束开始抢座")
        # 真正提交逻辑
        time_list = self.get_time_list()
        random.shuffle(time_list)
        t_start = time.time()
        for start_time, end_time in time_list:
            result = await self.reserve_seat(start_time, end_time)
            print(result)
            self.logger.info(
                f"手机号{self.p.get_user_name()},房间号{self.p.get_room_id()},座位{self.p.get_seat_num()},起始时间{start_time},结束时间{end_time},预约日期{self.reserve_day},预约结果{result.get('msg', '成功')}")
        t_end = time.time()
        self.logger.info(f"手机号{self.p.user_name},预约耗费{t_end - t_start}秒")

    async def pre_submit(self):
        """
        提前预约创建tcp链接
        :return:
        """
        await self.reserve_seat("08:00", "12:00", is_retry=False)
