import sys
import time
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import AdminWindow
import AdminLogin
import ProgressBar
import Read

class MainWindow():
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        
        #Add charactersitics to window
        self.window.setWindowTitle("Design")
        self.window.setGeometry(300,300,500,400)
        self.window.setMinimumHeight(500)
        self.window.setMinimumWidth(800)
        self.window.setMaximumHeight(500)
        self.window.setMaximumWidth(800)
        # Call function initGui
        self.initGui()
        # Parameter the steelsheet
        self.style_sheet = """
        
            QMainWindow{
                background-color:#333333
            }
            QPushButton{
            
                background-color:#005BA9;
               border: none
            }
            QPushButton#cancel_btn{
                background-color:#ff9900
            }
            QPushButton#AdminButton{
            
                background-color:grey;
                margin-right: 2px;
            }
        """
        
        
        #show the window
        self.window.show()
        app.setStyleSheet(self.style_sheet)
        sys.exit(app.exec_())
        

    def initGui(self):
         #Create the buttons
        self.setButtonIn()
        self.setButtonAdmin()
        self.setButtonOut()
        self.windowAdminLogin = None
        self.windowProgressBar = None
        
    def setButtonIn(self):
        buttonIn = QPushButton("In", self.window)
        #buttonIn.setStyleSheet('QPushButton {background-color:#005BA9; color: white; font-size: 120px; font-weight: BOLD;border: none}')
        buttonIn.setFixedSize(300,300)
        buttonIn.move(50,100)
        buttonIn.clicked.connect(self.badgeApp)
        
    def setButtonOut(self):
        buttonOut = QPushButton("Out", self.window)
        #buttonOut.setStyleSheet("QPushButton {background-color:#005BA9; color: white; font-size: 120px; font-weight: BOLD; border:none}")
        buttonOut.setFixedSize(300,300)
        buttonOut.move(450,100)
        buttonOut.clicked.connect(self.badgeApp)
                
    def setButtonAdmin(self):
        buttonAdmin = QPushButton("Admin", self.window)
        #buttonAdmin.setStyleSheet('QPushButton{background-color:#005BA9; color: black;}')
        buttonAdmin.move(725,0)
        buttonAdmin.setObjectName("AdminButton")
        buttonAdmin.clicked.connect(self.adminApp)
    #Create a question window
    def adminApp(self):
        adminInfo = QMessageBox.question(self, "Admin", "Voulez-vous vous connecter au compte administrateur ?", QMessageBox.Yes | QMessageBox.No)
        if adminInfo == QMessageBox.Yes:
            self.windowAdminLogin = AdminLogin.Window()
            self.windowAdminLogin.show()
            
        elif adminInfo == QMessageBox.No:
            pass
    #Create a badge window
    def badgeApp(self):
        QMessageBox.information(self, "Badge", "Vous avez 10 secondes pour passer le badge.")
        self.windowProgressBar = ProgressBar.MainWindow()
        self.windowProgressBar.show()   
# instantiate an object to class main window        
main = MainWindow()    
