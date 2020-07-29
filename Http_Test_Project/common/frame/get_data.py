import os
import yaml
from common.frame.pylog import log


class Getdata():

    def get_config_data(self, cfg_fname):
        '''get_config_data 获取config.yaml文件的内容，以字典的形式返回'''
        try:
            curPath = os.path.dirname(os.path.realpath(__file__))
            yamlPath = os.path.join(os.path.dirname(os.path.dirname(curPath)), "config\\" + cfg_fname)
            # mzlog.log.info("读取配置文件")
            with open(yamlPath, 'r', encoding='utf-8') as f:
                cfg = f.read()
            cfg_data = yaml.load(cfg)
            return cfg_data
        except Exception as err:
            log.error("读取配置文件失败：{}".format(err))


    def get_case_data(self, fpath, fname, ):
        try:
            curPath = os.path.dirname(os.path.realpath(__file__))
            caseFilepath = os.path.join(os.path.dirname(os.path.dirname(curPath)),
                                        "data\\http\\" + fpath + "\\" + fname)
            # mzlog.log.info("读取测试用例文件")
            with open(caseFilepath, encoding="utf-8") as f:
                case_data = f.read()
            return case_data
        except Exception as err:
            log.error("读取测试用例文件失败：{}".format(err))

    def get_interface_url(self, fname):

        try:
            curPath = os.path.dirname(os.path.realpath(__file__))
            urlFilepath = os.path.join(os.path.dirname(os.path.dirname(curPath)), "template\\http\\" + fname)
            # mzlog.log.info("读取url文件")
            with open(urlFilepath) as f:
                url_data = f.read()
            return url_data
        except Exception as err:
            log.error("读取url文件失败：{}".format(err))

    def get_ip_port(self, environment_type):

        '''根据环境类型，选择对于的测试ip和port'''
        if environment_type == "test":
            # mzlog.log.info("测试环境")
            ip = self.get_config_data("config.yaml")[environment_type]["ip"]
            port = self.get_config_data("config.yaml")[environment_type]["port"]
            return (ip, port)
        elif environment_type == "formal":
            # mzlog.log.info("测试环境")
            ip = self.get_config_data("config.yaml")["formal"]["ip"]
            port = self.get_config_data("config.yaml")["formal"]["port"]
            return (ip, port)
        else:
            return




if __name__ == '__main__':
    getdata = Getdata()
    data = getdata.get_config_data("config.yaml")
    print(data)
