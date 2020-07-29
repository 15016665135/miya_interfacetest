import unittest
import time
from module.assets.asstes import Assets
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class Test_Assets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.a = Assets(cls.mysql,cls.mysql_conn,cls.mzredis,cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_getmoney(self):
        '''获取个人资产'''
        result = self.a.getmoney()
        self.assertTrue(result[0],result[1])

    def test_getbag(self):
        '''获取个人背包'''
        result = self.a.getbag()
        self.assertTrue(result[0],result[1])

    def test_geteffect(self):
        '''获取用户使用的特效'''
        result = self.a.geteffect()
        self.assertTrue(result[0],result[1])

    def test_geteffectconf(self):
        '''获取特效配置'''
        result = self.a.geteffectconf()
        self.assertTrue(result[0],result[1])

    def test_h5money(self):
        "获取h5money"
        result = self.a.h5money()
        self.assertTrue(result[0],result[1])
    def test_useeffect(self):
        "佩戴特效"
        result = self.a.useeffect()
        self.assertTrue(result[0],result[1])

if __name__ == '__main__':
    unittest.main()