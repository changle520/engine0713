#coding:utf8
import datetime,os

curdate=datetime.datetime.now().strftime("%Y-%m-%d")
logpath=os.path.abspath("./log/{}.txt".format(curdate))
