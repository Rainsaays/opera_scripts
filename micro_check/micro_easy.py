#/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests,re,os,time,json
from lxml import etree
from dingtalkchatbot.chatbot import DingtalkChatbot  # pip install dingtalkchatbot

###引用日志类
from logger import logger_get
logger = logger_get("info")
###配置信息
domain_url="http://www.micro.com/"
eureka_name="user"
eureka_passwd="passwd"
webhook = "https://oapi.dingtalk.com/robot/send?access_token=123"

###初始化钉钉对象
def ding_message(message_text):
    xiaoding = DingtalkChatbot(webhook)
    at_mobiles = ['1373633366']
    xiaoding.send_markdown(title="micro server 报警",text=message_text,at_mobiles=at_mobiles)


###访问eureka获取所有server的信息
def eureka_url_get():
    logger.info("start access eureka")
    eureka_url = os.path.join(domain_url,"eureka/")
    logger.debug( eureka_url )
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
###利用lxml模块,取所有服务的信息
    html= etree.HTML(eureka_req.text)
    result = html.xpath('//a[contains(@href,"http")]')
    server_name_list=[]
    logger.info("start Processing server-name")
    for i in result:
        if not re.findall(r"eure?ka.*",i.text):
            logger.debug(i.text)
            server_name = re.split("-|:", i.text)[1]
            logger.debug(server_name)
            server_name_list.append( server_name )
    server_name_list= set(server_name_list)
    logger.info(server_name_list)
    return server_name_list



###所有server信息检测
def server_url_check():
    server_name_list=eureka_url_get()

    headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}
    logger.info("start check all server node")
    for i in server_name_list:

        server_url = os.path.join(domain_url,''.join([i,"/health"]) )
        logger.info(server_url)
        try:
            server_req = requests.get(server_url, headers=headers)
            if server_req.status_code == requests.codes.ok:
                logger.info(''.join([i," server node access success"]) )
                logger.debug ( json.loads( server_req.content ) )
                server_json = json.loads(server_req.content)
                if server_json["status"] == 'UP':
                    logger.info( ''.join([i," server node check success"]) )
                elif server_json["details"]["diskSpace"]["status"]["code"] == 'UP':
                    logger.info(''.join([i, " server node check success"]))
                else:
                    logger.error(''.join([i, " server node check failure"]))
                    logger.error(server_json)
                    ding_message(''.join([i, "检测失败,", "详情:", server_json]))
            else:
                logger.error(''.join([i, " server node check failure"]))
                logger.error(server_req.text)
                ding_message( ''.join([i, "检测失败,","详情:",server_req.text]))

        except Exception as e:
            logger.error(''.join([i, "server node access failure"]) )
            logger.error(e)
            ding_message(''.join([i, "连接超时请注意!!!"]) )

if __name__ == "__main__":
    server_url_check()

