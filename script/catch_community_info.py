import logging
import os
path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家'
os.chdir(path)

from script.http_ops.html_service import get_one_page_html
from pyquery import PyQuery as pq
import re
import numpy as np


class HouseDistrictCatching:
    """ 小区信息提取 """
    def __init__(self, base_url=None):
        """ base_url: 链家首页 """
        self.url_base = base_url if base_url else 'https://sh.lianjia.com'
        self.url_selection = 'https://sh.lianjia.com/xiaoqu/bp6ep10000/'  # 均价6w以上小区 TODO 修改为动态生成
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
        for i in doc('div[data-role=ershoufang]')('a').items():
            res.append({'area': i.text(),
                        'url': self.url_base + i.attr('href')})
        self.urls_area = res

        return res

    @staticmethod
    def generate_hd_urls(url) -> list:
        """
        解析当前页面下的房源url

        :param url: 支持首页，区域页面，区域pg页等
        :return:
            [{'house': abc, 'url': 小区页面地址}]
        """
        doc = pq(get_one_page_html(url))
        res = []
        for i in doc('div.title > a').items():
            res.append({'house': i.text(),
                        'url': i.attr('href')})
        return res

    def calculate_pg_num(self, area=None, num_one_pg=30):
        """
        计算需要的pg数量

        :param area: 某区域
        :param num_one_pg: 网页中一页的房源
        :return:
        """
        if not area:
            doc = self.doc_base
            house_num = int(doc('div.resultDes')('h2.total.fl')('span').text())
        else:
            url_area = self.get_url_by_area(area)
            doc = pq(get_one_page_html(url_area))
            house_num = int(doc('div.resultDes')('h2.total.fl')('span').text())

        return int(house_num/num_one_pg)+1

    @staticmethod
    def get_hd_info(url_house):
        """ 获取小区基础信息 url_house: 房源的链接 """
        html_house = get_one_page_html(url_house)
        doc = pq(html_house)
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

    @staticmethod
    def generate_pg_url(url, n):
        """
        根据pg号生成页面，针对https://sh.lianjia.com/xiaoqu/**开头

        :param url: 区域页面或者总页面
        :param n: pg号
        :return:
        """
        tmp = url.split('/')
        tmp[-2] = 'pg{}'.format(n) + tmp[-2]
        url_pg = '/'.join(tmp)
        return url_pg

    def get_url_by_area(self, area):
        """ 获取某区域的url """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        return area_url

    def get_area_hd_info(self, area):
        """
        获取某个区的全部小区信息

        :param area:
        :return:
        """
        area_info_list = self.generate_area_urls()
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        if not area_url:
            return False, '未获取到该区 {} 的链接，支持的区域为 {}'.format(area, [i.area for i in area_url])

        # 获取该区域全部小区的url
        pg_num = self.calculate_pg_num(area)
        urls_pg_list = [self.generate_pg_url(area_url, i) for i in range(pg_num)]
        urls_hd_list = list()
        for i in urls_pg_list:
            urls_hd_list += self.generate_hd_urls(i)

        print('== {} 区域总计 {} 个小区'.format(area, len(urls_hd_list)))  # TODO 改成logging方法
        # 分url获取

        return urls_hd_list
