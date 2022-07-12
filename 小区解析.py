# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 10:28:03 2022

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

base_url = 'https://sh.lianjia.com'
url = 'https://sh.lianjia.com/xiaoqu/bp6ep10000/'

#%%
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
 

def generate_area_urls(html):
    """ 解析主页，返回各区的urls dict """
    doc = pq(html)
    res = {}
    for i in doc('div[data-role=ershoufang]')('a').items():
        res[i.text()] = base_url + i.attr('href')
    return res


def generate_community_urls(html):
    """ 解析分区页，返回小区详细信息urls dict """
    # html = 'https://sh.lianjia.com/xiaoqu/pudong/bp6ep10000/'  # pudong case
    doc = pq(html)
    res = {}
    for i in doc('div.title > a').items():
        res[i.text()] = i.attr('href')
    return res


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


def main(n):
    global df_community_info
    i = df_community_urls.iloc[n]
    info_dict = get_community_info(get_one_page_html(i))
    info_dict['url'] = i
    df_community_info = df_community_info.append(info_dict, ignore_index=True)
    return
#%%
if __name__ == '__main__':
    
    # 获取首页html 仅保留房价6w起步的小区
    base_html = get_one_page_html(url)
    # 生成分区域urls字典
    area_urls = generate_area_urls(base_html)
    # =========================================
    # 对各分区生成分页信息，并抓取房源urls
    area_community_urls = {}
    for i in area_urls:
        print('== 开始{}区域的url抓取 ==\r\n'.format(i))
        community_urls = {}        
        for j in range(1, 51):
            tmp = area_urls[i].split('/')
            tmp[-2] = 'pg{}'.format(j)
            url_pg = '/'.join(tmp)
            one_page_html = get_one_page_html(url_pg)
            if one_page_html:
                community_urls.update(generate_community_urls(get_one_page_html(url_pg)))
            print('= 完成page{}的抓取 ='.format(j))
        area_community_urls.update({i:community_urls})
        print('== 完成{}区域的url抓取 =='.format(i))
    # 整理小区urls表
    df_community_urls = pd.DataFrame(area_community_urls).stack()
    df_community_urls.name = 'url'
    df_community_urls.index.set_names(('name', 'area'), [0, 1], inplace=True)
    df_community_urls = df_community_urls.swaplevel('area', 'name')
    # ========================================
    # 输出一下urls
    # json
    with open(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\data\小区urls.txt', 'w', encoding='utf-8') as f:
        json.dump(area_community_urls, f,  ensure_ascii=False)
    # dataframe
    df_community_urls.to_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\data\小区urls.xlsx',
                           merge_cells=False, header=['url'])
    # 抓取小区信息
    df_community_info = pd.DataFrame()
    n = 0
    time0 = time.time()
    time00 = time.time()
    print('= 开始获取小区具体信息, 共计{}个小区 ='.format(len(df_community_urls)))
    
    # ========================== 多线程
    pool = Pool()
    
    # ===========================
    pool.map(main, [i for i in range(len(df_community_urls))])
    # for i in df_community_urls:
    #     info_dict = get_community_info(get_one_page_html(i))
    #     info_dict['url'] = i
    #     df_community_info = df_community_info.append(info_dict, ignore_index=True)
    #     n += 1
    #     time1 = time.time()
    #     timedelta = time1 - time0
    #     if n % 100 == 0:
    #         time0 = time1            
    #         print('= 已经完成{}个房源记录, 耗时{}秒 ='.format(n, round(timedelta, 2)))
    print('== 房源记录全部处理完毕，耗时{}秒 =='.format(round(time.time()-time00, 2)))
    df_community_info.to_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\result\小区基础信息.xlsx')
    # # 分区域抓取信息
    # for i in dict_urls.values():
    #     generate_house_urls(i)

#%% sample test

s_url = 'https://sh.lianjia.com/xiaoqu/5011102207057/'
s_html = get_one_page_html(s_url)

doc = pq(s_html)

#%%
for i in doc('li.fl').items()
#%% MongoDB test
import pymongo
client = pymongo.MongoClient("localhost",27017)

db_test = client.bw_test # databases
res = [{'area': i, 'url': b[i]} for i in b]
db_test.area_urls.insert_many(res)


#%% main_test

h = get_one_page_html(url)
t = generate_area_urls(h)
url_pudong = t['浦东']
t2 = generate_house_urls(get_one_page_html(t['浦东']))

