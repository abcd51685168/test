import os
import json
import codecs
import MySQLdb
from time import time
from math import log
import csv


DLL_API_FEATURES = ["lable", " slc.dll", " api-ms-win-core-errorhandling-l1-1-0.dll", " api-ms-win-core-libraryloader-l1-1-0.dll", " winsta.dll", " msvbvm60.dll", " secur32.dll", " mfc42u.dll", " userenv.dll", " setupapi.dll", " uxtheme.dll", " api-ms-win-security-base-l1-1-0.dll", " api-ms-win-core-processthreads-l1-1-0.dll", " powrprof.dll", " mfc42.dll", " api-ms-win-core-misc-l1-1-0.dll", " api-ms-win-core-profile-l1-1-0.dll", " api-ms-win-core-localregistry-l1-1-0.dll", " wbemcomn.dll", " oledlg.dll", " api-ms-win-core-sysinfo-l1-1-0.dll", " mswsock.dll", " ntdll.dll", "iswalpha", "SetClassLongA", "SetThreadUILanguage", "ConvertSidToStringSidW", "RegisterTraceGuidsW", "NtQueryValueKey", "CheckTokenMembership", "_wsetlocale", "UnregisterTraceGuids", "wcscat_s", "VerSetConditionMask", "RtlLengthSid", "memmove_s", "?what@exception@@UBEPBDXZ", "RtlCaptureContext", "ShellExecuteA", "RtlFreeHeap", "swprintf_s", "_ftol2", "AppendMenuA", "GetTraceEnableLevel", "wcscpy_s", "_CItan", "__wgetmainargs", "RevertToSelf", "ConvertStringSecurityDescriptorToSecurityDescriptorW", "RtlLookupFunctionEntry", "GetTraceLoggerHandle", "TraceMessage", "GetTraceEnableFlags", "RtlVirtualUnwind", "GetConsoleScreenBufferInfo", "SHBrowseForFolderA", "__C_specific_handler", "_fmode", "wcstol", "LookupAccountNameW", "NtDeviceIoControlFile", "_callnewh", "NtOpenFile", "vfwprintf", "__winitenv", "SHGetFileInfoA", "_commode", "wprintf", "RtlNtStatusToDosError"]
strip_dll_api = map(str.strip, DLL_API_FEATURES)
SECTION_NAMES = [u'RT_CODE', u'RT_DATA', u'.nep', u'.rsrc', u'.bss', u'consent', u'RT_BSS', u'.reloc', u'PAGELK', u'.orpc', u'.idata', u'.rdata', u'FE_TEXT', u'.data', u'.pdata', u'.text', u'.tls', u'other']
CATEGORIES = ["white", "Packed", "Trojan", "Downloader"]

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
            virus_name = "white" if table == "white_detail" else "black"
            sample_count += 1
            if sample_count > 1000:
                break

            for tmp_dll, apis in r1.iteritems():   # type of apis is list
                for api in apis:
                    if api in dict_api:
                        dict_api[api][virus_name] += 1
                    else:
                        dict_api[api] = {virus_name: 1}

                dll = tmp_dll.lower()
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
    cur.executemany(sql_content, calc_info(dict_data))
    conn.commit()


def select(data, thresh, ratio):
    result = []
    for i in data:
        if i[1]*i[2] == 0:
            if i[1] + i[2] > thresh:
                result.append(i[0])
        else:
            if i[3] > ratio:
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
        if result[1]:
            r1 = json.loads(result[1])
            if r1.values()[0][0].find(',') != -1 or r1.values()[-1][0].find(',') != -1:
                continue

            if table == "white_detail":
                row[0] = 0
            else:
                row[0] = CATEGORIES.index(category)

            sample_count += 1
            if sample_count > 1000:
                break

            for tmp_dll, apis in r1.iteritems():   # type of apis is list
                for api in apis:
                    try:
                        index = DLL_API_FEATURES.index(api)
                        row[index] = 1
                    except ValueError:
                        continue

                dll = tmp_dll.lower()
                try:
                    index = DLL_API_FEATURES.index(dll)
                    row[index] = 1
                except ValueError:
                    continue

            rows.append(row)

            r2 = json.loads(result[2])

            for item in r2:
                try:
                    index = SECTION_NAMES.index(item["Name"])
                    row[index + len(DLL_API_FEATURES)] = 1
                except ValueError:
                    row[-1] += 1
    return rows


def write_csv(rows, csv_file):
    csvfile = file(csv_file, 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(strip_dll_api + SECTION_NAMES)
    writer.writerows(rows)
    csvfile.close()


if __name__ == "__main__":
    conn = MySQLdb.connect(db="malware_info", user="root", passwd="polydata", host="localhost", port=3306, charset="utf8")
    cur = conn.cursor()
    # time1 = time()
    # dict_white_dll, dict_white_api = count_peinfo("white_detail")
    # time2 = time()
    # dict_black_dll, dict_black_api = count_peinfo("VT_detail")
    # time3 = time()
    # print "cost time --> white_detail: %.2fs, VT_detail: %.2fs" % (time2 - time1, time3 - time2)
    # dict_dll = combine(dict_white_dll, dict_black_dll)
    # dict_api = combine(dict_white_api, dict_black_api)
    # dll_info = calc_info(dict_dll)
    # api_info = calc_info(dict_api)
    # # insert_db("dlls", "dll", dict_dll)
    # # insert_db("apis", "api", dict_api)
    # dll_feature = select(dll_info, 20, 0.6)
    # api_feature = select(api_info, 100, 0.85)
    #
    # DLL_API_FEATURES = ["lable"] + dll_feature + api_feature
    #
    white = count_sample_info("white_detail")
    black = count_sample_info("VT_detail", "Packed")
    write_csv(white + black, '/root/Packed.csv')

    black = count_sample_info("VT_detail", "Trojan")
    write_csv(white + black, '/root/Trojan.csv')

    black = count_sample_info("VT_detail", "Downloader")
    write_csv(white + black, '/root/Downloader.csv')
    cur.close()
    conn.close()
