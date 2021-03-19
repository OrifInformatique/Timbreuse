# File that connect the project to the BDD

import mysql.connector as MC


host = '127.0.0.1'
user = 'admin'
password = 'OrifInfo2009'
db = "timbreuse-orif"
    

connection = MC.connect(host=host,
                       user=user,
                       password=password,
                       database=db)
cursor = connection.cursor()


print(cursor.execute("SELECT * FROM t_timbreuse"))

if(connection.is_connected()):
    print("IN DB")
    print(connection)
    cursor.close()
    connection.close()
        

