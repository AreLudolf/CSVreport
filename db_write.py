#!/usr/bin/env python

import sqlite3
import datetime
#import FileReader

#hentes fra metadata på sikt
tablerows = ['date', 'time', 'server', 'alarmID', 'alarmName', 'launchedBy', 'status', 'alarmGroup', 'txtMsg', 'dspMsg1', 'dspMsg2', 'alarmRef']

#Filnavn = dato + klokkeslett
dateandtime = datetime.datetime.now()
dbname = (dateandtime.strftime("%d%m%Y_%H-%M-%S"))
conn = sqlite3.connect(dateandtime.strftime(dbname)+".db")
print("Opened database successfully")

#Oppretter tabell
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS ALARM (%s)" % ", ".join(tablerows))
print("Table created successfully")


#Leser input-fil og legger alle entries inn i databasen
with open("eksempel_input.txt", "r", encoding="utf-8") as file:
    line_list = []
    for line in file:
        line_list = [entry.strip() for entry in line.split(",")]
        cursor.execute('''INSERT INTO ALARM (alarmRef) VALUES(?) ''', [line_list[11]])
        for i in range(len(line_list) - 1):
            cursor.execute('''UPDATE ALARM SET (%s) = (?) WHERE alarmRef == ("%s");''' % (tablerows[i], line_list[11]), [line_list[i]])
print("Entries added to database")

conn.commit()

#hente ut fil uten canceled status med mindre det er tilstede og borte
cursor.execute('''SELECT date, time, alarmName, status FROM ALARM WHERE status != "Canceled" OR alarmGroup = "Empty group"''')
data = cursor.fetchall()
print(data)
file1 = open("output_" + dbname + ".csv", "a")
for row in data:
    file1.write(', '.join(row) + '\n')


file1.close()

cursor.close()
print("Closed database")
