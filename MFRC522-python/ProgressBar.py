from PySide2.QtWidgets import *
import sys
from PySide2.QtGui import *
import Read
import time


#Create the window
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Progress Bar")
        self.setGeometry(300,300,500,400)
        self.setMinimumHeight(480)
        self.setMinimumWidth(800)
        self.setMaximumHeight(480)
        self.setMaximumWidth(800)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#DBCEB1"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setIcon()
        self.Read = Read.Read()
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(self.Read.startTime)
        self.progressBar.setMaximum(self.Read.endTime)
        self.StatusBar()
    
   
    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)
        
    #Create the status bar
    def StatusBar(self):
        self.statusBar = QStatusBar()
        self.statusBar.addWidget(self.progressBar, 1)
        self.setStatusBar(self.statusBar)
        self.progressBar.setValue(self.Read.startTime)    
        self.progressBar.setFixedSize(750,150)
        self.progressBar.move(100,0)
        self.progressBar.setStyleSheet('QStatusBar {background-color: #005BA9; color: black;}')
