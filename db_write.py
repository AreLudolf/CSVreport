#!/usr/bin/env python

import sqlite3
import datetime
import FileReader
'''
Tester alle funksjonene i samme fil foreløpig, ikke sikkert det må deles opp heller, kanskje dette
bare blir main.

Tar outputen fra FileReader.py og skriver det inn i databasen.
(det vil si, foreløpig gjør den det ikke det, som du ser er values til tabellen hardkodet eksempel-values fra et eksempel jeg fant på interveebs.)

Oppretter sqlite3 database-fil og kobler til den.
'''
db_name = datetime.datetime.now()

print(db_name.strftime("%d%m%Y_%H-%M-%S"))
conn = sqlite3.connect(db_name.strftime("%d%m%Y_%H-%M-%S")+".db")
print("Opened database successfully")

FileReader.fileread()

conn.execute('''CREATE TABLE ALARM
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         AGE            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SALARY         REAL);''')
print("Table created successfully")

conn.execute('''INSERT INTO ALARM (ID,NAME,AGE,ADDRESS,SALARY)
VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00);
    ''')
conn.commit()
cursor = conn.execute("SELECT id, name, address, salary from ALARM")

for row in cursor:
    print("ID = ", row[0])
    print("NAME = ", row[1])
    print("ADDRESS = ", row[2])
    print("SALARY = ", row[3], "\n")

conn.close()
print("Closed database")
