#!/usr/bin/env python

import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from pandastable import Table

cursor = ''
dbname = ''
file_name = ''
labeltext = ''
print('Tester sublime merge')
#DETTE ER EN TESTMELDING TIL GIT
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
    clean_to_csv()

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
    print("Cleaned up csv written to file: " + dbname + "_output.csv")
    df = pd.read_csv(file_name)
    if (len(df) == 0):
        msg.showinfo('No Rows Selected', 'CSV has no rows')
    else:

        # saves in the current directory
        with pd.ExcelWriter('{}.xlsx'.format(dbname)) as writer:
            df.to_excel(writer, 'Alarm')
            writer.save()
            msg.showinfo('Excel file ceated', 'Excel File created and database created')
    outputFile.close()


#regne ut responstid:
def response_time():
    global file_name
    global dbname
    cursor.execute('''SELECT Date, Time, Alarm_Name FROM ALARM
    WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"''')
    responsQuery = cursor.fetchall()
    responsQuery.reverse()
    active_alarm = [("Date", "Time", "Alarm Name")]
    response_file = open(dbname + '_responstid.csv', 'w')
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
                    write_response = ', '.join(i + (str(tdelta),))
                    print(write_response)
                    response_file.write(write_response + '\n')
                    active_alarm.remove(i)

    response_file.close()


'''
-----------------------------------GUI----------------------------------
'''
class csv_to_excel:

    def __init__(self, root):

        self.root = root
        self.file_name = ''
        self.f = Frame(self.root,
                       height=200,
                       width=300)

        # Place the frame on root window
        self.f.pack()

        # Creating label widgets
        self.message_label = Label(self.f,
                                   text='CSV cleanup',
                                   fg='Black')
        self.message_label2 = Label(self.f,
                                    text='Det spretter opp en melding når den er ferdig å lese filene.',
                                    fg='Red')

        # Buttons
        self.convert_button = Button(self.f,
                                     text='Åpne',
                                     command=self.convert_csv_to_xls)
        self.display_button = Button(self.f,
                                     text='Cleanup',
                                     command=self.display_xls_file)
        self.exit_button = Button(self.f,
                                  text='Responstid',
                                  command=response_time)

        # Placing the widgets using grid manager
        self.message_label.grid(row=1, column=1)
        self.message_label2.grid(row=2, column=1)
        self.convert_button.grid(row=3, column=0,
                                 padx=0, pady=15)
        self.display_button.grid(row=3, column=1,
                                 padx=10, pady=15)
        self.exit_button.grid(row=3, column=2,
                              padx=10, pady=15)

    def convert_csv_to_xls(self):
        try:
            self.file_name = filedialog.askopenfilename(initialdir='/Desktop',
                                                        title='Select a CSV file',
                                                        filetypes=(('CSV file', '*.csv'),
                                                                   ('Text file', '*.txt'),
                                                                   ('All files', '*.*')))

            df = pd.read_csv(self.file_name)
            global file_name
            file_name = self.file_name
            read_to_db()
            # Next - Pandas DF to Excel file on disk
            if (len(df) == 0):
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:

                # saves in the current directory
                with pd.ExcelWriter('{}.xlsx'.format(file_name)) as writer:
                    df.to_excel(writer, 'Alarm')
                    writer.save()
                    msg.showinfo('Excel file ceated', 'Excel File created and database created')

            # Now display the DF in 'Table' object
            # under'pandastable' module
            self.f2 = Frame(self.root, height=200, width=300)
            self.f2.pack(fill=BOTH, expand=1)
            self.table = Table(self.f2, dataframe=df, read_only=True)
            self.table.show()

        except FileNotFoundError as e:
            msg.showerror('Error in opening file', e)

    def display_xls_file(self):
        self.table.close()
        try:
            csv_file_name = dbname + "_output.csv"
            df = pd.read_csv(csv_file_name)
            if (len(df) == 0):
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:

                # saves in the current directory
                with pd.ExcelWriter('{}_output.xlsx'.format(dbname)) as writer:
                    df.to_excel(writer, 'Alarm')
                    writer.save()
                    msg.showinfo('Rensket', 'Rensket excel-fil mekket: {}_output.xlsx'.format(dbname))

            self.file_name = dbname + '_output.xlsx'
            df = pd.read_excel(self.file_name)

            if (len(df) == 0):
                msg.showinfo('No records', 'No records')
            else:
                pass

            # Now display the DF in 'Table' object
            # under'pandastable' module

            self.f2 = Frame(self.root, height=200, width=300)
            self.f2.pack(fill=BOTH, expand=1)
            self.table = Table(self.f2, dataframe=df, read_only=True)
            self.table.show()

        except FileNotFoundError as e:
            print(e)
            msg.showerror('Error in opening file', e)


# Driver Code
root = Tk()
root.title('CSV converter')

obj = csv_to_excel(root)
root.geometry('800x600')
root.mainloop()
