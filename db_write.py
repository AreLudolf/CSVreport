#!/usr/bin/env python

import sqlite3
import datetime

db_name = datetime.datetime.now()

print(db_name.strftime("%d%m%Y_%H-%M-%S"))
conn = sqlite3.connect(db_name.strftime("%d%m%Y_%H-%M-%S")+".db")

conn.execute('''CREATE TABLE COMPANY
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         AGE            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SALARY         REAL);''')
print("Table created successfully")

print("Opened database successfully")

conn.close()
print("Closed database")

