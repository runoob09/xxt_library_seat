import base64
import time
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import sys
from lxml import etree
import logging

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
    tomorrow = today + timedelta(days=1)
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


def get_date():
    """
    获取日期字符串
    :param cls:
    :return:
    """
    return time.strftime('%a %b %d %Y %I:%M:%S GMT+0800 ', time.localtime(time.time())) + '(中国标准时间)'


def parse_mappid(html: str):
    selector = etree.HTML(html)
    mappid = selector.xpath('/html/body/div[1]/div[3]/ul/li[1]/@onclick')
    if mappid:
        mappid = mappid[0].split('(')[1].split(',')[0]
    else:
        mappid = selector.xpath("//div[@role='option']/@mappid")[0]
    return mappid


def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger
