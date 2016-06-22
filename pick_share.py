# coding=utf-8

from datetime import datetime, timedelta
import time
import tushare as ts
DELTA_DATE = 5
LIMIT = 9.95


def get_date(day_delta):
    end_date = datetime.now()
    delta = timedelta(days=day_delta)
    end = end_date.strftime('%Y-%m-%d')
    start = (end_date - delta).strftime('%Y-%m-%d')
    return start, end


def decline(dict_data):
    volume = dict_data["volume"]
    open = dict_data["open"]
    close = dict_data["close"]
    p_change = dict_data["p_change"]

    # 不考虑停牌的情况
    if len(volume) < DELTA_DATE:
        return ""

    # case1 最近三天持续缩量下跌，且第一天是下跌，绿柱实体至少一个点，且收盘价持续下降
    if (open[2] - close[2]) / close[3] > 0.01:
        if volume[2] > volume[1] > volume[0]:
            if open[2] > close[2] > close[1] > close[0]:
                return "case1"

    # case2 前三天持续缩量下跌，且第一天是下跌，绿柱实体至少一个点，第四天放量翻红
    if (open[3] - close[3]) / close[4] > 0.01:
        if volume[0] > volume[1] < volume[2] < volume[3]:
            if open[0] < close[0] and open[3] > close[3] > close[2] > close[1]:
                return "case2"

    # 收盘连续两天跌停，加关注
    if p_change[0] < -LIMIT > p_change[1]:
        return "case3"
    return ""


def test(dict_data):
    results = []
    for i in range(len(dict_data) - DELTA_DATE):
        try:
            volume = dict_data["volume"][i:i + 6]
            open = dict_data["open"][i:i + 6]
            close = dict_data["close"][i:i + 6]
            ma5 = dict_data["ma5"][i:i + 6]
            if (open[4] - close[4]) / close[5] > 0.01:
                if volume[0] > volume[1] > volume[2] < volume[3] < volume[4]:
                    if open[4] > close[4] > close[3] > close[2]:
                        if close[0] > open[1] < close[1]:
                            if close[0] > ma5[0]:
                                results.append(i + 1)
        except:
            continue
    return results


if __name__ == '__main__':
    start, end = get_date(DELTA_DATE + 1)
    # print start, end
    with open("shares.txt") as f:
        shares = f.readlines()
    shares = map(str.strip, shares)
    # shares = ["000799"]
    select_shares = {"case1": [], "case2": []}
    t1 = time.time()
    # for share in shares:
    #     data = ts.get_hist_data(share, start, end)
    #     # print data
    #     try:
    #         dict_data = data.to_dict('list')
    #         ret = decline(dict_data)
    #         if ret:
    #             select_shares[ret].append(share)
    #     except AttributeError:
    #         continue
    # print select_shares
    # for key in select_shares:
    #     print len(select_shares[key])
    # t2 = time.time()
    # print "cost {} seconds".format(t2 - t1)

    for share in shares:
        data = ts.get_hist_data(share, '2015-06-20', end)
        try:
            dict_data = data.to_dict('list')
            # print dict_data["ma5"], len(dict_data["volume"])
            results = test(dict_data)
            if results:
                print share, results
        except AttributeError:
            continue

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
