# Necessary imports
import RPi.GPIO as GPIO
import MFRC522

import sys
import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import mysql.connector as MC

# import from python files in MFRC522
import Read
import Write
import ProgressBar
# from Timbreuse import ProgressingBar

# import time to make the countdown
import time


class MainWindow():
    # Declare boolean in order to show what's necessary
    base = True
    admin = False
    config = False

    
    def DataBaseConnection(self):
        try:
            host = '127.0.0.1'
            user = 'admin'
            password = 'OrifInfo2009'
            db = "timbreuse-orif"
    

            connection = MC.connect(host=host,
                                    user=user,
                                    password=password,
                                    database=db)
            QMessageBox.information(self.window, "Connection", "Connected to DataBase")
        except MC.Error as err:
            QMessageBox.information(self.window, "Failed", "Failed to connect to database")
            
            sys.exit(app.exec_())
            
    def __init__(self):
        super().__init__()
        #Creation of the app
        app = QtWidgets.QApplication(sys.argv)

        # Create window
        self.window = QtWidgets.QMainWindow()

        # Set window title
        self.window.setWindowTitle("Timbreuse")

        
        # define all objects
            # Button
            # Database connection testing
        self.db = QPushButton(self.window)
        self.buttonAdmin = QPushButton(self.window)
        self.buttonAdmin.hide()
        
        self.buttonAttributeRFID = QPushButton(self.window)
        self.buttonAttributeRFID.hide()
        
        self.buttonBackConf = QPushButton(self.window)
        self.buttonBackConf.hide()
        
        self.buttonIn = QPushButton(self.window)
        # self.buttonIn.hide()
        
        self.buttonOut = QPushButton(self.window)
        # self.buttonOut.hide()
        
        self.buttonSection = QPushButton(self.window)
        self.buttonSection.hide()
        
        self.configButton = QPushButton(self.window)
        self.configButton.hide()
        
        self.writeButton = QPushButton(self.window)
        self.writeButton.hide()
        
            # List - scroll
        self.scrollableListSection = QListWidget(self.window)
        self.scrollableListSection.hide()
        
        self.scroll_bar = QScrollBar(self.window)
        self.scroll_bar.hide()
        
            # Item
        self.itemSectionInformatique = QListWidgetItem("Section Informatique Pomy")
        # self.itemSectionInformatique.hide()
        
        self.itemSIT = QListWidgetItem("SIT Préverenges")
        
        
            # RFID
        self.labelName = QLineEdit(self.window)
        self.labelName.hide()
        
        self.labelUID = QLineEdit(self.window)
        self.labelUID.hide()
        
        self.lineName = QLineEdit(self.window)
        self.lineName.hide()
        
        self.lineUID = QLineEdit(self.window)
        self.lineUID.hide()
        
        self.scanRFID = QPushButton(self.window)
        self.scanRFID.hide()
            # ProgressBar
        # self.progressBar = QProgressBar(self)
        # self.progressBar.hide()
            # Countdown line
        self.countDownLabel = QLineEdit(self.window)
        self.countDownLabel.hide()
        
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
        # self.scrollableListSection = None
        # self.scroll_bar = None
        # self.labelName = None
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
        self.databaseButton()
        self.countDownLabel.hide()
        
    def databaseButton(self):
       self.db.setText("db") 
       self.db.setFixedSize(120,90)
       self.db.move(90,10)
       self.db.clicked.connect(self.DataBaseConnection)
       self.db.show()
       
     # Create Button IN
    def setButtonIn(self):
        
        self.buttonIn.setText("IN")
        self.buttonIn.setFixedSize(300,300)
        self.buttonIn.move(50,100)
        #add action when buttonIn is pressed
        self.buttonIn.setObjectName("buttonIN")
        self.buttonIn.clicked.connect(self.badgeApp)
        self.buttonIn.show()

    # Create button OUT
    def setButtonOut(self):
        
        self.buttonOut.setText("OUT")
        self.buttonOut.setFixedSize(300,300)
        self.buttonOut.move(450,100)
        #add action when buttonOut is pressed
        self.buttonOut.clicked.connect(self.badgeApp)
        self.buttonOut.show()
    
    # Create badge window
    def badgeApp(self):
        
        self.buttonIn.hide()
        Read.Read()
        # self.countDown(10)
        # Read.Read()
