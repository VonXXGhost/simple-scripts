from tweepy import OAuthHandler, API, Cursor, TweepError
import socks
import socket
import os
import webbrowser
import sys
import pickle

# socks5代理设置
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

# 验证连接
consumer_key = "sEQ69q6kXjNw79D2WekrtqdSF"
consumer_secret = "MxpbymrjkKMxqpfKMeAbatHSYf0UAXT9CvX92eGuuB0MSNhUMb"
auth = OAuthHandler(consumer_key, consumer_secret)


# 获取指定用户关注列表
def get_all_friends(username):
    ids = []
    for page in Cursor(api.friends_ids, screen_name=username).pages():
        ids.extend(page)
    return ids


# 对比列表获取相同关注
def get_common_friends(users):
    def _get_common_friends(ids1, ids2):
        set1 = set(ids1)
        set2 = set(ids2)
        com_users = set1 & set2
        return list(com_users)

    c_ids = []
    for username in users:
        ids = get_all_friends(username)
        if c_ids:
            c_ids = _get_common_friends(c_ids, ids)
        else:
            c_ids = ids
    return c_ids


# 获取名字
def get_users(ids):
    return api.lookup_users(user_ids=ids)


# 输出列表
def output_users(ids, save_flag, users):
    def print_users(ids):
        print('对比结果如下:')
        users = get_users(ids)
        ct = 0
        text = ''
        for user in users:
            ct = ct + 1
            s = ''.join([str(ct), '.', user.name, ' @', user.screen_name])
            print(s)
            text += s + '\n'
        return text

    def save_file(text):
        with open('result.txt', 'a+', encoding='utf-8') as file:
            head = '、'.join(users) + '的对比结果：\n'
            file.write(head)
            file.write(text)
            file.write('\n')

    text = print_users(ids)
    if save_flag:
        save_file(text)


def login():
    print('网络连接中……')
    try:
        redirect_url = auth.get_authorization_url()
    except TweepError:
        print('获取信息失败，请检查网络连接')
        os.system('pause')
        sys.exit(0)
    webbrowser.open(redirect_url)
    verifier = input('登陆并输入验证码:')
    try:
        token = auth.get_access_token(verifier)
        with open('token', 'wb') as file:
            pickle.dump(token, file)
    except TweepError:
        print('验证错误，登陆失败.')
        os.system('pause')
        sys.exit(0)
    print('登陆成功')
    return token


if __name__ == '__main__':

    # 验证连接
    if os.path.exists('token'):
        with open('token', 'rb') as file:
            token = pickle.load(file)
            print('检测到已登录，若无法正常运行请删除同目录下的token文件')
    else:
        token = login()
    auth.set_access_token(token[0], token[1])
    api = API(auth)

    print('输入两个或更多需要查找对比的账号ID，以半角空格隔开（@XXX中的XXX）：')
    txt = input().strip()
    users = txt.split(' ')
    choice = input('是否保存为文件？（Y/N）：').strip()
    save_flag = False
    if choice == 'Y' or choice == 'y':
        save_flag = True
    c_ids = get_common_friends(users)
    output_users(c_ids, save_flag, users)
    os.system('pause')
