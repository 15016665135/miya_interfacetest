from common.frame.pylog import log
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import sys

def sendmail(report_file_path,bodytext,my_user,my_sender, my_pass):
    try:
        message = MIMEMultipart()
        message['From'] = Header("测试组", 'utf-8')
        message['To'] = Header("测试", 'utf-8')
        message.attach(MIMEText(bodytext, 'plain', 'utf-8'))
        subject = '接口测试结果'
        message['Subject'] = Header(subject, 'utf-8')
        att1 = MIMEText(open(report_file_path, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="jtreport.html"'
        message.attach(att1)
        server = smtplib.SMTP("smtp.mxhichina.com", 80)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, my_user, message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        log.debug("发送邮件")
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        log.error("发送邮件异常：{}".format(err))

def sendmail_or_not(report_file_path):
    # 设置邮件基本信息
    my_sender = 'linchuanhui@xinyu100.com'  # 发件人邮箱账号
    my_pass = 'Lch15016665135'  # 发件人邮箱密码
    num = sys.version_info[2]
    if num == 1:  # 判断是否是构建机，注个人电脑信息不同不一定都可用，1为本地电脑
        my_user = ['linchuanhui@xinyu100.com']  # 收件人邮箱账号
    else:
        my_user = ['miya-qa@xinyu100.com']

    error_msg = '<span class="tj errorCase">Error</span>'
    fail_msg = '<span class="tj failCase">Failure</span>'
    with open(report_file_path,encoding='utf-8') as f:
        report_f = f.read()
    if fail_msg in report_f and error_msg not in report_f:
        text = '接口测试自动化,测试报告发现有用例测试不通过,测试结果请看附件'
        sendmail(report_file_path,text,my_user,my_sender, my_pass)
        return True
    elif error_msg in report_f:
        my_user = ['zhangxiaohui@xinyu100.com']
        text = '接口测试自动化,测试报告发现程序执行有错误,具体错误请看附件'
        sendmail(report_file_path,text,my_user,my_sender, my_pass)
        return True
    else:
        log.debug("测试过程中未发现错误")


if __name__ == '__main__':
    # report_file_path ="E:\\PycharmProjects\Http_Test_Project\\report\\2020-03-23_14-15-25.html"
    # report_file_path = "E:\\PycharmProjects\Http_Test_Project\\report\\2020-03-23_11-06-32.html"
    report_file_path = "C:\\Users\\Administrator\\Desktop\\jtreport-2.html"
    # sendmail(report_file_path)
    sendmail_or_not(report_file_path)

