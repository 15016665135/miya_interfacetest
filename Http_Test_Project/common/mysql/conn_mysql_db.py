import pymysql
from common.frame.get_data import Getdata
from common.frame.pylog import log
import time

class MySql:

    def conn_mysql(self):
        db_data = Getdata().get_config_data("config.yaml")
        db_ip = db_data["test"]["db_ip"]
        db_port = db_data["test"]["db_port"]
        user_name = db_data["test"]["user_name"]
        user_pwd = str(db_data["test"]["user_pwd"])
        db_name = db_data["test"]["db_name"]

        try:
            log.debug("连接mysql，ip:{},port:{}".format(db_ip,db_port))
            connect = pymysql.connect(host=db_ip, port=db_port, user=user_name, passwd=user_pwd, db=db_name, charset='utf8')
            return connect
        except Exception as err:
            log.error("连接mysql失败：{}".format(err))
            return

    def query_sql(self, connect, sql):
        time.sleep(0.5)  # 查询数据库休眠2秒，防止数据更新不及时
        cursor = connect.cursor()
        try:
            log.debug("执行sql:{}".format(sql))
            cursor.execute(sql)
            cursor.close()
            connect.commit()
            return cursor.fetchall()
        except Exception as err:
            log.error("执行sql错误:{}".format(err))
            return


if __name__ == '__main__':
    mysql = MySql()
    connect = mysql.conn_mysql()
    sql = "SELECT * FROM xhx_log.log_box limit 2"
    print(mysql.query_sql(connect, sql))
