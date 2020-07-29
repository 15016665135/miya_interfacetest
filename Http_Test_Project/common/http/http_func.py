import requests
from common.frame.get_data import Getdata
from common.frame.pylog import log
class Httpfunc:
    def __init__(self):
        self.getdata = Getdata()
        self.ip_port = self.getdata.get_ip_port("test")
    def http_request_post(self, interface_url, body,headers=None):
        ip = self.ip_port[0]
        port = self.ip_port[1]
        # print(ip,port)
        # request_url = "http://" + ip + ":" + str(port) + interface_url
        request_url = "http://" + ip + interface_url
        request_data = body.encode("utf-8") # body带有中文需转码
        headers = headers
        try:
            log.debug("pos请求url:{},请求body:{}".format(request_url, request_data))
            request_result = requests.post(url=request_url, data=request_data,headers=headers)
            log.debug("post请求，返回结果：{}".format(request_result.text))
            return request_result.text
        except Exception as err:
            log.error("http post 请求失败:{}".format(err))
            return

    def http_request_get(self, interface_url, body, headers=None):
        ip = self.ip_port[0]
        port = self.ip_port[1]
        request_url = "http://" + ip  + interface_url
        request_data = body
        header = headers
        try:
            log.info("get请求url:{},请求body:{}".format(request_url, request_data))
            request_result = requests.get(url=request_url, params=request_data, headers=header)
            log.info("get请求，返回结果：{}".format(request_result.text))
            return request_result.text
        except Exception as err:
            log.error("http get 请求失败:{}".format(err))
            return

if __name__ == '__main__':
    httpfunc = Httpfunc()
    headers = {}
    headers["Content-Type"] = "text/plain"
    interface_url = "/auto"
    body = "[{\"obj\":\"UserExtObj\",\"func\":\"GetPlayer\",\"param\":\"{\\\"id\\\":2001114}\",\"global\":{\"uid\":\"2001114\",\"roomid\":\"2001114\"}}]"
    res = httpfunc.http_request_post(interface_url,body,headers)
    print(res)

