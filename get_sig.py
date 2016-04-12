# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import json
import codecs

cuckoo2_root = "/polydata/cuckoo_test/cuckoo_20160302/storage/analyses"  # 16-52
cuckoom_root = "/polydata/cuckoo_test/cuckoo_modified_20151130/storage/analyses"  # 8-44

result = {}

for i in range(16, 53):
    with open(os.path.join(cuckoo2_root, str(i), "reports", "report.json")) as f:
        data = json.load(f)
        name = data["target"]["file"]["name"]
        result[name] = []
        for sig in data["signatures"]:
            tmp_sig = {"description": sig["description"], "name": sig["name"]}
            result[name].append(tmp_sig)
with open("/tmp/cuckoo2.txt", "w") as f:
    json.dump(result, f, indent=4)


for i in range(8, 45):
    with open(os.path.join(cuckoom_root, str(i), "reports", "report.json")) as f:
        data = json.load(f)
        name = data["target"]["file"]["name"]
        result[name] = []
        for sig in data["signatures"]:
            tmp_sig = {"description": sig["description"], "name": sig["name"]}
            result[name].append(tmp_sig)

with open("/tmp/cuckoom.txt", "w") as f:
    json.dump(result, f, indent=4)

