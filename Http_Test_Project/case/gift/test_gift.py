import unittest
from module.gift.gift import Gift
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class testGift(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.gift = Gift(cls.mysql,cls.mysql_conn,cls.mzredis,cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_presentGift(self):
        '''赠送礼物'''
        result = self.gift.presentGift()
        self.assertTrue(result[0],result[1])

    def test_buyGift(self):
        '''购买礼物'''
        result = self.gift.buyGift()
        self.assertTrue(result[0],result[1])
    def test_transferGift(self):
        '''物品转赠'''
        result = self.gift.transferGift()
        self.assertTrue(result[0],result[1])

if __name__ == '__main__':
    unittest.main()