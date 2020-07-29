from sshtunnel import SSHTunnelForwarder

server = SSHTunnelForwarder(
    ssh_address_or_host="beta-hn1c-1.xiaohuxi.cn",
    ssh_username="root",
    ssh_password="4fAyYs^b1LxkOoG@",
    remote_bind_address=('beta-hn1c-0.redis.rds.aliyuncs.com', 6379),
    local_bind_address=('0.0.0.0', 6381)
)
server.start()





