# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.pylog import log
from common.frame.result_handle import resp_handle


class Store():
    getdata = Getdata()
    PLAYER_ID = getdata.get_config_data("config.yaml")["test"]["player_id"]
    ROOM_ID = getdata.get_config_data("config.yaml")["test"]["room_id"]
    urlData = getdata.get_interface_url("interfaceurl.json")
    ITERFACEURL = eval(urlData)["interfaceurl"]

    def __init__(self,mysql,mysql_conn,mzredis,redis_conn):
        self.mysql = mysql
        self.mysql_conn = mysql_conn
        self.mzredis = mzredis
        self.redis_conn = redis_conn

    def getStoreTabs(self):
        '''获取商城标签'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "getStoreTab.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        sql = "SELECT name FROM xhx_log.store_tabs WHERE is_show = 1"
        result = self.mysql.query_sql(self.mysql_conn, sql)
        result_set = set()
        result_exp_set = set()
        r = eval(r)
        for r_name in r[0]['res']['tabs']:
            result_set.add(r_name['name'])
        for name in result:
            result_exp_set.add(name[0])
        if result_set == result_exp_set:
            return True, None
        else:
            msg = "getstoreTabs error:{},expect：{}".format(result_set, result_exp_set)
            return False, msg

    def getPacketTabs(self):
        '''获取背包所有标签'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "getPacketTab.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        sql = "SELECT name FROM xhx_log.packet_tabs WHERE is_show = 1"
        result = self.mysql.query_sql(self.mysql_conn, sql)
        result_set = set()
        result_exp_set = set()
        r = eval(r)
        for r_name in r[0]['res']['tabs']:
            result_set.add(r_name['name'])
        for name in result:
            result_exp_set.add(name[0])
        if result_set == result_exp_set:
            return True, None
        else:
            msg = "getstoreTabs error:{},expect：{}".format(result_set, result_exp_set)
            return False, msg

    def effectList(self):
        '''获取背包中的特效列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "effectList.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(r):
            return True, None
        else:
            return False, r

    def packetList(self):
        '''获取背包中的物品'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "packetList.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(r):
            return True, None
        else:
            return False, r

    def buy(self):
        '''商城购买'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "buy_hammer.txt") % (self.PLAYER_ID, self.ROOM_ID)
        a_dict = eval((eval(body)[0]['param']))['id']
        a_num = eval((eval(body)[0]['param']))['num']
        # 查询原始金币
        Useroldmoney = "SELECT Gold from money WHERE PlayerId = {} ".format(self.PLAYER_ID)
        sqlUseroldmoney = self.mysql.query_sql(self.mysql_conn, Useroldmoney)[0][0]
        # 查询物品id
        giftid = "SELECT AssetId FROM xhx_log.conf_stores WHERE Id = {}".format(a_dict)
        sqlgiftid = self.mysql.query_sql(self.mysql_conn, giftid)[0][0]
        # 查询原本背包物品个数
        Useroldgift = "SELECT Amount FROM xhx.gift_item WHERE playerId = {} AND GiftId = {}".format(self.PLAYER_ID, sqlgiftid)
        sqlrqs = self.mysql.query_sql(self.mysql_conn, Useroldgift)
        if len(sqlrqs) != 0:   #判断用户是否首次购买该礼物
            sqlUseroldgift = sqlrqs[0][0]
        else:
            sqlUseroldgift = 0
        # 查询原本用户的财富值
        Useroldwealth = "SELECT Wealth FROM xhx.player WHERE Id = {}".format(self.PLAYER_ID)
        sqlUseroldwealth = self.mysql.query_sql(self.mysql_conn, Useroldwealth)[0][0]
        # 查询商城配置表商品的价格
        sqlPrice = "SELECT Price FROM xhx_log.conf_stores WHERE Id = {}".format(a_dict)
        sqlsqlPrice = self.mysql.query_sql(self.mysql_conn, sqlPrice)[0][0]
        result_set = set()
        result_exp_set = set()
        result_exp_set.add(sqlsqlPrice * a_num)
        if sqlUseroldmoney >= sqlsqlPrice * a_num:
            r = httpfunc.http_request_post(self.ITERFACEURL, body)
            r = eval(r)[0]['res']['gold']
            result_set.add(r)
            if result_set == result_exp_set:
                # 查询新的金币数量
                Usernewmoney = "SELECT Gold from money WHERE PlayerId = {} ".format(self.PLAYER_ID)
                sqlUsernewmoney = self.mysql.query_sql(self.mysql_conn, Usernewmoney)[0][0]
                # 查询新的物品个数
                Usernewgift = "SELECT Amount FROM xhx.gift_item WHERE playerId = {} AND GiftId = {}".format(
                    self.PLAYER_ID, sqlgiftid)
                sqlUsernewgift = self.mysql.query_sql(self.mysql_conn, Usernewgift)[0][0]
                # 查询新的财富值
                Usernewwealth = "SELECT Wealth FROM xhx.player WHERE Id = {}".format(self.PLAYER_ID)
                sqlUsernewwealth = self.mysql.query_sql(self.mysql_conn, Usernewwealth)[0][0]
                if sqlUsernewmoney == sqlUseroldmoney - sqlsqlPrice * a_num and \
                        sqlUsernewgift == sqlUseroldgift + a_num and \
                        sqlUsernewwealth == sqlUseroldwealth + sqlsqlPrice * a_num:
                    return True, None
                else:
                    msg = "原本金币数：{}，购买后金币数：{}，应该减少的金币：{}".format(sqlUseroldmoney, sqlUsernewmoney,
                                                                 sqlsqlPrice * a_num) + "原本物品个数：{}，购买后礼物个数：{}，应该增" \
                                                                                        "加的物品个数：{}".format(
                        Useroldgift, Usernewgift, a_num) + "原本财富值：{}，购买后的财富值：{}，应该增加的财富值：{}".format(sqlUseroldwealth, sqlUsernewwealth, sqlsqlPrice * a_num)
            else:
                msg = "商城配置的金额:{},购买时候消耗的金额:{}".format(result_exp_set, result_set)
                return False, msg
        else:
            msg = "用户金币不足购买礼物"
            return False, msg

    def getStoreConf(self):
        '''获取商城物品配置'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "getStoreconf.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        sql = "SELECT Id FROM xhx_log.conf_stores"
        result = self.mysql.query_sql(self.mysql_conn, sql)
        result_set = set()
        result_exp_set = set()
        r = eval(r)
        for r_name in r[0]['res']['store']:
            result_set.add(r_name['id'])
        for name in result:
            result_exp_set.add(name[0])
        if result_set == result_exp_set:
            return True, None
        else:
            msg = "getStoreConf error:{},expect：{}".format(result_set, result_exp_set)
            return False, msg

    def getExchangeConf(self):
        '''获取兑换配置'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("store", "getExchangeconf.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(r):
            return True, None
        else:
            return False, r



if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()
    s = Store(mysql,mysql_conn,mzredis,redis_conn)
    s.buy()
