'''
功能：根据potplayer标题名创建存档提示文件
'''

from win32gui import *
import time, os
from difflib import SequenceMatcher

titles = []
anime_path = r'D:\Anime'
ex_dirs = []    # 排除目录名
last_title = None


def get_windows_titles(titles):
    def foo(hwnd, mouse):
        if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
            titles.append(GetWindowText(hwnd))

    titles.clear()
    EnumWindows(foo, 0)
    return titles


def get_last_episode(name):
    path = None
    for root, dirs, files in os.walk(anime_path):
        for dir in dirs:
            if dir in ex_dirs:
                dirs.remove(dir)
        for file in files:
            if file[-5:] == '.save' and \
                    SequenceMatcher(None, file[:-5], name).ratio() > 0.9:
                return root, file[:-5]
            elif path is None and \
                    SequenceMatcher(None, file[:-5], name).ratio() > 0.8:
                path = root
    else:
        return path, None


def save_progress(path, name):
    if not path:
        return
    for root, dirs, files in os.walk(path):
        for file in files:
            if file[-5:] == '.save':
                os.remove(os.path.join(root, file))
    filepath = os.path.join(path, ''.join([name, '.save']))
    with open(filepath, 'w') as file:
        pass
    print('已保存')


def exe():
    titles = []
    get_windows_titles(titles)
    Pot_flag = False
    for title in titles:
        if title[-9:] == 'PotPlayer':
            Pot_flag = True
            name = title[:-12]
            global last_title
            if name == last_title:
                continue
            else:
                last_title = name
            path, last_episode = get_last_episode(name)
            if name == last_episode:
                continue
            save_progress(path, name)
    else:
        print('无保存')
        if not Pot_flag:
            time.sleep(90)


if __name__ == '__main__':
    while True:
        print('running')
        try:
            exe()
        except:
            pass
        time.sleep(10)
