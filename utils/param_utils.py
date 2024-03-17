"""
调用参数相关的工具
"""
import sys
from model.param import param


def get_param():
    """
    加载配置文件，获取参数
    :return: 参数对象
    """
    params_dict = {}
    p = param()
    # 从文件中加载数据
    with open("resources/config.properties", mode="r", encoding="utf-8") as f:
        line = [i.replace("\n", "").split("=") for i in f.readlines()]

        for k, v in line:
            params_dict[k] = v
    try:
        # 默认命令行配置的参数优先级更高
        for k, v in [i.split("=") for i in sys.argv]:
            params_dict[k] = v
    except:
        print("用户没有输入命令行参数")
    # 根据param的参数从param_dict中获取数据进行填充
    for k, v in p.__dict__.items():
        if k in params_dict:
            if str(params_dict[k]).isdigit():
                setattr(p, k, int(params_dict[k]))
            else:
                setattr(p, k, params_dict[k])
    return p
