import sys
import time
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import AdminWindow
import AdminLogin
import ProgressBar
import Read
from PySide2 import QtGui



#Create the main window
class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("Buttons App")
        self.setGeometry(300,300,500,400)
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)
        self.setMaximumHeight(500)
        self.setMaximumWidth(800)
        #palette = self.palette()
        #palette.setColor(QPalette.Window, QColor("#333333"))
        #self.setPalette(palette)
        #self.setAutoFillBackground(True)
        # Call all necessary function present in this ButtonsApp.py
        self.setIcon()
        self.setButtonIn()
        self.setButtonAdmin()
        self.setButtonOut()
        self.windowAdminLogin = None
        self.windowProgressBar = None
        
    #Insert the icon
    def setIcon(self):
        #appIcon = QIcon("/home/pi/Desktop/SPI-Py/MFRC522-python/logo_orif_square_transparent.png")
        #self.setWindowIcon(appIcon)
        self.setWindowIcon(QtGui.QIcon('logo_orif_square_transparent.png'))
    #Create the buttons
    def setButtonIn(self):
        buttonIn = QPushButton("In", self)
        #buttonIn.setStyleSheet('QPushButton {background-color:#005BA9; color: white; font-size: 120px; font-weight: BOLD;border: none}')
        buttonIn.setFixedSize(300,300)
        buttonIn.move(50,100)
        buttonIn.clicked.connect(self.badgeApp)
        
    def setButtonOut(self):
        buttonOut = QPushButton("Out", self)
        #buttonOut.setStyleSheet("QPushButton {background-color:#005BA9; color: white; font-size: 120px; font-weight: BOLD; border:none}")
        buttonOut.setFixedSize(300,300)
        buttonOut.move(450,100)
        buttonOut.clicked.connect(self.badgeApp)
                
    def setButtonAdmin(self):
        buttonAdmin = QPushButton("Admin", self)
        #buttonAdmin.setStyleSheet('QPushButton{background-color:#005BA9; color: black;}')
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
    #Create a badge window
    def badgeApp(self):
        QMessageBox.information(self, "Badge", "Vous avez 10 secondes pour passer le badge.")
        self.windowProgressBar = ProgressBar.Window()
        self.windowProgressBar.show()
        
        
        
if __name__=="__main__":
    #Create Qt App
    mainApp = QApplication(sys.argv)
    window = Window()
    #Show the window
    window.show()
    #run the main loop
    mainApp.exec_()