#         QMessageBox.information(self.window, "Badge", "Vous avez 10 secondes pour passer le bagde.")
        
#         self.windowProgressBar = ProgressBar.Window()
#         self.windowProgressBar.show()
    
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
        
        # hide label-line-scroll
        if (self.hidingLabelLineScroll == False):
            print(" dans if de config")
            self.labelName.hide()
            self.labelUID.hide()
            self.lineName.hide()
            self.lineUID.hide()
            self.scrollableListSection.hide()
            self.scroll_bar.hide()
#             self.scroll_bar.hide()
            
            # show buttons AdminWindow
            self.setWriteButton()
            self.setConfigButton()
            
            # disable admin Button
            self.buttonAdmin.setEnabled(False)
        else:
            pass
            
        print("In admin window")

    # define setWriteButton
    def setWriteButton(self):
        
        self.writeButton.setText("Write")
        self.writeButton.setFixedSize(300,300)
        self.writeButton.move(50,100)
        self.writeButton.clicked.connect(self.WriteApp)
        self.writeButton.show()
    # define setConfigButton
    def setConfigButton(self):
        
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
        
        # hide label-line-scroll
        if (self.hidingLabelLineScroll == True):
            print(" dans if de config")
            self.labelName.hide()
            self.labelUID.hide()
            self.lineName.hide()
            self.lineUID.hide()
            self.scrollableListSection.hide()
            self.scroll_bar.hide()
            self.buttonBackConf.hide()
            self.scanRFID.hide()
            # show buttons ConfigWindow
            self.setSettingsButton()
            self.attributeRFID()
            
            self.hidingLabelLineScroll = False
        else:  
            # self.buttonBackConf.hide()
            # show the 2 buttons
            self.setSettingsButton()
            self.attributeRFID()
        

    # Show set section button  
    def setSettingsButton(self):
        
        self.buttonSection.setText("Section")
        self.buttonSection.move(50,100)
        self.buttonSection.setFixedSize(300,300)
        self.buttonSection.clicked.connect(self.setSection)
        self.buttonSection.show()
    '''
                    LIST ITEM
    '''
    # Show list of section available 
    def setSection(self):
        # Create scroll list
        # self.scrollableListSection = QListWidget(self.window)
        
        #  Set size of scroll list
        self.scrollableListSection.setFixedSize(300,300)
        self.scrollableListSection.move(225,50)

        # # Create Item
        # self.itemSectionInformatique = QListWidgetItem("Section Informatique Pomy")
        # self.itemSIT = QListWidgetItem("SIT Préverenges")

        # USE DATABASE TO INTEGRATES ITEM
        try:
            host = '127.0.0.1'
            user = 'admin'
            password = 'OrifInfo2009'
            db = "timbreuse-orif"
        

            connection = MC.connect(host=host,
                                    user=user,
                                    password=password,
                                    database=db)
            QMessageBox.information(self.window, "Connection", "Connected to DataBase")
            cursor = connection.cursor()

            cursor.execute("SELECT nom_section FROM t_section")
            records = cursor.fetchall()
            # print(records)
            print_records = ''
            for record in records:
                print_records = str(record[0])
                # print(print_records)
                self.scrollableListSection.addItem(print_records)
                
        except MC.Error as err:
            QMessageBox.information(self.window, "Failed", "Failed to connect to database")
            cursor.close()
            connection.close()
            sys.exit(app.exec_())

        # Add Item to scrollable list
        # self.scrollableListSection.addItem(self.itemSectionInformatique)
        # self.scrollableListSection.addItem(self.itemSIT)
        
        # scroll bar
        # self.scroll_bar = QScrollBar(self.window)

        # stylesheet
        self.scroll_bar.setStyleSheet(open('./style.css').read())

        # setting vertical scroll bar
        # self.scrollableListSection.setVerticalScrollBar(self.scroll_bar)

        # get scroll bar
        # self.value = self.scrollableListSection.setVerticalScrollBar()
        
        # show all
        self.scrollableListSection.show()
        # self.scroll_bar.show()

        #  Get selected Item
        self.scrollableListSection.itemDoubleClicked.connect(self.getSelectedSection)
        self.section = self.getSelectedSection
