#coding:utf8

from configparser import SafeConfigParser
from common.log import Logger
import common

class configRD():
    def __init__(self,path):
        self.path=path
        self.log=Logger(common.logpath)
        try:
            self.cRD=SafeConfigParser()
            self.cRD.read(self.path)
        except Exception as error:
            self.log.error(error)

    def get(self,section,key):
        try:
            return self.cRD.get(section,key)
        except Exception as error:
            self.log.error(error)

    def getint(self,section,key):
        try:
            return self.cRD.getint(section,key)
        except Exception as error:
            self.log.error(error)

    def getitems(self,field):
        try:
            self.items= self.cRD.items(field)
            values=[]
            keys=[]
            for key ,value in self.items:
                values.append(value)
                keys.append(key)
            return values,keys
        except Exception as error:
            self.log.error(error)

# if __name__=="__main__":
#     rd=configRD('../config/cf.ini')
#     print(rd.getint('sMySQ2L','port'))
#



