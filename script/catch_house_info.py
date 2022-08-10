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
    def __init__(self, base_url=None):
        """ base_url: 链家首页 """
        self.url_base = base_url if base_url else 'https://sh.lianjia.com'
        self.url_selection = 'https://sh.lianjia.com/xiaoqu/bp6ep10000/'  # 均价6w以上小区 TODO 修改为动态生成
        self.html_base = get_one_page_html(self.url_selection)  # 筛选页首页html
        self.doc_base = pq(self.html_base)  # 生成pg包的doc文件
        self.urls_area = None