from tweepy import OAuthHandler, API, Cursor
from typing import List, Tuple, Iterable, Set
import time
import socks
import socket
import re

import csv
from openpyxl import load_workbook
from openpyxl.worksheet._read_only import ReadOnlyCell

# socks5代理设置
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

# 验证连接
consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = API(auth,
          wait_on_rate_limit=True,
          wait_on_rate_limit_notify=True)


def all_friends(username: str) -> Iterable[Tuple[str, str, str]]:
    for page in Cursor(api.friends, screen_name=username).pages():
        for user in page:
            yield (user.name, user.screen_name, user.id_str)


def save_to_csv(users: Iterable[Tuple[str, str, str]], filepath: str = None):
    if filepath is None:
        filepath = time.strftime('%Y-%m-%d-%H-%M-%S.csv', time.localtime())
    with open(filepath, 'w', newline='', encoding='utf8') as file:
        fields = ['name', 'screen_name', 'id']
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(users)
    print('文件已保存')


def save_friends(username: str, filepath: str = None):
    save_to_csv(all_friends(username), filepath)


def lookup_users(usernames: Iterable[str], save_file: str = None) -> Iterable[Tuple[str, str, str]]:
    def _lookup(l_names: List[str]) -> Iterable[Tuple[str, str, str]]:
        users = api.lookup_users(screen_names=l_names)
        for user in users:
            yield (user.name, user.screen_name, user.id_str)

    def save_usernames(l_names: List[str], filename: str):
        with open(filename, 'a', encoding='utf8') as f:
            f.writelines([x+'\n' for x in l_names])

    l_names = []
    for username in usernames:
        if len(l_names) >= 100:
            if save_file:
                save_usernames(l_names, save_file)
            yield from _lookup(l_names)
            l_names.clear()
        l_names.append(username)
    else:
        if l_names:
            if save_file:
                save_usernames(l_names, save_file)
            yield from _lookup(l_names)


def save_from_xlsx(xlsx_path: str, dest_filepath: str = None):
    def _contain_username_and_not_strike(cell: ReadOnlyCell) -> bool:
        if cell.font and cell.value:
            return not cell.font.strikethrough and 'twitter.com' in cell.value
        return False

    def _get_username(cell: ReadOnlyCell) -> str:
        reg = re.compile('twitter.com/([a-zA-Z\d_]+)')
        return reg.search(cell.value).group(1)

    def _valid_usernames_from_xlsx(xlsx_path: str) -> Iterable[str]:
        sheets = load_workbook(filename=xlsx_path, read_only=True)
        for sheet in sheets.worksheets:
            for row in sheet:
                for cell in row:
                    if _contain_username_and_not_strike(cell):
                        yield _get_username(cell)

    save_to_csv(lookup_users(_valid_usernames_from_xlsx(xlsx_path), 'usernames.txt'), dest_filepath)


def check_invalid_username(all_names: Iterable[str], valid_names: Iterable[str]) -> Set[str]:
    va = set(valid_names)
    all = set(all_names)
    return all.difference(va)


def check_username_of(f_csv: str, f_all: str):
    def _get_csv_username(f_csv: str) -> Iterable[str]:
        with open(f_csv, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row['screen_name']

    def _get_all_username(f_all: str) -> Iterable[str]:
        with open(f_all, 'r', encoding='utf8') as f:
            for line in f.readlines():
                yield line.strip()

    diff = check_invalid_username(_get_all_username(f_all), _get_csv_username(f_csv))
    if diff:
        print('无效用户名：')
        for d in diff:
            print(d)
    else:
        print('不存在无效用户名')

