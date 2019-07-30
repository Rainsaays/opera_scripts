#/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging,logging.handlers,os,sys
log_fil="logs/micro.log"


###检测文件夹是否存在,不存在就创建目录
def file_check(log_fil):
    try:
        log_dir=os.path.split( log_fil )[0]
        # print(log_dir )
        if os.path.exists(log_dir) is False:
            # print(log_dir)
            os.makedirs(log_dir)
    except Exception as e:

        print (e)

###配置日志输出到文件跟控制台
def logger_get(log_Level):
    if log_Level.lower() == "notset":
        log_Level = logging.NOTSET
    elif log_Level.lower() == "debug":
        log_Level = logging.DEBUG

    elif log_Level.lower() == "info":
        log_Level = logging.INFO
    elif log_Level.lower() == "warning":
        log_Level = logging.WARNING
    elif log_Level.lower() == "error":
        log_Level = logging.ERROR
    elif log_Level.lower() == "critical":
        log_Level = logging.CRITICAL
    else:
        print("log Level error")
        exit(1)
    file_check(log_fil)
    logger = logging.getLogger("python")
    logger.setLevel(log_Level)
    handler = logging.handlers.RotatingFileHandler(log_fil, mode="w", maxBytes=20971520, backupCount=3,encoding="utf-8")
    handler.setLevel(log_Level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(log_Level)
    console.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger
if __name__ == "__main__":
    logger = logger_get("debug")
    logger.fatal("fatal")
    logger.debug("debug")
    logger.warning("warning")
    logger.error("error")

    logger.info("info")

