"""
时间相关的工具
"""
import time


def get_time_stamp():
    """
    获取十三位时间戳
    :return:
    """
    return int(time.time() * 1000)
