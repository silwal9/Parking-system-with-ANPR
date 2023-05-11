import sys
import time
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

datamode='a' #w for write r for read a for append
if datamode=='a':
    headerval=False
else:
    headerval = True
entry=list()
exit=list()
num=list()
date=list()

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
current_date=time.strftime("%Y-%m-%d", t)
date.append(current_date)
entry.append(current_time)
exit.append(current_time)
num.append(input("Enter number:"))

print(date,entry,exit,num)
data={'date':date,'entry time':entry,'exit time':exit,'v_number':num}
df=pd.DataFrame(data)
df.to_csv('data.csv', index=False, mode=datamode,header=headerval)



