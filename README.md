### log_check/log_check.py
```
1.该文件支持语法格式为python3 
2.日志文件需要跟可执行的python文件放同一目录 
3.执行方法:python log_check.py 
4.执行后生成的文件cms_error.log 为error日志统计,cms_warn.log 为warm日志统计 
5.cms_error.log,cms_warn.log 跟可执行的python文件在同一目录
 
```
### micro_check/logger.py
```
写日志到文件跟控制台

```
### micro_check/micro.py micro_check/micro_easy.py
```
根据eureka检测各个微服务的状况,并发钉钉消息,micro.py只需要配置网关地址,micro_easy.py需提供eureka的地址,并且需要能正常访问注册到eureka的地址

```

### pinpoint_check/pinpoint.py  
```
根据pinpoint的接口,查询error,show慢次数并发送钉钉消息

```
### excel/message.py
```
发邮件的函数
```

### excel/commodity_info.py
```
从数据库查询数据,并导入到excel
```

### shell/jenkins_update.sh
```
根据dockerfile打包镜像上传到harbor,发布pod
```
