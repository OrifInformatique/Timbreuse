# import all necessary ressources

import sys, time, AdminWindow, AdminWindow, ProgressBar, Read, Write
from PySide2 import QtGui
from PySide2.QtWidgets import *
from PySde2.QtGui import *

#Create the CSS class
class CSS(QWidget):
    def SetCSS(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#333333"))
        self.setPalette(palette)
        self.setAutoFillBackground(true)
        setStyleSheet('QPushButton{background-color :#0056ba9; border: none; font-size: 120px, font-weight: BOLD, color: white}')
