#coding:utf

import logging
class Logger():
    def __init__(self,path,clevel=logging.DEBUG,flevel=logging.DEBUG):

        self.logger=logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt=logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',"%Y-%m-%d %H:%M:%S")
        # sh=logging.StreamHandler()
        # sh.setFormatter(fmt)
        # sh.setLevel(clevel)

        fh=logging.FileHandler(path)
        fh.setFormatter(fmt)
        fh.setLevel(flevel)
        self.logger.addHandler(fh)
        # self.logger.addHandler(sh)


    def debug(self,message):
        self.logger.debug(message)

    def info(self,message):
        self.logger.info(message)

    def war(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)

if __name__=="__main__":
    # logyyx=Logger('d:/yyx.log',logging.ERROR,logging.DEBUG)
    # logyyx.debug('onedebugerror')
    # logyyx.info('oneinfoerror')

    # logyyx2=Logger('d:/yyx.log',logging.ERROR,logging.DEBUG)
    # logyyx2.debug('onedebugerror2')
    # logyyx2.info('oneinfoerror2')
    pass



