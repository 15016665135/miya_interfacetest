import unittest
import time
from common.mysql.conn_redis_db import MzRedis
from common.mysql.conn_mysql_db import MySql
from module.friend.friend import Friend


class Test_Friends(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql = MySql()
        cls.mysql_conn = cls.mysql.conn_mysql()

        cls.mzredis = MzRedis()
        cls.redis_conn = cls.mzredis.conn_redis()
        cls.f = Friend(cls.mysql, cls.mysql_conn, cls.mzredis, cls.redis_conn)

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_friendalias(self):
        '''设置好友备注名称'''
        result = self.f.friendalias()
        self.assertTrue(result[0], result[1])

    def test_friendlist_gf(self):
        '''获取好友列表'''
        result = self.f.friendlist_gf()
        self.assertTrue(result[0], result[1])

    def test_friendlist_follow(self):
        '''获取关注列表'''
        result = self.f.friendlist_follow()
        self.assertTrue(result[0], result[1])

    def test_friendlist_pullblack(self):
        '''获取黑名单'''
        result = self.f.friendlist_pullblack()
        self.assertTrue(result[0], result[1])

    def test_uersig(self):
        '''获取用户sig'''
        result = self.f.usersig()
        self.assertTrue(result[0], result[1])

    def test_friendoper_1(self):
        '''关注好友'''
        result = self.f.friendoper_1()
        self.assertTrue(result[0], result[1])

    def test_friendoper_2(self):
        '''取消好友'''
        result = self.f.friendoper_2()
        self.assertTrue(result[0], result[1])

    def test_friendoper_3(self):
        '''拉黑好友'''
        result = self.f.friendoper_3()
        self.assertTrue(result[0], result[1])

    def test_friendoper_4(self):
        '''取消拉黑'''
        result = self.f.friendoper_4()
        self.assertTrue(result[0], result[1])

    def test_friendonlinelist(self):
        '''好友在线列表'''
        result = self.f.friendonlinelist()
        self.assertTrue(result[0], result[1])

    def test_fanslist(self):
        '''粉丝列表'''
        result = self.f.fanslist()
        self.assertTrue(result[0], result[1])

    def test_updatespecialattention(self):
        '''设置特别关注'''
        result = self.f.updatespecialattention()
        self.assertTrue(result[0], result[1])

    def test_updatespecialattention_no(self):
        '''取消特别关注'''
        result = self.f.updatespecialattention_no()
        self.assertTrue(result[0], result[1])

    def test_intimatelist(self):
        '''获取挚友列表'''
        result = self.f.intimatelist()
        self.assertTrue(result[0], result[1])

    @unittest.skip("无法调用login，执行时会提示不在线，故先跳过该用例")
    def test_applyintimate(self):
        '''请求成为挚友'''
        result = self.f.applyintimate()
        self.assertTrue(result[0], result[1])

    def test_intimateconfext(self):
        '''获取挚友配置'''
        result = self.f.intimateconfext()
        self.assertTrue(result[0], result[1])

    def test_getintimateheartbeat(self):
        '''获取心跳位置配置'''
        result = self.f.getintimateheartbeat()
        self.assertTrue(result[0], result[1])


if __name__ == '__main__':
    unittest.main()
