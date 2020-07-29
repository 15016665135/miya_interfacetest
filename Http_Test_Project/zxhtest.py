
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.pylog import log
from common.frame.result_handle import resp_handle
getdata = Getdata()
PLAYER_ID = getdata.get_config_data("config.yaml")["test"]["player_id"]
ROOM_ID = getdata.get_config_data("config.yaml")["test"]["room_id"]
urlData = getdata.get_interface_url("interfaceurl.json")
ITERFACEURL = eval(urlData)["interfaceurl"]
# mysql = MySql()
# mysql_conn = mysql.conn_mysql()
#
# mzredis = MzRedis()
# redis_conn = mzredis.conn_redis()

# httpfunc = Httpfunc()
# body = getdata.get_case_data("store", "buy_hammer.txt") % (PLAYER_ID, ROOM_ID)
# r = httpfunc.http_request_post(ITERFACEURL, body)
# r = eval(r)[0]['res']['gold']
# # print(type(r))
# Useroldmoney = "SELECT Gold from money WHERE PlayerId = {} ".format(PLAYER_ID)
# sqlUseroldmoney = mysql.query_sql(mysql_conn, Useroldmoney)[0][0]
# print(sqlUseroldmoney)

httpfunc = Httpfunc()
body = getdata.get_case_data("user", "getRank.txt") % (PLAYER_ID, ROOM_ID)
result = httpfunc.http_request_post(ITERFACEURL, body)
r = eval(result)[0]['res']
print("week_rank" in r.keys())