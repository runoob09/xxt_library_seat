"""
座位预约系统的相关工具类
"""
from lxml import etree


def parse_mappid(html: str):
    """
    从html中解析出数据
    :param html:
    :return:
    """
    xpath = ['/html/body/div[1]/div[3]/ul/li[1]/@onclick',
             "/html/body/div[1]/div[4]/ul/li[1]/@onclick"]
    selector = etree.HTML(html)
    mappid = []
    for x in xpath:
        mappid = selector.xpath(x)
        if len(mappid) != 0:
            break
    # 判断当前的解析结果
    if len(mappid) == 0:
        # 使用其他解析
        return selector.xpath("//div[@role='option']/@mappid")[0]
    else:
        return mappid[0].split('(')[1].split(',')[0]
