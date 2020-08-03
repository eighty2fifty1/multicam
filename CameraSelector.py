import RPi.GPIO as GPIO
from time import sleep
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject


class Selector(QObject):
    camSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(18, GPIO.OUT, initial=GPIO.HIGH)

    def selectCamera(self, sel):
        self.sel = sel
        if self.sel == 1:
            GPIO.output(32, 1)
            GPIO.output(16, 1)
            GPIO.output(18, 1)
            self.camSelected.emit(1)
        elif self.sel == 2:
            GPIO.output(32, 0)
            GPIO.output(16, 1)
            GPIO.output(18, 1)
            self.camSelected.emit(2)
        elif self.sel == 3:
            GPIO.output(32, 1)
            GPIO.output(16, 0)
            GPIO.output(18, 1)
            self.camSelected.emit(3)
        elif self.sel == 4:
            GPIO.output(32, 0)
            GPIO.output(16, 0)
            GPIO.output(18, 1)
            self.camSelected.emit(4)

    def pairCamera(self, pair):
        self.pair = pair

        if self.pair == 1:
            GPIO.output(32, 1)
            GPIO.output(16, 1)
            GPIO.output(18, 0)
            self.camSelected.emit(1)

        elif self.pair == 2:
            GPIO.output(32, 0)
            GPIO.output(16, 1)
            GPIO.output(18, 0)
            self.camSelected.emit(2)

        elif self.pair == 3:
            GPIO.output(32, 1)
            GPIO.output(16, 0)
            GPIO.output(18, 0)
            self.camSelected.emit(3)

        elif self.pair == 4:
            GPIO.output(32, 0)
            GPIO.output(16, 0)
            GPIO.output(18, 0)
            self.camSelected.emit(4)
