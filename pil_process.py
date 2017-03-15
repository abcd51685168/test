# coding:utf-8

import os
import time
import threading
import binascii
import multiprocessing
from math import sqrt
from multiprocessing import cpu_count
from queue import Queue

from PIL import Image
import numpy

WIDTHS = []
CPU_COUNT = cpu_count()
filename_list = []
exe_path = r"/data/test_virus/"
pic_dir = r"/data/test_pic"
(DST_W, DST_H, SAVE_Q) = (512, 512, 90)


def resize_from_img(ori_img, dst_img, dst_w, dst_h, save_q=75):
    im = Image.open(ori_img)
    resize_img = im.resize((dst_w, dst_h), Image.ANTIALIAS)
    resize_img.save(dst_img, quality=save_q)


def resize_from_fh(fh, dst_img, dst_w, dst_h, save_q=75):
    im = Image.fromarray(fh)
    resize_img = im.resize((dst_w, dst_h), Image.ANTIALIAS)
    resize_img.save(dst_img, quality=save_q)


def get_matrix_from_bin(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)  # 将二进制文件转换为十六进制字符串
    fh = numpy.array([int(hexst[i: i + 2], 16) for i in range(0, len(hexst), 2)])  # 按字节分割
    width = int(sqrt(len(fh)))
    WIDTHS.append(width)
    fh = numpy.reshape(fh[:width * width], (-1, width))  # 根据设定的宽度生成矩阵
    fh = numpy.uint8(fh)
    return fh


def do_job(filename):
    # filename = args[0]
    img_name = os.path.basename(filename).split('.')[0]
    dst_img = os.path.join(pic_dir, img_name) + ".jpg"
    # print(filename, dst_img)
    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)  # 将二进制文件转换为十六进制字符串
    fh = numpy.array([int(hexst[i: i + 2], 16) for i in range(0, len(hexst), 2)])  # 按字节分割
    width = int(sqrt(len(fh)))
    WIDTHS.append(width)
    fh = numpy.reshape(fh[:width * width], (-1, width))  # 根据设定的宽度生成矩阵
    fh = numpy.uint8(fh)

    im = Image.fromarray(fh)
    resize_img = im.resize((DST_W, DST_H), Image.ANTIALIAS)
    resize_img.save(dst_img, quality=SAVE_Q)


def list_files(path, depth=1):
    os.chdir(path)
    for obj in os.listdir(os.curdir):
        if os.path.isfile(obj):
            filename_list.append(os.getcwd() + os.sep + obj)
        if os.path.isdir(obj):
            if depth > 1:
                list_files(obj, depth - 1)
                os.chdir(os.pardir)


class WorkManager(object):
    def __init__(self, file_list, thread_num=1):
        self.work_queue = Queue()
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
        for filename in file_list:
            self.add_job(do_job, filename)

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
            except Exception as e:
                print(str(e))
                break


if __name__ == "__main__":
    # data_path = r"C:/tmp/data.txt"
    # tmp_dir = r"C:/tmp/tmp"
    # pic_dir = r"C:/tmp/pic"
    # virus_dir = r"C:/tmp/virus"
    # for i, filename in enumerate(os.listdir(virus_dir), 1):
    #     print(i, os.path.join(virus_dir, filename))
    #     # get_matrix_from_bin(os.path.join(virus_dir, filename))
    #     im = Image.fromarray(get_matrix_from_bin(os.path.join(virus_dir, filename)))  # 转换为图像
    #     tmp_pic_path = os.path.join(tmp_dir, filename + ".jpg")
    #     im.save(tmp_pic_path)
    #     clipResizeImg(ori_img=tmp_pic_path, dst_img=os.path.join(pic_dir, filename + ".jpg"), dst_w=dst_w,
    #                   dst_h=dst_h, save_q=save_q)

    # array_widths = numpy.array(WIDTHS)
    # numpy.savetxt(data_path, array_widths, fmt="%d")

    cwd = os.getcwd()
    list_files(exe_path)
    os.chdir(cwd)

    start = time.time()
    # work_manager = WorkManager(filename_list)
    # work_manager.wait_allcomplete()

    print("Using %s cpu cores" % CPU_COUNT)
    pool = multiprocessing.Pool(processes=CPU_COUNT, maxtasksperchild=400)
    for i, filename in enumerate(filename_list):
        # print(i, filename)
        pool.apply_async(do_job, (filename,))  # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去

    pool.close()
    pool.join()  # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    end = time.time()
    print("cost all time: %s seconds." % (end - start))
