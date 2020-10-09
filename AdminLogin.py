import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import AdminWindow

#Create the main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Administrator Login")
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
        self.setLabelUser()
        self.setLabelPassword()
        self.setLoginButton()
        self.userLine = QLineEdit("",self)
        self.userLine.setGeometry(QRect(90, 310, 221, 21))
        self.userLine.move(150,150)
        self.passwordLine = QLineEdit(self)
        self.passwordLine.setEchoMode(QLineEdit.Password)
        self.passwordLine.setGeometry(QRect(90, 310, 221, 21))
        self.passwordLine.move(150, 300)
        self.windowAdminWindow = None
        

    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("Y:\Administratif\LogoEtModeles\logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)

    #Create the labels
    def setLabelUser(self):
        labelUser = QLabel("Nom d'utilisateur : ", self)
        labelUser.setStyleSheet('QLabel {background-color: none; color: black;}')
        labelUser.move(50,150)

    def setLabelPassword(self):
        labelPassword = QLabel("Mot de Passe : ", self)
        labelPassword.setStyleSheet('QLabel {background-color: none; color: black;}')
        labelPassword.move(50,300)

    #Create the button
    def setLoginButton(self):
        loginButton = QPushButton("Login",self)
        loginButton.setStyleSheet('QPushButton {background-color: #AE9B70; color: black;}')
        loginButton.setFixedSize(100,30)
        loginButton.move(350, 350)
        loginButton.clicked.connect(self.validation)

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
            self.windowAdminWindow.show()
        
        else :
            QMessageBox.information(self, "Erreur", "Vous n'avez pas le droit à l'accès.")
        