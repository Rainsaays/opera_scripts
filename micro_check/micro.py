#/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests,re,os,time,json
from lxml import etree
from dingtalkchatbot.chatbot import DingtalkChatbot  # pip install dingtalkchatbot

###引用日志类
from logger import logger_get
logger = logger_get("info")
###配置信息
eureka_url="http://www.micro.com/eureka/"
eureka_name="user"
eureka_passwd="passwd"
webhook = "https://oapi.dingtalk.com/robot/send?access_token=123"


###初始化钉钉对象
def ding_message(message_text):
    xiaoding = DingtalkChatbot(webhook)
    at_mobiles = ['1373633366']
    xiaoding.send_markdown(title="micro server 报警",text=message_text,at_mobiles=at_mobiles)

###访问eureka获取所有server的url
def eureka_url_get():
    logger.info("start access eureka")
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}
    eureka_session=requests.Session()
    eureka_session.auth = (eureka_name,eureka_passwd)
    try:
        eureka_req = eureka_session.get(eureka_url,headers=headers)
        if eureka_req.status_code != requests.codes.ok:
            logger.error("eureka access failure")
            ding_message("eureka连接失败请注意!!!")
            exit(1)
    except Exception as e:
        logger.error("eureka access failure")
        ding_message("eureka连接超时请注意!!!")
        logger.error(e)
        exit(1)
###利用lxml模块,取所有服务的连接
    html= etree.HTML(eureka_req.text)
    result = html.xpath('//a[contains(@href,"http")]')
    eureka_url_list=[]
    server_url_list=[]
    logger.info("start Processing url")
    for i in result:
        if re.findall(r"^eur.?ka.*",i.text):
            logger.debug(i.text)
            if re.findall(r"eureka/$",i.get("href")):
                eureka_url_list.append(i.get("href") )
        else:
            server_url = i.get("href").replace( "actuator",re.split("-|:", i.text)[1] )
            server_url = server_url.replace("info", "health")
            server_url_list.append( server_url )
            logger.debug(server_url)
    logger.info(eureka_url_list)
    logger.info(server_url_list)
    return eureka_url_list,server_url_list

###eureka 检测
def eureka_url_check():
    eureka_url_list,server_url_list=eureka_url_get()
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}
    logger.info("start check eureka")
    eureka_session = requests.Session()
    eureka_session.auth = (eureka_name, eureka_passwd)
    for i in eureka_url_list:

        logger.info(i)
        try:
            eureka_req = eureka_session.get(i, headers=headers)

            if eureka_req.status_code == requests.codes.ok:
                logger.info("eureka server node access success")
            else:
                logger.error ("eureka server node access failure")
                ding_message("eureka节点连接失败请注意!!!")
        except Exception as e:
            logger.error( "eureka server node access failure" )
            ding_message("eureka节点连接失败请注意!!!")
            logger.error(e)


###所有server信息检测
def server_url_check():
    eureka_url_list,server_url_list=eureka_url_get()
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}

    logger.info("start check all server node")
    for i in server_url_list:
        logger.info(i)
        server_name=re.split("/",i) [3]
        try:
            server_req = requests.get(i, headers=headers)
            if server_req.status_code == requests.codes.ok:
                logger.info(''.join([server_name," server node access success"]) )
                logger.debug ( json.loads( server_req.content ) )
                server_json = json.loads(server_req.content)
                if server_json["status"] == 'UP':
                    logger.info( ''.join([server_name," server node check success"]) )
                elif server_json["details"]["diskSpace"]["status"]["code"] == 'UP':
                    logger.info(''.join([server_name, " server node check success"]))
                else:
                    logger.error(''.join([server_name, " server node check failure"]))
                    logger.error(server_json)
                    ding_message(''.join([server_name, "检测失败,", "详情:", server_json]))
            else:
                logger.error(''.join([server_name, " server node check failure"]))
                logger.error(server_req.text)
                ding_message( ''.join([server_name, "检测失败,","详情:",server_req.text]))

        except Exception as e:
            logger.error(''.join([server_name, " server node access failure"]) )
            logger.error(e)
            ding_message(''.join([server_name, " server node access failure"]) )
if __name__ == "__main__":
    eureka_url_check()
    server_url_check()