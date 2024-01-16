class param(object):
    def __init__(self):
        self.user_name = ""
        self.password = ""
        self.type = ""
        self.hour = 0
        self.room_id = 0
        self.seat_num = 0
        self.seat_id = 0
        self.day_offset = 0
        self.time_list = ""
        self.use_captcha = False
        self.system_type = "new"

    def set_user_name(self, user_name):
        self.user_name = user_name

    def set_password(self, password):
        self.password = password

    def set_type(self, type):
        self.type = type

    def set_hour(self, hour):
        self.hour = hour

    def set_room_id(self, room_id):
        self.room_id = room_id

    def set_seat_num(self, seat_num):
        self.seat_num = seat_num

    def set_seat_id(self, seat_id):
        self.seat_id = seat_id

    def set_day_offset(self, day_offset):
        self.day_offset = day_offset

    def set_time_list(self, time_list):
        self.time_list = time_list

    def get_user_name(self):
        return self.user_name

    def get_password(self):
        return self.password

    def get_type(self):
        return self.type

    def get_hour(self):
        return self.hour

    def get_room_id(self):
        return self.room_id

    def get_seat_num(self):
        return self.seat_num

    def get_seat_id(self):
        return self.seat_id

    def get_day_offset(self):
        return self.day_offset

    def get_time_list(self):
        return self.time_list
    def get_system_type(self):
        return self.system_type