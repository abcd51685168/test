# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import json
import codecs

result_root = "/polydata/sandbox/storage/analyses/"  # 1-100

result = {}

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
