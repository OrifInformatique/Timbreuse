import sys
import time
from PySide2 import QtWidgets, QtGui, QtCore


from PySide2.QtWidgets import *
from PySide2.QtGui import *
import AdminWindow
import AdminLogin
import ProgressBar
import Read
from PySide2 import QtGui

class MainWindow():
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        
        #Add charactersitics to window
        self.window.setWindowTitle("Design")
        self.window.setGeometry(500,100,350,600)
        

        
        
        
        self.initGui()
        
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
        """
        
        
        #show the window
        self.window.show()
        app.setStyleSheet(self.style_sheet)
        sys.exit(app.exec_())
        

    def initGui(self):
        
        #Create the pseudo field
        pseudo = QtWidgets.QTextEdit(self.window)
        pseudo.setGeometry(25,270,300,40)
        pseudo.setText("Pseudo")
        
        # Create Button
        btn = QtWidgets.QPushButton(self.window)
        btn.setText("CREATE AN ACCOUNT")
        btn.setGeometry(25,340,300,40)
        
        btn = QtWidgets.QPushButton(self.window)
        btn.setText("CANCEL")
        btn.setObjectName("cancel_btn")
        btn.setGeometry(25,400,300,40)
        
# instantiate an object to class main window        
main = MainWindow()    
