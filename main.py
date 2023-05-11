import ocr
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from collections import Counter
import csv  # import the csv module         #

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
        cap = cv2.VideoCapture("vid3f.mp4")
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
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        # create a text label for the video feed            ##
        self.video_label = QLabel('Video Feed', self)

        # create a text label for the CSV data
        self.csv_label = QLabel('Number Plate Data', self)           ##

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.video_label)              #
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.csv_label)                 #

        # read data from the CSV file and add it to the CSV label   ##
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                vbox.addWidget(QLabel('| '.join(row), self))        ##


        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

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