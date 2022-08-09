# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 15:56:16 2022

@author: 47176
"""


import requests
import pandas as pd
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
# from bs4 import BeautifulSoup
# import pymongo
# from config import *
# from multiprocessing import Pool

#
base_url = 'https://sh.lianjia.com'


def get_one_page_html(url):
    """ 获取网站每一页的html """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.121 Safari/537.36"
        }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


def find_page_url(html) -> [str]:
    """ 根据html获取分页url """
    doc = pq(html)
    pages_info = doc('div.content__article > ul > li > a').items()
    res = []
    for i in pages_info:
        res.append(base_url + i.attr('href'))
    return res


def find_room_url(html) -> [str]:
    """ 根据html去解析房间url链接 """
    doc = pq(html)
    urls_info = doc('.content__list')('div > a').items()
    res = []
    for i in urls_info:
        url_ = i.attr('href')
        url = base_url + url_
        res.append(url)
    return res


def get_room_info_page(html) -> [dict]:  # 获取一整个页面的房间信息
    """
    根据html获取房间信息字典。共有如下信息
        name: 房间名
        area: 面积
        price: 房间价格
        orientation: 朝向
        types: 房间类型
        floor: 房间楼层
        updated_info: 房间维护信息
    """
    
    doc = pq(html)  # doc
    room_info = doc('.content__list--item--main').items() # generator
    res = []
    for i in room_info:
        desc = i('.content__list--item--des').text()
        price = i('.content__list--item-price').text()
        updated_info = i('.content__list--item--time.oneline').text()
        desc_vec = desc.replace(' ', '').split('/')
        name = desc_vec[0]
        area = desc_vec[1]
        orientation = desc_vec[2]
        types = desc_vec[3]
        floor = desc_vec[4]
        dict_info = {'name': name, 'area': area, 'price': price,
                     'orientation': orientation, 'types': types, 'floor': floor,
                     'updated_info': updated_info}
        res.append(dict_info)
    return res


def get_room_info(html) -> dict:
    """
        获取单个房源url的信息
        暂时不需要房源额外信息，防止过多调用
    """
    pass


def main(path):
    my_html = get_one_page_html('https://sh.lianjia.com/zufang/pudong/rt200600000001l0l1rp6/?showMore=1')  # 浦东

    pages = find_page_url(my_html)

    df = pd.DataFrame()
    n = 0
    for p in pages:
        p_html = get_one_page_html(p)
        tmp = get_room_info_page(p_html)
        for i in tmp:
            df = df.append(i, ignore_index=True)
        n += 1
        print('== finish page {} df size is {}'.format(n, df.size))
    df.to_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\result\链家浦东.xlsx',
                index=None)

#%% TODOlist
"""
下一步将筛选条件参数化
"""
