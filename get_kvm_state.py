# -*- coding:utf-8 -*-
import argparse
import os
import sys
import MySQLdb
import psutil
import time

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-p", "--path", type=str, help="path", required=False)
    # parser.add_argument("-n", "--number", type=int, help="submit_num", required=False, default=0)
    # args = parser.parse_args()

    sql_command = "SELECT target,name from machines,tasks WHERE machines.id=tasks.machine_id and locked=1 ORDER BY tasks.id DESC;"
    conn = MySQLdb.connect(db="sandbox", user="polydata", passwd="data_poly@)!%", host="localhost", port=3306, charset="utf8")
    cur = conn.cursor()

    while True:
        cur.execute(sql_command)
        results = {}
        out = []
        print "VM                 ANALYSIS_FILE         VIRT   RES   SHR  %CPU %MEM "
        print "------------------------------------------------------------------------------------------------------"
        query_results = cur.fetchall()
        vms = [i[1] for i in query_results]
        virsh_list_vms = os.popen("virsh list | grep win | awk {'print $2'}").read().split('\n')
        for result in query_results:
            time.sleep(1)
            vm = result[1]
            if vm not in results:
                data = os.popen("virsh list | grep {}".format(vm)).read().split()
                if data:
                    results[vm] = result[0]
                    cmd = "top -w -b -n 1 -c | grep {} | grep -v grep".format(vm) + " | awk {'print $5,$6,$7,$9,$10'}"
                    ret = os.popen(cmd)
                    data1 = ret.read().strip()
                    out.append((result[1], result[0], data1))
        for o in out:
            print ("%-20s %-70s %-40s" % (o[0], o[1], o[2]))
            # print o[0], o[1], o[2]
        else:
            print "--------------------------------------------------------------------------------------------------\n"

    cur.close()
    conn.close()

    # ret = os.popen("ps -ef | grep winxp_sp3_10l_0 | grep -v grep |awk {'print $2'}")
    # data = ret.read().strip()
    # p = psutil.Process(int(data))
    # p = psutil.Process(16314)
    # print p.cpu_percent(interval=0.5)
    # print p.memory_percent()
    # print p.memory_info_ex()
    # print p.io_counters()
    # p.as_dict(['cpu_percent','memory_percent'])
