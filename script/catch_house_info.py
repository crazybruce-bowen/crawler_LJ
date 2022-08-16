import os
import sys
import traceback

path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家'
if path not in sys.path:
    sys.path.append(path)

from script.http_ops.html_service import get_one_page_html
from pyquery import PyQuery as pq
import re
import numpy as np
from script.common_ops.utils import print_time
import time
from script.io_ops.io_service import save_info_to_local, save_info_to_mongodb
from multiprocessing import Process, Pool


class HouseCatching:
    """ 小区信息提取 """
    def __init__(self, url_base=None):
        """ base_url: 链家首页 """
        self.url_base = url_base if url_base else 'https://sh.lianjia.com'
        # 均价5k-8k以上房源 TODO 修改为动态生成
        self.url_selection = 'https://sh.lianjia.com/zufang/rt200600000001l0l1rp6/?showMore=1'
        # self.html_base = get_one_page_html(self.url_selection)  # 筛选页首页html
        # self.doc_base = pq(self.html_base)  # 生成pg包的doc文件
        self.urls_area = None

    def generate_area_urls(self):
        """
        解析主页，生成分区域分页

        :return:
            [{'area': 小区区域, 'url': 分页地址}]
        """
        doc = pq(get_one_page_html(self.url_selection))
        res = []
        for i in doc('ul[data-target=area]')('a').items():
            if i.text() != '不限':
                res.append({'area': i.text(),
                            'url': self.url_base + i.attr('href')})
        self.urls_area = res

        return res

    def get_url_by_area(self, area):
        """ 获取某区域的url """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        return area_url

    def find_page_url(self, url) -> [str]:
        """ 根据区域url获取分页url list """
        doc = pq(get_one_page_html(url))
        res = [url]
        for i in doc('div.content__article > ul[style=display\:hidden] > li > a').items():
            res.append(self.url_base + i.attr('href'))  # 第二页开始的分页
        return res

    def find_room_url(self, url) -> [dict]:
        """ 根据分页地址去解析房间url链接 """
        doc = pq(get_one_page_html(url))
        urls_info = doc('.content__list')('div > a').items()
        res = []
        for i in urls_info:
            room_name = i.attr('title')
            url_ = i.attr('href')
            room_url = self.url_base + url_
            res.append({'room_name': room_name,
                        'url': room_url})
        return res

    def get_room_info_page(self, url_pg) -> [dict]:  # 获取一整个页面的房间信息
        """
        根据分页的页面获取房源信息
            name: 房间名
            area: 面积
            price: 房间价格
            orientation: 朝向
            types: 房间类型
            floor: 房间楼层
            updated_info: 房间维护信息
        """

        doc = pq(get_one_page_html(url_pg))  # doc
        room_info = doc('.content__list--item--main').items() # generator
        res = []
        for i in room_info:
            room_url = self.url_base + i('.twoline').attr('href')
            desc = i('.content__list--item--des').text()
            price_str = i('.content__list--item-price').text()
            updated_info = i('.content__list--item--time.oneline').text()
            desc_vec = desc.replace(' ', '').split('/')
            name = desc_vec[0]
            area_str = desc_vec[1]
            orientation = desc_vec[2]
            types = desc_vec[3]
            floor = desc_vec[4]
            price = float(re.findall('(\d+).* +元/月', price_str)[0])
            area = float(re.findall('(.*)㎡', area_str)[0])
            avg_price = round(price / area, 2)
            sub_area = name.split('-')[1]
            dict_info = {'name': name, 'area_str': area_str, 'price_str': price_str,
                         'area': area, 'price': price, 'avg_price': avg_price,
                         'orientation': orientation, 'types': types, 'floor': floor,
                         'updated_info': updated_info, '子区域': sub_area,
                         'room_url': room_url}
            res.append(dict_info)
        return res

    @staticmethod
    def get_room_info(url_room) -> dict:
        """ 获取单个房源url的信息, 暂时不需要房源额外信息，防止过多调用 """
        print(url_room)
        return dict()

    def get_room_info_by_area(self, area):
        area_url = self.get_url_by_area(area)
        if not area_url:
            return False, '未获取到该区 {} 的链接，支持的区域为 {}'.format(area, [i['area'] for i in self.generate_area_urls()])

        urls_area_pg = self.find_page_url(area_url)
        room_info_total = list()
        print('== 该区域 {} 共有页面 {} 个'.format(area, len(urls_area_pg)))
        n = 0
        for i in urls_area_pg:
            n += 1
            print('== 开始计算第 {} 个页面 =='.format(n))
            room_info_list = self.get_room_info_page(i)
            for room_info in room_info_list:
                room_info['区域'] = area
            room_info_total += room_info_list
        return room_info_total

    @print_time
    def get_room_info_total(self):
        urls_area_list = self.generate_area_urls()
        room_info_total = list()
        for i in urls_area_list:
            room_info_total += self.get_room_info_by_area(i['area'])
            print('== 完成 {} 区域'.format(i['area']))
        return room_info_total

    def main_multiprocess(self, area):
        """ 子进程方法执行全量数据 """
        print('=== 子进程开始执行 {} 区域 ==='.format(area))
        room_info_total = self.get_room_info_by_area(area)
        out_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家\result\20220816'
        file_name = area + '_20220816.xlsx'
        save_info_to_local(room_info_total, out_path, file_name)
        print('== {} 区域存储本地完毕，开始写入数据库 =='.format(area))

        db_config = {'db_name': 'bw_test', 'tb_name': 'room_info_0816'}
        save_info_to_mongodb(room_info_total, db_config)
        print('== {} 区域数据库写入完毕 =='.format(area))
        print('=== 子进程 {} 区域执行完毕 ==='.format(area))


# 测试
if __name__ == '__main__':
    t = HouseCatching()
    ## 区域测试
    # room_info_pudong = t.get_room_info_by_area('浦东')
    # out_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家\result\20220815'
    # flag1, df = save_info_to_local(room_info_pudong, out_path)
    # db_config = {'db_name': 'bw_test', 'tb_name': 'pudong_room_info'}
    # flag2 = save_info_to_mongodb(room_info_pudong, db_config)

    # # 全量测试
    # room_info_total = t.get_room_info_total()
    # out_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家\result\20220815'
    # flag1, df = save_info_to_local(room_info_total, out_path)
    # print('== flag1 ==', flag1)
    # db_config = {'db_name': 'bw_test', 'tb_name': 'room_info'}
    # flag2 = save_info_to_mongodb(room_info_total, db_config)
    # print('== flag2 ==', flag2)
    
    # url_pg = t.find_page_url(t.get_url_by_area('浦东'))[0]

    # multiprocess测试
    pool = Pool()
    area_info = t.generate_area_urls()
    area_list = [i['area'] for i in area_info]
    pool.map(t.main_multiprocess, area_list)
    print('== 全部执行完毕 ==')
