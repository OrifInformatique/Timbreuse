import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#Create the main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Administrator")
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
        self.setWriteButton()
        self.setConfigButton()
        self.windowConfigWindow = None
    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("Y:\Administratif\LogoEtModeles\logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)
        
    #Create the buttons
    def setWriteButton(self):
        writeButton = QPushButton("Write", self)
        writeButton.setStyleSheet('QPushButton {background-color: #AE9B70; color: white;}')
        writeButton.setFixedSize(300,300)
        writeButton.move(50,100)
        writeButton.clicked.connect(self.WriteApp)
        def setConfigButton(self):
        configButton = QPushButton("Configure", self)
        configButton.setStyleSheet('QPushButton {background-color: #AE9B70; color: white;}')
        configButton.setFixedSize(300,300)
        configButton.move(50,100)
        configButton.clicked.connect(self.configWindow)
    #Open Config Window
    def configWindow(self):
        self.windowConfigWindow = ConfigWindow.Window()
        self.windowConfigWindow.show()
     
    def WriteApp(self):
        Write()
    

    
