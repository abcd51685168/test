#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import MySQLdb


def insert(values):
    sql_insert = "INSERT INTO md5_imphash(md5, imphash) VALUES (%s, %s)"
    cur.executemany(sql_insert, values)
    conn.commit()


def get_imphash():
    sql_content = 'SELECT File_detail->\'$." File identification"\' FROM VT_detail;'
    cur.execute(sql_content)

    results = cur.fetchall()
    values = []
    for result in results:
        if result[0]:
            r1 = json.loads(result[0])
            try:
                values.append((r1["MD5"], r1["imphash"]))
                if len(values) >= 10000:
                    insert(values)
                    values = []
            except:
                continue
    if values:
        insert(values)


if __name__ == "__main__":
    conn = MySQLdb.connect(db="malware_info", user="root", passwd="polydata", host="192.168.25.62", port=3306,
                           charset="utf8")
    cur = conn.cursor()
    get_imphash()
    cur.close()
    conn.close()
