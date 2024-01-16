from chaoxing import Chaoxing
from model.param import param
from sign.enc import enc


class OldChaoxing(Chaoxing):
    def __init__(self, p: param):
        super().__init__(p)
        self.list_room_url = "https://reserve.chaoxing.com/data/apps/seatengine/room/list"

    def list_room(self):
        return super().get_room_id_list(self.list_room_url)

    async def get_submit_token(self, page_token):
        """
        获取提交token
        :return:
        """
        url = "https://reserve.chaoxing.com/front/third/apps/seatengine/select"
        p = {
            "id": self.p.get_room_id(),
            "day": self.today,
            "backLevel": "2",
            "seatId": self.p.get_seat_id(),
            "fidEnc": self.deptIdEnc
        }
        headers = {
            "Referer": f"https://reserve.chaoxing.com/front/third/apps/seatengine/list?deptIdEnc={self.deptIdEnc}&seatId={self.p.get_seat_id()}"
        }
        res = self.session.get(url, params=p, headers=headers)
        return self.token_pattern.findall(res.text)[0], res.url

    async def reserve_seat(self, start_time, end_time):
        """
        旧版系统提交逻辑
        """
        # 1.获取提交时的token
        submit_token, referer = self.get_submit_token(None)
        # 2.提交座位请求
        url = "https://reserve.chaoxing.com/data/apps/seatengine/submit"
        headers = {
            "Referer": referer,
            "X-Requested-With": "XMLHttpRequest"
        }
        p = {
            "roomId": self.p.get_room_id(),
            "startTime": start_time,
            "endTime": end_time,
            "day": self.reserve_day,
            "captcha": "",
            "seatNum": self.p.get_seat_num(),
            "token": submit_token
        }
        p["enc"] = enc(p)
        data = self.session.get(url, params=p, headers=headers).json()
        return data
