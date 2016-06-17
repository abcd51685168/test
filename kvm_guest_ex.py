#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from time import sleep, time
import argparse
import xmlrpclib
import threading
import sys
import Queue
from collections import namedtuple
import logging
import logging.handlers

LOG_ROOT = "/polydata/log/"
log = logging.getLogger(__file__)
formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

fh = logging.handlers.WatchedFileHandler(os.path.join(LOG_ROOT, 'kvm_guest_ex.log'))
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

log.setLevel(logging.INFO)

XML_PATH = "/polydata/image/"
BACKUP_PATH = "/polydata/image/backup/"
QEMU_PATH = "/etc/libvirt/qemu/"


VM = namedtuple('VM', ['type', 'mac', 'num', 'start_ip'])
STATUS_INIT = 0x0001
DOMAIN_IP_MAC = []


class VM_Operation(object):
    def __init__(self):
        # num -- number of vms
        # start_ip -- start_ip of domain index and ip
        self.vms = [
            VM("win2k3_sp2s_",      "52:54:00:33:10:", 2, 20),
            VM("winxp_sp2s_",       "52:54:00:33:11:", 2, 26),
            VM("winxp_sp3s_",       "52:54:00:33:12:", 2, 31),
            VM("win7_sp1_32s_",     "52:54:00:33:13:", 2, 36),
            VM("win2k3_sp2l_",      "52:54:00:33:14:", 2, 50),
            VM("winxpl_",           "52:54:00:33:15:", 2, 60),
            VM("winxp_sp2l_",       "52:54:00:33:16:", 2, 70),
            VM("winxp_sp3_03l_",    "52:54:00:33:17:", 2, 85),
            VM("winxp_sp3_07l_",    "52:54:00:33:18:", 2, 100),
            VM("winxp_sp3_10l_",    "52:54:00:33:19:", 10, 115),
            VM("win7_32l_",         "52:54:00:33:1a:", 2, 145),
            VM("win7_sp1_32l_",     "52:54:00:33:1b:", 10, 155),
            VM("win7_sp1_64l_",     "52:54:00:33:1c:", 2, 185)
        ]

        # self.vms = [
        #     VM("win2k3_sp2s_",      "52:54:00:33:10:", 1, 20),
        #     VM("winxp_sp2s_",       "52:54:00:33:11:", 1, 26),
        #     VM("winxp_sp3s_",       "52:54:00:33:12:", 1, 31),
        #     VM("win7_sp1_32s_",     "52:54:00:33:13:", 1, 36),
        #     VM("win2k3_sp2l_",      "52:54:00:33:14:", 1, 50),
        #     VM("winxpl_",           "52:54:00:33:15:", 1, 60),
        #     VM("winxp_sp2l_",       "52:54:00:33:16:", 1, 70),
        #     VM("winxp_sp3_03l_",    "52:54:00:33:17:", 1, 85),
        #     VM("winxp_sp3_07l_",    "52:54:00:33:18:", 1, 100),
        #     VM("winxp_sp3_10l_",    "52:54:00:33:19:", 1, 115),
        #     VM("win7_32l_",         "52:54:00:33:1a:", 1, 145),
        #     VM("win7_sp1_32l_",     "52:54:00:33:1b:", 1, 155),
        #     VM("win7_sp1_64l_",     "52:54:00:33:1c:", 1, 185)
        # ]
        self.prefix_ip = "10.14.24."

    def get_vm_ip_by_mac(self):
        for vm in self.vms:
            for i in range(vm.num):
                domain = vm.type + str(i)
                mac = vm.mac + str(i + 10)
                ip = self.prefix_ip + str(i + vm.start_ip)
                DOMAIN_IP_MAC.append((domain, ip, mac))

    def define_vm0(self):
        """define vm_0 from xml"""
        for vm in self.vms:
            create0_cmd = "qemu-img create -f qcow2 -b {0}backup.qcow2 {0}0.qcow2 > /dev/null".format(vm.type)
            log.info(create0_cmd)
            os.system(create0_cmd)
            define_cmd = "virsh define {}0.xml > /dev/null".format(vm.type)
            log.info(define_cmd)
            os.system(define_cmd)
    
    def clone(self):
        """clone vms form vm_0"""
        for vm in self.vms:
            vm_ori = vm.type + "0"
            for i in range(1, vm.num):
                vm_new = vm.type + str(i)
                mac = vm.mac + str(i + 10)
                clone_cmd = "virt-clone -o {0} -n {1} -f {1}.qcow2 -m {2} > /dev/null".format(vm_ori, vm_new, mac)
                log.info(clone_cmd)
                os.system(clone_cmd)

    # make sure .qcow2/.xml/snapshot.xml already exists in XMLPATH
    def define(self):
        for vm in self.vms:
            for i in range(vm.num):
                domain = vm.type + str(i)
                os.system("virsh define {}.xml > /dev/null".format(domain))
                os.system("virsh snapshot-create {0} {0}_snapshot.xml --redefine --current".format(domain))

    def destroy(self):
        for vm in self.vms:
            for i in range(vm.num):
                domain = vm.type + str(i)
                os.system("virsh destroy {} > /dev/null".format(domain))

    # rude method
    def undefine(self):
        self.destroy()
        sleep(2)

        for vm in self.vms:
            for i in range(vm.num):
                domain = vm.type + str(i)
                xml_path = QEMU_PATH + domain + ".xml"
                os.system("rm {} > /dev/null".format(xml_path))
        os.system("service libvirt-bin restart")

    def list_snapshot(self, domain=None):
        if domain:
            ret = os.popen("virsh snapshot-list {} | grep running".format(domain))
            log.info(domain, ret.read())
        else:
            for vm in self.vms:
                for i in range(vm.num):
                    domain = vm.type + str(i)
                    ret = os.popen("virsh snapshot-list {} | grep running".format(domain))
                    log.info(domain, ret.read())

    def rm_qcow2(self):
        for vm in self.vms:
            for i in range(vm.num):
                image = vm.type + str(i) + ".qcow2"
                os.system("rm {} > /dev/null".format(XML_PATH + image))


