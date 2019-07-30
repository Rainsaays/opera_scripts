#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cms_log


import re
FILE_NAME ="SudoCMS.LOG"
###读取日志文件,并检查error日志###
def log_error():
    error_file = "cms_error.log"
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file_read,open(error_file, "w", encoding="utf-8") as cms_warm_error:
            error_count = 0
            print("".join(["准备分析文件",FILE_NAME, ",","并写error日志到",error_file]))
            for num,value in enumerate(file_read):
                ret1 = re.findall(".*LoggerStream.write\(\).* |.*rsync error\: unexplained error.* |.*rsync\: read errors mapping.*"," ".join([str(num),value]))
                if ret1:
                    cms_warm_error.write (str(ret1[0]+"\n"))
                    error_count += 1
            cms_warm_error.write( ":".join( ["Total Errors",str(error_count),"\n"] ))
            print("error日志统计完成")
    except Exception as e:
        print ( e )
###读取日志文件,并检查warn日志###
def log_warn():
    warn_file = "cms_warn.log"
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file_read,open(warn_file, "w", encoding="utf-8") as cms_warm_warn:
            error_count = 0
            print("".join(["准备分析文件",FILE_NAME,",","并写warn日志到",warn_file] ) )
            for num,value in enumerate(file_read):
                ret1 = re.findall(".*Logger.warn\(\).* |.*rsync\: connection unexpectedly closed.*"," ".join([str(num),value]))
                if ret1:
                    cms_warm_warn.write (str(ret1[0]+"\n"))
                    error_count += 1
            cms_warm_warn.write( ":".join( ["Total Warnings",str(error_count),"\n"] ))
            print("warn日志统计完成")
    except Exception as e:
        print ( e )
###读取警告日志###

if __name__ == "__main__":
    log_error()
    log_warn()