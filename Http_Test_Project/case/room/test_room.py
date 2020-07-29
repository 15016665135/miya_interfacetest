import unittest
from module.room.room import Room
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class TestRoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.r = Room(cls.mysql,cls.mysql_conn,cls.mzredis,cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()



    def test_enterroom(self):
        '''进入房间'''
        result = self.r.enterRoom()
        self.assertTrue(result[0],result[1])

    def test_leaveroom(self):
        '''离开房间'''
        result = self.r.leaveRoom()
        self.assertTrue(result[0],result[1])

    def test_setroom(self):
        '''设置房间名称'''
        result = self.r.setRoom()
        self.assertTrue(result[0],result[1])

    def test_getroomconf(self):
        '''房间配置'''
        result = self.r.getRoomConf()
        self.assertTrue(result[0],result[1])

    def test_setroomadmin(self):
        '''设置管理员'''
        result = self.r.setRoomAdmin()
        self.assertTrue(result[0],result[1])

    def test_forbidspeal(self):
        '''禁言'''
        result = self.r.forbidspeal()
        self.assertTrue(result[0],result[1])

    def test_kickoutroom(self):
        '''踢出房间'''
        result = self.r.kickoutroom()
        self.assertTrue(result[0],result[1])
    def test_getblacklist(self):
        '''获取黑名单'''
        result = self.r.getblacklist()
        self.assertTrue(result[0],result[1])

    def test_getadminlist(self):
        '''管理员列表'''
        result = self.r.getadminlist()
        self.assertTrue(result[0],result[1])

    def test_getplayerlist(self):
        '''获取房间用户列表'''
        result = self.r.getplayerlist()
        self.assertTrue(result[0],result[1])

    def test_getsceneplayer(self):
        '''获取场景玩家'''
        result = self.r.getsceneplayer()
        self.assertTrue(result[0],result[1])

    def test_setchairstatus(self):
        '''设置嘉宾位状态'''
        result = self.r.setchairstatus()
        self.assertTrue(result[0],result[1])

    def test_setchairspeak(self):
        '''设置开麦/1禁麦'''
        result = self.r.setchairspeak()
        self.assertTrue(result[0],result[1])

    def test_getflowerinfo(self):
        '''获取在线鲜花信息'''
        result = self.r.getflowerinfo()
        self.assertTrue(result[0],result[1])

    def test_playdice(self):
        '''举牌'''
        result = self.r.playdice()
        self.assertTrue(result[0],result[1])




if __name__ == '__main__':
    unittest.main()