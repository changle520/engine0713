#coding:utf8

from common.ConnectDB import connDB
from common.log import Logger
from common.TestResult import xlsw
import datetime,os

curdate=datetime.datetime.now().strftime("%Y-%m-%d")
logpath=os.path.abspath("./log/{}.txt".format(curdate))

class getmessage():
    def __init__(self,conrd):
        self.conrd=conrd
        self.log=Logger(logpath)
        self.havemids = []  # 存储已经核对的messageid

        #标准数据库实例化
        self.conn_standard=connDB(self.conrd.get('sMySQL','host'),
                         self.conrd.getint('sMySQL','port'),
                         self.conrd.get('sMySQL','user'),
                         self.conrd.get('sMySQL','passwd'),
                         self.conrd.get('sMySQL','dbname'),
                         self.conrd.get('sMySQL','charset'),
                         self.conrd.getint('sMySQL','read_timeout'))
        self.conns = self.conn_standard.connect()
        self.curs = self.conn_standard.getcursor(self.conns)

        #实际结果数据库实例化
        self.conn_reality=connDB(self.conrd.get('rMySQL','host'),
                         self.conrd.getint('rMySQL','port'),
                         self.conrd.get('rMySQL','user'),
                         self.conrd.get('rMySQL','passwd'),
                         self.conrd.get('rMySQL','dbname'),
                         self.conrd.get('rMySQL','charset'),
                         self.conrd.getint('rMySQL','read_timeout'))
        self.connr = self.conn_reality.connect()
        self.curr = self.conn_reality.getcursor(self.connr)

    def result(self,sqlRlt):
        result={}
        for value in sqlRlt:
            result[value[0]]=value[1].split(',')
        return result

#获取标准数据库中的警示信息内容
    def getMessage_standard(self, sql, dbname, starttime,endtime):

        try:
            self.curs.execute(sql.format(dbname,starttime,endtime))
            rlt = self.curs.fetchall()
            return self.result(rlt)
        except Exception as error:
            self.log.error(error)

# 获取需验证引擎的数据库中的警示信息内容
    def getMessage_reality(self, sql, dbname, starttime,endtime):

        try:
            self.curr.execute(sql.format(dbname,starttime,endtime))
            rlt = self.curr.fetchall()
            return self.result(rlt)
        except Exception as error:
            self.log.error(error)

#比较两个数据库中的点评数据
    def compareMessage(self,message_s,message_r):
        samemessage={}  #存储警示信息相同的数据
        standardHave={} #存储同一个处方或患者或就诊流水号，标准库里面有跑出警示信息，实际对照的库里面没有跑出警示信息
        realityHave={}  #存储同一个处方或患者或就诊流水号，标准库里面没有跑出警示信息，实际对照的库里面有跑出警示信息

        for key,message in message_s.items():
            if message_r:
                if key in message_r:
                    if message_r[key]==message_s[key]:
                        samemessage[key]=message
                    elif message_r[key]!=message_s[key]:
                        standardHave[key]=set(message_s[key])-set(message_r[key])
                        realityHave[key] = set(message_r[key]) - set(message_s[key])
            else:
                self.log.info('message_r is null')
                break
        return samemessage,dict(standardHave),dict(realityHave)

#获取门诊的key_date
    def getoptKeyDate_s(self,dbname):
        self.sql=self.conrd.get('keydate','optalert')
        try:
             self.curs.execute(self.sql.format(dbname))
             self.date=self.curs.fetchall()
             self.starttime,self.endtime=self.date[4],self.date[11]
             return self.starttime[0],self.endtime[0]
        except Exception as error:
             self.log.error(error)

# 获取住院的key_date
    def getiptKeyDate_s(self,dbname):
        self.sql=self.conrd.get('keydate','iptalert')
        try:
             self.curs.execute(self.sql.format(dbname))
             self.date = self.curs.fetchall()
             self.starttime, self.endtime = self.date[4], self.date[11]
             return self.starttime[0], self.endtime[0]
        except Exception as error:
             self.log.error(error)

