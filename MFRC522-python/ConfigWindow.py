import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#Create the main window
class MainWindow():
    def __init__(self):
        super().__init__()
 
        # Create window and app
        appConfiguration = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        
        # SET TITLE
        self.window.setWindowTitle("Administrator Configuration")
        # self.setGeometry(300,300,500,400)
        # self.setMinimumHeight(480)
        # self.setMinimumWidth(800)
        # self.setMaximumHeight(480)
        # self.setMaximumWidth(800)
        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor("#DBCEB1"))
        # self.setPalette(palette)
        # self.setAutoFillBackground(True)

        self.initGui()

        appConfiguration.setStyleSheet(open('./style.css').read())

        self.window.showFullScreen()

        sys.exit(appConfiguration.exec_())

    def initGui(self):

        self.setIcon()

    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)

main = MainWindow()