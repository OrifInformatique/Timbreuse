import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#Create the main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Administrator Configuration")
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
    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)
