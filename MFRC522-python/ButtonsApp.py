import sys
import time
# PySide2
from PySide2 import QtCore, QtGui, QtWidgets

from PySide2 import QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#Import from other file present in the project
import AdminWindow
import AdminLogin
import ProgressBar
import Read
import Write


#Create main class

class MainWindow():
    # create __init__ function
    def __init__(self):

        # Creation of the app and window
        app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()

        # Set window title
        self.window.setWindowTitle("Buttons App")

        # call the initGui function
        self.initGui()
        
        # Set the file "style.css" as stylesheet
        app.setStyleSheet(open('./style.css').read())

        # set window in full screen
        self.window.showFullScreen()

        # show window
        self.window.show()
        sys.exit(app.exec_())

    # Create the GUI function which import all buttons and add icon
    def initGui(self):

        # Set Icon
        self.setIcon()

        # Create buttons
        self.setButtonIn()
        self.setButtonOut()
        self.setButtonAdmin()

        #do not show admin login window
        self.windowAdminLogin = None

        #do not show progress bar
        self.windowProgressBar = None

    # set Icon
    def setIcon(self):
        self.window.setWindowIcon(QtGui.QIcon('logo_orif_square_transparent.png'))

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

    # Create admin button
    def setButtonAdmin(self):
        buttonAdmin = QPushButton(self.window)
        buttonAdmin.setText("Admin")
        buttonAdmin.move(725,0)
        buttonAdmin.setObjectName("AdminButton")
        #add action when buttonAdmin is pressed
        buttonAdmin.clicked.connect(self.adminApp)
    
    # Create question window for admin app
    def adminApp(self):
        adminInfo = QMessageBox.question(self.window, "Admin", "Voulez-vous vous connecter au compte administrateur ?", QMessageBox.Yes | QMessageBox.No)
        if adminInfo == QMessageBox.Yes:
#             app.destroy()
            # self.windowAdminLogin = AdminLogin.MainWindow()
            self.windowAdminLogin = AdministrationWindow.main
            # self.windowAdminLogin.showFullScreen()
        elif adminInfo == QMessageBox.No:
            pass
    # Create badge window
    def badgeApp(self):
        QMessageBox.information(self.window, "Badge", "Vous avez 10 secondes pour passer le bagde.")
        self.windowProgressBar = ProgressBar.Window()
        self.windowProgressBar.show()
# Instantiate object window
main = MainWindow()

#****************************************************************************************************************
#                                          Login to Administrator Class
#****************************************************************************************************************


#****************************************************************************************************************
#                                          Administration Class
#****************************************************************************************************************
class AdministrationWindow(QWidget):
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
main = AdministrationWindow()
