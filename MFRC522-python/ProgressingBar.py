# Necessary imports
import sys
import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

# import from python files in MFRC522
import Read
import Write
from Timbreuse import *


class ProgressingBar(MainWindow):
    
    def __init__(self):
        super().__init__()
        self.Read = Read.Read()
        
        self.progressBar = QProgressBar()


    def ProgressBar(self):
        self.progressBar.setGeometry(30,40,200,25)
        
        # Set timer
        self.timer = QBasicTimer()
        
        # Set step (=initial position)
        self.step = self.Read.startTime
        
        
        self.progressBar.show(self.window)
        
        
    def startProgress(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(100,self)

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.setButtonBackToConfigure("baseWindow")
            return
        self.step += 1
        self.progressBar.setValue(self.step)