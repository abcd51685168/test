import os
import sys
import json
import time
import argparse
import requests

file_path = "/polydata/data/sample"
maxfile = 100
ip = "192.168.25.55"
port = 8989

if __name__ == "__main__":
    p = argparse.ArgumentParser()

    p.add_argument("--path", type=str, default=file_path, help="task file path")
    p.add_argument("--maxprocfiles", type=int, default=maxfile, help="max file to process")
    p.add_argument("--ip", type=str, default=ip, help="restapi server ip")
    p.add_argument("--port", type=int, default=port, help="restapi server port")

    args = p.parse_args()

    args.path = args.path if args.path else file_path
    args.maxprocfiles = args.maxprocfiles if args.maxprocfiles else maxfile
    args.ip = args.ip if args.ip else ip
    args.port = args.port if args.port else port

    counts = 0
    for root, dirs, files in os.walk(args.path):
        for f in files:
            counts += 1
            file_path = os.path.join(root, f)

            # post file task one by one
            with open(file_path, "rb") as fs:
                # files = {"file": }
                data = {'params': json.dumps(dict(analyse_method='1', realfile=f, reanalyse='1'))}
                # print "data:", data
                files = {"file": (f, fs)}
                print "files: {0}".format(file_path)
                url = 'https://{0}:{1}/polydata/service/tasks/file'.format(args.ip, args.port)

                r = requests.post(url, data=data, files=files, verify=False)
                print r.text, "\r\n"

            os.remove(file_path)

            print '>>>>>>>>>>>>>>>>>>>>>>>>>submited count: {0}'.format(counts)
            if counts >= args.maxprocfiles:
                sys.exit(0)

                # time.sleep(1)
