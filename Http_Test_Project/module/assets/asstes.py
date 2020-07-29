# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.result_handle import resp_handle
from common.frame.pylog import log

class Assets:
    getdata = Getdata()
    PLAYER_ID = getdata.get_config_data("config.yaml")["test"]["player_id"]
    ROOM_ID = getdata.get_config_data("config.yaml")["test"]["room_id"]
    urlData = getdata.get_interface_url("interfaceurl.json")
    ITERFACEURL = eval(urlData)["interfaceurl"]

    def __init__(self, mysql, mysql_conn, mzredis, redis_conn):
        self.mysql = mysql
        self.mysql_conn = mysql_conn
        self.mzredis = mzredis
        self.redis_conn = redis_conn

    def getmoney(self):
        '''获取个人资产'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "getmoney.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            money = eval(result)[0]["res"]["money"]
            gold = money["gold"]  # 请求返回金币
            gift_ticket = money["gift_ticket"]  # 请求返钻石
            sql = "SELECT Gold,GiftTicket FROM money WHERE PlayerId = {}".format(self.PLAYER_ID)
            sqlres = self.mysql.query_sql(self.mysql_conn, sql)
            sqlgold = sqlres[0][0]
            sqlgift_ticket = sqlres[0][1]
            if gold == sqlgold and gift_ticket == sqlgift_ticket:  # 判断返回的金币和钻石是否与实际的一致
                return True, None
            else:
                msg = "请求返回得结果和查询结果不一致,gold:{},sqlgold{},gift_ticket:{},sqlgift_ticket:{}".format(gold, sqlgold,
                                                                                                  gift_ticket,
                                                                                                  sqlgift_ticket)
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def getbag(self):
        '''获取用户背包礼物信息'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "getbag.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            items_list = eval(result)[0]["res"]["items"]
            sql = "SELECT GiftId,Amount FROM gift_item WHERE PlayerId = {}".format(self.PLAYER_ID)
            res_dic = {}  # 请求返回的礼物数量
            sql_dic = {}  # 查询sql返回的礼物数量
            for item in items_list:
                if "amount" in item.keys():
                    res_dic[item["gift_id"]] = item["amount"]
                else:  # 当key amount不存在时，礼物数量为0
                    res_dic[item["gift_id"]] = 0
            sqlres = self.mysql.query_sql(self.mysql_conn, sql)

            for i in sqlres:
                sql_dic[i[0]] = i[1]
            if res_dic == sql_dic:
                return True, None
            else:
                msg = "请求返回的礼物数量和查询结果不一致，res_dic：{},sql_dic：{}".format(res_dic, sql_dic)
                return False, msg

        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def geteffect(self):
        '''获取用户使用的特效'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "geteffect.txt") % (self.PLAYER_ID, self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            msg = "请求返回错误信息：{}".format(result)
            return False, msg

    def geteffectconf(self):
        '''获取特效配置'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "geteffectconf.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        res_set = set()
        sql_set = set()
        if "nil" in result:
            itmes_dic = eval(result)[0]["res"]["list"]
            for key,value in itmes_dic.items(): #将请求配置的特效id添加到集合res_set
                res_set.add(key)
            sql = "SELECT id FROM conf_effect"
            sqlres = self.mysql.query_sql(self.mysql_conn,sql)
            for i in sqlres:
                sql_set.add(str(i[0]))
            if res_set == sql_set:
                return True,None
            else:
                msg = "请求和查询获取的特效id不一致，res_set：{}，sql_set：{}".format(res_set,sql_set)
                return False,msg
        else:
            msg = "请求返回错误：{}".format(result)
            return False,msg

    def h5money(self):
        '''获取个人资产'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "h5money.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            money = eval(result)[0]["res"]["money"]
            gold = money["gold"]  # 请求返回金币
            gift_ticket = money["gift_ticket"]  # 请求返钻石
            sql = "SELECT Gold,GiftTicket FROM money WHERE PlayerId = {}".format(self.PLAYER_ID)
            sqlres = self.mysql.query_sql(self.mysql_conn, sql)
            sqlgold = sqlres[0][0]
            sqlgift_ticket = sqlres[0][1]
            if gold == sqlgold and gift_ticket == sqlgift_ticket:  # 判断返回的金币和钻石是否与实际的一致
                return True, None
            else:
                msg = "请求返回得结果和查询结果不一致,gold:{},sqlgold{},gift_ticket:{},sqlgift_ticket:{}".format(gold, sqlgold,
                                                                                                  gift_ticket,
                                                                                                  sqlgift_ticket)
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def useeffect(self):
        '''使用特效'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("assets", "geteffect.txt") % (self.PLAYER_ID, self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        res_dic = eval(result)[0]["res"]
        if "effect" in res_dic.keys():   #先判断用户是否拥有特效
            effect_id = res_dic["effect"][0]["id"]  #默认获取第一个特效进行佩戴
            body2 = self.getdata.get_case_data("assets", "useeffect.txt") % (
            effect_id, self.PLAYER_ID, self.PLAYER_ID)
            result2 = httpfunc.http_request_post(self.ITERFACEURL, body2)
            if resp_handle(result2):
                return True,None
            else:
                msg = "请求返回错误：{}".format(result2)
                return False,msg
        else:
            msg = "用户没有特效"
            log.info(msg)
            return True,None

if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()
    a = Assets(mysql,mysql_conn,mzredis,redis_conn)
    a.useeffect()
