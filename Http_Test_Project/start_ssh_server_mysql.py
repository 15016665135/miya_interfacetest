from sshtunnel import SSHTunnelForwarder
server = SSHTunnelForwarder(
    ssh_address_or_host="beta-hn1c-1.xiaohuxi.cn",
    ssh_username="root",
    ssh_password="4fAyYs^b1LxkOoG@",
    remote_bind_address=('beta-hn1c-mysql0.mysql.rds.aliyuncs.com', 3306),
    local_bind_address=('0.0.0.0', 3308)
)
server.start()




