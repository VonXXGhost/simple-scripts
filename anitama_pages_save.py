#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import os
import time
import json
import datetime
import re
import csv
from multiprocessing import Pool, Manager


ROOT_URL = 'http://www.anitama.cn'
r_json_url = 'https://app.anitama.net'

# 指定页数获取链接列表
def get_urls(start_page, end_page):
    urls = []
    pages_numbers = list(range(int(start_page), int(end_page) + 1))
    root_url = 'http://www.anitama.cn/channel/all/'
    for page_number in pages_numbers:
        home_url = root_url + str(page_number)
        response = requests.get(home_url)
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('#area-article-channel > div.inner')
        for article in articles[0]('a', recursive=False):
            url = article['href']
            url = ROOT_URL + url
            urls.append(url)
    return urls

# 文章字数计算
def cal_length(soup):
    # response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'lxml')
    content = soup.select('#area-content-article')[0]
    length = 0
    for string in content.strings:
        length += len(string)
    return length

# 解析网页，返回一个字典类型于共享list中或返回字典
def get_info_of(url, m_list):
    data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    data['标题'] = str(soup.select('#area-title-article > h1')[0].string)
    data['副标题'] = str(soup.select('#area-title-article > h2')[0].string)
    data['频道'] = str(soup.select('#area-title-article > p > a')[0].string)
    data['作者'] = str(soup.select('#area-title-article > p > span.author')[0].string)
    json_url = r_json_url + re.search('(?<=www\.anitama\.cn).*$', url).group() + '/stat'
    json_data = requests.get(json_url).text
    data['评论数'] = json.loads(json_data)['data']['comments']
    data['字数'] = str(cal_length(soup))

    timedata = soup.select('#area-title-article > p > span.time')[0].string
    today = datetime.date.today()
    if re.search('\d+月\d+日', timedata) is not None:
        if timedata.find('年') == -1:
            year = today.year
        else:
            m = re.search('(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日', timedata)
            year = m.group('year')
        m = re.search('(?P<month>\d+)月(?P<day>\d+)日', timedata)
        month = m.group('month')
        day = m.group('day')
    else:
        year = today.year
        month = today.month
        if timedata.find('前天') != -1:
            day = (today.today() + datetime.timedelta(days=-2)).day
        elif timedata.find('昨天') != -1:
            day = (today.today() + datetime.timedelta(days=-1)).day
        else:
            day = today.day
    data['日期'] = str(year) + str(month).zfill(2) + str(day).zfill(2)
    data['年'] = year
    data['月'] = month
    data['日'] = day
    data['地址'] = url
    print(data)
    m_list.put(data)

# 保存当前共享list于csv文件中
def save_list(m_list):
    with open('anitama_db.csv', 'a', newline='',encoding='utf-8') as csvfile:
        fieldnames = ['标题', '副标题', '作者', '频道', '评论数', '日期', '字数', '年', '月', '日', '地址']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not os.path.getsize('anitama_db.csv'):  # 判断是否第一次写入
            writer.writeheader()
        while not m_list.empty():
            data = m_list.get()
            writer.writerow(data)



if __name__ == '__main__':
    pool = Pool(4)
    start_page = input('起始页数:')
    end_page = input('结束页数:')
    print('获取网页列表中……')
    urls = get_urls(start_page, end_page)
    manager = Manager()
    m_list = manager.Queue()
    ct = 0
    print('获取相关数据中……')
    for url in urls:
        pool.apply_async(get_info_of, args=(url, m_list))
        ct += 1
        if ct == 100:
            save_list(m_list)
            time.sleep(0.1)
            ct = 0
    pool.close()
    pool.join()
    save_list(m_list)
    print('保存完成')
    os.system('pause')
