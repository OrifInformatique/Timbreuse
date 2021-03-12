# Necessary imports
import sys
import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

# import log
# import logging

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
        
        
            
        # self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        
        # self.formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
        
        # self.file_handler = logging.FileHandler('traceback.log')
        # self.file_handler.setLevel(logging.ERROR)
        # self.file_handler.setFormatter(self.formatter)
        
        # self.logger.addHandler(self.file_handler)

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
        self.hidingLabelLineScroll = False
        #set Icon
        self.setIcon()

        if(self.base == True):
            print("base")
            self.baseWindow()
        
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
        self.setButtonAdmin()
     # Create Button IN
    def setButtonIn(self):
        self.buttonIn = QPushButton(self.window)
        self.buttonIn.setText("IN")
        self.buttonIn.setFixedSize(300,300)
        self.buttonIn.move(50,100)
        #add action when buttonIn is pressed
        self.buttonIn.setObjectName("buttonIN")
        self.buttonIn.clicked.connect(self.badgeApp)
        self.buttonIn.show()

    # Create button OUT
    def setButtonOut(self):
        self.buttonOut = QPushButton(self.window)
        self.buttonOut.setText("OUT")
        self.buttonOut.setFixedSize(300,300)
        self.buttonOut.move(450,100)
        #add action when buttonOut is pressed
        self.buttonOut.clicked.connect(self.badgeApp)
        self.buttonOut.show()
    
    # Create badge window
    def badgeApp(self):
        self.buttonIn.hide()
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
        global base
        global admin
        self.buttonAdmin = QPushButton(self.window)
        self.buttonAdmin.setText("Admin")
        self.buttonAdmin.move(725,0)
        self.buttonAdmin.setObjectName("AdminButton")
        #add action when buttonAdmin is pressed
        self.buttonAdmin.clicked.connect(self.adminWindow)
        self.buttonAdmin.show()
        
        '''
        Actually this button is showed in the base window for testing action

         when button clicked : it should print admin window in console OK
                                it should show up config and write button DOES'NT WORK
                                it's like we have to refresh the app's window
        '''

    '''
                                WINDOW ADMINISTRATOR
    '''
    # Window for admin
    def adminWindow(self):
        self.buttonIn.hide()
        self.buttonOut.hide()
        # disable admin Button
        self.buttonAdmin.setEnabled(False)
        self.setWriteButton()
        self.setConfigButton()
        print("In admin window")

    # define setWriteButton
    def setWriteButton(self):
        self.writeButton = QPushButton(self.window)
        self.writeButton.setText("Write")
        self.writeButton.setFixedSize(300,300)
        self.writeButton.move(50,100)
        self.writeButton.clicked.connect(self.WriteApp)
        self.writeButton.show()
    # define setConfigButton
    def setConfigButton(self):
        self.configButton = QPushButton(self.window)
        self.configButton.setText("Conf")
        self.configButton.move(450,100)
        self.configButton.setFixedSize(300,300)
        self.configButton.clicked.connect(self.configWindow)
        self.configButton.show()
    # # define config window
    # def configWindow(self):
    #     self.windowConfigWindow = ConfigWindow.Window()
    #     self.windowConfigWindow.show()
    
    # define write app
    def WriteApp(self):
        Write.Write()
    '''
                                WINDOW CONFIGURATION
    '''
    # Window to link RFID card to user or set Section
    def configWindow(self):
        self.configButton.hide()
        self.writeButton.hide()
        print("Retour dans config Window")
        # self.logger.exception('Exception Error')
        # hide label-line-scroll
        if (self.hidingLabelLineScroll == True):
            print(" dans if de config")
            self.labelName.hide()
            self.labelUID.hide()
            self.lineName.hide()
            self.lineUID.hide()
            self.scrollableListSection.hide()
            self.scroll_bar.hide()
            # self.logger.exception('Exception Error')
            # show buttons ConfigWindow
            self.setSettingsButton()
            self.attributeRFID()
            self.buttonBackConf.hide()
            self.hidingLabelLineScroll = False
        else:
            pass  
        # self.buttonBackConf.hide()
        # show the 2 buttons
        self.setSettingsButton()
        self.attributeRFID()
        

    # Show set section button  
    def setSettingsButton(self):
        self.buttonSection = QPushButton(self.window)
        self.buttonSection.setText("Section")
        self.buttonSection.move(50,100)
        self.buttonSection.setFixedSize(300,300)
        self.buttonSection.clicked.connect(self.setSection)
        self.buttonSection.show()
    
    # Show list of section available 
    def setSection(self):
        # Create scroll list
        self.scrollableListSection = QListWidget(self.window)
        
        #  Set size of scroll list
        self.scrollableListSection.setFixedSize(300,300)
        self.scrollableListSection.move(225,50)

        # Create Item
        self.itemSectionInformatique = QListWidgetItem("Section Informatique Pomy")
        self.itemSIT = QListWidgetItem("SIT Préverenges")

        # Add Item to scrollable list
        self.scrollableListSection.addItem(self.itemSectionInformatique)
        self.scrollableListSection.addItem(self.itemSIT)
        
        # scroll bar
        self.scroll_bar = QScrollBar(self.window)

        # stylesheet
        self.scroll_bar.setStyleSheet(open('./style.css').read())

        # setting vertical scroll bar
        self.scrollableListSection.setVerticalScrollBar(self.scroll_bar)

        # get scroll bar
        # self.value = self.scrollableListSection.setVerticalScrollBar()
        
        # show all
        self.scrollableListSection.show()
        self.scroll_bar.show()

        # hide sectionbutton
        self.buttonSection.hide()
        self.buttonAttributeRFID.hide()
        self.setButtonBackToConfigure()

    # show attribution RFID card button
    def attributeRFID(self):
        self.buttonAttributeRFID = QPushButton(self.window)
        self.buttonAttributeRFID.setText("Set UID")
        self.buttonAttributeRFID.setFixedSize(300,300)
        self.buttonAttributeRFID.move(450,100)
        self.buttonAttributeRFID.clicked.connect(self.setUID)
        self.buttonAttributeRFID.show()
    def setUID(self):
        # hide rfid button + section
        self.buttonAttributeRFID.hide()
        self.buttonSection.hide()
        # UID
        self.lineUID = QLineEdit(self.window)
        self.lineUID.setText("")
        self.labelUID = QLineEdit(self.window)
        self.labelUID.setText("RFID UID")
        self.labelUID.setReadOnly(True)
        
        self.lineUID.setFixedSize(300,50)
        self.labelUID.setFixedSize(100,50)
        
        self.lineUID.move(175,160)
        self.labelUID.move(75,160)

        

        # User
        self.lineName = QLineEdit(self.window)
        self.lineName.setText("")
        self.labelName = QLineEdit(self.window)
        self.labelName.setText("Name User")
        self.labelName.setReadOnly(True)
        
        self.labelName.setFixedSize(100,50)
        self.labelName.move(50,250)
        
        self.lineName.setFixedSize(300,50)
        self.lineName.move(175,250)

        # set name for label
        self.labelUID.setObjectName("labelUID")
        self.labelName.setObjectName("labelName")
        # set stylesheet for label
        self.labelUID.setStyleSheet(open('./style.css').read())
        self.labelName.setStyleSheet(open('./style.css').read())
        
        self.labelUID.show()
        print("Show label UID")
        self.lineUID.show()
        print("Show line UID")
        self.labelName.show()
        self.lineName.show()
        
        self.setButtonBackToConfigure()

    def setButtonBackToConfigure(self):
        # configure button
        self.buttonBackConf = QPushButton(self.window)
        self.buttonBackConf.setText("Back")
        self.buttonBackConf.setObjectName("BackToConf")
        self.buttonBackConf.setFixedSize(100,100)
        self.buttonBackConf.move(10,10)
        
        # create boolean to say that we have to hide some objects
        self.hidingLabelLineScroll = True
        
        self.buttonBackConf.clicked.connect(self.configWindow)
        self.buttonBackConf.show()
        
        
        

main = MainWindow()