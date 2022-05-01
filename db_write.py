#!/usr/bin/env python

import sqlite3
import datetime
import sys

file_name = sys.argv[1]
#file_name = "ex_meta.csv"

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


cursor.close()
print("Closed database")
