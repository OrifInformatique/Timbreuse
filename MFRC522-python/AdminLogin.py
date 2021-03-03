import sys
import time
# PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
#Import from other file present in the project
import AdminWindow

#Create the main window
class MainWindow():
    def __init__(self):
        super().__init__()

        #Creation of the window and app
        appLogin = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        
        #Set window title
        self.window.setWindowTitle("Administrator Login")

        # call the initGui
        self.initGui()

        #Set file css as stylesheet
        appLogin.setStyleSheet(open('./style.css').read())

        # set window in full screeen
        self.window.showFullScreen()

        #show window
        self.window.show()
#         sys.exit(appLogin.exec_())
    # creation of the gui init
    def initGui(self):
        # SetIcon
        self.setIcon()

        #Create Label, line, button
#         self.setLabelUser()
#         self.setUserText()
        self.setUserLine()
        self.setLabelPassword()
#         self.setPasswordText()
        self.setPasswordLine()
        self.setLoginButton()

    #Insert the icon
    def setIcon(self):
        self.window.setWindowIcon(QtGui.QIcon('logo_orif_square_transparent.png'))

    #Create the labels
    def setLabelUser(self):
        labelUser = QLabel("Nom d'utilisateur : ", self.window)
#         labelUser.setStyleSheet('QLabel {background-color: none; color: black;}')
        labelUser.move(50,150)

    def setLabelPassword(self):
        labelPassword = QLabel("Mot de Passe : ", self.window)
#         labelPassword.setStyleSheet('QLabel {background-color: none; color: black;}')
        labelPassword.move(50,300)

    #Create the button
    def setLoginButton(self):
        loginButton = QPushButton("Login",self.window)
#         loginButton.setStyleSheet('QPushButton {background-color: #AE9B70; color: black;}')
        loginButton.setFixedSize(100,30)
        loginButton.move(350, 350)
#         loginButton.clicked.connect(self.validate)
        loginButton.clicked.connect(self.validation)

#******************************************************************************************************
#                                       TEST OF PYQT.QTextEdit
#******************************************************************************************************

    # # Create user text edit
    # def setUserText(self):
    #     self.pseudo = QtWidgets.QTextEdit(self.window)
    #     self.pseudo.setGeometry(60,150,250,40)
    #     pseudo = self.pseudo.setText()
    #     return pseudo == "Admin"
    
    # # Create password text edit
    # def setPasswordText(self):
    #     self.password = QtWidgets.QTextEdit(self.window)
    #     self.password.setGeometry(60,300,250,40)
    #     password = self.password.setText()
    #     return password == "Password"

    # # VALIDATE
    # def validate(self):
    #     if(self.pseudo() and self.password()):
    #         self.windowAdminWindow == AdminWindow.MainWindow()
    #         self.windowAdminWindow.showFullScreen()
    #     else:
    #         QMessageBox.information(self.window, "Erreur", "Vous n'avez pas le droit à l'accès.")

#******************************************************************************************************
#                                       END TEST OF PYQT.QTextEdit
#******************************************************************************************************    
    #Create the text's line

    def setUserLine(self):
     user = self.userLine.text()
     return user == "Admin"
 
    def setPasswordLine(self):
         password = self.passwordLine.text()
         return password == "Password"
 
     #Validate the login
    def validation(self):
         if (self.setUserLine() and self.setPasswordLine()) : 
             self.windowAdminWindow = AdminWindow.Window()
             self.windowAdminWindow.showFullScreen()
         
         else :
             QMessageBox.information(self.window, "Erreur", "Vous n'avez pas le droit à l'accès.")

main = MainWindow()
