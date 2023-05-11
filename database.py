import sys
import time
from datetime import datetime
import pandas as pd
import qr
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
            enter = df.loc[num, 'entry time'].iloc[-1]
            print("entry: ",enter)
            exit = self.entry[-1]
            print("exit: ", exit)

            duration = self.calcTime(enter, exit)
            total_seconds = duration.total_seconds()
            fee_per_second = 0.0277  # Rs 100/hr= Rs 0.0277/sec
            fee = total_seconds * fee_per_second
            print("fee:", fee)
            df.loc[num, 'fee'] = int(fee)
            qr.qrshow()

            #enter = time
            #exit = self.entry
            #print(enter,exit)
            #duration = self.calcTime(enter, exit)
            #print(f"Duration is {duration} (Hours:Minutes:Seconds)")
            # Output: Duration is 0:00:05 (Hours:Minutes:Seconds)
            df.to_csv('data.csv', index=False )
            return True, fee
        else:
            self.datawrite()
            return False, 0


        ''' didnt work: spaces in between rows
        with open("data.csv", "r") as csvfile, tempfile:
        # Create a temporary file in write mode ("w")to hold new values
        tempfile = NamedTemporaryFile(mode="w", delete=False)
        # Fields are the columns for the CSV file we wish to update
        fields = ['date','entry time','exit time','v_number','fee']
        # Open the CSV file in read mode ("r").
        # We will write into the temporary file first.
            # Create reader and writer objects using csv library.
            reader = csv.DictReader(csvfile, fieldnames=fields)
            writer = csv.DictWriter(tempfile, fieldnames=fields)
            # Loop trow the rows of the CSV file
            for row in reader:
                # Based on the value of the "ID" column, create edits on the temporary file
                if row["v_number"] == str(V_number):
                    print("Updating row with plate=", row["v_number"])
                    # New data
                    self.exit=[{self.current_time}]
                    self.fee=[120]
                    new_data = [{'date':self.date,'entry time':self.entry,'exit time':self.exit,'v_number':self.num,'fee':self.fee}]
                    # Update the dictionary data with the new data, new_data.
                    row["date"], row["entry time"], row["exit time"], row["v_number"],row["fee"] = new_data
                    # create a complete row of data to write into the temporary file
                    row = {"date": row["date"],"entry time": row["entry time"],"exit time": row["exit time"],"v_number": row["v_number"],"fee":row["fee"]}
                    # write the row with the new data
                    writer.writerow(new_data)
        # Move the temporary file to the original CSV file. This replaces employees.csv.

        shutil.move(tempfile.name, "data.csv")
        '''


        '''
        fieldnames=['date','entry time','exit time','v_number','fee']
        with open('data.csv', 'r') as csvfile , open('data.csv', 'a') as csvfile2 :
           reader = csv.DictReader(csvfile, fieldnames=fieldnames)
           writer = csv.DictWriter(csvfile2, fieldnames=fieldnames)
           for row in reader:
               if V_number == row['v_number']:
                self.exit.append(self.current_time)
                self.fee=200
                # write the row either way
               writer.writerow({'date':self.date,'entry time':self.entry,'exit time':self.exit,'v_number':self.num,'fee':self.fee})
        '''

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



#vehicle = DataEntry('12989')


#BAA8451
#vehicle.datawrite()

