# Necessary imports
import sys
import PySide2
from PySide2 import QtCore, QtWidgets, QtGui, QProgressBar
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


# import from python files in MFRC522
import Read
import Write
import ProgressBar


class MainWindow():
    # Declare boolean in order to show what's necessary
    base = True
    admin = False
    config = False

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
        sys.exit(app.exec_())

    def initGui(self):
        global base
        global admin
        global config

        #set Icon
        self.setIcon()

        if(self.base == True):
            print("base")
            # self.baseWindow()
        
        elif(self.admin == True):
            print("admin")
            # self.adminWindow()
        
        elif(self.config == True):
            print("config")
            # self.configWindow()
        
    
    # Insert Icon
    def setIcon(self):
        self.window.setWindowIcon(QtGui.QIcon('logo_orif_square_transparent.png'))
    
    '''
                                WINDOW IN/OUT
    '''
    # Window with in/out button
    def baseWindow(self):
        self.setButtonIn()
        self.setButtonOut()

     # Create Button IN
    def setButtonIn(self):
        buttonIn = QPushButton(self.window)
        buttonIn.setText("IN")
        buttonIn.setFixedSize(300,300)
        buttonIn.move(50,100)
        #add action when buttonIn is pressed
        buttonIn.clicked.connect(self.badgeApp)

    # Create button OUT
    def setButtonOut(self):
        buttonOut = QPushButton(self.window)
        buttonOut.setText("OUT")
        buttonOut.setFixedSize(300,300)
        buttonOut.move(450,100)
        #add action when buttonOut is pressed
        buttonOut.clicked.connect(self.badgeApp)
    
    # Create badge window
    def badgeApp(self):
        QMessageBox.information(self.window, "Badge", "Vous avez 10 secondes pour passer le bagde.")
        self.windowProgressBar = ProgressBar.Window()
        self.windowProgressBar.show()
    
    '''
                                WELCOME WINDOW
    '''

    def welcomeWindow(self):
        self.welcomeMessage = QtWidgets.QTextEdit("Bienvenue [nomPersonne]")

        '''
        if [nomPersonne] == "Admin":
            self.setButtonAdmin()
        else:
            ????
        '''
    # Create admin button
    def setButtonAdmin(self):
        buttonAdmin = QPushButton(self.window)
        buttonAdmin.setText("Admin")
        buttonAdmin.move(725,0)
        buttonAdmin.setObjectName("AdminButton")
        #add action when buttonAdmin is pressed
        buttonAdmin.clicked.connect(self.adminWindow)



    # '''
    #                             WINDOW ADMINISTRATOR
    # '''
    # Window for admin
    def adminWindow(self):
        pass

    '''
                                WINDOW CONFIGURATION
    '''
    # Window to link RFID card to user
    def configWindow(self):
        pass
