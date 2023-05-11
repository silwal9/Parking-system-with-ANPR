import ocr
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QTimer      #
import numpy as np
from collections import Counter
import csv  # import the csv module                                      #
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem              #

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
        cap = cv2.VideoCapture("vid1.mp4")
        i = 0
        while True:
            try:
                    ret, cv_img = cap.read()
                    cv_img,text = ocr.readtxt(cv_img)
                    strings.append(text)
                    if ret:
                        self.change_pixmap_signal.emit(cv_img)
                        # Press Q on keyboard to exit
            except:
                print( 'plate no.', tally(strings))
                exit()

text=''
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 640
        self.display_height = 480

        # create the table widget                                       ##
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)                              ##

        # read data from CSV file and add to table widget
        '''with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:
                    self.tableWidget.setColumnCount(len(row))
                self.tableWidget.insertRow(i)
                for j, val in enumerate(row):
                    item = QTableWidgetItem(val)
                    self.tableWidget.setItem(i, j, item)                ## '''

        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        # create a text label
        self.textLabel = QLabel(ttxt)

        # create a text label for the video feed
        self.video_label = QLabel('Video Feed', self)       #


        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.tableWidget)               #
        vbox.addWidget(self.video_label)              #
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)

        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

        # start a timer to periodically load data from CSV          ##
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(1000)                                      ##


    def load_data(self):                                            ##
        # read data from CSV file and add to table widget
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(len(rows[0]))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(val)
                    self.tableWidget.setItem(i, j, item)            ##


    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())