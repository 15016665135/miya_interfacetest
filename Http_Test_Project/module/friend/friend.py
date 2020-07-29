# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.result_handle import resp_handle
from common.frame.pylog import log


class Friend:
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

    def friendalias(self):
        '''设置好友备注名称'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendalias.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        friendid = eval(eval(body)[0]["param"])["id"]
        alias_name = eval(eval(body)[0]["param"])["name"]
        if "nil" in result:
            sql = "SELECT Alias FROM friend WHERE playerid = {} and friendid = {}".format(self.PLAYER_ID, friendid)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sql_res) == 1:
                sql_alias_name = sql_res[0][0]
                if alias_name == sql_alias_name:
                    return True, None
                else:
                    msg = "数据库和请求修改的名称不一致，alias_name：{}，sql_alias_name：{}".format(alias_name, sql_alias_name)
                    return False, msg
            else:
                msg = "请求的fiendid在fiend表找不到"
                log.info(msg)
                return True, None
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendlist_gf(self):
        '''请求好友列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendlist_gf.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        result = result.replace("true", "True")  # 返回存在好友是否在线true
        if "nil" in result:
            res = eval(result)[0]["res"]
            if len(res) == 0:  # 返回好友列表为空，验证数据库是否无好友
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = 2".format(self.PLAYER_ID)
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                if len(sql_res) == 0:
                    return True, None
                else:
                    msg = "请求用户无好友：{},但是查询数据库存在好友：{}".format(self.PLAYER_ID, sql_res)
                    return False, msg
            else:
                friend_list = res["list"]
                result_set = set()
                result_exp_set = set()
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = 2".format(self.PLAYER_ID)
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                for i in friend_list:  # 请求返回好友列表
                    result_set.add(i["id"])
                for j in sql_res:
                    result_exp_set.add(j[0])
                if result_set == result_exp_set:
                    return True, None
                else:
                    msg = "请求返回的好友id：{}，和查询结果好友id：{},不一致"
                    return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendlist_follow(self):
        '''请求关注列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendlist_follow.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        result = result.replace("true", "True")  # 返回存在关注用户是否在线true
        if "nil" in result:
            res = eval(result)[0]["res"]
            if len(res) == 0:  # 返回关注列表为空，验证数据库是否无好友
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = 1 and FriendId != {}".format(
                    self.PLAYER_ID, self.PLAYER_ID)  # 服务端历史遗留问题，关注列表需要排除自己
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                print(sql_res)
                if len(sql_res) == 0:
                    return True, None
                else:
                    msg = "请求用户无关注用户：{},但是查询数据库存在关注用户：{}".format(self.PLAYER_ID, sql_res)
                    return False, msg
            else:
                friend_list = res["list"]
                result_set = set()
                result_exp_set = set()
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = 1 and FriendId != {}".format(
                    self.PLAYER_ID, self.PLAYER_ID)
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                for i in friend_list:  # 请求返回关注列表
                    result_set.add(i["id"])
                for j in sql_res:
                    result_exp_set.add(j[0])
                if result_set == result_exp_set:
                    return True, None
                else:
                    msg = "请求返回的关注id：{}，和查询结果关注id：{},不一致"
                    return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendlist_pullblack(self):
        '''请求黑名单列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendlist_pullblack.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            res = eval(result)[0]["res"]
            if len(res) == 0:  # 返回黑名单为空，验证数据库是否有拉黑用户
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = -1".format(self.PLAYER_ID)
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                if len(sql_res) == 0:
                    return True, None
                else:
                    msg = "请求用户无拉黑用户：{},但是查询数据库存在拉黑用户：{}".format(self.PLAYER_ID, sql_res)
                    return False, msg
            else:
                friend_list = res["list"]
                result_set = set()
                result_exp_set = set()
                sql = "SELECT FriendId FROM friend WHERE playerid = {} and Type = -1".format(self.PLAYER_ID)
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                for i in friend_list:  # 请求返回黑名单
                    result_set.add(i["id"])
                for j in sql_res:
                    result_exp_set.add(j[0])
                if result_set == result_exp_set:
                    return True, None
                else:
                    msg = "请求返回的黑名单id：{}，和查询结果黑名单id：{},不一致"
                    return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def usersig(self):
        '''获取用户sig'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "usersig.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            return False, result

    def friendoper_1(self):
        '''关注'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendoper_1.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        friendid = eval(eval(body)[0]["param"])["id"]
        # 删除记录，相当于每次关注一个新人
        del_sql = "DELETE FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
        self.mysql.query_sql(self.mysql_conn, del_sql)
        key = "v2:friendRel:{}:{}".format(self.PLAYER_ID, friendid)
        self.mzredis.del_redis(self.redis_conn, key)

        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT Type FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sql_res):
                friendtype = sql_res[0][0]
                # 查询数据库type为1代表关注成功,type为2,对方有关注自己
                if friendtype == 1 or friendtype == 2:
                    return True, None
                else:
                    msg = "关注后，查询数据库type错误：{}".format(friendtype)
                    return False, msg
            else:
                msg = "关注好友，查询结果为空"
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendoper_2(self):
        '''取消关注'''
        self.friendoper_1()  # 先关注，然后取消关注
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendoper_2.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        friendid = eval(eval(body)[0]["param"])["id"]
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT Type FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sql_res) == 0:  # 查询数据库结果为空，代表取消关注成功
                return True, None
            else:
                msg = "取消关注好友，查询结果为：{}".format(sql_res)
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendoper_3(self):
        '''拉黑用户'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendoper_3.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        friendid = eval(eval(body)[0]["param"])["id"]
        # 删除记录，相当于每次关注一个新人
        del_sql = "DELETE FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
        self.mysql.query_sql(self.mysql_conn, del_sql)
        key = "v2:friendRel:{}:{}".format(self.PLAYER_ID, friendid)
        self.mzredis.del_redis(self.redis_conn, key)

        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT Type FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sql_res):
                friendtype = sql_res[0][0]
                # 查询数据库type为-1代表拉黑成功
                if friendtype == -1:
                    return True, None
                else:
                    msg = "拉黑后，查询数据库type错误：{}".format(friendtype)
                    return False, msg
            else:
                msg = "拉黑好友，查询结果为空"
                return False, msg
        else:

            msg = "请求失败：{}".format(result)
            print(msg)
            return False, msg

    def friendoper_4(self):
        '''取消拉黑'''
        self.friendoper_3()  # 先拉黑，然后取消拉黑
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendoper_4.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        friendid = eval(eval(body)[0]["param"])["id"]
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT Type FROM friend WHERE PlayerId = 1015735 and FriendId = {}".format(friendid)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            if len(sql_res) == 0:  # 查询数据库结果为空，代表取消拉黑成功
                return True, None
            else:
                msg = "取消拉黑好友，查询结果为：{}".format(sql_res)
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def friendonlinelist(self):
        '''好友在线列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "friendonlinelist.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True, None
        else:
            msg = "请求出错：{}".format(result)
            return False, msg

    def fanslist(self):
        '''获取粉丝列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "fanslist.txt") % (self.PLAYER_ID, self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            fans_list = eval(result)[0]["res"]["list"]
            result_set = set()  # 请求返回粉丝列表前20
            result_exp_set = set()  # 数据库查询粉丝前20
            for i in fans_list:
                result_set.add(i["id"])
            sql = "select PlayerId from friend WHERE FriendId = {} and Type = 1 and PlayerId != {} limit 0,20".format(
                self.PLAYER_ID, self.PLAYER_ID)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            for j in sql_res:
                result_exp_set.add(j[0])
            if result_set == result_exp_set:
                return True, None
            else:
                msg = "请求返回结果和查询结果不一致,request：{}，sql：{}"
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def updatespecialattention(self):
        '''好友设置特别关注'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "updatespecialattention.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        # 初始化数据，使好友处于未特别关注状态
        updata_sql = "UPDATE friend set special_attention = 0 WHERE PlayerId = {} and FriendId = 2001080".format(
            self.PLAYER_ID)
        self.mysql.query_sql(self.mysql_conn, updata_sql)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT special_attention FROM friend WHERE PlayerId = {} and FriendId = 2001080".format(
                self.PLAYER_ID)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            # special_attention 为1代表特别关注，0代表取消特别关注
            if sql_res[0][0] == 1:
                return True, None
            else:
                msg = "好友特别关注失败，当前special_attention为：{}".format(sql_res[0][0])
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def updatespecialattention_no(self):
        '''取消特别关注'''
        self.updatespecialattention()  # 取消特别关注之前需要设置特别关注
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "updatespecialattention_no.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            sql = "SELECT special_attention FROM friend WHERE PlayerId = {} and FriendId = 2001080".format(
                self.PLAYER_ID)
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            # special_attention 为1代表特别关注，0代表取消特别关注
            if sql_res[0][0] == 0:
                print(111)
                return True, None
            else:
                msg = "取消特别关注失败，当前special_attention为：{}".format(sql_res[0][0])
                return False, msg
        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def intimatelist(self):
        '''获取挚友列表'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "intimatelist.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if "nil" in result:
            intimatelist_res = eval(result)[0]["res"]["data"]
            result_set = set()
            result_exp_set = set()
            for i in intimatelist_res:
                result_set.add(i["friend_id"])
            sql = "SELECT FriendId FROM intimate_friend WHERE PlayerId = 1015735"
            sql_res = self.mysql.query_sql(self.mysql_conn, sql)
            for j in sql_res:
                result_exp_set.add(j[0])
            if result_set == result_exp_set:
                return True, None
            else:
                msg = "请求返回结果与查询结果不一致，请求结果：{}，查询结果：{}".format(result_set, result_exp_set)
                return False, msg

        else:
            msg = "请求失败：{}".format(result)
            return False, msg

    def applyintimate(self):
        '''请求成为挚友'''
        # 该请求较特殊，用户id写死
        send_uid = 1018438
        accept_uid = 1021023
        httpfunc = Httpfunc()
        # 先解除亲密挚友，才能重复请求绑定为亲密挚友
        relieving = self.getdata.get_case_data("friend", "dismissintimate.txt")
        # 解除成功后下面可以绑定挚友，若返回错误说明没有挚友关系
        httpfunc.http_request_post(self.ITERFACEURL, relieving)
        # 申请成为挚友需要两个人在同一个房间
        send_enterroom = self.getdata.get_case_data("room", "enterroom.txt") % (send_uid, accept_uid)
        accept_enterroom = self.getdata.get_case_data("room", "enterroom.txt") % (accept_uid, accept_uid)
        httpfunc.http_request_post(self.ITERFACEURL, send_enterroom)
        httpfunc.http_request_post(self.ITERFACEURL, accept_enterroom)
        send_reqbody = self.getdata.get_case_data("friend", "applyintimate.txt")
        send_res = httpfunc.http_request_post(self.ITERFACEURL, send_reqbody)
        intimate_type = eval(eval(send_reqbody)[0]["param"])["type"]
        if "nil" in send_res:
            accept_resbody = self.getdata.get_case_data("friend", "replyintimate.txt")
            accept_res = httpfunc.http_request_post(self.ITERFACEURL, accept_resbody)
            if "nil" in accept_res:
                sql = "SELECT Type FROM intimate_friend WHERE PlayerId = 1018438 and FriendId = 1021023"
                sql_res = self.mysql.query_sql(self.mysql_conn, sql)
                if sql_res[0][0] == intimate_type:
                    return True, None
                else:
                    msg = "成为亲密挚友失败，send_res：{}，sqlres：{}".format(send_res, sql_res)
                    return False, msg
            else:
                msg = "同意成为挚友请求错误：{}".format(accept_res)
                return False, msg

        else:
            msg = "申请成为挚友请求错误：{}".format(send_res)
            return False, msg

    def intimateconfext(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "intimateconfext.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            msg = "请求挚友配置失败：{}".format(result)
            return False, msg

    def getintimateheartbeat(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("friend", "getintimateheartbeat.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            msg = "请求心跳位置错误：{}".format(result)
            return False, msg



if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()

    f = Friend(mysql, mysql_conn, mzredis, redis_conn)
    f.getintimateheartbeat()
