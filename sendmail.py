# coding: utf-8


import smtplib
import email.mime.multipart
import email.mime.text


def sendEmail(title, content, sendto=None): # sendto 为发送列表

    from_addr = '' # 发出邮箱
    to_addr = [] # 目标邮箱
    from_smtp_server = '' # 发出邮箱的 SMTP 服务器地址
    from_smtp_port = '' # 发出邮箱的 SMTP 端口
    from_password = '' # 发出邮箱的密码

    msg = email.mime.multipart.MIMEMultipart()
    msg['to'] = to_addr
    msg['from'] = from_addr
    msg['subject'] = title
    content = content
    
    txt = email.mime.text.MIMEText(content)
    msg.attach(txt)
    
    smtp = smtplib.SMTP()
    smtp.connect(from_smtp_server, from_smtp_port) # 发出邮箱的 SMTP 服务器地址、端口
    smtp.login(from_addr, from_password) # 发出邮箱的账号、密码
    if sendto is None:
        sendto = [to_addr]
    if alsosendto and len(alsosendto) > 0:
        for emailAddr in alsosendto:
            smtp.sendmail(from_addr, emailAddr, str(msg))
    smtp.quit()


if __name__ == '__main__':
    sendEmail('title', 'content')
