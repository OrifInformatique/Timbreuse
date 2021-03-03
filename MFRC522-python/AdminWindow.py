import sys
# PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
#Import from other file present in the project
import Write
import ConfigWindow

#Create the main window
class MainWindow():
    def __init__(self):
        super().__init__()

        #Create the app and window
        appAdministration = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()

        # Set window title
        self.window.setWindowTitle("Administrator")

        #call init gui
        self.initGui()

        # Set the css as stylesheet for appAdministration
        appAdministration.setStyleSheet(open('./style.css').read())

        # set window in full screen
        self.window.showFullScreen()

        #sys exit
        sys.exit(appAdministration.exec_())
    
    # define initGui
    def initGui(self):

        # call icon
        self.setIcon()

        # call write button
        self.setWriteButton()

        # call configuration button
        self.setConfigButton()

    # define setIcon
    def setIcon(self):
        self.window.setWindowIcon(QtGui.QIcon('logo_orif_square_transparent.png'))
    
    # define setWriteButton
    def setWriteButton(self):
        writeButton = QPushButton(self.window)
        writeButton.setText("Write")
        writeButton.setFixedSize(300,300)
        writeButton.move(50,100)
        writeButton.clicked.connect(self.WriteApp)
    
    # define setConfigButton
    def setConfigButton(self):
        configButton = QPushButton(self.window)
        configButton.setText("Conf")
        configButton.move(450,100)
        configButton.setFixedSize(300,300)
        configButton.clicked.connect(self.configWindow)

    # define config window
    def configWindow(self):
        appLogin.destroy()
        self.windowConfigWindow = ConfigWindow.Window()
        self.windowConfigWindow.show()
    
    # define write app
    def WriteApp(self):
        Write.Write()

# Instantiate main window
AdminMain = MainWindow()