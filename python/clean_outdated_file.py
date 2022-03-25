"""
pip install Send2Trash
"""

import os
from send2trash import send2trash
from typing import List
from datetime import datetime

ROOT_PATH = r'.'  # 需要扫描的路径
OUTDATED_DAYS = 60  # 过期天数定义


def collect_files_to_delete(path: str) -> List[str]:
    result = []
    for root, dirs, files in os.walk(path):
        sub_result = []
        # 是否本文件夹下所有都已过期
        all_outdated = True
        for file in files:
            file_path = os.path.join(root, file)
            mod_time = os.path.getmtime(file_path)
            mod_datetime = datetime.utcfromtimestamp(mod_time)
            day = (datetime.now() - mod_datetime).days
            if day >= OUTDATED_DAYS:
                sub_result.append(file_path)
            else:
                all_outdated = False
        if all_outdated:
            # 全部过期，只返回本目录即可
            result.append(root)
        else:
            result.extend(sub_result)
    return result


def delete_files(to_delete_files: List[str]):
    for file_path in to_delete_files:
        send2trash(file_path)
        print(f"已删除至回收站：{file_path}")


def run():
    print("开始统计待删除文件...")
    to_delete_files = collect_files_to_delete(ROOT_PATH)
    inp = input(f"统计完毕，是否显示待删除列表(Size:{len(to_delete_files)})？[Y/N]").upper()
    if inp == 'Y':
        print('\n'.join(to_delete_files))
    inp = input("确定开始删除？[Y/N]").upper()
    if inp == 'Y':
        delete_files(to_delete_files)
        print("删除完毕")


if __name__ == '__main__':
    run()
