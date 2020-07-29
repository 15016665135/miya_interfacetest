import unittest
import time
from module.egg.crack_egg import CrackEgg
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class Crack_Egg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.egg = CrackEgg(cls.mysql,cls.mysql_conn,cls.mzredis,cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_crackegg(self):
        '''砸蛋'''
        result = self.egg.crackegg()
        self.assertTrue(result[0],result[1])

    def test_getEggShift(self):
        '''砸蛋进度'''
        result = self.egg.getEggShift()
        self.assertTrue(result[0],result[1])

    def test_getCrackTime(self):
        '''获取砸蛋间隔时间'''
        result = self.egg.getCrackTime()
        self.assertTrue(result[0],result[1])

    def test_getRewardList(self):
        '''获取砸蛋奖品列表'''
        result = self.egg.getRewardList()
        self.assertTrue(result[0],result[1])

    def test_getLuck(self):
        '''获取奖金池/幸运值'''
        result = self.egg.getLuck()
        self.assertTrue(result[0],result[1])

    def test_getCrackCopywriting(self):
        '''获取砸蛋文案'''
        result = self.egg.getCrackCopywriting()
        self.assertTrue(result[0],result[1])

if __name__ == '__main__':
    unittest.main()