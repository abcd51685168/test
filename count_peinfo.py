#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import codecs
import MySQLdb
from time import time
from math import log
import csv
import sys
from pefile import PEFormatError, PE
import shutil
from ctypes import cdll, string_at
from collections import Counter


so_path = "/polyhawk/lib/libmcla.so"
cfg_path = "/polydata/content/mcla/mcla.cfg"
libpefile = cdll.LoadLibrary(so_path)


MCLA_DIR = "/polydata/content/mcla/"
CSV_PATH = os.path.join(MCLA_DIR, "data")

SECTION_NAMES = [u'RT_CODE', u'RT_DATA', u'.nep', u'.rsrc', u'.bss', u'consent', u'RT_BSS', u'.reloc', u'PAGELK', u'.orpc', u'.idata', u'.rdata', u'FE_TEXT', u'.data', u'.pdata', u'.text', u'.tls', u'other']
SECTION_NAMES = map(lambda x: x.strip('.').lower(), SECTION_NAMES)
CATEGORIES = [u'White', u'Packed', u'Trojan', u'Ransom', u'Downloader', u'AdWare', u'PSW', u'low', u'GameThief', u'Virus', u'Backdoor', u'Spy', u'Clicker', u'Net-Worm', u'Dropper', u'Porn-Dialer', u'Worm', u'Banker', u'Hoax', u'WebToolbar', u'Rootkit', u'Email-Worm', u'Constructor', u'HackTool', u'Notifier', u'FakeAV', u'Exploit', u'P2P-Worm', u'Proxy', u'FraudTool', u'PSWTool', u'RiskTool', u'Dialer', u'Porn-Downloader', u'Monitor', u'VirTool', u'IM-Worm', u'RemoteAdmin', u'Porn-Tool', u'Mailfinder', u'IM-Flooder', u'Trojan-Downloader', u'Trojan-FakeAV', u'IM', u'NetTool', u'DDoS', u'Server-Proxy', u'Trojan-Spy', u'Email-Flooder', u'Client-SMTP', u'Client-IRC', u'Server-Web', u'SMS-Flooder', u'Flooder', u'Type_Win32', u'Server-FTP', u'Tool', u'IRC-Worm', u'Garbage', u'AVTool', u'DoS', u'SMS', u'CrackTool', u'AdTool']


def norm_str(s):
    if s:
        return s.strip().strip('.').strip("\x00").lower()
    else:
        return s


# {"GetCurrentProcess": {"white": 10, "black": 5, "P2P-Worm": 3, "Backdoor": 6}}
# {"xxx.dll": {"white": 10, "black": 5, "P2P-Worm": 3, "Backdoor": 6}}
def count_peinfo(table, category=None):
    sql_content = 'SELECT Sha256, File_detail->\'$." PE imports"\', File_detail->\'$." PE sections"\', Category FROM {}'
    if category:
        sql_content += ' WHERE Category="{}";'
    else:
        sql_content += ';'

    cur.execute(sql_content.format(table, category))

    results = cur.fetchall()
    sample_count = 0
    dict_dll = {}
    dict_api = {}
    for result in results:
        if result[1]:
            r1 = json.loads(result[1])
            if r1.values()[0][0].find(',') != -1 or r1.values()[-1][0].find(',') != -1:
                continue

            # virus_name = result[3]
            virus_name = "white" if table == "lvmeng_dll_exe_5m_white" else "black"
            sample_count += 1
            if sample_count > 1500:
                break

            for tmp_dll, apis in r1.iteritems():   # type of apis is list
                for api in apis:
                    api = norm_str(api)
                    if api in dict_api:
                        dict_api[api][virus_name] += 1
                    else:
                        dict_api[api] = {virus_name: 1}

                dll = norm_str(tmp_dll)
                if dll in dict_dll:
                    dict_dll[dll][virus_name] += 1
                else:
                    dict_dll[dll] = {virus_name: 1}

    print "table: %s, all samples: %s, valid samples: %s, dlls: %s, apis: %s"\
          % (table, len(results), sample_count, len(dict_dll), len(dict_api))
    # sorted_dll = sorted(counter_dll.iteritems(), key=lambda d: d[1], reverse=True)
    # sorted_api = sorted(counter_api.iteritems(), key=lambda d: d[1], reverse=True)
    return dict_dll, dict_api


def combine(dict_white, dict_black):
    for i in dict_white:
        if i in dict_black:
            dict_black[i].update(dict_white[i])
        else:
            dict_black[i] = dict_white[i]
    return dict_black


def calc_info(dict_data):
    result = []
    for key, value in dict_data.iteritems():
        args = [key, value.get("white", 0), value.get("black", 0)]
        ce = calc_ce(*args)
        args.append(ce)
        result.append(args)
    return result


def calc_ce(*args):
    pci = 1.0 / (len(args) - 1)
    count_all = sum(args[1:])
    ce = 0.0
    for i in args[1:]:
        pciw = i * 1.0 / count_all
        if abs(pciw - 0.0) < 0.0001:
            pciw = 0.0001
        ce += pciw * log((pciw / pci), 2)
    return ce


