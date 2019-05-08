#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : psutil
# @Author: admin
# @Date  : 2018/4/22
import psutil
import time

def processinfo():
    pidlist = psutil.pids()
    memorylist=[]
    for eachPid in pidlist:
        try:
            eachProcess = psutil.Process(eachPid)
            processName = eachProcess.name()
            # processCpu = eachProcess.cpu_percent(interval=5)
            processMemory=eachProcess.memory_percent()
            memoryinfo=eachPid,processName,processMemory
            memorylist.append(memoryinfo)
        except psutil.NoSuchProcess as pid:
            print("no process found with pid=%s" % pid)
    memorylist = sorted(memorylist, key=lambda student: student[2], reverse=True)
    print (memorylist[0:5])
if __name__ == '__main__':
    processinfo()




