#coding:utf8

import pymysql
from common.log import Logger
import common


class connDB():
    def __init__(self,host,port,username,passwd,dbname,charset,timeout):
        self.host=host
        self.port=port
        self.username=username
        self.passwd=passwd
        self.dbname=dbname
        self.charset=charset
        self.timeout=timeout

        self.log=Logger(common.logpath)

    def connect(self):
        try:
            cdb=pymysql.connect(host=self.host,user=self.username,passwd=self.passwd,
                                db=self.dbname,charset=self.charset,read_timeout=self.timeout)
            return cdb
        except Exception as error:
             self.log.error(error)

    def getcursor(self,cdb):
        if cdb is not None:
            return cdb.cursor()

    def closecursor(self,cur):
        if cur is not None:
            return cur.close()

    def closeconn(self,cdb):
        if cdb is not None:
            return cdb.close()

# if __name__=="__main__":
#     conn=connDB('10.1.1.90',3306,'root','root','knowledge','utf8',288000)
#     cdb=conn.connect()
#     print(cdb)
#
