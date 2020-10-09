import sys
import time
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import AdminWindow
import AdminLogin
#Create the main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Buttons App")
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
        self.setButtonIn()
        self.setButtonAdmin()
        self.setButtonOut()
        self.windowAdminLogin = None
        
    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("Y:\Administratif\LogoEtModeles\logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)

    #Create the buttons
    def setButtonIn(self):
        buttonIn = QPushButton("In", self)
        buttonIn.setStyleSheet('QPushButton {background-color: #AE9B70; color: white;}')
        buttonIn.setFixedSize(300,300)
        buttonIn.move(50,100)
        buttonIn.clicked.connect(self.badgeApp)

    def setButtonOut(self):
        buttonOut = QPushButton("Out", self)
        buttonOut.setStyleSheet('QPushButton {background-color: #005BA9; color: white;}')
        buttonOut.setFixedSize(300,300)
        buttonOut.move(400,100)
        buttonOut.clicked.connect(self.badgeApp)

    def setButtonAdmin(self):
        buttonAdmin = QPushButton("Admin", self)
        buttonAdmin.setStyleSheet('QPushButton {background-color: #005BA9; color: white;}')
        buttonAdmin.move(725,0)
        buttonAdmin.clicked.connect(self.adminApp)

    #Create a question window
    def adminApp(self):
        adminInfo = QMessageBox.question(self, "Admin", "Voulez-vous vous connecter au compte administrateur ?", QMessageBox.Yes | QMessageBox.No)
        if adminInfo == QMessageBox.Yes:
            self.windowAdminLogin = AdminLogin.Window()
            self.windowAdminLogin.show()
            
        elif adminInfo == QMessageBox.No:
            pass

    #Create a badge warning window
    def badgeApp(self):
        QMessageBox.information(self, "Badge", "Vous avez 10 secondes pour passer le badge.")
    

#Create Qt App
mainApp = QApplication(sys.argv)
window = Window()

#Show the window
window.show()

#run the main loop
mainApp.exec_()


