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
# cursor.execute("DESCRIBE t_timbreuse")
# cursor.execute("INSERT INTO t_timbreuse (nom_timbreuse) VALUES ('SIBEC')")
# cursor.execute("INSERT INTO t_assures (nom_assures,prenom_assures,username_assures) VALUES (%s,%s,%s)", ("HERZIG","Grégoire","hegr"))
# connection.commit()

# for x in cursor:
    # print(x)
# cursor.execute("SELECT * FROM t_assures")

# for x in cursor:
#     print(x)
    
if(connection.is_connected()):
    print("IN DB")
    # print(connection)
    # print(cursor.execute("SELECT * FROM t_timbreuse"))    
    cursor.close()
    connection.close()
        

