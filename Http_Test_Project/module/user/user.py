# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.pylog import log
from common.frame.result_handle import resp_handle


class User:
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

    def getPlayer(self):
        '''获取用户信息'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "get_player.txt") % (self.PLAYER_ID, self.ROOM_ID)
        sqlUserInfo = "SELECT id,Nickname,Sex,Icon,Charm,CharmLevel,WealthLevel,Wealth,UNIX_TIMESTAMP(CreateAt) FROM player WHERE Id = {}".format(
            self.PLAYER_ID)
        sqlUserInfoRes = self.mysql.query_sql(self.mysql_conn, sqlUserInfo)
        userInfo_set = set()    #实际结果，将http请求返回结果，放入到集合里
        userInfo_exp_set = set()  #期望结果，将查询table的结果，放入到集合里
        if len(sqlUserInfoRes):
            userInfo = sqlUserInfoRes[0]
            for i in userInfo:
                userInfo_exp_set.add(i)
        else:
            log.info("输入id不存在")
            return True, None
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        userInfoDic = eval(result)[0]["res"]["player"]
        if len(userInfoDic) == 0:
            log.info("请求id不存在")
            return True, None
        else:
            for key, value in userInfoDic.items():
                if key == "online_exp" or key == "flags2" or key == "flags":  # 在线时长更新mysql存在延迟，导致数据不一致，故跳过该项校验,不知道为什么会出现flags2
                    pass
                else:
                    userInfo_set.add(value)
        # log.info(userInfoDic)
        # log.info(userInfo_set)
        # log.info(userInfo_exp_set)

        sql_id2 = "SELECT id2 FROM player WHERE Id = {}".format(self.PLAYER_ID)
        sql_id2Res = self.mysql.query_sql(self.mysql_conn, sql_id2)
        id2 = sql_id2Res[0][0]  #判断用户是否有靓号
        if id2 > 0:
            userInfo_exp_set.add(id2)
        if userInfo_set == userInfo_exp_set:
            return True, None
        else:
            msg = "userInfo_set:{},userInfo_exp_set:{}".format(userInfo_set, userInfo_exp_set)
            return False, msg

    def setUserInfoSignature(self):
        '''设置用户信息'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "set_userinfo_signature.txt") % (self.PLAYER_ID, self.ROOM_ID)
        body = body
        reqSignature = eval(eval(body)[0]["param"])["signature"]
        key = "ONOFFSTATUS:41"
        value = self.mzredis.query_redis(self.redis_conn, key)
        OnOffDic = eval(value.decode("utf-8"))
        if "status" in OnOffDic.keys():
            result = httpfunc.http_request_post(self.ITERFACEURL, body)
            result = result.replace("null", "None")
            detail = eval(eval(result)[0]["err"])["detail"]
            if detail == "功能维护中":  #审核开关开启时，无法修改数据
                return True, None
            else:
                return False
        else:
            httpfunc.http_request_post(self.ITERFACEURL, body)
            sql = "SELECT signature FROM user_info WHERE userId = {}".format(self.PLAYER_ID)
            sqlRes = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sqlRes) != 0:
                signature = sqlRes[0][0]

            else:
                log.info("查询userid不存在")
                msg = "查询userid不存在"
                return False, msg
            if signature == reqSignature:  #signature数据查询的签名，reqSignature请求参数的签名
                return True, None
            else:
                msg = "signature:{},reqSignature:{}"
                return False, msg

    def getOnOffStatus(self):
        '''获取某个开关状态'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "get_onoffstatus.txt") % (self.PLAYER_ID, self.ROOM_ID)
        onoffType = eval(eval(body)[0]["param"])["type"]
        key = "ONOFFSTATUS:" + str(onoffType)
        value = self.mzredis.query_redis(self.redis_conn, key)
        if value == None:
            log.info("输入type值不存在")
            msg = "输入type值不存在"
            return False, msg
        else:
            onoffExpDic = eval(value.decode("utf-8"))
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        onoffDic = eval(result)[0]["res"]["on_off"]
        onoffExpSet = set()
        onoffSet = set()
        for key, value in onoffExpDic.items():
            if key == "status" or key == "type":
                onoffExpSet.add(onoffExpDic[key])
                onoffSet.add(onoffDic[key])

        if onoffSet == onoffExpSet:
            return True, None
        else:
            msg = "onoffSet:{},onoffExpSet{}".format(onoffSet, onoffExpSet)
            return False, msg

    def diamondChangeCoin(self):  # 个人钻石兑换金币
        pwd = "123456"  # 兑换密码
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "diamondchangcoin.txt") % (pwd, self.PLAYER_ID, self.ROOM_ID)
        inputGiftTicket = eval(eval(body)[0]["param"])["value"][0] #输入的兑换值
        sql = "SELECT GiftTicket,Gold FROM money WHERE PlayerId = {}".format(self.PLAYER_ID)
        sqlRes = self.mysql.query_sql(self.mysql_conn, sql) #用户兑换之前
        # log.info(sqlRes)
        giftTicket = sqlRes[0][0] #用户兑换之前的钻石
        Gold = sqlRes[0][1] #用户兑换之前的金币
        import time
        time.sleep(10)
        httpfunc.http_request_post(self.ITERFACEURL, body) #请求兑换
        sqlResNew = self.mysql.query_sql(self.mysql_conn, sql)#用户兑换之后
        giftTicketNew = sqlResNew[0][0] #用户兑换之后的钻石
        GoldNew = sqlResNew[0][1]   #用户兑换之后的金币
        if inputGiftTicket > giftTicket:
            log.info("输入兑换钻石数大于当前拥有的钻石数")
            msg = "输入兑换钻石数大于当前拥有的钻石数"
            return False, msg
        if giftTicket - giftTicketNew == inputGiftTicket and GoldNew - Gold == inputGiftTicket:
            return True, None
        else:
            msg = "giftTicket - giftTicketNew:{},inputGiftTicket{},GoldNew - Gold:{}".format(giftTicket - giftTicketNew,
                                                                                             inputGiftTicket,
                                                                                             GoldNew - Gold)
            return False, msg

    def withdrawDiamand(self):  # 个人提现钻石
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "withdrawdiamand.txt") % (self.PLAYER_ID, self.ROOM_ID)
        giftTicket_value = eval(eval(body)[0]["param"])["value"]
        sql = "SELECT GiftTicket FROM money  WHERE PlayerId = {}".format(self.PLAYER_ID)
        sqlRes = self.mysql.query_sql(self.mysql_conn, sql)
        giftTicket = sqlRes[0][0]
        if giftTicket_value < 10000 or giftTicket_value > giftTicket:
            import time
            time.sleep(10)
            result = httpfunc.http_request_post(self.ITERFACEURL, body)
            if "钻石不足" in result:
                return True, None
            else:
                return False, result
        else:
            import time
            time.sleep(10)
            httpfunc.http_request_post(self.ITERFACEURL, body)
            sqlResNew = self.mysql.query_sql(self.mysql_conn, sql)
            giftTicketNew = sqlResNew[0][0]
            if giftTicket - giftTicket_value == giftTicketNew:
                return True, None
            else:
                msg = "giftTicket - giftTicket_value:{},giftTicketNew:{}".format(giftTicket - giftTicket_value,
                                                                                 giftTicketNew)
                return False, msg

    def roomChangeCoin(self):  # 房间钻石兑换金币
        pwd = "123456"  # 兑换密码
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "roomchangcoin.txt") % (pwd, self.PLAYER_ID, self.ROOM_ID)
        inputGiftTicket = eval(eval(body)[0]["param"])["value"][0]
        sqlGiftTicket = "SELECT GiftTicket FROM room1 WHERE Id = {}".format(self.PLAYER_ID)
        sqlGiftTicketRes = self.mysql.query_sql(self.mysql_conn, sqlGiftTicket)
        roomGiftTicket = sqlGiftTicketRes[0][0]
        sqlGold = "SELECT Gold FROM money WHERE PlayerId = {}".format(self.PLAYER_ID)
        sqlGoldRes = self.mysql.query_sql(self.mysql_conn, sqlGold)
        userGold = sqlGoldRes[0][0]
        import time
        time.sleep(10)
        httpfunc.http_request_post(self.ITERFACEURL, body)
        sqlGiftTicketResNew = self.mysql.query_sql(self.mysql_conn, sqlGiftTicket)
        giftTicketNew = sqlGiftTicketResNew[0][0]
        sqlGoldResNew = self.mysql.query_sql(self.mysql_conn, sqlGold)
        userGoldNew = sqlGoldResNew[0][0]
        if inputGiftTicket > roomGiftTicket:
            log.info("输入兑换钻石数大于当前拥有的钻石数")
            msg = "输入兑换钻石数大于当前拥有的钻石数"
            return False, msg
        if roomGiftTicket - giftTicketNew == inputGiftTicket and userGoldNew - userGold == inputGiftTicket:
            return True, None
        else:
            msg = "roomGiftTicket - giftTicketNew:{},userGoldNew - userGold:{},inputGiftTicket{}".format(
                roomGiftTicket - giftTicketNew, userGoldNew - userGold, inputGiftTicket)
            return False, msg

    def roomWithdrawDiamand(self):  # 房间提现钻石
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "roomWithdrawDiamand.txt") % (self.PLAYER_ID, self.ROOM_ID)
        giftTicket_value = eval(eval(body)[0]["param"])["value"]
        sql = "SELECT GiftTicket FROM room1  WHERE id = {}".format(self.PLAYER_ID)
        sqlRes = self.mysql.query_sql(self.mysql_conn, sql)
        giftTicket = sqlRes[0][0]
        if giftTicket_value > giftTicket:
            import time
            time.sleep(10)
            result = httpfunc.http_request_post(self.ITERFACEURL, body)
            if "钻石不足" in result:
                log.info("钻石不足")
                return True, None
            else:
                return False, result
        elif giftTicket_value < 10000:
            import time
            time.sleep(10)
            result = httpfunc.http_request_post(self.ITERFACEURL, body)
            if "参数错误" in result:
                log.info("参数错误")
                return True, None
            else:
                return False, result
        else:
            import time
            time.sleep(10)
            httpfunc.http_request_post(self.ITERFACEURL, body)
            sqlResNew = self.mysql.query_sql(self.mysql_conn, sql)
            giftTicketNew = sqlResNew[0][0]
            if giftTicket - giftTicket_value == giftTicketNew:
                return True, None
            else:
                msg = "giftTicket - giftTicket_value:{},giftTicketNew:{}".format(giftTicket - giftTicket_value,
                                                                                 giftTicketNew)
                return False, msg

    def getNewAuthToken(self):
        '''请求app验证登录'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "getnewauthtoken.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "auth_req_token" in eval(result)[0]["res"].keys():
            return True, None
        else:
            return False, result

    def changePasswd(self):
        '''修改账号登录密码'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "changePasswd.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            return False, result

    def superManager(self):
        '''超级管理员'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "superManager.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        r = result.replace('null', 'None')
        r = eval(eval(r)[0]['err'])['code']
        if r == 33027:
            return True, None
        else:
            return False, r

    def getOnOffList(self):
        '''获取请求开关状态列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "getOnOffList.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            return False, result

    def getCanRechargeCredit(self):
        '''判断是否可以充值'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "getCanRechargeCredit.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            return False, result

    def h5RoomGiftTicket(self):
        '''获取房间收益'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "h5RoomGiftTicket.txt") % (self.PLAYER_ID, self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        r = eval(result)[0]["res"]
        if r["result"] == 1:
            sql = "SELECT GiftTicket FROM room1 WHERE Id ={}".format(self.PLAYER_ID)
            sqlRes = self.mysql.query_sql(self.mysql_conn, sql)[0][0]
            if r['value'] == sqlRes:
                return True, None
        else:
            msg = "{}账号不属于公会房间".format(self.PLAYER_ID)
            return False, msg

    def h5PlayerGains(self):
        '''获取个人收益'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "h5PlayerGains.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        tp = eval(eval(body)[0]['param'])
        if tp['type'] == 1:
            if resp_handle(result):
                return True, None
            else:
                return False, result
        elif tp['type'] == 2:
            if resp_handle(result):
                return True, None
            else:
                return False, result
        else:
            msg = "参数错误"
            return False, msg

    def h5TatolGain(self):
        '''获取总收益'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "h5TatolGain.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        tp = eval(eval(body)[0]['param'])
        if tp['type'] == 1:
            if resp_handle(result):
                return True, None
            else:
                return False, result
        elif tp['type'] == 2:
            if resp_handle(result):
                return True, None
            else:
                return False, result
        else:
            msg = "参数错误"
            return False, msg

    def deleteAccountCheck(self):
        '''注销检查'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "deleteAccountCheck.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            return False, result

    def getRank(self):
        '''获取排行榜'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("user", "getRank.txt") % (self.PLAYER_ID, self.ROOM_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        res = eval(result)[0]['res']
        r = eval(result)[0]['res']['week_rank'][0]['id']
        tp = eval(eval(body)[0]['param'])
        if tp['type'] == 0:
            sql = "SELECT PlayerId FROM rank_charm ORDER BY Week Desc"
            sqlRes = self.mysql.query_sql(self.mysql_conn, sql)[0][0]
            if r == sqlRes:
                return True, None
            elif 'week_rank' not in res.keys():
                sql1 = "SELECT Week FROM rank_charm ORDER BY Week Desc"
                sqlRes1 = self.mysql.query_sql(self.mysql_conn, sql1)[0][0]
                if sqlRes1 == 0:
                    return True, None
                else:
                    msg = '数据库中有数据，但是返回的数据中没有排行榜信息！'
                    return False, msg
            else:
                msg = '魅力排行榜第一id为：{},返回的数据中第一id为：{}'.format(sqlRes, r)
                return False, msg
        elif tp['type'] == 1:
            sql = "SELECT PlayerId FROM rank_wealth ORDER BY Week Desc"
            sqlRes = self.mysql.query_sql(self.mysql_conn, sql)[0][0]
            if r == sqlRes:
                return True, None
            elif 'week_rank' not in res.keys():
                sql1 = "SELECT Week FROM rank_wealth ORDER BY Week Desc"
                sqlRes1 = self.mysql.query_sql(self.mysql_conn, sql1)[0][0]
                if sqlRes1 == 0:
                    return True, None
                else:
                    msg = '数据库中有数据，但是返回的数据中没有排行榜信息！'
                    return False, msg
            else:
                msg = '贡献排行榜第一id为：{},返回的数据中第一id为：{}'.format(sqlRes, r)
                return False, msg
        else:
            msg = 'type参数返回错误'
            return False, msg




if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()

    u = User(mysql,mysql_conn,mzredis,redis_conn)
    u.getPlayer()

