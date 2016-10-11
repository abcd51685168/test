# -*- coding:utf-8 -*-
# ref_blog:http://www.open-open.com/home/space-5679-do-blog-id-3247.html
import Queue
import threading
import time
import argparse
import os
import sys
from multiprocessing import cpu_count

filename_list = []
TEST_ID = 100000


def list_files(path):
    os.chdir(path)
    for obj in os.listdir(os.curdir):
        if os.path.isfile(obj):
            filename_list.append(os.getcwd() + os.sep + obj)
        if os.path.isdir(obj):
            list_files(obj)
            os.chdir(os.pardir)


# 具体要做的任务
def do_job(args):
    pre_path = "/polyhawk/mds/script/staticscan/staticscan.py"
    cmd = "pypy " + pre_path + " {}".format(args[0])
    print cmd
    os.system(cmd)


class WorkManager(object):
    def __init__(self, file_list, thread_num=cpu_count()):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.__init_work_queue(file_list)
        self.__init_thread_pool(thread_num)

    """
      初始化线程
    """
    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue))

    """
      初始化工作队列
    """
    def __init_work_queue(self, file_list):
        for f in file_list:
            self.add_job(do_job, f)

    """
      添加一项工作入队
    """
    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    """
      检查剩余队列任务
    """
    def check_queue(self):
        return self.work_queue.qsize()

    """
      等待所有线程运行完毕
    """
    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive():
                item.join()


class Work(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            try:
                do, args = self.work_queue.get(block=False)  # 任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()  # 通知系统任务完成
            except Exception, e:
                print str(e)
                break


# class post(threading.Thread):
    # def __init__(self, post_id, filename):
        # threading.Thread.__init__(self)
        # self.post_id = post_id
        # self.filename = filename

    # def run(self):
        # cmd = "python /polyfalcon/analysis/preprocess/preprocess.py --id {0} --file {1}".format(self.post_id, self.filename)
        # print cmd
        # os.system(cmd)

# for filename in filename_list:
    # thread1 = post(post_id, filename)
    # thread1.start()
    # post_id += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="path", required=True)
    parser.add_argument("-t", "--thread", type=int, help="thread_num", required=False, default=cpu_count())
    parser.add_argument("-n", "--number", type=int, help="submit_num", required=False, default=0)
    args = parser.parse_args()

    cwd = os.getcwd()
    list_files(args.path)
    os.chdir(cwd)
    if args.number > 0:
        filename_list = filename_list[:args.number]

    start = time.time()
    work_manager = WorkManager(filename_list, args.thread)
    work_manager.wait_allcomplete()
    end = time.time()
    print "number of files: %s, cost all time: %s seconds." % (len(filename_list), end - start)