def insert_db(table, dict_data):
    sql_content = "INSERT INTO " + table + " VALUES(%s, %s, %s, %s);"
    # sql_content = "INSERT INTO " + table + "(" + column1 + ", white, black, ce)" + " VALUES(%s, %s, %s, %s);"
    try:
        cur.executemany(sql_content, calc_info(dict_data))
    except:
        print dict_data
    conn.commit()


def select(data, thresh, ratio):
    result = []
    for i in data:
        if i[1] + i[2] > thresh and i[3] > ratio:
            result.append(i[0])
    return result


def count_sample_info(table, category=None):
    sql_content = 'SELECT Sha256, File_detail->\'$." PE imports"\', File_detail->\'$." PE sections"\', Category FROM {}'
    if category:
        sql_content += ' WHERE Category="{}";'
    else:
        sql_content += ';'
    cur.execute(sql_content.format(table, category))
    results = cur.fetchall()
    sample_count = 0
    rows = []
    for result in results:
        row = [0] * (len(DLL_API_FEATURES) + len(SECTION_NAMES))
        if result[1] and result[2]:
            r1 = json.loads(result[1])
            if r1.values()[0][0].find(',') != -1 or r1.values()[-1][0].find(',') != -1:
                continue

            if table == "lvmeng_dll_exe_5m_white":
                row[0] = 0
            else:
                row[0] = CATEGORIES.index(category)

            sample_count += 1
            if sample_count > 1500:
                break

            for tmp_dll, apis in r1.iteritems():   # type of apis is list
                for api in apis:
                    api = norm_str(api)
                    if api in DLL_API_FEATURES:
                        index = DLL_API_FEATURES.index(api)
                        row[index] = 1

                dll = norm_str(tmp_dll)
                if dll in DLL_API_FEATURES:
                    index = DLL_API_FEATURES.index(dll)
                    row[index] = 1

            r2 = json.loads(result[2])
            for item in r2:
                se = norm_str(item["Name"])
                if se in SECTION_NAMES:
                    index = SECTION_NAMES.index(se)
                    row[index + len(DLL_API_FEATURES)] = 1
                else:
                    row[-1] += 1

            rows.append(row)
    return rows


