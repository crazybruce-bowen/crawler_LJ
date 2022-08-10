import os
import traceback

path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家'
os.chdir(path)

from script.http_ops.html_service import get_one_page_html
from pyquery import PyQuery as pq
import re
import numpy as np
from script.common_ops.utils import print_time
import time


class HouseCatching:
    """ 小区信息提取 """
    def __init__(self, url_base=None):
        """ base_url: 链家首页 """
        self.url_base = url_base if url_base else 'https://sh.lianjia.com'
        self.url_selection = 'https://sh.lianjia.com/zufang/rt200600000001l0l1rp6/?showMore=1'  # 均价5k-8k以上房源 TODO 修改为动态生成
        self.html_base = get_one_page_html(self.url_selection)  # 筛选页首页html
        self.doc_base = pq(self.html_base)  # 生成pg包的doc文件
        self.urls_area = None

    def generate_area_urls(self):
        """
        解析主页，生成分区域分页

        :return:
            [{'area': 小区区域, 'url': 分页地址}]
        """
        doc = self.doc_base
        res = []
        for i in doc('ul[data-target=area]')('a').items():
            res.append({'area': i.text(),
                        'url': self.url_base + i.attr('href')})
        self.urls_area = res

        return res

    def find_page_url(self, html) -> [str]:
        """ 根据html获取分页url """
        doc = pq(html)
        res = []
        for i in doc('div.content__article > ul[style=display\:hidden] > li > a').items():
            res.append(self.url_base + i.attr('href'))
        return res


#%% 测试区域
for i in doc('ul[data-target=area]')('a').items():
    res.append({'area': i.text(),
                'url': t.url_base + i.attr('href')})
#%%

url_pudong = 'https://sh.lianjia.com/zufang/putuo/rt200600000001l0l1rp6/'
doc = pq(get_one_page_html(url_pudong))
#%%
for i in doc('div.content__article > ul[style=display\:hidden] > li > a').items():
    print(i.attr('href'))