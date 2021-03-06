# coding=utf-8

from datetime import datetime, timedelta
import time
import threading
import Queue
import sys
import tushare as ts
DELTA_DATE = 5
LIMIT = 9.95
SHARE_DATE = []
PICK_SHARE = {}

all_shares = ts.get_stock_basics()
dict_shares = all_shares.name.to_dict()
SHARES = dict_shares.keys()
NAMES = dict_shares.values()
lock = threading.Lock()
# SHARES = ["000426"]


def get_start_date(day_delta):
    end_date = datetime.now()
    delta = timedelta(days=day_delta)
    start = (end_date - delta).strftime('%Y-%m-%d')
    return start

start = get_start_date(DELTA_DATE + 1)
# print start


def decline(share):
    data = ts.get_hist_data(share, start)
    try:
        dict_data = data.to_dict('list')
    except AttributeError:
        return
    volume = dict_data["volume"]
    open = dict_data["open"]
    close = dict_data["close"]
    high = dict_data["high"]
    low = dict_data["low"]
    p_change = dict_data["p_change"]
    case = ""
    # 不考虑停牌的情况，只需要最多四天的数据
    if len(volume) < 2:
        return ""

    # # case2 前三天持续缩量下跌，且第一天是下跌，绿柱实体至少一个点，第二天也下跌，第四天放量翻红
    # if (open[3] - close[3]) / close[3] > 0.01:
    #     if volume[3] > volume[2] > volume[1] < volume[0]:
    #         if open[3] > close[3] > close[2] < open[2] and close[1] < open[2]\
    #                 and close[0] > max(open[0], open[1], close[1]):
    #             case = "case2"
    #
    # # case1 最近三天持续缩量下跌，且第一天是下跌，绿柱实体至少一个点，且收盘价持续下降，第三天维持在
    # if (open[2] - close[2]) / close[2] > 0.01:
    #     if volume[2] > volume[1] > volume[0]:
    #         if open[2] > close[2] > close[1] < open[1] and close[0] < open[1]:
    #             case = "case1"

    # # case1 双针探底
    def shizixing(high, low, open, close):
        max0 = max(open, close)
        min0 = min(open, close)
        return True if (min0 - low) / low > 0.01 and (max0 - min0) / max0 < 0.02 else False

    # if volume[1] > volume[0]:
    #     if shizixing(high[0], low[0], open[0], close[0]) and shizixing(high[1], low[1], open[1], close[1]):
    #         case = "case1"

    # 收盘连续两天跌停，加关注
    if p_change[0] < -LIMIT > p_change[1]:
        case = "case3"

    # 一字板开板
    # print p_change[1], high[1], low[1], high[0], low[0]
    if p_change[1] > LIMIT and p_change[0] > LIMIT and high[1] == low[1] and high[0] == low[0]:
        case = "case4"

    lock.acquire()
    if case:
        if case in PICK_SHARE:
            PICK_SHARE[case].append(share)
        else:
            PICK_SHARE[case] = [share]
    lock.release()


# 弧形底
def test(share):
    data = ts.get_hist_data(share, '2016-03-01')
    try:
        dict_data = data.to_dict('list')
        all_data = data.to_dict('dict')
    except AttributeError:
        return

    dates = []
    volume = dict_data["volume"]
    open = dict_data["open"]
    close = dict_data["close"]
    for i in range(len(dict_data["volume"]) - 3):
        try:
            # case2 前三天持续缩量下跌，且第一天是下跌，绿柱实体至少一个点，第二天也下跌，第四天放量翻红
            if (open[i + 3] - close[i + 3]) / close[i + 3] > 0.01:
                if volume[i + 3] > volume[i + 2] > volume[i + 1] < volume[i]:
                    if open[i + 3] > close[i + 3] > close[i + 2] < open[i + 2] and close[i + 1] < open[i + 2] \
                            and close[i] > max(open[i], open[i + 1], close[i + 1]):

                        volume_values = all_data["volume"].values()
                        if volume_values.count(volume[i]) == 1:
                            date = all_data["volume"].keys()[volume_values.index(volume[i])]
                            dates.append(date)
                            continue
                        dates.append(i)
        except:
            continue
    lock.acquire()
    if dates:
        SHARE_DATE.append((share, dates))
        # print share, dates
    lock.release()


