# coding=utf-8
import MySQLdb
import csv
import os
import shutil
from collections import Counter


def get_label(csv_file='train_label.csv'):
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='root123', db='virus')
    cur = conn.cursor()
    cur.execute("SELECT Md5, Virus_Name from real_data WHERE Virus_Name != 'null'")
    results = cur.fetchall()
    cur.close()
    conn.close()

    # md5, virus_type
    data = [[r[0], r[1].split('.')[0]] for r in results]
    types = [r[1] for r in data]
    cnt = Counter(types)
    # remove those types whose samples' count is less than 25
    filter_types = [i[0] for i in cnt.items() if i[1] > 25]
    print len(filter_types), filter_types
    filter_data = [[line[0], line[1]] for line in data if line[1] in filter_types]

    csvfile = file(csv_file, 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(filter_data)
    csvfile.close()


def get_virus(csv_file='train_label.csv', exe_dir='/data/virus', dst_dir='/data/test_virus'):
    csvfile = file(csv_file, 'rb')
    reader = csv.reader(csvfile)
    md5s = ['VirusShare_' + line[0] for line in reader]
    csvfile.close()

    files = []
    for f in os.listdir(exe_dir):
        if f in md5s:
            shutil.copy2(os.path.join(exe_dir, f), dst_dir)
            files.append(f)

    # print len(md5s), len(files)


if __name__ == "__main__":
    get_label()
    get_virus()
