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

log = logging.getLogger(__file__)
formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

# fh = logging.handlers.WatchedFileHandler(os.path.join(LOG_ROOT, 'preprocess.log'))
# fh.setFormatter(formatter)
# log.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

log.setLevel(logging.INFO)


# num -- number of vms
# start_ip -- start_ip of domain index and ip
# (winxp_sp2_0  10.14.24.10), (winxp_sp3_0  10.14.24.50), (win2k3_sp2_0, 10.14.24.160), (win7_sp1_0, 10.14.24.110)
VM = namedtuple('VM', ['type', 'mac', 'num', 'start_ip'])
VMS = [
    VM("win2k3-sp2s-",      "52-54-00-33-10-", 5, 20),
    VM("winxp-sp2s-",       "52-54-00-33-11-", 5, 26),
    VM("winxp-sp3s-",       "52-54-00-33-12-", 5, 31),
    VM("win7-sp1-32s-",     "52-54-00-33-13-", 5, 36),
    VM("win2k3-sp2l-",      "52-54-00-33-14-", 10, 50),
    VM("winxpl-",           "52-54-00-33-15-", 10, 60),
    VM("winxp-sp2l-",       "52-54-00-33-16-", 15, 70),
    VM("winxp-sp3-03l-",    "52-54-00-33-17-", 15, 85),
    VM("winxp-sp3-07l-",    "52-54-00-33-18-", 15, 100),
    VM("winxp-sp3-10l-",    "52-54-00-33-19-", 30, 115),
    VM("win7-32l-",         "52-54-00-33-1a-", 10, 145),
    VM("win7-sp1-32l-",     "52-54-00-33-1b-", 30, 155),
    VM("win7-sp1-64l-",     "52-54-00-33-1c-", 10, 185)
]

DOMAIN_IP_MAC = []
prefix_ip = "10.14.24."


def gen_ip_mac():
    for vm in VMS:
        print "\nrem {0} ip-mac".format(vm.type)
        for i in range(vm.num):
            domain = vm.type + str(i)
            mac = vm.mac + str(i + 10)
            ip = prefix_ip + str(i + vm.start_ip)
            DOMAIN_IP_MAC.append((domain, ip, mac))
            out = " ".join(["rem", domain, mac, ip])
            print out


if __name__ == '__main__':
    gen_ip_mac()
