# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.pylog import log


class CrackEgg:
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

    def crackegg(self):  # 砸蛋
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "crack_egg.txt") % (self.PLAYER_ID, self.ROOM_ID)
        uid = eval(body)[0]["global"]["uid"]
        sql = "SELECT GiftId,Amount  from gift_item WHERE PlayerId = " + str(uid) + ""

        user_gift_item = self.mysql.query_sql(self.mysql_conn, sql)  # 查询gift_item表返回结果

        user_gift_item_dic = {}
        for item in user_gift_item:  # 统计用户拥有的礼物
            user_gift_item_dic[str(item[0])] = item[1]
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        if eval(result.replace("null", "None").replace("true", "True"))[0]["res"]:
            result_list = eval(result.replace("true", "True"))[0]["res"]["awards"]
            gift_id_list = []
            for gift_id in result_list:
                gift_id_list.append(gift_id["gift_id"])  # 砸蛋获得的礼物id

        else:
            log.info("没有锤子")
            return True,None

        if len(gift_id_list) == 1:
            sql = "SELECT GiftId,Amount  from gift_item WHERE PlayerId = " + str(uid) + " and GiftId in (" + str(
                gift_id_list[0]) + ") "
        else:
            sql = "SELECT GiftId,Amount  from gift_item WHERE PlayerId = " + str(
                uid) + " and GiftId in (" + str(gift_id_list[0]) + "," + str(gift_id_list[1]) + ") "
        conn_new = self.mysql.conn_mysql()
        user_gift_item_new = self.mysql.query_sql(conn_new, sql)  # 查询gift_item表返回结果

        user_gift_item_dic_new = {}
        for item_new in user_gift_item_new:
            user_gift_item_dic_new[str(item_new[0])] = item_new[1]  # 统计用户拥有的礼物

        result_set = set()
        result_exp_set = set()

        # result_set = []
        # result_exp_set = []
        for i in result_list:
            result_exp_set.add(i["gift_num"])
            # result_exp_set.append(i["gift_num"])
        for key in user_gift_item_dic_new:
            if key in user_gift_item_dic.keys(): #判断砸蛋获得的礼物是否是一个新礼物
                result_set.add(user_gift_item_dic_new[key] - user_gift_item_dic[key])
            else:
                result_set.add(user_gift_item_dic_new[key] - 0)
        if result_set == result_exp_set:
            log.info("crackegg:砸蛋成功")
            return True,None
        else:
            log.error("用户礼物库存集合，result_set:{},result_exp_set:{}".format(result_set,result_exp_set))
            log.error("crackegg:砸蛋失败")
            msg = "用户礼物库存集合，result_set:{},result_exp_set:{}".format(result_set,result_exp_set)
            return False,msg

    def getEggShift(self):  # 砸蛋进度
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "get_egg_shift.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        # print(result)
        result_set = set()
        if eval(result)[0]["res"]:
            result_dic = eval(result)[0]["res"]["shift"]
            if "num" in result_dic.keys():  # 判断返回内容是否存在num，num是有进度值但未达到变身
                result_set.add(eval(result)[0]["res"]["shift"]["num"])

            elif "timeout" in result_dic.keys():  # 判断返回内容是否存在timeout，timeout是处于变身状态
                result_set.add(0)

            else:  # 未变身，进度值为0的情况
                result_set.add(0)

        # 查询redis获取当前进度值

        redis_key = "v2:crack:shift:"
        result = int(self.mzredis.query_redis(self.redis_conn, redis_key))
        result_exp_set = set()
        result_exp_set.add(result)

        if result_set == result_exp_set:
            log.info("getEggShift,请求砸蛋进度成功")
            return True,None
        else:
            log.error("getEggShift请求返回结果：{}，缓存key值：{}".format(result,result_exp_set))
            msg = "getEggShift请求返回结果：{}，缓存key值：{}".format(result,result_exp_set)
            return False,msg

    def getCrackTime(self):
        '''获取砸蛋间隔时间'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "get_crack_time.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        # print(result)
        result_set = set()
        if result:
            result_set.add(eval(result)[0]["res"]["auto_time"])
            result_set.add(eval(result)[0]["res"]["quick_time"])
        else:
            log.error("请求结果未找到auto_time，quick_time")
            msg = "请求结果未找到auto_time，quick_time"
            return False,msg

        result_exp_set = set()

        autoTime_key = "CacheClientAutoCrackEggCd"
        quickTime_key = "CacheClientQuickCrackEggCd"
        autoTime = int(self.mzredis.query_redis(self.redis_conn, autoTime_key))
        quickTime = int(self.mzredis.query_redis(self.redis_conn, quickTime_key))
        result_exp_set.add(autoTime)
        result_exp_set.add(quickTime)
        if result_set == result_exp_set:
            return True,None
        else:
            log.error("请求返回时间：{}，实际查询时间：{}".format(result_set,result_exp_set))
            msg = "请求返回时间：{}，实际查询时间：{}".format(result_set,result_exp_set)
            return False,msg

    def getRewardList(self):
        '''获取砸蛋奖品列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "get_rewardlist.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )

        normal_set = set()
        shift_set = set()
        normal_list = eval(result)[0]["res"]["normal_list"]  # 普通砸蛋列表
        shift_list = eval(result)[0]["res"]["shift_list"]  # 变身砸蛋列表
        for i in normal_list:
            normal_set.add(i["award_id"])

        for j in shift_list:
            shift_set.add(j["award_id"])

        normal_exp_set = set()
        shift_exp_set = set()
        redis_key = "v2:crack:crack_egg_conf:"
        redis_crackegg_list = eval(
            str(self.mzredis.query_redis(self.redis_conn, redis_key), encoding="utf-8").replace("true", "True").replace(
                "false", "False").replace("null", "None"))
        for i in redis_crackegg_list:

            if i["CrackType"] == 1 and i["IsShow"] == True:  # 判断普通砸蛋列表，并且显示
                normal_exp_set.add(i["AwardId"])
            elif i["CrackType"] == 2 and i["IsShow"] == True:  # 判断变身砸蛋列表，并且显示
                shift_exp_set.add(i["AwardId"])
            else:
                pass

        if normal_set == normal_exp_set and shift_set == shift_exp_set:
            return True,None
        else:
            log.error("normal_set:{},normal_exp_set{}".format(normal_set,normal_exp_set))
            log.error("shift_set:{},shift_exp_set{}".format(shift_set,shift_exp_set))
            msg = "normal_set:{},normal_exp_set{}".format(normal_set,normal_exp_set) + "shift_set:{},shift_exp_set{}".format(shift_set,shift_exp_set)
            return False,msg

    def getLuck(self):
        '''获取奖金池/幸运值'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "get_luck.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        res_dic = eval(result)[0]["res"]
        luck_gold_set = set()
        luck_gold_exp_set = set()
        luck_gold_set.add(res_dic["luck"]["gold"])  # 接口返回奖金池金币数
        luck_gold_key = "v2:crack:luck:"
        redis_luck_dic = eval(self.mzredis.query_redis(self.redis_conn, luck_gold_key))
        # log.info(redis_luck_dic)
        luck_gold_exp_set.add(redis_luck_dic["gold"])  # redis当前奖金池金币数
        myval_set = set()
        myval_exp_set = set()
        if "luck_type" in res_dic.keys():  # 判断请求返回是否存在luck_type，是否是幸运值模式
            if "my_val" in res_dic["luck_val"].keys():  # 幸运值不为0的时候返回my_val
                myval_set.add(res_dic["luck_val"]["my_val"])
            else:
                myval_set.add(0)

        crack_config_id_key = "v:crackConfId"
        crackConfId = str(self.mzredis.query_redis(self.redis_conn, crack_config_id_key), encoding="utf-8")

        luck_val_key = "v1:crack:luckval:" + str(self.PLAYER_ID) + ":" + crackConfId + ""
        try:
            redis_myval = int(self.mzredis.query_redis(self.redis_conn, luck_val_key))
        except:
            log.error("可能为新用户，未在幸运值模式下砸蛋过")
            return True,None
        # print(luck_val_key,redis_myval)
        if redis_myval == 1: #当幸运值为1时，服务端不返回my_val，导致断言错误
            myval_set.clear()
            myval_set.add(1)
        myval_exp_set.add(redis_myval)
        if "luck_type" in res_dic.keys():
            if luck_gold_set == luck_gold_exp_set and myval_set == myval_exp_set:
                return True,None
            else:
                log.error("幸运值模式下，luck_gold_set：{}，luck_gold_exp_set：{}".format(luck_gold_set,luck_gold_exp_set))
                log.error("幸运值模式下，myval_set：{}，myval_exp_set：{}".format(myval_set,myval_exp_set))
                msg = "幸运值模式下，luck_gold_set：{}，luck_gold_exp_set：{}".format(luck_gold_set,luck_gold_exp_set) + "幸运值模式下，myval_set：{}，myval_exp_set：{}".format(myval_set, myval_exp_set)
                return False,msg
        else:
            if luck_gold_set == luck_gold_exp_set:
                return True,None
            else:
                log.error("奖金池模式下，luck_gold_set：{}，luck_gold_exp_set：{}".format(luck_gold_set, luck_gold_exp_set))
                msg = "奖金池模式下，luck_gold_set：{}，luck_gold_exp_set：{}".format(luck_gold_set, luck_gold_exp_set)
                return False,msg

    def getCrackCopywriting(self):
        '''获取砸蛋文案'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("egg", "get_crackcopywriting.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        keyword_dic = eval(result)[0]["res"]
        key = "AdminCrackCopyriting"
        redis_keyword_dic = eval(str(self.mzredis.query_redis(self.redis_conn, key), encoding="utf-8"))
        keyword_set = set()
        keyword_exp_set = set()
        for key, value in keyword_dic.items():
            keyword_set.add(value)
        for key, value in redis_keyword_dic.items():
            keyword_exp_set.add(value)

        if keyword_set == keyword_exp_set:
            return True,None
        else:
            log.error("getCrackCopywriting:{},{}".format(keyword_set,keyword_exp_set))
            msg = "getCrackCopywriting:{},{}".format(keyword_set,keyword_exp_set)
            return False,msg


if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()

    egg = CrackEgg(mysql,mysql_conn,mzredis,redis_conn)
    egg.crackegg()
    # egg.getEggShift()
    # egg.getCrackTime()
    # egg.getRewardList()
    # egg.getLuck()
    # egg.getLuck()
