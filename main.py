import sys
import os
from os.path import dirname, join
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow ,QApplication, QWidget, QDialog, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import pandas as pd
import cv2
import numpy as np
import csv
import ocr
import database

from collections import Counter
strings=['']
def tally(strings):
    # Create a dictionary to store the count of each string
    count = Counter(strings)
    # Find the most common string
    most_common = max(count, key=count.get)
    return most_common

ttxt=tally(strings)

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture("vid1f.mp4")
        i = 0
        while True:
            ret, cv_img = cap.read()
            try:
                    store=cv_img
                    cv_img,text = ocr.readtxt(cv_img)
                    strings.append(text)
            except:
                    #print('plate no.', tally(strings))
                    #vehicle = database.Dataentry(tally(strings))
                    cv_img=store
                    plno=tally(strings)
                    print('plate no', plno)
                    vehicle= database.DataEntry(plno)
                    screen.closeEvent()
                    #exit()
            if ret:
                        self.change_pixmap_signal.emit(cv_img)
                        # Press Q on keyboard to exit


class CamVideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture("vid6r.mp4")
        i = 0
        while True:
                ret, cv_img = cap.read()
                if ret:
                    self.change_pixmap_signal.emit(cv_img)
                    # Press Q on keyboard to exit


class UserUI(QMainWindow):
    def __init__(self):
        super(UserUI, self).__init__()
        loadUi("uiuser.ui",self)

        width=1200
        height=720
        self.setMinimumSize(width, height)

        self.display_width = 540
        self.display_height = 720
        #video parameters:
        # create the video capture thread
        self.thread = CamVideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()


        self.actionAdminView.triggered.connect(self.gotoadminView)

    def gotoadminView(self):
        ascreen = AdminUI()
        widget.addWidget(ascreen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.show()

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

        # video parameters:
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()


        #button actions:
        self.actionUserView.triggered.connect(self.gotouserView)
        self.UpdateButton.clicked.connect(self.loaddata)

    def gotouserView(self):
        widget.setCurrentIndex(widget.currentIndex()-1)

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


app = QApplication(sys.argv)
screen= UserUI()
widget= QtWidgets.QStackedWidget()
widget.addWidget(screen)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")