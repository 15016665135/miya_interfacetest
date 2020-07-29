from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_mysql_db import MySql
from common.mysql.conn_redis_db import MzRedis
from common.frame.pylog import log
import time


class Gift:
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


    def getGiftConfig(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("gift", "get_gift_config.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )

    def presentGift(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("gift", "present_gift.txt") % (self.PLAYER_ID)

        giftId = eval(eval(body)[0]["param"])["gift_entry"]
        giftNum = eval(eval(body)[0]["param"])["gift_num"]
        cofigKey = "CacheGiftConf"
        giftConfig = eval(
            str(self.mzredis.query_redis(self.redis_conn, cofigKey), encoding="utf-8").replace("null", "None").replace(
                "false", "False").replace("true", "True"))
        giftList = giftConfig["gifts"]
        sqlGiftAmount = "SELECT Amount from gift_item WHERE PlayerId = {} and GiftId = {}".format(self.PLAYER_ID,
                                                                                                  giftId)
        sqlGiftAmountRes = self.mysql.query_sql(self.mysql_conn, sqlGiftAmount)

        if sqlGiftAmountRes:
            giftAmount = sqlGiftAmountRes[0][0]
        else:
            giftAmount = None
        giftPrice = 0
        giftPercent = 0
        for i in giftList:
            if i["GiftId"] == giftId:
                giftPrice = i["Price"]
                giftPercent = i["Percent"]
                break
            else:
                pass
        '''查下送礼者当前的财富值和金币数额，收礼者的魅力值'''
        sqlWealth = "SELECT Wealth FROM player WHERE id = {}".format(self.PLAYER_ID)
        sendGiftUserWealth = self.mysql.query_sql(self.mysql_conn, sqlWealth)[0][0]
        sqlGlod = "SELECT Gold FROM money WHERE PlayerId = {}".format(self.PLAYER_ID)
        sendGiftUserGold = self.mysql.query_sql(self.mysql_conn, sqlGlod)[0][0]
        acceptGiftUserId = eval(eval(body)[0]["param"])["to_id"]
        sqlCharm = "SELECT Charm FROM player WHERE id = {}".format(acceptGiftUserId)
        acceptGiftUserCharm = self.mysql.query_sql(self.mysql_conn, sqlCharm)[0][0]
        if sendGiftUserGold > giftPrice * giftNum:
            '''执行送礼'''
            httpfunc.http_request_post(self.ITERFACEURL, body, )
        else:
            pass

        '''送礼后送礼者和收礼者的财富魅力金币'''
        sendGiftUserWealthNew = self.mysql.query_sql(self.mysql_conn, sqlWealth)[0][0]
        sendGiftUserGoldNew = self.mysql.query_sql(self.mysql_conn, sqlGlod)[0][0]
        acceptGiftUserCharmNew = self.mysql.query_sql(self.mysql_conn, sqlCharm)[0][0]

        if giftAmount:  # 赠送库存礼物
            if sendGiftUserWealthNew - sendGiftUserWealth == 0 and \
                    acceptGiftUserCharmNew - acceptGiftUserCharm == int(giftPrice * giftNum * (
                    giftPercent / 100)):   #由于后台取整，无浮点数，使用int取整
                return True, None
            else:
                log.error("赠送库存礼物，送礼者原有财富值{}，当前财富值{}".format(sendGiftUserWealth, sendGiftUserWealthNew))
                log.error("赠送库存礼物，收礼者原有魅力值{}，当前魅力值{}，增加的魅力值{}".format(acceptGiftUserCharm, acceptGiftUserCharmNew,
                                                                      int(giftPrice * giftNum * (
                                                                              giftPercent / 100))))
                msg = "赠送库存礼物，送礼者原有财富值{}，当前财富值{}".format(sendGiftUserWealth,
                                                         sendGiftUserWealthNew) + "赠送库存礼物，收礼者原有魅力值{}，当前魅力值{}，增加的魅力值{}".format(
                    acceptGiftUserCharm, acceptGiftUserCharmNew,
                    giftPrice * giftNum * (
                            giftPercent / 100))
                return False, msg
        else:  # 花金币赠送礼物
            if sendGiftUserWealthNew - sendGiftUserWealth == giftPrice * giftNum and \
                    acceptGiftUserCharmNew - acceptGiftUserCharm == int(giftPrice * giftNum * (
                    giftPercent / 100)) and sendGiftUserGold - sendGiftUserGoldNew == giftPrice * giftNum:
                return True, None
            else:
                log.error("花金币赠送礼物，送礼者原有财富值{}，当前财富值{},增加的财富值{}".format(sendGiftUserWealth, sendGiftUserWealthNew,
                                                                     giftPrice * giftNum))
                log.error("花金币赠送礼物，收礼者原有魅力值{}，当前魅力值{}，增加的魅力值{}".format(acceptGiftUserCharm, acceptGiftUserCharmNew,
                                                                       int(giftPrice * giftNum * (
                                                                               giftPercent / 100))))
                msg = "花金币赠送礼物，送礼者原有财富值{}，当前财富值{},增加的财富值{}".format(sendGiftUserWealth, sendGiftUserWealthNew,
                                                                 giftPrice * giftNum) + "花金币赠送礼物，收礼者原有魅力值{}，当前魅力值{}，增加的魅力值{}".format(
                    acceptGiftUserCharm, acceptGiftUserCharmNew,
                    int(giftPrice * giftNum * (
                            giftPercent / 100)))
                return False, msg

    def buyGift(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("gift", "buy_gift.txt") % (self.PLAYER_ID, self.ROOM_ID)
        giftId = eval(eval(body)[0]["param"])["gift_id"]
        giftAmount = eval(eval(body)[0]["param"])["amount"]
        sqlWealth = "SELECT Wealth FROM player WHERE id = {}".format(self.PLAYER_ID)
        userWealth = self.mysql.query_sql(self.mysql_conn, sqlWealth)[0][0]
        sqlGiftAmount = "SELECT Amount from gift_item WHERE PlayerId = {} and GiftId = {}".format(self.PLAYER_ID,
                                                                                                  giftId)
        sqlUserGold = "SELECT Gold from money WHERE PlayerId = {} ".format(self.PLAYER_ID)
        userGold = self.mysql.query_sql(self.mysql_conn, sqlUserGold)[0][0]
        userGiftAmountRes = self.mysql.query_sql(self.mysql_conn, sqlGiftAmount)
        if userGiftAmountRes:
            userGiftAmount = userGiftAmountRes[0][0]
        else:
            userGiftAmount = 0

        cofigKey = "CacheGiftConf"
        giftConfig = eval(
            str(self.mzredis.query_redis(self.redis_conn, cofigKey), encoding="utf-8").replace("null", "None").replace(
                "false", "False").replace("true", "True"))
        giftList = giftConfig["gifts"]

        for i in giftList:
            if i["GiftId"] == giftId:
                giftPrice = i["Price"]
                break
            else:
                pass

        if userGold >= giftPrice * giftAmount:

            httpfunc.http_request_post(self.ITERFACEURL, body, )
        else:
            log.info("金币不足")
            msg = "金币不足"
            return False, msg
        userWealthNew = self.mysql.query_sql(self.mysql_conn, sqlWealth)[0][0]
        userGiftAmountNew = self.mysql.query_sql(self.mysql_conn, sqlGiftAmount)[0][0]
        userGoldNew = self.mysql.query_sql(self.mysql_conn, sqlUserGold)[0][0]

        if userWealthNew - userWealth == giftPrice * giftAmount and \
                userGiftAmountNew - userGiftAmount == giftAmount and \
                userGold - userGoldNew == giftPrice * giftAmount:
            log.info("buyGift,购买礼物成功")
            return True, None
        else:
            log.error("原财富值{}，当前财富值{}，应该增加的财富值{}".format(userWealth, userWealthNew, giftPrice * giftAmount))
            log.error("原礼物数{}，当前礼物数{}，应该增加礼物数{}".format(userGiftAmount, userGiftAmountNew, giftAmount))
            log.error("原金币{}，当前金币{}，应该减少金币{}".format(userGold, userGoldNew, giftPrice * giftAmount))
            log.error("buyGift,购买礼物失败")
            msg = "原财富值{}，当前财富值{}，应该增加的财富值{}".format(userWealth, userWealthNew,
                                                     giftPrice * giftAmount) + "原礼物数{}，当前礼物数{}，应该增加礼物数{}".format(
                userGiftAmount, userGiftAmountNew, giftAmount) + "原金币{}，当前金币{}，应该减少金币{}".format(userGold, userGoldNew,
                                                                                                giftPrice * giftAmount)
            return False, msg

    def getGiftWall(self):

        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("gift", "get_gift_wall.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body, )
        giftWallList = []
        if len(eval(result)[0]["res"]) != 0:
            giftWallList = eval(result)[0]["res"]["giftWall"]
        else:
            pass

    def transferGift(self):
        '''物品转赠'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("gift", "transfer_gift.txt") % (self.PLAYER_ID, self.ROOM_ID)
        param = eval(eval(body)[0]["param"])
        giftEntry = param["gift_entry"]
        giftNum = param["gift_num"]
        toId = param["to_id"]
        userId = self.PLAYER_ID
        sqlUidGiftItem = "SELECT Amount FROM gift_item WHERE  PlayerId = {} and GiftId = {}".format(userId, giftEntry)
        sqlUidGiftItemRes = self.mysql.query_sql(self.mysql_conn, sqlUidGiftItem)
        sqlToIdGiftItem = "SELECT Amount FROM gift_item WHERE  PlayerId = {} and GiftId = {}".format(toId, giftEntry)
        sqlToIdGiftItemRes = self.mysql.query_sql(self.mysql_conn, sqlToIdGiftItem)
        if len(sqlUidGiftItemRes):
            userGiftNum = sqlUidGiftItemRes[0][0]
        else:
            userGiftNum = 0
            log.info("用户无库存，无法赠送")
            return True, None
        if userGiftNum < giftNum:
            log.info("库存不足，无法赠送")
            return True, None
        else:
            httpfunc.http_request_post(self.ITERFACEURL, body, )

        if len(sqlToIdGiftItemRes):
            toIdGiftNum = sqlToIdGiftItemRes[0][0]
        else:
            toIdGiftNum = 0

        sqlUidGiftItemNewRes = self.mysql.query_sql(self.mysql_conn, sqlUidGiftItem)
        userGiftNumNew = None
        if len(sqlUidGiftItemNewRes):
            userGiftNumNew = sqlUidGiftItemNewRes[0][0]

        sqlToIdGiftItemNewRes = self.mysql.query_sql(self.mysql_conn, sqlToIdGiftItem)
        toIdGiftNumNew = None
        if len(sqlToIdGiftItemNewRes):
            toIdGiftNumNew = sqlToIdGiftItemNewRes[0][0]

        if userGiftNum - userGiftNumNew == giftNum and toIdGiftNumNew - toIdGiftNum == giftNum:
            return True, None
        else:
            log.error("赠送者，原有的礼物库存：{}，当前的礼物库存：{}".format(userGiftNum, userGiftNumNew))
            log.error("收礼者，原有的礼物库存：{}，当前的礼物库存：{}".format(toIdGiftNum, toIdGiftNumNew))
            msg = "赠送者，原有的礼物库存：{}，当前的礼物库存：{}".format(userGiftNum, userGiftNumNew) + "收礼者，原有的礼物库存：{}，当前的礼物库存：{}".format(
                toIdGiftNum, toIdGiftNumNew)
            return False, msg


if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()
    g = Gift(mysql,mysql_conn,mzredis,redis_conn)
    g.buyGift()
