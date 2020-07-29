import redis
from common.frame.get_data import Getdata
from common.frame.pylog import log
import time
class MzRedis:

    def conn_redis(self):
        db_data = Getdata().get_config_data("config.yaml")
        redis_ip = db_data["test"]["redis_ip"]
        redis_port = db_data["test"]["redis_port"]
        redis_db = db_data["test"]["redis_db"]
        redis_pwd = db_data["test"]["redis_pwd"]
        try:
            log.debug("连接redis，ip:{},port{}".format(redis_ip,redis_port))
            pool = redis.ConnectionPool(host=redis_ip,port=redis_port,db=redis_db,password=redis_pwd)
            conn = redis.Redis(connection_pool=pool)
            return conn
        except Exception as err:
            log.error("连接redis，出错：{}".format(err))
            return

    def query_redis(self,connect,redis_key,type="get"):
        time.sleep(0.5)  # 查询数据库休眠2秒，防止数据更新不及时
        if type == "get":
            result = connect.get(redis_key)
        elif type == "hvals":
            result = connect.hvals(redis_key)
        elif type == "hvals2":
            result = connect.hgetall(redis_key)
        else:
            return
        if result:
            return result
        else:
            return
    def del_redis(self,connect,redis_key):
        time.sleep(0.5)
        result = connect.delete(redis_key)
        return result

if __name__ == '__main__':

    r = MzRedis()
    conn = r.conn_redis()
    res = r.del_redis(conn,"v2:friendRel:1015735:1003891")
    print(res)