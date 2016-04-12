import os
import json
import codecs
import MySQLdb
from time import time
from math import log
import csv

DLL_API_FEATURES = ["label", " slc.dll", " api-ms-win-core-errorhandling-l1-1-0.dll", " api-ms-win-core-libraryloader-l1-1-0.dll", " winsta.dll", " msvbvm60.dll", " secur32.dll", " mfc42u.dll", " userenv.dll", " setupapi.dll", " uxtheme.dll", " api-ms-win-security-base-l1-1-0.dll", " api-ms-win-core-processthreads-l1-1-0.dll", " powrprof.dll", " mfc42.dll", " api-ms-win-core-misc-l1-1-0.dll", " api-ms-win-core-profile-l1-1-0.dll", " api-ms-win-core-localregistry-l1-1-0.dll", " wbemcomn.dll", " oledlg.dll", " api-ms-win-core-sysinfo-l1-1-0.dll", " mswsock.dll", " ntdll.dll", "iswalpha", "SetClassLongA", "SetThreadUILanguage", "ConvertSidToStringSidW", "RegisterTraceGuidsW", "NtQueryValueKey", "CheckTokenMembership", "_wsetlocale", "UnregisterTraceGuids", "wcscat_s", "VerSetConditionMask", "RtlLengthSid", "memmove_s", "?what@exception@@UBEPBDXZ", "RtlCaptureContext", "ShellExecuteA", "RtlFreeHeap", "swprintf_s", "_ftol2", "AppendMenuA", "GetTraceEnableLevel", "wcscpy_s", "_CItan", "__wgetmainargs", "RevertToSelf", "ConvertStringSecurityDescriptorToSecurityDescriptorW", "RtlLookupFunctionEntry", "GetTraceLoggerHandle", "TraceMessage", "GetTraceEnableFlags", "RtlVirtualUnwind", "GetConsoleScreenBufferInfo", "SHBrowseForFolderA", "__C_specific_handler", "_fmode", "wcstol", "LookupAccountNameW", "NtDeviceIoControlFile", "_callnewh", "NtOpenFile", "vfwprintf", "__winitenv", "SHGetFileInfoA", "_commode", "wprintf", "RtlNtStatusToDosError"]
LEN_FEATURES = len(DLL_API_FEATURES)
# {"GetCurrentProcess": {"white": 10, "black": 5, "P2P-Worm": 3, "Backdoor": 6}}
# {"xxx.dll": {"white": 10, "black": 5, "P2P-Worm": 3, "Backdoor": 6}}
def count_peinfo(table):
    sql_content = 'SELECT Sha256, File_detail->\'$." PE imports"\', Category FROM {};'.format(table)
    cur.execute(sql_content)

    results = cur.fetchall()
    white_count = 0
    black_count = 0
    dict_dll = {}
    dict_api = {}
    for result in results:
        if result[1]:
            r0 = json.loads(result[1])
            if r0.values()[0][0].find(',') != -1 or r0.values()[-1][0].find(',') != -1:
                continue

            virus_name = result[2]
            if virus_name == "white":
                white_count += 1
                if white_count > 1000:
                    continue
            else:
                black_count += 1
                if black_count > 1000:
                    if white_count > 1000:
                        break
                    continue

            for tmp_dll, apis in r0.iteritems():   # type of apis is list
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
          % (table, len(results), white_count+ black_count, len(dict_dll), len(dict_api))
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


def insert_db(table, column1, dict_data):
    result = []
    sql_content = "INSERT INTO " + table + "(" + column1 + ", white, black, ce)" + " VALUES(%s, %s, %s, %s);"
    for key, value in dict_data.iteritems():
        args = [key, value.get("white", 0), value.get("black", 0)]
        ce = calc_ce(*args)
        args.append(ce)
        result.append(args)
    return result
    #     cur.execute(sql_content, (key, value.get("white", 0), value.get("black", 0), ce))
    # conn.commit()


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


def select(data, thresh, ratio):
    result = []
    for i in data:
        if i[1]*i[2] == 0:
            if i[1] + i[2] > thresh:
                result.append(i)
        else:
            if i[3] > ratio:
                result.append(i)
    return result


def count_dll_api(table):
    sql_content = 'SELECT Sha256, File_detail->\'$." PE imports"\', Category FROM {};'.format(table)
    cur.execute(sql_content)
    results = cur.fetchall()
    sample_count = 0
    dlls = []
    apis = []
    rows = []
    for result in results:
        features = []
        row = [0] * LEN_FEATURES
        if result[1]:
            r0 = json.loads(result[1])
            if r0.values()[0][0].find(',') != -1 or r0.values()[-1][0].find(',') != -1:
                continue

            if table == "white_detail":
                row[0] = 0
            else:
                row[0] = 1

            sample_count += 1
            if sample_count > 1000:
                break

            for tmp_dll, tmp_apis in r0.iteritems():   # type of apis is list
                apis.extend(tmp_apis)
                dlls.append(tmp_dll)

            for tmp_dll, apis in r0.iteritems():   # type of apis is list
                for api in apis:
                    try:
                        index = DLL_API_FEATURES.index(api)
                        row[index] = 1
                    except ValueError:
                        continue
                    # if api in DLL_API_FEATURES:
                    #     features.append(api)

                dll = tmp_dll.lower()
                try:
                    index = DLL_API_FEATURES.index(dll)
                    row[index] = 1
                except ValueError:
                    continue
                # if dll in DLL_API_FEATURES:
                #     features.append(dll)
            rows.append(row)
    return rows


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
    #
    # result = insert_db("dlls", "dll", dict_dll)
    # # sort_result = sorted(result, key=lambda d: d[3], reverse=True)
    # ret1 = select(result, 20, 0.6)
    #
    # result = insert_db("apis", "api", dict_api)
    # ret2 = select(result, 100, 0.85)
    #
    # feature = ""
    # for i in ret1 + ret2:
    #     feature = feature + i[0] + "\n"
    # with open("/tmp/select_feature.txt", "w") as f:
    #     f.write(feature)
    white_rows = count_dll_api("white_detail")
    black_rows = count_dll_api("VT_detail")
    rows = white_rows + black_rows
    csvfile = file('/root/sample_data.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(DLL_API_FEATURES)
    writer.writerows(rows)
    csvfile.close()
    cur.close()
    conn.close()
