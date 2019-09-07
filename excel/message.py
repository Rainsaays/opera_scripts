#/usr/bin/env python3
# -*- coding: utf-8 -*-


# -*- coding:utf-8 -*-
import smtplib,os
import email

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
from email import encoders

# 发件人地址，通过控制台创建的发件人地址
from_addr = 'opsyunw@126.com'


# 发件人密码，通过控制台创建的发件人密码
password = '123'
# 收件人地址或是地址列表，支持多个收件人用逗号分隔，最多30个
to_addr = '123@126.com,333@126.com'
stmp_addr = 'smtp.126.com'
stmp_port = 465

def message(email_subject,email_text,file_path=""):
    # 构建alternative结构
    msg = MIMEMultipart()
    msg['Subject'] = Header(email_subject).encode()
    msg['From'] = '%s <%s>' % (Header('运维').encode(), from_addr)
    msg['To'] = to_addr
    msg['Reply-to'] = from_addr
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    # 邮件正文的text/plain部分
    textplain = MIMEText(email_text, _subtype='plain', _charset='UTF-8')
    msg.attach(textplain)
    # 邮件正文的text/html部分
    # texthtml = MIMEText(email_text, _subtype='html', _charset='UTF-8')
    # msg.attach(texthtml)
    # 添加附件
    if file_path:
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('ccc','aaa',filename=file_name)
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename=file_name)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)
        # 发送邮件
    try:
        #python 2.7以上版本，若需要使用SSL，可以这样创建client
        client = smtplib.SMTP_SSL(stmp_addr, stmp_port)
        # #SMTP普通端口为25
        # client = smtplib.SMTP()
        # client.connect(stmp_addr, stmp_port)
        #开启DEBUG模式
        client.set_debuglevel(0)
        client.login(from_addr,password)
        #发件人和认证地址必须一致
        #备注：若想取到DATA命令返回值,可参考smtplib的sendmaili封装方法:
        client.sendmail(from_addr, to_addr.split(','), msg.as_string())
        client.quit()
        print('邮件发送成功！')
    except smtplib.SMTPConnectError as e:
        print ('邮件发送失败，连接失败:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPAuthenticationError as e:
        print ('邮件发送失败，认证错误:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPSenderRefused as e:
        print ('邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPRecipientsRefused as e:
        print ('邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPDataError as e:
        print ('邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPException as e:
        print ('邮件发送失败, ', e.message)
    except Exception as e:
        print ('邮件发送异常,', str(e))


if __name__ == "__main__":
    message("111", "")