# 获取未跑出的警示信息的相关内容便于排查问题
    def messageContent_s(self,db_knowledge,db_dp,messageid,id,sql):
        self.sql=sql
        # print(self.sql.format(db_knowledge,db_dp,messageid,id))
        self.curs.execute(self.sql.format(db_knowledge,db_dp,messageid,id))
        sqlrlt=self.curs.fetchall()
        if sqlrlt:
            rlt=sqlrlt[0]
            return rlt

# 获取未跑出的警示信息的相关内容便于排查问题
    def messageContent_r(self, db_knowledge, db_dp, messageid, id, sql):
            self.sql = sql
            # print(self.sql.format(db_knowledge,db_dp,messageid,id))
            self.curr.execute(self.sql.format(db_knowledge, db_dp, messageid, id))
            sqlrlt = self.curr.fetchall()
            if sqlrlt:
                rlt = sqlrlt[0]
                return rlt

# 标准库里有跑出来，实际库里未跑出来的规则统计出来
    def messageContents_s(self, standardHave,db_knowledge,db_dp,sql,name):

            count=1

            self.xlsx = xlsw('./result/{}_{}_s.xlsx'.format(curdate,name))
            for id, messageids in standardHave.items():
                if set(messageids) & set(self.havemids)==set(messageids): #如果messageid已经在其它处方或医嘱中验证过便跳出此次循环
                    # print(messageids)
                    continue
                for messageid in messageids:
                    rlt=self.messageContent_s(db_knowledge,db_dp,messageid,id,sql)
                    if rlt:
                        if messageid not in self.havemids:
                             self.xlsx.writeData(count,rlt)
                             # print(rlt)
                             self.havemids.append(messageid)
                             count+=1
                             # if count==30:break
                # if count==30:break
            self.xlsx.closeXlsx()

# 实际库里有跑出来，标准库里未跑出来的规则统计出来
    def messageContents_r(self,realityHave,db_knowledge,db_dp,sql,name):
            print("输出实际数据库跑出来的结果")
            count=1
            havemids=[]#存储已经核对的messageid
            self.xlsx_r = xlsw('./result/{}_{}_r.xlsx'.format(curdate,name))
            for id, messageids in realityHave.items():
                if set(messageids) & set(havemids)==set(messageids): #如果messageid已经在其它处方或医嘱中验证过便跳出此次循环
                    # print(messageids)
                    continue
                for messageid in messageids:
                    rlt=self.messageContent_r(db_knowledge,db_dp,messageid,id,sql)
                    if rlt:
                        if messageid not in havemids:
                             self.xlsx_r.writeData(count,rlt)
                             havemids.append(messageid)
                             count+=1
                             # if count==30:break
                # if count==30:break
            self.xlsx_r.closeXlsx()

#获取知识建设库与点评库的messageid,公共的方法,代替以上备注的四个方法
    def messages_data(self,dbname,sqlname,field):
        self.sql=self.conrd.get(field,sqlname)
        self.curs.execute(self.sql.format(dbname))
        messages=self.curs.fetchall()
        return ([str(i[0]).strip() for i in messages])

#获取点评库中跑出警示信息的recipeid/eventno
    def getdpID(self,dbname,sqlname,messageid,field):
        self.sql = self.conrd.get(field, sqlname)
        # print(self.sql.format(dbname,messageid))
        self.curs.execute(self.sql.format(dbname,messageid))
        id = self.curs.fetchall()
        if id:
            return id[0][0]
        else:
            return None

