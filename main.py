#coding:utf8
from db.opt.message import getmessage
from common.ConfigRead import configRD

conrd=configRD('./config/cf.ini')
getm=getmessage(conrd)
exesqls=conrd.getitems('exesql')[0]
dbname_s=conrd.get('sMySQL','dbname')
dbname_knowledge=conrd.get('sMySQL','dbname_knowledge')
dbname_r = conrd.get('rMySQL', 'dbname')
dbnamer_k = conrd.get('rMySQL', 'dbname_knowledge')
sqlname=conrd.getitems('messages')[1]
dpid=conrd.getitems('dpid')[1]
rltkey=conrd.getitems('havemessage')[1]
starttime,endtime=getm.getoptKeyDate_s(dbname_s)
print(starttime,endtime)

#以门诊处方为维度进行测试
def run_opt():
    sql=conrd.get('enginecontent','optalert')
    message_s=getm.getMessage_standard(exesqls[0],dbname_s,starttime,endtime)
    message_r=getm.getMessage_reality(exesqls[0], dbname_r, starttime,endtime)
    # print(message_s,'\n',message_r)
    samemessage, standardHave, realityHave=getm.compareMessage(message_s,message_r)
    print(standardHave, '\n',realityHave)
    print(len(samemessage), '\n', len(standardHave), '\n', len(realityHave))
    getm.messageContents_s(standardHave,dbname_knowledge,dbname_s,sql,name='门诊处方_标准')
    getm.messageContents_r(realityHave, dbnamer_k, dbname_r, sql, name='门诊处方_实际')

#以住院患者为维度进行测试
def run_ipt():
    sql = conrd.get('enginecontent', 'iptalert')
    messageipt_s = getm.getMessage_standard(exesqls[1], dbname_s, starttime, endtime)
    messageipt_r = getm.getMessage_reality(exesqls[1], dbname_r, starttime, endtime)
    samemessage_ipt, standardHave_ipt, realityHave_ipt = getm.compareMessage(messageipt_s, messageipt_r)
    print(standardHave_ipt)
    print(len(samemessage_ipt), '\n', len(standardHave_ipt), '\n', len(realityHave_ipt))
    getm.messageContents_s(standardHave_ipt, dbname_knowledge, dbname_s, sql,name="住院患者_标准")
    getm.messageContents_r(realityHave_ipt, dbnamer_k, dbname_r, sql, name='住院患者_实际')

#以知识库中每条规则对应的警示信息id为维度进行测试
def runmessages():
       getm.checkmessages(dbnames_k=dbname_knowledge,dbnames_dp=dbname_s,sqlnameAll=sqlname[0],sqlnameOpt=sqlname[1],
                       sqlnameIpt=sqlname[2],sqlnameOpt_p=sqlname[3],recipeid=dpid[0],eventno=dpid[1],patinetid=dpid[2],
                       dbnamer_dp=dbname_r,dbnamer_k=dbnamer_k,optrlt=rltkey[0],iptrlt=rltkey[1],optrlt_p=rltkey[2],
                       field1='messages',field2='dpid',field3='havemessage')


if __name__=="__main__":
    print("执行住院患者维度下的点评数据核对............")
    run_ipt()
    print("住院患者维度下的点评数据核对结束")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("执行门诊处方维度下的点评数据核对............")
    run_opt()
    print("门诊处方维度下的点评数据核对结束")


