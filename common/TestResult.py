#coding:utf8

import xlsxwriter
import common
from common.log import Logger


class xlsw():

    def __init__(self,bookname):
        try:
            self.log=Logger(common.logpath)
            self.bookname=bookname
            self.creatXlsx()
            self.createColname()
        except Exception as error:
            self.log.error(error)


    def creatXlsx(self):
        try:
            self.book=xlsxwriter.Workbook(self.bookname)
            self.sheet=self.book.add_worksheet()
            self.sheet.set_column('A:H',20)
        except Exception as error:
            self.log.error(error)

    def createColname(self):
        try:
            self.sheet.write(0,0,'recipe_id/event_no/patient_id')
            self.sheet.write(0,1, 'message_id')
            self.sheet.write(0,2, 'branch_name')
            self.sheet.write(0,3, 'subject_id')
            self.sheet.write(0,4, 'subject_type')
            self.sheet.write(0,5, 'msg_content')
            self.sheet.write(0,6, 'advice')
            self.sheet.write(0,7,'severity')

        except Exception as error:
            self.log.error(error)

    def writeData(self,count,contents):
        try:
            for i in range(len(contents)):
                self.sheet.write(count,i,str(contents[i]))
                # print(count,i,str(contents[i]))
        except Exception as error:
            self.log.error(error)

    def closeXlsx(self):
        self.book.close()

