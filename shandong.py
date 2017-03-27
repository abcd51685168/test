# coding=utf-8

import os
import sys
import time
import logging.handlers
import MySQLdb
import argparse
from datetime import datetime
import pandas as pd

log = logging.getLogger()
formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

fh = logging.handlers.WatchedFileHandler('shandonggongan.log')
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

log.setLevel(logging.INFO)

DATA_HEAD = 'num_id,operate_condition,operate_name,operate_result,operate_time,operate_type,organization,' \
            'organization_id,reg_id,terminal_id,user_id,user_name,error_code'
# FREQUENT_LOGIN
FREQUENT_LOGIN_INTERVAL = 60  # seconds
FREQUENT_LOGIN_INTERVAL_COUNTS = 10

# FREQUENT_QUERY
FREQUENT_QUERY_INTERVAL = 10
FREQUENT_QUERY_INTERVAL_COUNTS = 50

# MULTI_REG_QUERY
REG_COUNTS = 2
MULTI_REG_QUERY_TIMES = 20
MULTI_REG_QUERY_INTERVAL = 10 * 60
MULTI_REG_QUERY_INTERVAL_COUNTS = 0  # 只要有一次满足条件即可

# LONGTIME_QUERY
LONGTIME_QUERY_TIMES = 15  # 判断多少次操作之间的时间间隔，其余默认为2，iteration=1
LONGTIME_QUERY_INTERVAL = 60 * 60  # seconds
LONGTIME_QUERY_INTERVAL_COUNTS = 8

# AIMLESS_QUERY
AIMLESS_QUERY_COUNTS = 100  # 同IP24小时内查询不同信息的次数

# OPERATION CODE
LOGIN_OPERATION = 0
QUERY_OPERATION = 1

FACTOR = 1000000


def is_operation_interval_counts(time_list, time_interval, operation_counts, operation_interval=1):
    # 同ip24小时内operation_interval次操作时间间隔小于time_interval的次数  大于operation_counts
    if len(time_list) <= operation_counts:
        return False

    strptime_list = [datetime.strptime(str(t), "%Y%m%d%H%M%S") for t in time_list]

    operation_count = 0
    i = operation_interval
    length_time_list = len(strptime_list)
    while i < length_time_list:
        delta_seconds = (strptime_list[i] - strptime_list[i - operation_interval]).seconds
        if delta_seconds < time_interval:
            operation_count += 1
            i += operation_interval
        else:
            i += 1

    return True if operation_count > operation_counts else False


def frequent_operation(month_data):
    frequent_operation_results = []
    dates = set(map(lambda x: x / FACTOR, month_data['operate_time']))
    month_data["operate_date"] = map(int, month_data["operate_time"] / FACTOR)
    # month_data.to_csv('modified.csv')
    dates = sorted(list(dates))
    for date in dates:
        log.info(date)
        data = month_data.loc[month_data["operate_date"] == date]
        terminal_ids = set(data["terminal_id"])
        for i, terminal_id in enumerate(terminal_ids):
            tmp_behaviour = []
            terminal_data = data.loc[data["terminal_id"] == terminal_id]

            # case: FREQUENT_LOGIN
            frequent_login_data = terminal_data.loc[terminal_data["operate_type"] ==
                                                    LOGIN_OPERATION].sort_values(['operate_time'])
            if is_operation_interval_counts(frequent_login_data['operate_time'], FREQUENT_LOGIN_INTERVAL,
                                            FREQUENT_LOGIN_INTERVAL_COUNTS):
                tmp_behaviour.append('FREQUENT_LOGIN')

            # case: FREQUENT_QUERY
            frequent_query_data = terminal_data.loc[terminal_data["operate_type"] ==
                                                    QUERY_OPERATION].sort_values(['operate_time'])
            if is_operation_interval_counts(frequent_query_data['operate_time'], FREQUENT_QUERY_INTERVAL,
                                            FREQUENT_QUERY_INTERVAL_COUNTS):
                tmp_behaviour.append('FREQUENT_QUERY')

            # # case: MULTI_REG_QUERY
            # multi_reg_query_data = terminal_data.loc[terminal_data["operate_type"] == QUERY_OPERATION]
            # regs = set(multi_reg_query_data["reg_id"])
            # reg_query_counts = 0
            # if len(regs) >= REG_COUNTS:
            #     for _, reg in enumerate(regs):
            #         reg_data = multi_reg_query_data.loc[multi_reg_query_data["reg_id"] == reg]
            #         if is_operation_interval_counts(reg_data['operate_time'], MULTI_REG_QUERY_INTERVAL,
            #                                         MULTI_REG_QUERY_INTERVAL_COUNTS, MULTI_REG_QUERY_TIMES):
            #             reg_query_counts += 1
            #
            # if reg_query_counts >= REG_COUNTS:
            #     tmp_behaviour.append('MULTI_REG_QUERY')

            # case: LONGTIME_QUERY
            longtime_query_data = terminal_data.loc[terminal_data["operate_type"] ==
                                                    QUERY_OPERATION].sort_values(['operate_time'])
            if is_operation_interval_counts(longtime_query_data['operate_time'], LONGTIME_QUERY_INTERVAL,
                                            LONGTIME_QUERY_INTERVAL_COUNTS, LONGTIME_QUERY_TIMES):
                tmp_behaviour.append('LONGTIME_QUERY')

            # case: AIMLESS_QUERY
            aimless_query_data = terminal_data.loc[terminal_data["operate_type"] == QUERY_OPERATION]
            if is_query_larger_than_thresh(aimless_query_data, AIMLESS_QUERY_COUNTS, True):
                tmp_behaviour.append('AIMLESS_QUERY')

            if tmp_behaviour:
                frequent_operation_results.append([date, terminal_id, ','.join(tmp_behaviour)])

    return frequent_operation_results


def is_query_larger_than_thresh(terminal_data, query_counts=0, unique=False):
    if unique:
        query_data = set(terminal_data["operate_condition"])
    else:
        query_data = terminal_data["operate_condition"]

    return True if len(query_data) > query_counts else False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log_file', help="Log file to analyze", type=str, action="store")
    args = parser.parse_args()

    start = time.time()
    data = pd.read_csv(args.log_file, '~', header=None, names=DATA_HEAD.split(','))
    results = frequent_operation(data)
    # log.info(results)
    conn = MySQLdb.connect(host='10.15.42.21', port=3306, user='root', passwd='root', db='sddb')
    cur = conn.cursor()
    sqli = "insert into machine_behaviour(date,ip,behaviour) values(%s,%s,%s)"
    cur.executemany(sqli, results)
    conn.commit()
    cur.close()
    conn.close()
    end = time.time()
    log.info("cost all time: %s seconds." % (end - start))
