import unittest
import time
from common.report import HTMLTestRunner_cn
import os
from common.frame.send_mail import sendmail_or_not
import subprocess
import sys

curPath = os.path.dirname(os.path.realpath(__file__))
report_path = os.path.join(curPath, "report")
if not os.path.exists(report_path): os.mkdir(report_path)
case_path = os.path.join(curPath, "case")


def add_case(casepath=case_path, rule="test*.py"):
    discover = unittest.defaultTestLoader.discover(casepath,
                                                   pattern=rule, )

    return discover

def run_case(all_case, reportpath=report_path):
    '''执行所有的用例, 并把结果写入测试报告'''
    reportname = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
    num = sys.version_info[2]
    if num == 1:   #判断是否是构建机，注个人电脑信息不同不一定都可用，1为本地电脑
        htmlreport = reportpath + r"\\"+reportname+".html"
    # print("测试报告生成地址：%s" % htmlreport)
    else:
        htmlreport = "E:\\jenkins\\workspace\\caramel_test" + r"\\"+reportname+".html"  #构建机上指定的报告路径
    fp = open(htmlreport, "wb")
    runner = HTMLTestRunner_cn.HTMLTestRunner(stream=fp,
                                              verbosity=2,
                                              title="测试报告",
                                              description="用例执行情况")

    # 调用add_case函数返回值
    runner.run(all_case)
    fp.close()
    return htmlreport

def kill_pid():
    '''执行后杀掉转发端口'''
    try:
        for i in range(10):
            cmd3307_data = os.popen("netstat -ano | findstr 3308")
            cmd3307_list = cmd3307_data.read().split()
            l_index = cmd3307_list.index("LISTENING")
            cmd1 = "taskkill /pid " + str(cmd3307_list[l_index + 1]) + " -t -f"
            os.popen(cmd1)
            time.sleep(1)
    except:
        print("该端口号3308找不到对应的LISTENING进程")

    try:
        for j in range(10):
            cmd6380_data = os.popen("netstat -ano | findstr 6381")
            cmd6380_list = cmd6380_data.read().split()
            l = cmd6380_list.index("LISTENING")
            print(l)
            cmd2 = "taskkill /pid " + str(cmd6380_list[l + 1]) + " -t -f"
            os.popen(cmd2)
            time.sleep(1)
    except Exception as e:
        print(e)
        print("该端口号6381找不到对应的LISTENING进程")


if __name__ == "__main__":
    pro_path = os.path.dirname(__file__)
    mysql_path = os.path.join(pro_path,"start_ssh_server_mysql.py")
    redis_path = os.path.join(pro_path,"start_ssh_server_redis.py")
    subprocess.Popen("python "+ mysql_path)
    subprocess.Popen("python " + redis_path)
    cases = add_case()
    repor_path = run_case(cases)
    sendmail_or_not(repor_path)
    kill_pid()
