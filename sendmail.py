# coding: utf-8


import smtplib
import email.mime.multipart
import email.mime.text


def sendEmail(title, content, sendto=[]): # sendto 为目标邮箱列表，支持多个

    for item in sendto:
        msg = email.mime.multipart.MIMEMultipart()
        msg['to'] = item 
        msg['from'] = '' # 来源邮箱地址
        msg['subject'] = title
        content = content
        smtp_server = '' # 来源邮箱的 SMTP 服务器地址
        smtp_port = '' # 来源邮箱的 SMTP 端口
        sender_password = '' # 来源邮箱的密码

        if not msg['from']:
            print('来源邮箱地址无效。')
            exit()
        if not smtp_server:
            print('来源邮箱 SMTP 服务器地址无效。')
            exit()
        if not smtp_port:
            print('来源邮箱 SMTP 端口无效。')
            exit()
        if not sender_password:
            print('来源邮箱密码无效。')
            exit()
        
        txt = email.mime.text.MIMEText(content)
        msg.attach(txt)
        
        smtp = smtplib.SMTP()
        smtp.connect(smtp_server, smtp_port)
        smtp.login(msg['from'], sender_password)
        smtp.sendmail(msg['from'], item, str(msg))
        smtp.quit()


if __name__ == '__main__':
    sendEmail('title', 'content')
