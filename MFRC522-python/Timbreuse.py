# Necessary imports
import sys
# import PySide2 as p2
# from p2 import QtCore, QtWidgets, QtGui
# from p2.QtWidgets import *
# from p2.QtGui import *
# from p2.QtCore import *

class MainWindow():
    # Declare boolean in order to show what's necessary
    def boolean(self):
        base = True
        admin = False
        config = False
        return base, admin, config
    def __init__(self):
        super().__init__()

        #Creation of the app
        app = QtWidgets.QApplication(sys.argv)

        # Create window
        self.window = QtWidgets.QMainWindow()

        # Set window title
        self.window.setWindowTitle("Timbreuse")

        # call the init gui
        self.initGui()

        # set file css as stylesheet
        app.setStyleSheet(open('./style.css').read())

        # Set window in full screen
        self.window.showFullScreen()

    def initGui(self):
        

        #set Icon
        self.setIcon()

        if(base == True):
            print("base")
            # self.baseWindow()
        
        elif(admin == True):
            print("admin")
            # self.adminWindow()
        
        elif(config == True):
            print("config")
            # self.configWindow()
        
    
    # Insert Icon
    def setIcon(self):
        self.window.setIcon(QtGui.QIcon('logo_orif_square_transparent.png'))
    
    # Window with in/out button
    def baseWindow(self):
        pass
    # Window for admin
    def AdminWindow(self):
        pass
    # Window to link RFID card to user
    def ConfigWindow(self):
        pass