def write_csv(rows, csv_file):
    csvfile = file(csv_file, 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(DLL_API_FEATURES + SECTION_NAMES)
    writer.writerows(rows)
    csvfile.close()


def write_csv_ex(rows, csv_file):
    csvfile = file(csv_file, 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(DLL_API_FEATURES)
    rows = map(lambda x: x[:len(DLL_API_FEATURES)], rows)
    writer.writerows(rows)
    csvfile.close()


def count_category(table="VT_detail"):
    sql_content = 'SELECT DISTINCT Category FROM {}'.format(table)
    cur.execute(sql_content)
    return [category[0] for category in cur.fetchall() if category[0] not in ['()', None]]


def train():
    count = 0
    for root, dirs, files in os.walk(CSV_PATH):
        for name in files:
            if name.find('csv') >= 0 and name.find('norm') < 0:
                ori_data_path = os.path.join(CSV_PATH, name)
                norm_data_path = ori_data_path.replace('.csv', '_norm.csv')
                svm_data_path = norm_data_path.replace('csv', 'svm')

                para_path = os.path.join(MCLA_DIR, name).replace('.csv', '_norm.para')
                svm_model_path = para_path.replace('para', 'model')

                normalizer_path = os.path.join(MCLA_DIR, "csv_normalizer.py")
                cmd = "python %s %s %s %s > /dev/null" % (normalizer_path, ori_data_path, norm_data_path, para_path)
                os.system(cmd)
                cmd = "csv_to_svm %s %s > /dev/null" % (norm_data_path, svm_data_path)
                os.system(cmd)
                cmd = "svm-train -t 0 %s %s > /dev/null" % (svm_data_path, svm_model_path)
                os.system(cmd)
                # cmd = "svm-train -t 0 -v 5 %s" % svm_data_path
                # os.system(cmd)

                count += 1


def get_pe_info(target):
    row = [0] * (len(DLL_API_FEATURES) + len(SECTION_NAMES))
    try:
        pe = PE(target)
    except PEFormatError:
        # log.exception("%s, not valid PE File" % target)
        return None

    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll = norm_str(entry.dll)
            if dll in DLL_API_FEATURES:
                index = DLL_API_FEATURES.index(dll)
                row[index] = 1

            for imp in entry.imports:
                api = norm_str(imp.name)
                if api in DLL_API_FEATURES:
                    index = DLL_API_FEATURES.index(api)
                    row[index] = 1
    else:
        return None

    for section in pe.sections:
        se = norm_str(section.Name)
        if se in SECTION_NAMES:
            index = SECTION_NAMES.index(se)
            row[index + len(DLL_API_FEATURES)] = 1
        else:
            row[-1] += 1

    # change list to string
    return ",".join(map(str, row))


def test_mcla():
    csv_count = libpefile.pecker_gmcla_group_model_num()
    print "csv count: ", csv_count
    dir_paths = ["/root/virus", "/polydata/samples/lvmeng_white"]
    result = []
    for dir_path in dir_paths:
        count_mcla = Counter()
        for target in os.listdir(dir_path):
            target = os.path.join(dir_path, target)
            count = mcla_match_count(target)
            count_mcla.update([count])
        result.append(dict(count_mcla))
    return dict(zip(["worm", "white"], result))


def mcla_match(target):
    pe_info = get_pe_info(target)
    if not pe_info:
        return "no_pe_info"

    p_category = libpefile.pecker_gmcla_group_predict_vec_data(pe_info, len(DLL_API_FEATURES) + len(SECTION_NAMES))
    if p_category:
        return string_at(p_category)
    else:
        return None


def mcla_match_count(target):
    pe_info = get_pe_info(target)
    if not pe_info:
        return -1
    category_count = libpefile.pecker_gmcla_group_checkall_vec_data(pe_info, len(DLL_API_FEATURES) + len(SECTION_NAMES))
    return category_count


def mcla_check(path):
    results = Counter()
    if os.path.isfile(path):
        results.update([mcla_match(path)])
    elif os.path.isdir(path):
        for target in os.listdir(path):
            target = os.path.join(path, target)
            results.update([mcla_match(target)])
    return results


def mcla_check_count(path):
    results = Counter()
    if os.path.isfile(path):
        results.update([mcla_match_count(path)])
    elif os.path.isdir(path):
        for target in os.listdir(path):
            target = os.path.join(path, target)
            results.update([mcla_match_count(target)])
    return results


def mcla_match_count(target):
    pe_info = get_pe_info(target)
    if not pe_info:
        return -1
    category_count = libpefile.pecker_gmcla_group_checkall_vec_data(pe_info, len(DLL_API_FEATURES) + len(SECTION_NAMES))
    return category_count


if __name__ == "__main__":
    conn = MySQLdb.connect(db="malware_info", user="root", passwd="polydata", host="192.168.25.62", port=3306, charset="utf8")
    cur = conn.cursor()
    time1 = time()
    dict_white_dll, dict_white_api = count_peinfo("lvmeng_dll_exe_5m_white")
    time2 = time()
    dict_black_dll, dict_black_api = count_peinfo("VT_detail")
    time3 = time()

    dict_dll = combine(dict_white_dll, dict_black_dll)
    dict_api = combine(dict_white_api, dict_black_api)
    dll_info = calc_info(dict_dll)
    api_info = calc_info(dict_api)
    # insert_db("dlls_copy", dict_dll)
    # insert_db("apis_copy", dict_api)

    dll_feature = select(dll_info, 20, 0.5)
    api_feature = select(api_info, 35, 0.5)

    api_threshes = range(5, 91, 5)
    api_ratios = map(lambda x: x / 100.0, range(50, 61, 1))
    para_apis = [(i, j) for i in api_threshes for j in api_ratios]
    para_apis.reverse()
    para_apis = [(35, 0.5)]
    dict_results = {}
    for i, para in enumerate(para_apis, 1):
        api_feature = select(api_info, para[0], para[1])

        DLL_API_FEATURES = [u"lable"] + dll_feature + api_feature
        features = dll_feature + api_feature
        print features
        # features = dll_feature + api_feature + SECTION_NAMES

        # CATEGORIES = ["White"] + count_category()
        white = count_sample_info("lvmeng_dll_exe_5m_white")
        shutil.rmtree(CSV_PATH, True)
        os.makedirs(CSV_PATH)
        for c in CATEGORIES[1:]:
            black = count_sample_info("VT_detail", c)
            if len(black) > len(white) / 10:
                category_csv_path = os.path.join(CSV_PATH, c + ".csv")
                write_csv_ex(white + black, category_csv_path)

        train()
        # print "cost time --> white_detail: %.2fs, VT_detail: %.2fs" % (time2 - time1, time3 - time2)
        # print len(DLL_API_FEATURES), DLL_API_FEATURES
        print ("api_thresh:%s, api_ratio:%s" % para)

        ret = libpefile.pecker_gmcla_init(cfg_path, len(features))
        if not ret:
            pass
            # print("load %s successfully" % so_path)
        else:
            print("load %s failed, ret: %s" % (so_path, ret))
            sys.exit(1)
        dict_mcla = test_mcla()
        dict_mcla.update(dict(zip(["api_thresh", "api_ratio"], para)))
        dict_mcla.update({"feature_num": len(features), "features": features})
        dict_results[i] = dict_mcla
        libpefile.pecker_gmcla_free()

        with open("/root/mcla0510/{}.txt".format(i), 'w') as f:
            json.dump(dict_results, f)

    cur.close()
    conn.close()
    time4 = time()
    print "total cost time %.2fs" % (time4 - time1)
