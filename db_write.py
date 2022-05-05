#!/usr/bin/env python

import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import scrolledtext as st

cursor = ''
dbname = ''
file_name = ''
labeltext = ''


def read_to_db():
    global file_name
    global dbname
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
    global cursor
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
    global cursor
    cursor.execute('''SELECT Date, Time, Alarm_Name, Alarm_Status FROM ALARM 
    WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"''')
    queryResult = cursor.fetchall()
    #skriver til fil
    outputFile = open(dbname + "_output.csv", "a")
    for row in queryResult:
        outputFile.write(', '.join(row) + '\n')
        print(', '.join(row) + '\n')
        text_area.insert(tk.INSERT, row)
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


def write_to_scrolled():
    with open(dbname + "_output.csv", "r", encoding="utf-8") as file:
        for line in file:
            text_area.insert(tk.INSERT, line)


def select_file():
    filetypes = (
        ('All files', '*.*'),
        ('text files', '*.txt'),
        ('CSV files', '*.csv')
    )
    global file_name
    file_name = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    labeltext = file_name
    label = ttk.Label(root, text=labeltext)
    label.pack()
    print(file_name)


'''
-----------------------------------GUI----------------------------------
'''
root = tk.Tk()
root.title('CSV-rapportfikser')

window_width = 900
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

open_button = ttk.Button(
    root,
    text='Open a File',
    command=select_file
)

open_button.pack(ipadx=0, ipady=0, )

submit_button = ttk.Button(
    root,
    text='Submit',
    command=read_to_db
)

submit_button.pack(ipadx=1, ipady=0)

hitit_button = ttk.Button(
    root,
    text='Hit it!',
    command=clean_to_csv
)
hitit_button.pack()

root.mainloop()
test = tk.Tk()
window_width = 900
window_height = 300
screen_width = test.winfo_screenwidth()
screen_height = test.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
test.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
test.resizable(height=False, width=False)
treeview_frame = tk.Frame(test, background="#FFF0C1", bd=1)
graph_frame = tk.Frame(test, background="#D2E2FB", bd=1, relief="sunken")
text_frame = tk.Frame(test, background="#CCE4CA", bd=1, relief="sunken")
button_frame = tk.Frame(test, background="#F5C2C1", bd=1, relief="sunken")

treeview_frame.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
graph_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
text_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)
button_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=2, pady=2)

test.grid_rowconfigure(0, weight=3)
test.grid_rowconfigure(1, weight=2)

test.grid_columnconfigure(0, weight=3)
test.grid_columnconfigure(1, weight=2)
test.grid_columnconfigure(2, weight=2)

sb = ttk.Scrollbar(text_frame)
sb.pack(side="right", fill="y")

open_button = ttk.Button(
    treeview_frame,
    text='Open a File',
    command=select_file
)

open_button.pack()

submit_button = ttk.Button(
    treeview_frame,
    text='Submit',
    command=read_to_db
)

submit_button.pack()

hitit_button = ttk.Button(
    treeview_frame,
    text='Hit it!',
    command=clean_to_csv
)
hitit_button.pack()
test.mainloop()
