#!/usr/bin/env python

import sqlite3
import datetime
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

cursor = ''
dbname = ''
file_name = ''
labeltext = ''

def read_to_db():
#file_name = sys.argv[1]

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
def clean_to_csv():
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
def response_time():
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


root = tk.Tk()
root.title('CSV-rapportfikser')

window_width = 500
window_height = 300

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')



def select_file():
    filetypes = (
        ('All files', '*.*'),
        ('text files', '*.txt'),
        ('CSV files', '*.csv')
    )

    file_name = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    labeltext = file_name
    label = ttk.Label(root, text=labeltext)
    label.pack()



    open_button.pack(expand=True)


# open button
open_button = ttk.Button(
    root,
    text='Open a File',
    command=select_file
)

open_button.pack(expand=True)

submit_button = ttk.Button(
    root,
    text='Process',
    command=read_to_db()
)
submit_button.pack()

root.mainloop()
