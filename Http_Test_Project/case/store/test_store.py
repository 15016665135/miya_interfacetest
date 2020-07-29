import unittest
from module.store.store import Store
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.s = Store(cls.mysql, cls.mysql_conn, cls.mzredis, cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_getStoreTabs(self):
        '''获取商城标签'''
        result = self.s.getStoreTabs()
        self.assertTrue(result[0], result[1])

    def test_getPacketTabs(self):
        '''获取背包标签'''
        result = self.s.getPacketTabs()
        self.assertTrue(result[0], result[1])

    def test_effectList(self):
        '''获取背包中的特效列表'''
        result = self.s.effectList()
        self.assertTrue(result[0], result[1])

    def test_packetList(self):
        '''获取背包中的物品'''
        result = self.s.packetList()
        self.assertTrue(result[0], result[1])

    def test_buy(self):
        '''商城购买'''
        result = self.s.buy()
        self.assertTrue(result[0], result[1])

    def test_getStoreConf(self):
        '''获取商城配置'''
        result = self.s.getStoreConf()
        self.assertTrue(result[0], result[1])

    def test_getExchangeConf(self):
        '''获取兑换配置'''
        result = self.s.getExchangeConf()
        self.assertTrue(result[0], result[1])



if __name__ == '__main__':
    unittest.main()