def create_snapshot(args):
    """start vm, create snapshot, dumpxml, dumpsnapshotxml and destroy it"""
    domain = args[0]
    start_cmd = "virsh start {} > /dev/null".format(domain)
    log.info(start_cmd)
    os.system(start_cmd)
    url = "http://{0}:8000".format(args[1])
    server = xmlrpclib.ServerProxy(url)
    while True:
        sleep(1)
        try:
            status = server.get_status()
            if status == STATUS_INIT:
                # wait the system status tend to be stable
                sleep(20)
                break
        # error: [Errno 113] No route to host
        except:
            continue
    log.info("%s start successfully" % domain)
    reboot_cmd = "virsh reboot {} > /dev/null".format(domain)
    log.info(reboot_cmd)
    os.system(reboot_cmd)

    while True:
        sleep(1)
        try:
            status = server.get_status()
            if status == STATUS_INIT:
                # wait the system status tend to be stable
                sleep(20)
                break
        # error: [Errno 113] No route to host
        except:
            continue
    log.info("%s reboot successfully" % domain)

    snapshot_cmd = "virsh snapshot-create {} > /dev/null".format(domain)
    os.system(snapshot_cmd)
    log.info(snapshot_cmd)
    sleep(2)

    dumpxml_cmd = "virsh dumpxml --migratable {0} > {1}{0}.xml".format(domain, BACKUP_PATH)
    dumpsnapshot_cmd = "virsh snapshot-current {0} > {1}{0}_snapshot.xml".format(domain, BACKUP_PATH)
    os.system(dumpxml_cmd)
    os.system(dumpsnapshot_cmd)
    log.info(dumpxml_cmd)
    log.info(dumpsnapshot_cmd)
    sleep(1)

    copy_cmd = "cp {0}.qcow2 {1}".format(domain, BACKUP_PATH)
    os.system(copy_cmd)
    log.info(copy_cmd)
    sleep(2)

    destroy_cmd = "virsh destroy {} > /dev/null".format(domain)
    os.system(destroy_cmd)
    log.info(destroy_cmd)
    sleep(2)


class WorkManager(object):
    def __init__(self, thread_num=4):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.__init_work_queue()
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue))

    def __init_work_queue(self):
        for i in DOMAIN_IP_MAC:
            # 任务入队，Queue内部实现了同步机制
            self.work_queue.put((create_snapshot, i))

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
            except:
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--define", help="define vms", action="store_true", required=False)
    parser.add_argument("--undefine", help="undefine vms", action="store_true", required=False)
    parser.add_argument("--create", help="create vms", action="store_true", required=False)
    parser.add_argument("--list_snapshot", help="list snapshot", action="store_true", required=False)
    parser.add_argument("--domain", type=str, help="domain", action="store", required=False, default=None)
    parser.add_argument("--rm_qcow2", help="remove vm qcow2", action="store_true", required=False)
    args = parser.parse_args()

    vm_object = VM_Operation()

    if args.define:
        vm_object.define()

    if args.undefine:
        vm_object.undefine()

    if args.list_snapshot:
        vm_object.list_snapshot(args.domain)

    if args.rm_qcow2:
        vm_object.rm_qcow2()

    if args.create:
        if not os.path.exists(XML_PATH):
            sys.exit(0)
        if not os.path.exists(BACKUP_PATH):
            os.makedirs(BACKUP_PATH)

        start = time()
        os.chdir(XML_PATH)
        vm_object.get_vm_ip_by_mac()
        log.info(DOMAIN_IP_MAC)
        vm_object.define_vm0()
        vm_object.clone()
        work_manager = WorkManager()
        work_manager.wait_allcomplete()
        end = time()
        log.info("cost time: %s seconds." % (end - start))
