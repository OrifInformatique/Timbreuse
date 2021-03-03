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
        
        # call init gui
        self.initGui()

        # set the style as mentionned in the css
        appConfiguration.setStyleSheet(open('./style.css').read())

        # show the window in full screen
        self.window.showFullScreen()

        # sys exit
        sys.exit(appConfiguration.exec_())

    # define method initGui
    def initGui(self):

        self.setIcon()

    #Insert the icon
    def setIcon(self):
        appIcon = QIcon("logo_orif_square_transparent.png")
        self.setWindowIcon(appIcon)

# Instantiate main app
main = MainWindow()