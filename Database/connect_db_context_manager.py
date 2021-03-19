# File that connect the project to the BDD

import mysql.connector as MC

class DataBase():
    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'admin'
        self.password = 'OrifInfo2009'
        self.db = "timbreuse-orif"
        
        
        try:
            #  Connection to BD
            self.connection = MC.connect(host=self.host,
                                   user=self.user,
                                   password=self.password,
                                   database=self.db)
            self.cursor = self.connection.cursor()
            print("IN DB")
            
        except (Exception,
                ConnectionRefusedError,
                pymysql.err.OperationalError,
                pymysql.err.DatabaseError) as err:
            print(err)
        finally:
            if(self.connection.is_connected()):
                self.cursor.close()
                self.connection.close()