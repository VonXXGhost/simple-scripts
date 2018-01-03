#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime
import sched
import requests
from bs4 import BeautifulSoup
import lxml
import hashlib
import pickle
import os
from win10toast import ToastNotifier

COOKIES = {
    'ask.fm': '',
}


class UpdateNotifier:
    def __init__(self):
        self.LAST_DATA_MD5 = {}
        self.notifier = ToastNotifier()
        self.load_md5_data()

    def load_md5_data(self):
        if not os.path.exists('md5.dat'):
            with open('md5.dat', 'wb') as file:
                pass
        with open('md5.dat', 'rb') as file:
            try:
                self.LAST_DATA_MD5 = pickle.load(file)
            except:
                pass

    def save_md5_data(self):
        with open('md5.dat', 'wb') as file:
            pickle.dump(self.LAST_DATA_MD5, file)

    def md5_check(self, txt, title, func):
        md5 = hashlib.md5()
        md5.update(txt.encode("utf8"))
        if not self.LAST_DATA_MD5.__contains__(title):  # 初始化
            self.LAST_DATA_MD5[title] = md5.hexdigest()
        if md5.hexdigest() != self.LAST_DATA_MD5[title]:
            func(title, txt)
            self.LAST_DATA_MD5[title] = md5.hexdigest()
        self.save_md5_data()
        return

    def notify_directly(self, title, msg):
        self.notifier.show_toast(title, msg, icon_path="notifications.ico")


def txt_to_dic_cookies(txt):
    cookies = {}
    for element in [x.strip() for x in txt.split(';')]:
        if '=' in element:
            cookies[element.split('=')[0]] = element.split('=')[1]
    return cookies


def check_askfm(notifier):
    url = 'https://ask.fm/account/inbox'
    cookies = txt_to_dic_cookies(COOKIES['ask.fm'])
    page = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        first_question = ''.join(soup.find_all('header', class_='streamItem_header')[1].stripped_strings)
    except IndexError:
        return
    notifier.md5_check(first_question, 'ask.fm', notifier.notify_directly)


def perform_task():
    scheduler.enter(60, 0, perform_task)
    check_askfm(notifier)


if __name__ == '__main__':
    notifier = UpdateNotifier()
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(2, 0, perform_task)
    print('tasks run')
    scheduler.run()
