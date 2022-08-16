# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 14:07:24 2022

@author: 47176
"""

import requests
import pandas as pd
import numpy as np
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
import json
import time
from multiprocessing import Pool
import re
import pymongo

client = pymongo.MongoClient("localhost", 27017)
db_house_renting = client['house_renting']
collection = db_house_renting.community_info_lianjia
# df_community_info = pd.read_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\data\小区urls测试.xlsx')


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


def get_community_info(html):
    """ 获取小区基础信息 """
    doc = pq(html)
    # base info
    items_key = doc('div.xiaoquInfoItem > span.xiaoquInfoLabel').items()
    info_key = [i.text() for i in items_key]
    items_value = doc('div.xiaoquInfoItem > span.xiaoquInfoContent').items()
    info_value = [i.text() for i in items_value]
    base_info_dict = dict(zip(info_key, info_value))
    # price
    items_price = doc('li.fl')('span').items()
    list_price = [int(re.findall('\\d+', i.text())[0]) for i in items_price]
    items_house_desc = doc('li.fl')('div.goodSellItemDesc').items()
    list_desc = [float(re.findall(r"\d+\.?\d*", i.text().split('/')[0])[0]) for i in items_house_desc]
    list_avgprice = [i/j for i, j in zip(list_price, list_desc)]
    base_info_dict['avg_price'] = round(np.mean(list_avgprice), 2)
    return base_info_dict


# def save_to_mongo(result):
#     if collection.insert_one(result):
#         # print('存储到mongodb成功', result)
#         return True
#     return False


def main(area: str):
    """ 输入区域 """
    # global df_community_info  好像这样无法使用？？？
    df_community_info = pd.read_excel(r'D:\学习总文件夹\整体项目\爬虫\住房问题\链家\data\小区urls.xlsx')
    print('== 我要开始咯！ {} ==', area)
    time0 = time.time()
    df_out = pd.DataFrame()
    urls = df_community_info[df_community_info['area']==area]['url'].tolist()
    n = 0
    for url in urls:
        n += 1
        # 获取信息
        item_info = get_community_info(get_one_page_html(url))
        item_info['url'] = url
        # 导出信息
        df_out = df_out.append(item_info, ignore_index=True)  # pandas
        # save_to_mongo(item_info)
    df_out.to_excel(r'D:\学习总文件夹\整体项目\爬虫\住房问题\链家\result\{}_小区信息.xlsx'.format(area))
    time1 = time.time()
    timedelta = round(time1 - time0, 0)
    print('== 该区域 {} 共计 {} 个小区，耗时 {} 秒'.format(area, n, timedelta))
        
        
#%%
if __name__ == '__main__':
    df_community_info = pd.read_excel(r'D:\学习总文件夹\整体项目\爬虫\住房问题\链家\data\小区urls.xlsx')
    area_list = df_community_info['area'].unique().tolist()
    print('== 燥起来吧！！！！ ==')
    print('== 开始时间为{} =='.format(time.asctime()))
    pool = Pool()
    pool.map(main, [i for i in area_list])
    print('== 完事了！！！ ==')
    print('== 结束时间为{} =='.format(time.asctime()))
    
