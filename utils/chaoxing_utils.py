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
    selector = etree.HTML(html)
    mappid = selector.xpath('/html/body/div[1]/div[3]/ul/li[1]/@onclick')
    if mappid:
        mappid = mappid[0].split('(')[1].split(',')[0]
    else:
        mappid = selector.xpath("//div[@role='option']/@mappid")[0]
    return mappid
