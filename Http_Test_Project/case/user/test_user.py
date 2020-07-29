import unittest
import time
from module.user.user import User
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class Users(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.user = User(cls.mysql,cls.mysql_conn,cls.mzredis,cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_getplayer(self):
        '''获取用户信息'''
        result = self.user.getPlayer()
        self.assertTrue(result[0],result[1])

    def test_setuserinfosignature(self):
        '''个性签名'''
        result = self.user.setUserInfoSignature()
        self.assertTrue(result[0],result[1])

    def test_getonoffstatus(self):
        '''开关状态'''
        result = self.user.getOnOffStatus()
        self.assertTrue(result[0],result[1])

    def test_diamondchangecoin(self):
        '''兑换金币'''
        result = self.user.diamondChangeCoin()
        self.assertTrue(result[0],result[1])

    def test_withdrawDiamand(self):
        '''个人提现'''
        result = self.user.withdrawDiamand()
        self.assertTrue(result[0],result[1])

    def test_roomChangeCoin(self):
        '''房间兑换金币'''
        result = self.user.roomChangeCoin()
        self.assertTrue(result[0],result[1])

    def test_roomWithdrawDiamand(self):
        '''房间提现'''
        result = self.user.roomWithdrawDiamand()
        self.assertTrue(result[0],result[1])

    def test_changePasswd(self):
        '''修改账号登录密码'''
        result = self.user.changePasswd()
        self.assertTrue(result[0], result[1])

    def test_superManager(self):
        '''超级管理员'''
        result = self.user.superManager()
        self.assertTrue(result[0], result[1])

    def test_getOnOffList(self):
        '''获取请求开关状态列表'''
        result = self.user.getOnOffList()
        self.assertTrue(result[0], result[1])

    def test_getCanRechargeCredit(self):
        '''判断是否可以充值'''
        result = self.user.getCanRechargeCredit()
        self.assertTrue(result[0], result[1])

    def test_h5RoomGiftTicket(self):
        '''获取房间收益'''
        result = self.user.h5RoomGiftTicket()
        self.assertTrue(result[0], result[1])

    def test_h5PlayerGains(self):
        '''获取个人收益'''
        result = self.user.h5PlayerGains()
        self.assertTrue(result[0], result[1])

    def test_h5TatolGain(self):
        '''获取总收益'''
        result = self.user.h5TatolGain()
        self.assertTrue(result[0], result[1])

    def test_deleteAccountCheck(self):
        '''注销检查'''
        result = self.user.deleteAccountCheck()
        self.assertTrue(result[0], result[1])

    def test_getRank(self):
        '''获取排行榜'''
        result = self.user.getRank()
        self.assertTrue(result[0], result[1])

if __name__ == '__main__':
    unittest.main()