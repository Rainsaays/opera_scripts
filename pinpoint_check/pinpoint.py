# -*- coding: utf-8 -*-
# @Time: 2019/6/18 10:15
# 功能：调用pinpoint接口，监控每个应用的调用错误数，并将告警信息发送到钉钉。
import sys
import os
import requests
import time
import datetime
import json
from dingtalkchatbot.chatbot import DingtalkChatbot  # pip install dingtalkchatbot

webhook = "https://oapi.dingtalk.com/robot/send?access_token=123"
PPURL = "http://www.pinpoint.cn"

'''获取最近N分钟内的时间戳'''
From_Time = datetime.datetime.now() + datetime.timedelta(seconds=-600)
To_Time = datetime.datetime.now()
From_TimeStamp = int(time.mktime(From_Time.timetuple())) * 1000
To_TimeStamp = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
# print( From_Time,To_Time,From_TimeStamp,To_TimeStamp )

def message_text(type,error_count,service_type,application_name):
    text = """
        <pinpoint报警
        报警策略：{type} COUNT
        报警内容：{type} COUNT value is {error_count} during the past 10 mins.
        服务类型：{service_type}
        服务名：{application_name}
    """.format(type=type, error_count=error_count, service_type=service_type, application_name=application_name)
    return text

"""获取pinpoint中所有服务的基础信息,包括服务名，服务类型等"""
def get_applications():
    '''return application dict
    '''
    applicationListUrl = PPURL + "/applications.pinpoint"
    res = requests.get(applicationListUrl)
    if res.status_code != requests.codes.ok:
        print("请求异常,请检查")
        return
    # print(res.json())
    return res.json()


'''传入服务名，返回该服务的节点数和各节点的节点名'''
def getAgentList(appname):
    AgentListUrl = PPURL + "/getAgentList.pinpoint"

    param = {
        'application': appname
    }
    res = requests.get(AgentListUrl, params=param)
    if res.status_code != requests.codes.ok:
        print("请求异常,请检查")
        return
    # print( len(res.json().keys()), json.dumps(list(res.json().keys())) )
    return len(res.json().keys()), json.dumps(list(res.json().keys()))


'''获取调用失败次数'''
def update_servermap(appname, from_time=From_TimeStamp, to_time=To_TimeStamp, serviceType='TOMCAT'):
    '''更新app上下游关系
    :param appname: 应用名称
    :param serviceType: 应用类型
    :param from_time: 起始时间
    :param to_time: 终止时间
    :
    '''
    param = {
        'applicationName': appname,
        'from': from_time,
        'to': to_time,
        'callerRange': 1,
        'calleeRange': 1,
        'serviceTypeName': serviceType
    }
    serverMapUrl = "{}{}".format(PPURL, "/getServerMapData.pinpoint")
    res = requests.get(serverMapUrl, params=param)
    if res.status_code != requests.codes.ok:
        print("请求异常,请检查")
        return
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    links = res.json()["applicationMapData"]["linkDataArray"]
    # links包含该app的上下游调用关系链，以及相互之间调用的次数和失败的次数等信息。
    # print(links)
    # print(len(links))
    #    totalCount=0
    errorCount = 0
    slowCount=0
    threeCount=0
    fiveCount=0

    for link in links:
        ###只检查prod环境
        if link['sourceInfo']['applicationName'].startswith('prod'):
        # 应用名称、应用类型、下游应用名称、下游应用类型、应用节点数、下游应用节点数、总请求数、 错误请求数、慢请求数(本应用到下一个应用的数量)
        #        application = link['sourceInfo']['applicationName']
        #        serviceType = link['sourceInfo']['serviceType']
        #        to_application = link['targetInfo']['applicationName']
        #        to_serviceType = link['targetInfo']['serviceType']
        #        agents = len(link.get('fromAgent',' '))
        #        to_agents =  len(link.get('toAgent',' '))

            '''总错误数进行累计'''
        #        totalCount += link['totalCount']
            errorCount += link['errorCount']
            slowCount += link['slowCount']
            if link['histogram'].__contains__('3s'):
                threeCount += link['histogram']['3s']
            if link['histogram'].__contains__('5s'):
                fiveCount += link['histogram']['5s']
    return errorCount,slowCount,threeCount,fiveCount


def ding_message():
    '''初始化钉钉对象'''
    xiaoding = DingtalkChatbot(webhook)
    at_mobiles = ['1373633366']

    '''获取所有服务的app名和服务类型，并存到字典中'''
    applicationLists = get_applications()
    # print(applicationLists)

    '''轮询application，查询每个application在过去五分钟内的总错误数，并通过钉钉报警'''
    for app in applicationLists:
        application_name = app['applicationName']
        service_type = app['serviceType']
        error_count = update_servermap(application_name, from_time=From_TimeStamp, to_time=To_TimeStamp,serviceType=service_type)[0]
        slow_count = update_servermap(application_name, from_time=From_TimeStamp, to_time=To_TimeStamp,serviceType=service_type)[1]
        threes_count = update_servermap(application_name, from_time=From_TimeStamp, to_time=To_TimeStamp,serviceType=service_type)[2]
        fives_count = update_servermap(application_name, from_time=From_TimeStamp, to_time=To_TimeStamp,serviceType=service_type)[3]
        error_text=message_text("ERROR",error_count,service_type,application_name)
        slow_text = message_text("SLOW", error_count, service_type, application_name)
        threes_text = message_text("3s", error_count, service_type, application_name)
        fives_text = message_text("5s", error_count, service_type, application_name)
        '''如果总调用错误数超过阈值5(根据实际需求进行设置)，则报警'''
        if error_count >= 1:

            xiaoding.send_markdown(title='pinpoint报警', text=error_text, at_mobiles=at_mobiles)
        if slow_count >= 3:
            xiaoding.send_markdown(title='pinpoint报警', text=slow_text, at_mobiles=at_mobiles)
        if threes_count >= 60:
            xiaoding.send_markdown(title='pinpoint报警', text=threes_text, at_mobiles=at_mobiles)
        if fives_count >= 30:
            xiaoding.send_markdown(title='pinpoint报警', text=fives_text, at_mobiles=at_mobiles)





if __name__ == "__main__":
    print(f"started at {time.strftime('%X')}")
    ding_message()
    print(f"finished at {time.strftime('%X')}")



