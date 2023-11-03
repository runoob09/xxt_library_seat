import base64
import time
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import sys

# 获取当前的十三位时间戳
def get_time_stamp():
    return int(time.time() * 1000)


# 延迟，预备抢座，默认一秒60次
def delay(hour, freq=60):
    while datetime.now().hour != hour:
        time.sleep(1 / freq)


def encryptByAES(s):
    """
    加密函数
    :param s: 传入的字符串
    :return: 加密后的结果
    """
    key = "u2oh6Vu^HWe4_AES"
    iv = key.encode('utf-8')
    aeskey = key.encode('utf-8')
    secretData = s.encode('utf-8')
    cipher = AES.new(aeskey, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(secretData, AES.block_size))
    ciphertext = base64.b64encode(encrypted).decode('utf-8')
    return ciphertext


def get_date():
    """
    获取当前的日期字符串
    :return: 当前的日期字符串
    """
    return time.strftime('%a %b %d %Y %I:%M:%S GMT+0800 ', time.localtime(time.time())) + '(中国标准时间)'


def get_today_and_tomorrow():
    # 获取今天的日期
    today = datetime.now().date()
    # 获取明天的日期
    tomorrow = today + timedelta(days=2)
    # 格式化日期为 "yyyy-MM-dd" 格式
    today = today.strftime("%Y-%m-%d")
    tomorrow = tomorrow.strftime("%Y-%m-%d")
    return today, tomorrow


def get_param_dict():
    """
    获取传入的参数字典
    :return:
    """
    params = {}
    for k, v in [i.split("=") for i in sys.argv[1:]]:
        params[k] = v
    return params
