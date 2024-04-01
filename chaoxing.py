import json
import re

import aiohttp
import requests
from tabulate import tabulate

from config import LogConfig
from model.param import param
from sign.captcha import captcha_key_and_token
from utils import chaoxing_utils, system_utils, sign_utils, date_utils, time_utils


class Chaoxing:
    def __init__(self, p: param):

        self.deptIdEnc = None
        self.async_session: aiohttp.ClientSession = None
        self.session: requests.Session = requests.session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57",
        }
        self.p = p
        self.logger = system_utils.get_logger(log_path=LogConfig.log_path, logging_name=LogConfig.logging_name)
        self.mappid = None
        self.incode = None
        self.token_pattern = re.compile("token = '(.*?)'")
        self.page_token_pattern = re.compile(r"'&pageToken=' \+ '(.*)'}")
        # 当天的日期
        self.today = date_utils.get_date(0)
        self.reserve_day = date_utils.get_date(int(self.p.day_offset))
        self.retry_cnt = 10
        # 访问的地址
        self.page_token_url = "https://office.chaoxing.com/front/apps/seat/list?deptIdEnc={}"

    def get_time_list(self):
        global params
        default = [("08:00", "12:00"), ("12:00", "16:00"), ("16:00", "20:00"), ("20:00", "22:00")]
        value = self.p.get_time_list()
        if value is None or value == "":
            return default
        else:
            return [key_value.split("-") for key_value in value.split(",")]

    def get_cookies(self):
        """
        获取cookies
        :return:
        """
        return self.session.cookies

    def login(self):
        """
        登录
        :return:
        """
        c_url = 'https://passport2.chaoxing.com/mlogin?' \
                'loginType=1&' \
                'newversion=true&fid=&' \
                'refer=http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Findex'
        self.session.get(c_url)
        data = {
            'fid': -1,
            'uname': sign_utils.encryptByAES(self.p.get_user_name()),
            'password': sign_utils.encryptByAES(self.p.get_password()),
            'refer': 'http%3A%2F%2Fi.chaoxing.com',
            't': 'true',
            'forbidotherlogin': 0,
            'validate': '',
            'doubleFactorLogin': 0,
            'independentId': 0
        }
        self.session.post('http://passport2.chaoxing.com/fanyalogin', data=data)

    def get_fid_enc(self):
        """
        获取fid
        :return: 获取到的fid
        """
        data = {
            'searchName': ''
        }
        res = self.session.post(url='https://i.chaoxing.com/base/cacheUserOrg', data=data)
        for index in res.json()["site"]:
            fid = index['fid']
            res = self.session.get(url=f"https://uc.chaoxing.com/mobileSet/homePage?fid={fid}")
            # 当前页面包含座位预约这个应用
            if res.text.find("预约") != -1:
                self.logger.info(f"你的单位：{index['schoolname']}")
                fid = index['fid']
                res = self.session.get(url=f"https://uc.chaoxing.com/mobileSet/homePage?fid={fid}")
                self.mappid = chaoxing_utils.parse_mappid(res.text)  # ☆ 注意 这一步可能需要调整 否则不能正常获取到mappid 每个学校不一样此处就没有用RE ☆
        self.incode = self.session.cookies.get_dict()['wfwIncode']
        url = f"https://v1.chaoxing.com/mobile/openRecentApp?mappId={self.mappid}&incode={self.incode}"
        res = self.session.get(url=url, allow_redirects=False)
        # 每个学校的deptIdEnc值是固定的，如果是为只为你的学校提供服务请直接将deptIdEnc保存！不需要再执行get_fidEnc()方法了
        self.deptIdEnc = re.compile("fidEnc%3D(.*?)%").findall(res.headers['Location'])[0]
        self.logger.info(f"你所属单位的fidEnc是:{self.deptIdEnc}")
        return self.deptIdEnc

    async def get_room_id_list(self, url):
        """
        获取所在单位的自习室名称和id
        :return:
        """
        p = {
            "time": "",
            "cpage": "1",
            "pageSize": "100",
            "firstLevelName": "",
            "secondLevelName": "",
            "thirdLevelName": "",
            "deptIdEnc": self.deptIdEnc,
            "seatId": self.p.get_seat_id()
        }
        room_data = self.session.get(url=url, params=p).json()
        # 展示自习室信息
        data = [
            ["自习室id", "自习室名称"]
        ]
        for i in room_data["data"]["seatRoomList"]:
            room_name = (i["firstLevelName"] + "-" + i["secondLevelName"] + "-" + i["thirdLevelName"]).replace("\n", "")
            room_id = i["id"]
            data.append([room_id, room_name])
        table = tabulate(data, headers="firstrow", tablefmt="plain", colalign=("left", "right"))
        print(table)
        return room_data

    async def get_page_token(self):
        """
        解析得到页面token
        :return:
        """
        url = self.page_token_url.format(self.deptIdEnc)
        async with self.async_session.get(url) as response:
            html = await response.text()
            page_token = re.compile("'&pageToken=' \+ '(.*&?)'").findall(html)[0]
            return page_token

    async def get_submit_token(self, page_token):
        """
        获取提交座位预约时的token
        :param page_token: 页面token
        :return: token
        """
        pass

    async def get_slide_captcha_data(self, page_token):
        """
        获取验证码的相关数据
        :param page_token:
        :return:
        """
        url = "https://captcha.chaoxing.com/captcha/get/verification/image"
        t = time_utils.get_time_stamp()
        capture_key, token = captcha_key_and_token(t)
        referer = f"https://reserve.chaoxing.com/front/third/apps/seat/select?id={self.p.get_room_id()}&day={self.today}&backLevel=2&pageToken={page_token}"
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
        async with self.async_session.get(url=url, params=params) as res:
            text = await res.text()
            data = text.replace("jQuery33105878581853212221_1698141785783(",
                                ")").replace(")", "")
            data = json.loads(data)
            captcha_token = data["token"]
            bg = data["imageVerificationVo"]["shadeImage"]
            tp = data["imageVerificationVo"]["cutoutImage"]
            return captcha_token, bg, tp

    async def __async_fetch__(self, url):
        async with self.async_session.get(url) as response:
            return await response.content.read()

    async def submit(self):
        pass

    async def list_room(self):
        pass