#实际数据库是否有跑出警示信息
    def getdbr_messageid(self,dbnamer_dp,dbnamer_k,dpid,longid,sqlname,field):
        self.sql = self.conrd.get(field, sqlname)
        # print(self.sql)
        # print(self.sql.format(dbnamer_dp,dpid,dbnamer_k,longid))
        self.curr.execute(self.sql.format(dbnamer_dp,dpid,dbnamer_k,longid))
        id = self.curr.fetchall()
        if id:
            return str(id[0][0])
        else:
            return None

    def checkmessages(self,**kwargs):
        #标准知识库中所有规则的messageid
        self.knowledge_messages=self.messages_data(kwargs['dbnames_k'],kwargs['sqlnameAll'],kwargs['field1'])
        #标准点评库中门诊处方跑出来的所有messageid
        self.opt_messages=self.messages_data(kwargs['dbnames_dp'],kwargs['sqlnameOpt'],kwargs['field1'])
        #标准点评库中住院跑出来的所有messageid
        self.ipt_messages=self.messages_data(kwargs['dbnames_dp'],kwargs['sqlnameIpt'],kwargs['field1'])
        # 标准点评库中门诊患者跑出来的所有messageid
        self.optp_messages=self.messages_data(kwargs['dbnames_dp'],kwargs['sqlnameOpt_p'],kwargs['field1'])
        print(self.knowledge_messages)
        passmessages=[]
        failmessages=[]
        count_i,count_optr,count_optp = 1,1,1
        # self.xlsx = xlsw('./result/{}2.xlsx'.format(curdate))
        self.xlsx_ipt = xlsw('./result/{}_ipt.xlsx'.format(curdate))
        self.xlsx_optr = xlsw('./result/{}_optr.xlsx'.format(curdate))
        self.xlsx_optp = xlsw('./result/{}_optp.xlsx'.format(curdate))


        for messageid in self.knowledge_messages:
            if messageid in self.ipt_messages:
                self.id=self.getdpID(kwargs['dbnames_dp'],kwargs['eventno'],messageid,kwargs['field2'])
                self.rlt=self.getdbr_messageid(kwargs['dbnamer_dp'],kwargs['dbnamer_k'],self.id,messageid,kwargs['iptrlt'],kwargs['field3'])
                if self.rlt and self.rlt == messageid:
                    passmessages.append(messageid)
                else:
                    self.sql=self.conrd.get("enginecontent",'iptalert')
                    # print(self.id,self.sql)
                    result = self.messageContent(kwargs['dbnames_k'], kwargs['dbnames_dp'], messageid, self.id,self.sql)
                    # print(result)
                    self.xlsx_ipt.writeData(count_i, result)
                    count_i += 1
                    # if count==30:break

            elif messageid in self.opt_messages:
                self.id=self.getdpID(kwargs['dbnames_dp'],kwargs['recipeid'],messageid,kwargs['field2'])
                self.rlt=self.getdbr_messageid(kwargs['dbnamer_dp'],kwargs['dbnamer_k'],self.id,messageid,kwargs['optrlt'],kwargs['field3'])
                if self.rlt and self.rlt == messageid:
                    passmessages.append(messageid)
                else:
                    self.sql = self.conrd.get("enginecontent", 'optalert')
                    result = self.messageContent(kwargs['dbnames_k'], kwargs['dbnames_dp'], messageid, self.id, self.sql)
                    self.xlsx_optr.writeData(count_optr, result)
                    count_optr += 1
                    # if count==23:break
            elif messageid in self.optp_messages:
                self.id = self.getdpID(kwargs['dbnames_dp'], kwargs['patinetid'], messageid, kwargs['field2'])
                self.rlt = self.getdbr_messageid(kwargs['dbnamer_dp'], kwargs['dbnamer_k'], self.id, messageid,
                                                 kwargs['optrlt_p'], kwargs['field3'])
                if self.rlt and self.rlt == messageid:
                    passmessages.append(messageid)

                else:

                    self.sql = self.conrd.get("enginecontent", 'optalert_p')
                    result = self.messageContent(kwargs['dbnames_k'], kwargs['dbnames_dp'], messageid, self.id,
                                                 self.sql)
                    self.xlsx_optp.writeData(count_optp, result)
                    count_optp += 1
                    # if count == 10: break
            else:
                self.rlt=None
                failmessages.append(messageid)

        print(len(passmessages),passmessages)
        print(len(failmessages))
        self.xlsx_ipt.closeXlsx()
        self.xlsx_optr.closeXlsx()
        self.xlsx_optp.closeXlsx()


# if __name__=="__main__":
#     conrd = configRD('../../config/cf.ini')
#
#     dbname_s=conrd.get('sMySQL','dbname')
#     dbname_knowledge=conrd.get('sMySQL','dbname_knowledge')
#     getm = getmessage(conrd)
#     print(getm.messageContent(dbname_knowledge,dbname_s,'1513071367103'))