#         print("Print Section : " + self.section)
        
        # hide sectionbutton
        self.buttonSection.hide()
        self.buttonAttributeRFID.hide()
        self.setButtonBackToConfigure("configWindow")
        
    def getSelectedSection(self, lstItem):
        print(lstItem.text())

    '''
                    RFID CONFIGURATION
    '''
    # show attribution RFID card button
    def attributeRFID(self):
        
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
        self.scanning = False
        self.scanRFID.setFixedSize(150,50)
        self.scanRFID.setText("scan")
        self.scanRFID.move(500,160)
        self.scanRFID.setObjectName("attributeRFID")
        self.scanRFID.setStyleSheet(open('./style.css').read())
        self.scanRFID.clicked.connect(self.scanningRFID)
        self.scanRFID.show()
        
        # self.lineUID = QLineEdit(self.window)           
        self.lineUID.setText(" NO SCANNED UID")
        # self.labelUID = QLineEdit(self.window)
        self.labelUID.setText("RFID UID")
        self.labelUID.setReadOnly(True)
        self.lineUID.setReadOnly(True)
        
        self.lineUID.setFixedSize(300,50)
        self.labelUID.setFixedSize(100,50)
        
        self.lineUID.move(175,160)
        self.labelUID.move(50,160)

        

        # User
        # self.lineName = QLineEdit(self.window)
        self.lineName.setText("")
        # self.labelName = QLineEdit(self.window)
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
        
        self.setButtonBackToConfigure("configWindow")
    def scanningRFID(self):
        read = Read.Read()
        # Create an object of the class MFRC522
        MIFAREReader = MFRC522.MFRC522()
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        self.uid = read.uid()
        print("SCANUID : {}" .format(self.uid))
        
        self.scannedUID = ("{}".format(self.uid))
        self.lineUID.setText(self.scannedUID)  
        
        return self.uid
    def setButtonBackToConfigure(self, last_page:str):
        # configure button
        
        self.buttonBackConf.setText("Back")
        self.buttonBackConf.setObjectName("BackToConf")
        self.buttonBackConf.setFixedSize(75,75)
        self.buttonBackConf.move(10,10)
        
        # use style.css as styleshett
        self.buttonBackConf.setStyleSheet(open('./style.css').read())
        
        # create boolean to say that we have to hide some objects
        self.hidingLabelLineScroll = True
        
        exec(f"self.buttonBackConf.clicked.connect(self.{last_page})")
        self.buttonBackConf.show()

    # create countdown function
    def countDown(self,t):
        print("Debut def countDown t= : " +str(t))
        t=10
        print("Après réinitialisation t= : " +str(t))
        self.buttonIn.hide()
        self.buttonOut.hide()
        self.countDownLabel.setFixedSize(100,50)
        self.countDownLabel.move(350,350)
        self.countDownLabel.setText("")
        self.countDownLabel.setReadOnly(True)
        self.countDownLabel.show()
        
        counter = t
        print("Av for counter= : " +str(t))
        t = 10
        for counter in range (t):
            Read.Read()
            print("Debut for countDown t= : " +str(t))
            # print("Debut for countDown counter= : " +str(t))
            self.countDownLabel.show()
            self.countDownLabel.setText(str(t))
            QApplication.instance().processEvents()
            self.countDownLabel.show()
            time.sleep(1)
            counter = counter - 1
            # print("counter -1 = : " +str(counter))
            t = t - 1
            print("t -1 = : " +str(t))
#         counter = 0
        # print("Remise 0 counter = : " +str(counter))
#         t=0
        print("Remise 0 t = : " +str(t))
        self.baseWindow()
#         self.setButtonBackToConfigure("baseWindow")

main = MainWindow()