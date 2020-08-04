#!/usr/bin/python3
# this version is an attempt to use 2 separate .ui files and some mega multiple inheritance.
# it won't load both screens at once and won't scale the small screen image properly.
# probably a dead end

import sys
import threading
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QCoreApplication
from CameraSelector import *
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import sys
import cv2
import queue
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QApplication, QPushButton

running = False          # use this to pause the stream
capture_thread = None
bigwindowShown = False
bigwindow_class = uic.loadUiType("multicam2.ui")[0]
smallwindow_class = uic.loadUiType("multicamSmall.ui")[0]
pressTime = 0
relTime = 0
q = queue.Queue()


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)
        self.setGeometry(0, 0, 640, 480)

    def mousePressEvent(self, e):
        print("event triggered")
        self.clicked.emit()
        super(ClickableLabel, self).mousePressEvent(e)


class Thread(QThread):

    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while running:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                if q.qsize() < 10:
                    q.put(frame)
                else:
                    print(q.qsize())

                if not q.empty():
                    f = q.get()
                    rgbImage = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    i = convertToQtFormat.copy()
                    self.changePixmap.emit(i)

        if self.isFinished():
            print("thread killed")


class MyWindowClass(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.sel = Selector()
        self.press = 0
        self.rel = 0
        # self.startButton.clicked.connect(self.start_clicked)
        self.videoLbl = ClickableLabel(self.videoLbl)
        self.setWindowTitle('Camera')

        self.connectSignals()
        # self.th = Thread(self)
        # self.th.changePixmap.connect(self.setImage)
        # self.th.start()
        # self.show()

    @pyqtSlot(QImage)
    def setImage(self, i):
        p = i.scaled(self.videoLbl.size(), Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(p)
        self.videoLbl.setPixmap(pixmap)

    def prPress(self):
        global pressTime
        pressTime = time.time()
        print(self.buttonGroup.checkedId())

    def prRel(self):
        global relTime
        relTime = time.time()
        cam2pair = self.buttonGroup.checkedId()

        if relTime - pressTime > 3:
            print("attempting to pair")
            threading.Thread(target=self.pair, args=(cam2pair,)).start()

    def pair(self, c):
        self.sel.pairCamera(c)
        print(f"pairing cam {c}")
        sleep(5)
        self.sel.selectCamera(c)
        print("done")

    def selected(self, active):
        if active == 1:
            self.cam1.setChecked(True)
        elif active == 2:
            self.cam2.setChecked(True)
        elif active == 3:
            self.cam3.setChecked(True)
        elif active == 4:
            self.cam4.setChecked(True)
        print(f"camera {active} selected")

    def _resize(self):
        global bigwindowShown
        if bigwindowShown:
            big_window.hide()
            small_window.show()
            bigwindowShown = False

        else:
            big_window.show()
            small_window.hide()
            bigwindowShown = True

    # signal connections
    def connectSignals(self):
        self.cam1.clicked.connect(lambda: self.sel.selectCamera(1))
        self.cam2.clicked.connect(lambda: self.sel.selectCamera(2))
        self.cam3.clicked.connect(lambda: self.sel.selectCamera(3))
        self.cam4.clicked.connect(lambda: self.sel.selectCamera(4))

        self.buttonGroup.setId(self.cam1, 1)
        self.buttonGroup.setId(self.cam2, 2)
        self.buttonGroup.setId(self.cam3, 3)
        self.buttonGroup.setId(self.cam4, 4)
        '''
        self.resizeButton.clicked.connect(resizeWindow)
        self.posCheck.clicked.connect(posit)
        '''
        self.pairButton.pressed.connect(self.prPress)
        self.pairButton.released.connect(self.prRel)

        self.sel.camSelected.connect(self.selected)
        self.videoLbl.clicked.connect(self._resize)


class BigWindowClass(MyWindowClass, bigwindow_class):
    def __init__(self, parent=None):
        MyWindowClass.__init__(self, parent)


class SmallWindowClass(MyWindowClass, smallwindow_class):
    def __init__(self, parent=None):
        MyWindowClass.__init__(self, parent)

        self.videoLbl.setGeometry(0, 0, 200, 150)

th = Thread()


app = QtWidgets.QApplication(sys.argv)
big_window = BigWindowClass(None)
small_window = SmallWindowClass(None)
th.changePixmap.connect(big_window.setImage)
th.changePixmap.connect(small_window.setImage)
th.start()

small_window.move(600, 60)
small_window.show()
running = True

app.exec_()
