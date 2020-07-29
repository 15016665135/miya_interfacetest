# coding=utf-8
from common.frame.get_data import Getdata
from common.http.http_func import Httpfunc
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from common.frame.pylog import log
from common.frame.result_handle import resp_handle

class Room:
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
    def enterRoom(self):
        '''进入房间'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)
        key = "Room1.0_PlayerRoom:"+str(self.PLAYER_ID)
        roomid = self.mzredis.query_redis(self.redis_conn,key).decode("utf-8")
        if roomid == str(self.ROOM_ID):
            return True,None
        else:
            log.error(roomid)
            log.error("进入房间请求：{}".format(r))
            msg = "进入房间请求：{}".format(r)
            return False,msg

    def leaveRoom(self):
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.ROOM_ID)
        r = httpfunc.http_request_post(self.ITERFACEURL, body)  #进入房间
        key = "Room1.0_PlayerRoom:" + str(self.PLAYER_ID)
        # roomid = self.mzredis.query_redis(self.redis_conn, key).decode("utf-8")
        body2 = self.getdata.get_case_data("room", "leaveroom.txt") % (self.PLAYER_ID, self.ROOM_ID)
        httpfunc.http_request_post(self.ITERFACEURL, body2)  #离开房间，Room1.0_PlayerRoom:* key不存在
        roomid2 = self.mzredis.query_redis(self.redis_conn, key)
        if roomid2 == None:
            return True,None
        else:
            log.error("roomid:{}".format(roomid2))
            log.error("请求离开房间错误：{}".format(r))
            msg = "roomid:{}".format(roomid2) + "请求离开房间错误：{}".format(r)
            return False,msg

    def setRoom(self):
        '''设置房间名称'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "setroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        body = body
        req_room_name = eval(eval(body)[0]["param"])["name"]
        httpfunc.http_request_post(self.ITERFACEURL, body)
        sql = "SELECT `Name` FROM room1 WHERE id = {}".format(self.PLAYER_ID)
        result = self.mysql.query_sql(self.mysql_conn,sql)[0][0]
        if req_room_name == result:
            return True,None
        else:
            log.error("setRoom error:{},{}".format(req_room_name,result))
            msg = "setRoom error:{},{}".format(req_room_name,result)
            return False,msg
    def getRoomConf(self):
        '''房间配置'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "getroomconf.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result
    def setRoomAdmin(self):
        '''设置管理员'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "setroomadmin.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def forbidspeal(self):
        '''禁言'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "forbidspeak.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def kickoutroom(self):
        '''踢出房间'''
        httpfunc = Httpfunc()
        body = self.getdata.get_case_data("room", "kickoutroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def getblacklist(self):
        '''获取黑名单'''
        httpfunc = Httpfunc()
        body1 = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        body2 = self.getdata.get_case_data("room", "getblacklist.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        httpfunc.http_request_post(self.ITERFACEURL, body1)
        result = httpfunc.http_request_post(self.ITERFACEURL, body2)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result
    def getadminlist(self):
        '''获取管理员列表'''
        httpfunc = Httpfunc()
        body1 = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        httpfunc.http_request_post(self.ITERFACEURL, body1)
        body= self.getdata.get_case_data("room", "getadminlist.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def getplayerlist(self):
        '''获取房间用户列表'''
        httpfunc = Httpfunc()
        body1 = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        httpfunc.http_request_post(self.ITERFACEURL, body1)
        body= self.getdata.get_case_data("room", "getplayerlist.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def getsceneplayer(self):
        '''获取场景玩家'''
        httpfunc = Httpfunc()
        body= self.getdata.get_case_data("room", "getsceneplayer.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result
    def setchairstatus(self):
        '''设置嘉宾位状态'''
        httpfunc = Httpfunc()
        body= self.getdata.get_case_data("room", "setchairstatus.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            return False,result

    def setchairspeak(self):
        '''设置开麦/1禁麦'''
        httpfunc = Httpfunc()
        body= self.getdata.get_case_data("room", "setchairspeak.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def getflowerinfo(self):
        '''获取在线鲜花信息'''
        httpfunc = Httpfunc()
        body= self.getdata.get_case_data("room", "getflowerinfo.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result

    def playdice(self):
        '''举牌'''
        httpfunc = Httpfunc()
        body1 = self.getdata.get_case_data("room", "enterroom.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        httpfunc.http_request_post(self.ITERFACEURL, body1)
        body= self.getdata.get_case_data("room", "playdice.txt") % (self.PLAYER_ID, self.PLAYER_ID)
        result = httpfunc.http_request_post(self.ITERFACEURL, body)
        if resp_handle(result):
            return True,None
        else:
            log.error(result)
            return False,result


if __name__ == '__main__':
    mysql = MySql()
    mysql_conn = mysql.conn_mysql()

    mzredis = MzRedis()
    redis_conn = mzredis.conn_redis()

    r = Room(mysql,mysql_conn,mzredis,redis_conn)
    r.enterRoom()
