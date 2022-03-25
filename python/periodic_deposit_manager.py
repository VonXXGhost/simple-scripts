import csv
import json
from datetime import datetime
from typing import List, Dict

# python-dateutil
from dateutil.relativedelta import *

INFO_CSV_PATH = r'..\resources\periodic_deposit_info.csv'
FILE_ENCODING = 'GBK'

# 是否保存输出到文件
SAVE_RESULT = False
SAVE_RESULT_PATH = r'.\periodic_deposit_info_calc.csv'

# 过滤条件，保持为空即统计全部，填入条件即只统计符合条件的数据
PLATFORM_FILTER = []
SELLER_FILTER = []


class PeriodicInfo:
    # 下一次释放时间
    next_release_date: datetime = None

    def __init__(self, line: dict):
        self.platform: str = line['平台']
        self.seller: str = line['销售方']
        self.product: str = line['产品']
        self.amount: float = float(line['金额'])
        self.start_date: datetime = datetime.strptime(line['起始日期'], '%Y/%m/%d')
        self.period: str = line['周期'].lower()
        self._calc_next_release_date()

    def __str__(self):
        return f"platform: {self.platform}, seller: {self.seller}, product: {self.product}," \
               f" amount: {self.amount}, start_data: {self.start_date}, period: {self.period}," \
               f" next_release_date: {self.next_release_date}"

    def _calc_next_release_date(self):
        self.next_release_date = self.start_date + self._period_time_delta()
        while self.next_release_date < datetime.now():
            self.next_release_date = self.next_release_date + self._period_time_delta()

    def _period_time_delta(self) -> relativedelta:
        num = int(self.period[:-1])
        if self.period.endswith('d'):
            return relativedelta(days=num)
        elif self.period.endswith('m'):
            return relativedelta(months=num)
        elif self.period.endswith('y'):
            return relativedelta(years=num)


def load_base_info() -> List[PeriodicInfo]:
    result = []
    with open(INFO_CSV_PATH, 'r', encoding=FILE_ENCODING) as file:
        csv_reader = csv.DictReader(file)
        for line in csv_reader:
            result.append(PeriodicInfo(line))
    return result


def total_amount_by_month(infos: List[PeriodicInfo]) -> Dict[str, float]:
    """
    根据下一次释放时间，按月统计总金额
    :return:
    """
    result = {}
    for info in infos:
        month = info.next_release_date.strftime('%Y/%m')
        result.setdefault(month, 0)
        result[month] += info.amount
    return dict(sorted(result.items()))


def filtrate_infos(infos: List[PeriodicInfo]) -> List[PeriodicInfo]:
    """
    根据条件过滤出要统计的数据
    :param infos:
    :return:
    """
    result = []
    for info in infos:
        if len(PLATFORM_FILTER) > 0 and info.platform not in PLATFORM_FILTER:
            continue
        if len(SELLER_FILTER) > 0 and info.seller not in SELLER_FILTER:
            continue
        result.append(info)
    return result


def save_result(infos: List[PeriodicInfo]):
    with open(SAVE_RESULT_PATH, 'w', encoding=FILE_ENCODING, newline='') as file:
        writer = csv.DictWriter(file, vars(infos[0]))
        writer.writeheader()
        for info in infos:
            writer.writerow(vars(info))


if __name__ == '__main__':
    base_infos = load_base_info()
    base_infos = filtrate_infos(base_infos)
    month_amounts = total_amount_by_month(base_infos)
    print('总览：')
    print(json.dumps(month_amounts, indent=2))
    if SAVE_RESULT:
        save_result(base_infos)
