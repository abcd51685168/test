import os
import shutil

source_dir = "/polydata/62samples"
target_dir = "/polydata/collected/"
categories = {"doc": "Word", "xls": "Excel", "ppt": "PowerPoint",
              # "doc": "Microsoft Office Word", "xls": "Microsoft Office Excel", "ppt": "Microsoft Office PowerPoint",
              # "docx": "Microsoft Word 2007+", "xlsx": "Microsoft Excel 2007+", "pptx": "Microsoft PowerPoint 2007+",
              "pdf": "PDF", "swf": "Flash",
              "exe32": "PE32 executable (GUI)", "dll32": "PE32 executable (DLL)",
              "exe64": "PE32+ executable (GUI)", "dll64": "PE32+ executable (DLL)", }

for category in categories.keys():
    category_dir = os.path.join(target_dir, category)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)

os.chdir(source_dir)
for f in os.listdir(source_dir):
    ret = os.popen("file {}".format(f))
    data = ret.read().strip()
    for category, keyword in categories.items():
        if data.find(keyword) != -1:
            shutil.copy2(f, os.path.join(target_dir, category))
            break
