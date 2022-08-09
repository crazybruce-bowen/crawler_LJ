# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 09:50:19 2022

@author: 47176
摘抄自: https://www.jb51.net/article/200465.htm
"""
import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import pymongo
from config import *
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL)  # 申明连接对象
db = client[MONGO_DB]  # 申明数据库

def get_one_page_html(url):  # 获取网站每一页的html
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


def get_room_url(html):  # 获取当前页面上所有room_info的url
  doc = pq(html)
  room_urls = doc('.r_lbx .r_lbx_cen .r_lbx_cena a').items()
  return room_urls


def parser_room_page(room_html):
  soup = BeautifulSoup(room_html, 'lxml')
  title = soup.h1.text
  price = soup.find('div', {'class': 'room-price-sale'}).text[:-3]
  x = soup.find_all('div', {'class': 'room-list'})
  area = x[0].text[7:-11]  # 面积
  bianhao = x[1].text[4:]
  house_type = x[2].text.strip()[3:7]  # 户型
  floor = x[5].text[4:-2]  # 楼层
  location1 = x[6].find_all('a')[0].text  # 分区
  location2 = x[6].find_all('a')[1].text
  location3 = x[6].find_all('a')[2].text
  subway = x[7].text[4:]
  addition = soup.find_all('div', {'class': 'room-title'})[0].text
  yield {
    'title': title,
    'price': price,
    'area': area,
    'bianhao': bianhao,
    'house_type': house_type,
    'floor': floor,
    'location1': location1,
    'location2': location2,
    'location3': location3,
    'subway': subway,
    'addition': addition
  }


def save_to_mongo(result):
  if db[MONGO_TABLE].insert_one(result):
    print('存储到mongodb成功', result)
    return True
  return False


def main(page):
  url = 'http://www.xxxxx.com/room/sz?page=' + str(page)  # url就不粘啦，嘻嘻
  html = get_one_page_html(url)
  room_urls = get_room_url(html)
  for room_url in room_urls:
    room_url_href = room_url.attr('href')
    room_html = get_one_page_html(room_url_href)
    if room_html is None:  # 非常重要，否则room_html为None时会报错
      pass
    else:
      results = parser_room_page(room_html)
      for result in results:
        save_to_mongo(result)

if __name__ == '__main__':
  pool = Pool() # 使用多进程提高爬取效率
  pool.map(main, [i for i in range(1, 258)])