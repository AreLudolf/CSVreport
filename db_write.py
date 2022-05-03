#!/usr/bin/env python

import sqlite3
import datetime
import sys

#file_name = sys.argv[1]
file_name = "ex_meta.csv"

# Filnavn = dato + klokkeslett
dateandtime = datetime.datetime.now()
dbname = (dateandtime.strftime(file_name + "_%d%m%Y_%H-%M-%S"))
conn = sqlite3.connect(dateandtime.strftime(dbname)+".db")
print("Opened database successfully")

#lager metadata av første linje i fila
with open(file_name) as f:
    firstline = f.readlines()[0].rstrip()
    meta = [entry.strip().replace(" ", "_") for entry in firstline.split(",")]

# Oppretter tabell
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS ALARM (%s)" % ", ".join(meta))
print("Table created successfully")


# Leser input-fil og legger alle entries inn i databasen
with open(file_name, "r", encoding="utf-8") as file:
    for line in file:
        line_list = [entry.strip() for entry in line.split(",")]
        values = ','.join(['?'] * len(line_list))
        cursor.execute('''INSERT INTO ALARM ({}) VALUES({}) '''.format(", ".join(meta), values), line_list)


print("Entries added to database")

conn.commit()

# hente ut fil uten canceled status med mindre det er tilstede og borte
cursor.execute('''SELECT Date, Time, Alarm_Name, Alarm_Status FROM ALARM 
WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"''')
queryResult = cursor.fetchall()
#skriver til fil
outputFile = open(dbname + "_output.csv", "a")
for row in queryResult:
    outputFile.write(', '.join(row) + '\n')
print("Cleaned up csv written to file: " + dbname + "_output.csv")
outputFile.close()


#regne ut responstid:
cursor.execute('''SELECT Date, Time, Alarm_Name FROM ALARM
WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"''')
responsQuery = cursor.fetchall()
responsQuery.reverse()
active_alarm = [("Date", "Time", "Alarm Name")]
for row in responsQuery:
    alarmType = row[2].split(" ")
    alarmName = row[2]
    tilstedeBorte = ["Tilstede", "Borte"]
    entryExist = False
    if alarmType[0] not in tilstedeBorte:
        for i in active_alarm:
            if alarmName in i[2]:
                entryExist = True

        if entryExist == False:
            active_alarm.append(row)

        if entryExist == True:
            entryExist = False


    if alarmType[0] == "Tilstede":
        tilstedeTid = (row[0], row[1])
        tilstedeTidStr = datetime.datetime.strptime(' '.join(tilstedeTid), "%d.%m.%Y %H:%M:%S")

        for i in active_alarm:
            roomNr = i[2].split(" ")
            if alarmType[1] in roomNr:
                alarmTime = (i[0], i[1])
                alarmTimeStr = datetime.datetime.strptime(' '.join(alarmTime), "%d.%m.%Y %H:%M:%S")
                tdelta = tilstedeTidStr - alarmTimeStr
                active_alarm_type = i[2]
                print("Responstid på alarm", active_alarm_type, ": ", tdelta)
                active_alarm.remove(i)



print(active_alarm)

cursor.close()
print("Closed database")
