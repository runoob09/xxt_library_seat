"""
与时间相关的工具类
"""
import time
from datetime import datetime, timedelta


def get_date(day_offset: int):
    """
    :param day_offset: 日期偏移量
    :return: 日期字符串
    """
    # 获取今天的日期
    today = datetime.now().date()
    # 获取明天的日期
    offset_day = today + timedelta(days=day_offset)
    tomorrow = offset_day.strftime("%Y-%m-%d")
    return tomorrow


def get_date_str():
    """
    获取当前的日期字符串
    :return: 当前的日期字符串
    """
    return time.strftime('%a %b %d %Y %I:%M:%S GMT+0800 ', time.localtime(time.time())) + '(中国标准时间)'
