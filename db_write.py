#!/usr/bin/env python

import sqlite3
import datetime
import FileReader

#hentes fra metadata på sikt
tablerows = ['date', 'time', 'server', 'alarmID', 'alarmName', 'launchedBy', 'status', 'alarmGroup', 'txtMsg', 'dspMsg1', 'dspMsg2', 'alarmRef']

#Leser fil inn i line_list[]
with open("eksempel_input.txt", "r", encoding="utf-8") as file:
    # trenger sikkert ikke å definere variabelen utenfor for-løkka i python, men det skader ikke
    line_list = []
    for line in file:
        line_list = [entry.strip() for entry in line.split(",")]

#Filnavn = dato + klokkeslett
dateandtime = datetime.datetime.now()
dbname = (dateandtime.strftime("%d%m%Y_%H-%M-%S"))
conn = sqlite3.connect(dateandtime.strftime(dbname)+".db")
print("Opened database successfully")

cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS ALARM (%s)" % ", ".join(tablerows))
print("Table created successfully")

#for line in fileread execute(insert into ({}))
delim = ", "
rowstring = delim.join(tablerows)
values = ','.join(['?']) * len(tablerows)
print(rowstring)
conn.execute("INSERT INTO ALARM (%s)" % rowstring +
             "VALUES (%s)" % values, rowstring)

#','.join(['?'] * len(tablerows)

cursor.commit()
cursor = conn.execute("SELECT alarmID, alarmName, status from ALARM")



'''
sql = "select exists(SELECT * from USERS where PASSWORD = ? AND USERNAME = ?)"
args = (var1,var2)
cursor = database_connection.execute(sql, args)
'''
for row in cursor:
    print("ID = ", row[0])
    print("NAME = ", row[1])
    print("STATUS = ", row[2], "\n")

conn.close()
print("Closed database")