# 一字板开板
def test2(share):
    data = ts.get_hist_data(share, '2016-03-01')
    try:
        dict_data = data.to_dict('list')
        all_data = data.to_dict('dict')
    except AttributeError:
        return

    dates = []
    high = dict_data["high"]
    low = dict_data["low"]
    volume = dict_data["volume"]
    p_change = dict_data["p_change"]
    for i in range(len(high) - 1):
        if p_change[i+1] > LIMIT and p_change[i+0] > LIMIT and high[i+1] == low[i+1] and high[i+0] == low[i+0]:
            volume_values = all_data["volume"].values()
            if volume_values.count(volume[i]) == 1:
                date = all_data["volume"].keys()[volume_values.index(volume[i])]
                dates.append(date)
                continue
            dates.append(i)
    lock.acquire()
    if dates:
        SHARE_DATE.append((share, dates))
        # print share, dates
    lock.release()


# 双针探底 缩量
def test3(share):
    data = ts.get_hist_data(share, '2016-06-29', '2016-06-30')
    try:
        dict_data = data.to_dict('list')
        all_data = data.to_dict('dict')
    except AttributeError:
        return

    dates = []
    high = dict_data["high"]
    low = dict_data["low"]
    open = dict_data["open"]
    close = dict_data["close"]
    volume = dict_data["volume"]
    for i in range(len(high) - 2):
        max1 = max(open[i + 1], close[i + 1])
        max0 = max(open[i], close[i])
        min1 = min(open[i + 1], close[i + 1])
        min0 = min(open[i], close[i])
        if high[i + 1] > max1 >= min1 > low[i + 1] and high[i] > max0 >= min0 > low[i]:
            if abs(open[i + 1] - close[i + 1]) / max1 < 0.01 and abs(open[i] - close[i]) / max0 < 0.01:
                if (min1 - low[i + 1]) / low[i + 1] > 0.01 and (min0 - low[i]) / low[i] > 0.01:
                    if volume[i + 2] > volume[i + 1] > volume[i]:

                        volume_values = all_data["volume"].values()
                        if volume_values.count(volume[i]) == 1:
                            date = all_data["volume"].keys()[volume_values.index(volume[i])]
                            dates.append(date)
                            continue
                        dates.append(i)
    lock.acquire()
    if dates:
        SHARE_DATE.append((share, dates))
        # print share, dates
    lock.release()


class WorkManager(object):
    def __init__(self, func, thread_num=24):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.func = func
        self.__init_work_queue()
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue))

    def __init_work_queue(self):
        for share in SHARES:
            # 任务入队，Queue内部实现了同步机制
            self.work_queue.put((self.func, share))

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive():
                item.join()


class Work(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            try:
                do, args = self.work_queue.get(block=False)  # 任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()  # 通知系统任务完成
            except:
                break


if __name__ == '__main__':
    # print start, end

    t1 = time.time()
    work_manager = WorkManager(decline)
    work_manager.wait_allcomplete()
    t2 = time.time()
    print "cost {} seconds".format(t2 - t1)
    print SHARE_DATE
    # print [i[0] for i in SHARE_DATE]
    print PICK_SHARE

#             open   high  close    low     volume  price_change  p_change  \
# date
# 2016-06-21  17.88  17.95  17.81  17.75  158528.73         -0.04     -0.22
# 2016-06-20  17.93  17.93  17.86  17.75   96814.95          0.09      0.51
# 2016-06-17  17.75  17.99  17.79  17.74  174122.33         -0.01     -0.06
# 2016-06-16  17.67  17.93  17.80  17.60  308711.28          0.06      0.34
#
#                ma5    ma10    ma20      v_ma5     v_ma10     v_ma20  turnover
# date
# 2016-06-21  17.804  17.863  17.865  200299.81  207123.38  187827.34      0.08
# 2016-06-20  17.802  17.884  17.847  206140.78  209274.02  185471.22      0.05
# 2016-06-17  17.784  17.901  17.822  246880.96  217379.05  185820.88      0.09
# 2016-06-16  17.826  17.942  17.807  259573.09  218279.24  192595.99      0.17
#
# [4 rows x 14 columns]

#
# Definition: data.to_dict(self, outtype='dict')
# Docstring:
# Convert DataFrame to dictionary.
#
# Parameters
# ----------
# outtype : str {'dict', 'list', 'series', 'records'}
#     Determines the type of the values of the dictionary. The
#     default `dict` is a nested dictionary {column -> {index -> value}}.
#     `list` returns {column -> list(values)}. `series` returns
#     {column -> Series(values)}. `records` returns [{columns -> value}].
#     Abbreviations are allowed.
#
#
# Returns
# -------
# result : dict like {column -> {index -> value}}
