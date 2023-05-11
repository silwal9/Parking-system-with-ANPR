import sys
import qrcode
import time
import vecrec
import database
import os
from os.path import dirname, join
from PyQt5.QtGui import QPixmap
import qr
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow ,QApplication, QWidget, QFileDialog, QTableWidgetItem
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
    def __init__(self,pathname):
        super().__init__()
        self._run_flag = True
        self.path = pathname

    change_pixmap_signal = pyqtSignal(np.ndarray)


    def run(self):
        cap = cv2.VideoCapture(self.path) #use i for webcam
        # cap = cv2.VideoCapture(path, cv2.CAP_DSHOW) #for webcam
        time.sleep(2)  # time to allow for camera to set up`
        success , prev = cap.read()
        notfound = 0
        recframe=0
        frame = 0
        fee = 0
        chkframe = 0
        vehiclefee = False
        vdetect = False
        checkframe = False
        plno=''
        while cap.isOpened():
            ret, cv_img = cap.read()
            #print(ret,cap.isOpened)
            if ret:
                vfound=vecrec.vecrec(prev, cv_img)
                if vfound != 0 and not vdetect:
                    recframe +=1
                    checkframe=True
                    if recframe > 15 and chkframe <= 45:
                        vdetect=True
                        checkframe=False
                        recframe=0
                    elif recframe < 15 and chkframe>= 45:
                        recframe=0
                        chkframe=0
                if checkframe:
                    chkframe+=1
                print("rec",recframe)
                if vdetect and (frame <100) and vfound != 0:
                    print(frame)
                    frame+=1
                    cv_img, text = ocr.readtxt(cv_img)
                    if len(str(text)) in [7, 8]:
                        strings.append(text)
                    notfound=0
                elif vdetect and frame<100 and vfound==0:
                    frame += 1
                    notfound +=1
                    print("not found",notfound)
                elif vdetect and not(frame < 100) or notfound>15:
                    notfound=0
                    vdetect=False
                    if len(strings)!=0:
                        plno = tally(strings)
                    else:
                        plno=''
                    strings.clear()
                    if len(plno) in [7,8]:
                        print('plate no.', plno)
                        vehicle = database.DataEntry(plno)
                        vehiclefee, fee= vehicle.check(plno)
                        print (vehiclefee,fee)
                    if vehiclefee:
                        screen.setqr(fee,plno)
                        fee=0
                        ascreen.loaddata()
                    else:
                        screen.setqr(-1,plno)
                        ascreen.loaddata()
                    frame=0
                    recframe=0
                prev = cv_img
                #cv2.putText(cv_img, 'Frame no. : {}'.format(frame), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                self.change_pixmap_signal.emit(cv_img)

                # Press Q on keyboard to exit
            else:
                if len(strings) != 0:
                    plno = tally(strings)
                strings.clear()
                if len(plno) in [7, 8]:
                    print('plate no.', plno)
                    vehicle = database.DataEntry(plno)
                    vehiclefee, fee = vehicle.check(plno)

                    print(vehiclefee, fee)
                if vehiclefee:
                    screen.setqr(fee, plno)
                    ascreen.loaddata()
                    #fee=0
                    #widgetuser.addWidget(screen)
                   # widgetuser.showMaximized()
                else:
                    screen.setqr(-1, plno)
                    ascreen.loaddata()
                break

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class CamThread(VideoThread):
    def __init__(self):
        super().__init__(0)

    '''def run(self):
        cap = cv2.VideoCapture(self.path, cv2.CAP_DSHOW) #for webcam
        time.sleep(2)  # time to allow for camera to set up`
        success, prev = cap.read()
        notfound = 0
        recframe = 0
        frame = 0
        fee = 0
        chkframe = 0
        vehiclefee = False
        vdetect = False
        checkframe = False
        plno = ''
        while cap.isOpened():
            ret, cv_img = cap.read()
            # print(ret,cap.isOpened)
            if ret:
                vfound = vecrec.vecrec(prev, cv_img)
                if vfound != 0 and not vdetect:
                    recframe += 1
                    checkframe = True
                    if recframe > 15 and chkframe <= 45:
                        vdetect = True
                        checkframe = False
                        recframe = 0
                    elif recframe < 15 and chkframe >= 45:
                        recframe = 0
                        chkframe = 0
                if checkframe:
                    chkframe += 1

                if vdetect and (frame < 100) and vfound != 0:
                    print(frame)
                    frame += 1
                    cv_img, text = ocr.readtxt(cv_img)
                    if len(str(text)) in [7, 8]:
                        strings.append(text)
                    notfound = 0
                elif vdetect and frame < 100 and vfound == 0:
                    frame += 1
                    notfound += 1
                elif vdetect and not (frame < 100) or notfound > 15:
                    notfound = 0
                    vdetect = False
                    if len(strings) != 0:
                        plno = tally(strings)
                    strings.clear()
                    if len(plno) in [7, 8]:
                        print('plate no.', plno)
                        vehicle = database.DataEntry(plno)
                        vehiclefee, fee = vehicle.check(plno)
                        print(vehiclefee, fee)
                    if vehiclefee:
                        screen.setqr(fee, plno)
                        fee = 0
                        ascreen.loaddata()
                    else:
                        screen.setqr(-1, plno)
                        ascreen.loaddata()
                    frame = 0
                prev = cv_img
                # cv2.putText(cv_img, 'Frame no. : {}'.format(frame), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                self.change_pixmap_signal.emit(cv_img)

                break'''

class UserUI(QMainWindow):
    def __init__(self):
        super(UserUI, self).__init__()
        loadUi("uiuser.ui",self)
        width=1200
        height=720
        self.setMinimumSize(width, height)

        self.display_width = 540
        self.display_height = 720

    #buttion action:
        self.actionAdminView.triggered.connect(self.gotoadminView)

    def setqr(self,charge,numplate):

        if charge != -1:
            qt_img = qr.qrshow()
            qt_img = self.convert_cv_qt(qt_img)
            self.qr.setPixmap(qt_img)
            self.fee.setText(str("Fee:" + str(int(charge))+ " for No. Plate:" + numplate))
        else:
            self.fee.setText(str("Entry completed" + " for No. Plate:" + numplate))

    def gotoadminView(self):
        widget.addWidget(ascreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.video.setPixmap(qt_img)

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
        self.actionVideoFile.triggered.connect(self.startvdo)
        self.actionLiveFeed.triggered.connect(self.livefeed)
        #setup:
        self.loaddata()

        # video parameters:
    def startvdo(self):
            fname=QFileDialog.getOpenFileName(self, 'Open File', '')
            print(fname[0])
            # create the video capture thread
            self.thread = VideoThread(fname[0])
            # connect its signal to the update_image slot
            self.thread.change_pixmap_signal.connect(self.update_image)
            # start the thread
            self.thread.start()


    def gotouserView(self):
        widget.setCurrentIndex(widget.currentIndex()-1)
        widget.show()


    def livefeed(self):
            self.camthread=CamThread()
            # connect its signal to the update_image slot
            self.camthread.change_pixmap_signal.connect(self.update_image)
            # start the thread
            self.camthread.start()

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
        if self.event._run_flag == True:
            event.stop()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):

        """Updates the image_label with a new opencv image"""

        qt_img = self.convert_cv_qt(cv_img)
        screen.video.setPixmap(qt_img)
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