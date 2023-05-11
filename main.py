import sys
import time
import vecrec
import database
import os
from os.path import dirname, join
from PyQt5.QtGui import QPixmap
import qr
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow ,QApplication, QWidget, QDialog, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import pandas as pd
import cv2
import numpy as np
import csv
import ocr

from collections import Counter


strings=['']
def tally(strings):
    # Create a dictionary to store the count of each string
    count = Counter(strings)
    # Find the most common string
    most_common = max(count, key=count.get)
    return most_common


class VideoThread(QThread):


    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        i = 0
        frame = 0
        fee=0
        chkframe = 0
        vehiclefee=False
        vdetect= False
        checkframe = False
        path = i
        #cap = cv2.VideoCapture(path, cv2.CAP_DSHOW)
        cap = cv2.VideoCapture("vid000.mp4")
        time.sleep(2)  # time to allow for camera to set up
        success , prev = cap.read()


        while cap.isOpened():
            ret, cv_img = cap.read()
            #print(ret,cap.isOpened)
            if ret:
                vfound=vecrec.vecrec(prev, cv_img)
                if vfound != 0 and not vdetect:
                    frame +=1
                    #print(frame)
                    checkframe=True
                    if frame > 15 and chkframe <= 45:
                        vdetect=True
                        checkframe=False
                        frame=0
                    elif frame < 15 and chkframe> 45:
                        frame=0
                        chkframe=0
                #print(chkframe)
                if checkframe:
                    chkframe+=1
                if vdetect and (frame <100):
                    #print(frame)
                    frame+=1
                    cv_img, text = ocr.readtxt(cv_img)
                    if len(str(text)) in [7, 8]:
                        strings.append(text)
                elif vdetect and not(frame < 100):
                    vdetect=False
                    plno = tally(strings)
                    strings.clear()
                    if len(plno) in [7,8]:
                        print('plate no.', plno)
                        vehicle = database.DataEntry(plno)
                        vehiclefee, fee= vehicle.check(plno)
                        print (vehiclefee,fee)
                    if vehiclefee:
                        ascreen.loaddata()
                        screen.setqr(fee,plno)
                        ascreen.gotouserView()
                    else:
                        screen.setqr(-1,plno)
                        ascreen.loaddata()
                    frame=0
                prev = cv_img
                cv2.putText(cv_img, 'Frame no. : {}'.format(frame), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                self.change_pixmap_signal.emit(cv_img)

                # Press Q on keyboard to exit
            else:
                plno = tally(strings)
                strings.clear()
                if len(plno) in [7, 8]:
                    print('plate no.', plno)
                    vehicle = database.DataEntry(plno)
                    vehiclefee, fee = vehicle.check(plno)

                    print(vehiclefee, fee)
                if vehiclefee:
                    ascreen.loaddata()
                    screen.setqr(fee, plno)
                    ascreen.gotouserView()
                else:
                    screen.setqr(-1, plno)
                    ascreen.loaddata()



                cv2.waitKey(3000)
                break




class CamVideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        path = "ford.mp4"
        cap = cv2.VideoCapture(path)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class UserUI(QMainWindow):
    def __init__(self):
        super(UserUI, self).__init__()
        loadUi("uiuser.ui",self)
        width=1200
        height=720
        self.setMinimumSize(width, height)

        self.display_width = 540
        self.display_height = 720

        self.actionAdminView.triggered.connect(self.gotoadminView)

    def setqr(self,charge,numplate):

        if charge != -1:
            qt_img = qr.qrshow()
            qt_img = self.convert_cv_qt(qt_img)
            self.qr.setPixmap(qt_img)
            self.fee.setText(str("Fee:" + str(charge)+ " for No. Plate:" + numplate))
        else:
            self.fee.setText(str("Entry completed" + " for No. Plate:" + numplate))

    def gotoadminView(self):
        widget.addWidget(ascreen)
        ascreen.startvdo()
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.videoadm.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


class AdminUI(QMainWindow):
    def __init__(self):
        super(AdminUI, self).__init__()
        loadUi("ui.ui",self)
        width = 1200
        height = 720
        self.setMinimumSize(width, height)

        self.display_width = 540
        self.display_height = 720
        # button actions:
        self.actionUserView.triggered.connect(self.gotouserView)
        self.UpdateButton.clicked.connect(self.loaddata)

        # video parameters:
    def startvdo(self):
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()






    def videostop(self):
        self.thread.terminate()

    def gotouserView(self):
        widget.setCurrentIndex(widget.currentIndex()-1)

        widget.show()

    def loaddata(self):
        #use self.table...
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader) # skip header row
            rows = list(reader)
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(rows[0]))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(val)
                    self.table.setItem(i, j, item)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):

        """Updates the image_label with a new opencv image"""

        qt_img = self.convert_cv_qt(cv_img)
        self.videoadm.setPixmap(qt_img)


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)




app = QApplication(sys.argv)
screen= UserUI()
ascreen=AdminUI()
widget= QtWidgets.QStackedWidget()
widget.setWindowTitle("Parcc")
widget.setWindowIcon(QtGui.QIcon("logo.png"))
widget.addWidget(screen)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")