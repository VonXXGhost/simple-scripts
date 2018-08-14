import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import gc


DEBUG = False
LIMITED = False # 账号如果无法查看限制条目，此处填True
ROOT_URL = 'https://bgm.tv'
USER_NAME = ''    # 自己的用户名
# cookies 复制chrome加载首页时的显示文本
COOKIES_TEXT = ''
# 参考格式：'__cfduid=xxx; chii_cookietime=2592000; __utmc=1; prg_display_mode=normal; prg_list_mode=full; chii_searchDateLine=0; chii_auth=xxx;......; chii_sid=xxx; __utma=xxx; __utmt=1; __utmb=xxx'


def txt_to_dic_cookies(txt):
    cookies = {}
    for element in [x.strip() for x in txt.split(';')]:
        if '=' in element:
            cookies[element.split('=')[0]] = element.split('=')[1]
    return cookies


COOKIES = txt_to_dic_cookies(COOKIES_TEXT)


class SubjectScore:

    def __init__(self):
        name = ''
        url = ''
        count = 0
        score = None

    def __str__(self):
        return self.name + ':' + self.score


def get_friends_ids():
    print('获取好友列表中...')
    friend_url = ROOT_URL + '/user/{}/friends'.format(USER_NAME)
    response = requests.get(friend_url, cookies=COOKIES)
    soup = BeautifulSoup(response.text, 'lxml')
    friend_tags = soup.select('#memberUserList')[0].find_all('a', class_='avatar')
    urls = map(lambda x: x['href'][6:], friend_tags)
    return urls


def get_anime_list_from(id, page=1):  # 获取指定id的“看过”动画列表，跳过无评分页
    url = ROOT_URL + '/anime/list/{0}/collect'.format(id)
    response = requests.get(url, params={'orderby': 'rate', 'page': page})
    soup = BeautifulSoup(response.text, 'lxml')
    subject_tags = soup.select('#browserItemList')[0].find_all('a', class_='l')
    subject_paths = list(map(lambda x: x['href'], subject_tags))
    if not subject_paths \
            or not soup.select('.starsinfo'):
        return []
    print('已获取' + id + '的第' + str(page) + '页数据')
    if not DEBUG:
        subject_paths.extend(get_anime_list_from(id, page + 1))
    return subject_paths


def get_all_subjects_friends_score(subjects, friends_score):
    def get_subject_friends_score(subject, friends_score, done_set):
        url = ROOT_URL + subject
        response = requests.get(url, cookies=COOKIES)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        subject_score = SubjectScore()
        try:
            subject_score.name = soup.find('h1', class_='nameSingle').a.string
        except AttributeError:
            if LIMITED:
                print('查询出错，可能为账号权限不足')
                return
            if not is_online():
                raise RuntimeError('cookies失效')
        except Exception as e:
            raise e
        frdScore = soup.find('div', class_='frdScore')
        if not frdScore:
            print(subject_score.name + '无好友评分')
            if not is_online():
                raise RuntimeError('cookies失效')
            return
        print('已获取' + subject_score.name)
        done_set.append(subject)
        subject_score.url = url
        subject_score.score = frdScore.find(class_='num').string
        subject_score.count = frdScore.a.string[:-4]
        friends_score.append(subject_score)

    done_set = []
    count = 1
    max = len(subjects)
    for index, subject in enumerate(subjects):
        print('获取' + subject + '({} of {})'.format(str(index + 1), max))
        try:
            get_subject_friends_score(subject, friends_score, done_set)
        except:
            save_done_set(done_set)
            return
        count += 1
        if count > 100:  # 防止内存溢出
            count = 1
            save_done_set(done_set)
            save_as_csv(friends_score)
            del friends_score
            friends_score = []
            gc.collect()
    return


def save_as_csv(friends_score):
    friends_score.sort(key=lambda x: float(x.score), reverse=True)
    first = True
    if os.path.exists('friends_rank.csv'):
        first = False
    with open('friends_rank.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        if first:
            writer.writerow(['名字', '评分', '人数', '地址'])
        for score in friends_score:
            writer.writerow([score.name, score.score, score.count, score.url])
    print('已保存csv')


def save_anime_set(anime_set):
    with open('anime_set.txt', 'w', encoding='utf-8') as file:
        file.writelines(anime_set)
    print('已保存条目集')


def save_done_set(done_set):
    with open('done_set.txt', 'a', encoding='utf-8') as file:
        file.writelines(done_set)
    done_set = []
    print('已保存进度')


def read_anime_set():
    with open('anime_set.txt', 'r', encoding='utf-8') as file:
        s = file.readlines()
    return re.findall('/subject/\d+', s[0])


def read_done_set():
    if not os.path.exists('done_set.txt'):
        return []
    with open('done_set.txt', 'r', encoding='utf-8') as file:
        s = file.readlines()
    return re.findall('/subject/\d+', s[0])


def is_online():
    response = requests.get(ROOT_URL, cookies=COOKIES)
    if response.text.find(USER_NAME) > -1:
        return True
    else:
        return False


if not is_online():
    print('cookies失效，请重新设置')
    os.system('pause')
    exit(0)

# 获取所有好友评分过的条目，仅推荐在第一次运行时执行
friends = get_friends_ids()
anime_set = []
for friend in friends:
    anime_set.extend(get_anime_list_from(friend))
anime_set = set(anime_set)
save_anime_set(anime_set)
# 已存有条目文件时可将上述6行注释掉避免重复操作

anime_set = read_anime_set()
done_set = read_done_set()
anime_set = list(set(anime_set) - set(done_set))
friends_score = []
get_all_subjects_friends_score(anime_set, friends_score)
save_as_csv(friends_score)
