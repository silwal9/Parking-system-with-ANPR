import sys
import time
from datetime import datetime
import pandas as pd
from tempfile import NamedTemporaryFile
import shutil
import csv
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

class DataEntry():
    def __init__(self, V_number):
        self.fee= ''
        self.datamode='a'  #w for write r for read a for append
        self.entry = list()
        self.exit = list()
        self.num = list()
        self.date = list()
        self.t = time.localtime()
        self.current_time = time.strftime("%H:%M:%S", self.t)
        self.current_date = time.strftime("%Y-%m-%d", self.t)
        self.date.append(self.current_date)
        self.entry.append(self.current_time)
        self.exit.append('')
        self.num.append(V_number)
        self.setval()
        self.check(V_number)

    def calcTime(self, enter, exit):
        format = "%H:%M:%S"
        # Parsing the time to str and taking only the hour,minute,second
        # (without miliseconds)
        enterStr = str(enter).split(".")[0]
        exitStr = str(exit).split(".")[0]
        # Creating enter and exit time objects from str in the format (H:M:S)
        enterTime = datetime.strptime(enterStr, format)
        exitTime = datetime.strptime(exitStr, format)
        return exitTime - enterTime

    def check(self,V_number):
        df=pd.read_csv('data.csv')
        num= df['v_number'] == V_number
        result = (num).any()
        if result:
            #time = df.loc[num,'entry time']
            df.loc[num,'exit time']=self.entry
            #df.loc[num, 'fee'] = 1500
            #enter = time
            #exit = self.entry
            #print(enter,exit)
                #duration = self.calcTime(enter, exit)
                #total_seconds = duration.total_seconds()
                #fee_per_second = 1.66  # Rs 100/hr= Rs 1.66/sec
                #fee = total_seconds * fee_per_second
                #df.loc[num,'fee']=fee
            #print(f"Duration is {duration} (Hours:Minutes:Seconds)")
            # Output: Duration is 0:00:05 (Hours:Minutes:Seconds)

            df.to_csv('data.csv', index=False )
        else:
            self.datawrite()

    def setval(self):
        if self.datamode=='a':
            self.headerval=False
        else:
            self.headerval = True



    def datawrite(self):
        #print(self.date,self.entry,self.exit,self.num)
        self.data={'date':self.date,'entry time':self.entry,'exit time':self.exit,'v_number':self.num,'fee':self.fee}
        self.df=pd.DataFrame(self.data)
        self.df.to_csv('data.csv', index=False, mode=self.datamode,header=self.headerval)



#vehicle = DataEntry('999')  #BAA8451
#vehicle.datawrite()

