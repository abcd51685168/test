# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import json
import codecs
import MySQLdb

conn = MySQLdb.connect(db="virusname", user="polylab", passwd="liebesu", host="localhost", port=3306, charset="utf8")
cur = conn.cursor()

result_path = ["/root/cuckoo1.txt", "/root/cuckoo2.txt", "/root/cuckoom.txt"]

for file_path in result_path:
    with open(file_path) as f:
        data = json.load(f)

        sql_content = "SELECT"

        sql_content = "UPDATE polydect set cuckoo_2.0result=tasks (target, category, package, machine, memory, enforce_timeout, clock, added_on, status, sample_id, timedout) " \
                          "values('%s','file','%s','%s',%s,%s,'%s','%s', 'pending', %s, 0)" % (file_path, args.package, args.machine, args.memory, args.enforce_timeout, datetime.now(), datetime.now(), row[0])

for i in range(1, 124):
    file_path = os.path.join(result_root, str(i), "reports", "report.json")
    if not os.path.exists(file_path):
        print i
    with open(file_path) as f:
        data = json.load(f)
        name = data["targetdetail"]["target"]
        tmp_sig = []
        try:
            for sig in data["details"]["sandbox"]:
                tmp_sig.append(sig["name"])
            result[name] = tmp_sig

        except KeyError:
            print name
            result[name] = []

with open("/root/cuckoo1.txt", "w") as f:
    json.dump(result, f, indent=4)
