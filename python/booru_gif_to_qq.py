# -*- coding: utf-8 -*-

'''A plugin of qqbot[https://github.com/pandolia/qqbot]
'''

import re
import logging
import requests
import os
import pickle


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(process)d:%(thread)d [%(levelname)s]: %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join('.', 'log', 'booru_qq_bot.log'),
                    filemode='a')

PRE_BOORU_ABOUT_MSG = {}
BOT_API_URL_TEMPLATE = 'https://sakugabot.pw/api/posts/{0}'

if not os.path.exists('bot_auto_settings'):
    with open('bot_auto_settings', 'wb') as f:
        pickle.dump({}, f)
s_file = open('bot_auto_settings', 'rb')
AUTO_SETTINGS = pickle.load(s_file)
s_file.close()


def send_message(message, bot, contact):
    bot.SendTo(contact, message)


def send_gif_url(gif_url, id, bot, contact):
    send_message(''.join([id, ':\n', gif_url]), bot, contact)


def send_help(bot, contact):
    help_message = '使用指南：\n在群里at本账号同时附上sakugabooru的稿件链接，本账号将搜索是否存在微博gif数据， ' \
                   '如果存在则发送gif地址到群里（因为协议不支持发图），否则报错。\n如果同一条信息里没有链接， ' \
                   '则会使用聊天记录中最近的一条booru链接（小概率可能会找错，尽量使用第一种方法）。\n ' \
                   'at时附上"-auto"可开启自动检测链接模式，若需取消附上"-no-auto"即可，默认开启。' \
                   '自动模式下不会发送不存在的条目信息和错误信息，同时at模式仍然有效。\n' \
                   'at本账号同时带上"-h"或"-help"可再次获取本帮助。'
    bot.SendTo(contact, help_message)


def message_process(bot, contact, content, auto_model=False):
    group_name = contact.name
    logging.info(''.join(['处理信息：', group_name, ':', content]))
    id = re.findall(r'(?<=post/show/)(\d+)', content)[0]
    if id:
        try:
            response = requests.get(BOT_API_URL_TEMPLATE.format(id))
        except e:
            logging.error(e)
            send_message("服务器出错，请稍后再试", bot, contact)
        if response.status_code == 404 and not auto_model:
            logging.error('404 of ' + id)
            send_message("服务器中暂无此条目数据", bot, contact)
        elif response.status_code == 200:
            try:
                gif_url = response.json()['weibo']['img_url']
                if gif_url is None:
                    raise RuntimeError('no img url')
                send_gif_url(gif_url, id, bot, contact)
            except:
                logging.error(id + ' 暂未有微博数据')
                if not auto_model:
                    send_message("服务器中暂无此条目数据", bot, contact)
        elif not auto_model:
            logging.error(response.text)
            send_message("服务器出错，请稍后再试", bot, contact)


def blank_at_process(bot, contact):
    content = PRE_BOORU_ABOUT_MSG.get(contact.name, None)
    logging.info('处理空at from ' + contact.name)
    if content:
        message_process(bot, contact, content)
    else:
        send_message("没有找到booru网址", bot, contact)


def auto_set_process(bot, contact, undo=False):
    if undo:
        AUTO_SETTINGS[contact.name] = False
        send_message("已取消自动模式", bot, contact)
        logging.info("已取消自动模式-" + contact.name)
    else:
        AUTO_SETTINGS[contact.name] = True
        send_message("自动检测设置成功", bot, contact)
        logging.info("自动检测设置成功-" + contact.name)
    with open('bot_auto_settings', 'wb') as f:
        pickle.dump(AUTO_SETTINGS, f)


def onQQMessage(bot, contact, member, content):
    if 'sakugabooru.com/post/show/' in content:
        PRE_BOORU_ABOUT_MSG[contact.name] = content
        if AUTO_SETTINGS.get(contact.name, True) and '@ME' not in content:
            message_process(bot, contact, content, auto_model=True)
    if '@ME' in content:
        if '-h' in content or '-help' in content:
            send_help(bot, contact)
        elif 'sakugabooru.com/post/show/' in content:
            message_process(bot, contact, content)
        elif '-no-auto' in content:
            auto_set_process(bot, contact, undo=True)
        elif '-auto' in content:
            auto_set_process(bot, contact)
        else:
            blank_at_process(bot, contact)
