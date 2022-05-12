#!/usr/bin/env python

import sqlite3
import datetime
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from pandastable import Table
import os

cursor = ''
conn = ''
dbname = ''
file_name = ''
labeltext = ''
dateandtime = ''
meta = ''
cleanup_query = '''SELECT Date, Time, Alarm_Name, Alarm_Status FROM ALARM
WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"'''

response_query = '''SELECT Date, Time, Alarm_Name FROM ALARM
WHERE Alarm_Status != "Canceled" OR Alarm_Group = "Empty group"'''


def create_filename():
    global file_name
    global dbname
    global dateandtime
    dateandtime = datetime.datetime.now()
    dbname = (dateandtime.strftime(file_name + "_%d%m%Y_%H-%M-%S"))
    print('create_filename: file_name created')


def create_database():
    global dateandtime
    global meta
    global conn
    conn = sqlite3.connect(dbname + ".db")
    print("create_database: Opened database successfully")

    # lager metadata av første linje i fila
    with open(file_name) as f:
        firstline = f.readlines()[0].rstrip()
        meta = [entry.strip().replace(" ", "_") for entry in firstline.split(",")]
        print('create_database: metadata created successfully')

    global cursor
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ALARM (%s)" % ", ".join(meta))
    print("create_database: Table created successfully")
    conn.commit()


def write_to_db():
    global meta
    global conn
    # Leser input-fil og legger alle entries inn i databasen
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            line_list = [entry.strip() for entry in line.split(",")]
            values = ','.join(['?'] * len(line_list))
            cursor.execute('''INSERT INTO ALARM ({}) VALUES({}) '''.format(", ".join(meta), values), line_list)

    print("write_to_db: Entries added to database")
    conn.commit()


def write_to_xl(file_name):
    df = pd.read_csv(file_name)
    print('write_to_xl() file_name: ', file_name)
    if (len(df) == 0):
        msg.showinfo('No Rows Selected', 'CSV has no rows')
    else:

        # saves in the current directory
        with pd.ExcelWriter('{}.xlsx'.format(file_name)) as writer:
            df.to_excel(writer, 'Alarm')
            writer.save()
            msg.showinfo('Excel file ceated', 'Excel File created: {}.xlsx'.format(file_name))
            print('Excel File created: {}.xlsx'.format(file_name))


def clean_csv():
    global cursor
    cursor.execute(cleanup_query)
    query_result = cursor.fetchall()
    print('Clean_csv, DB queried successfully')
    # skriver til fil
    print('Clean_csv: opening file')
    output_file = open(dbname + "_output.csv", "a")
    for row in query_result:
        output_file.write(', '.join(row) + '\n')
    print("Cleaned up csv written to file: " + dbname + "_output.csv")

    output_file.close()

def show_table(CsvToExcel, df):
    CsvToExcel.f2 = Frame(CsvToExcel.root, height=200, width=300)
    CsvToExcel.f2.pack(fill=BOTH, expand=1)
    CsvToExcel.table = Table(CsvToExcel.f2, dataframe=df, read_only=True)
    CsvToExcel.table.show()

def response_time():
    global file_name
    global dbname
    cursor.execute(response_query)
    query_result = cursor.fetchall()
    query_result.reverse()
    active_alarm = [("Date", "Time", "Alarm Name")]
    response_file = open(dbname + '_responstid.csv', 'w')
    for row in query_result:
        alarmType = row[2].split(" ")
        alarmName = row[2]
        tilstede_borte = ["Tilstede", "Borte"]
        entry_exist = False

        if alarmType[0] not in tilstede_borte:
            for i in active_alarm:
                if alarmName in i[2]:
                    entry_exist = True

            if entry_exist == False:
                active_alarm.append(row)

            if entry_exist == True:
                entry_exist = False

        if alarmType[0] == "Tilstede":
            tilstede_tid = (row[0], row[1])
            tilstede_tid_str = datetime.datetime.strptime(' '.join(tilstede_tid), "%d.%m.%Y %H:%M:%S")

            for i in active_alarm:
                roomNr = i[2].split(" ")
                if alarmType[1] in roomNr:
                    alarmTime = (i[0], i[1])
                    alarm_time_str = datetime.datetime.strptime(' '.join(alarmTime), "%d.%m.%Y %H:%M:%S")
                    tdelta = tilstede_tid_str - alarm_time_str
                    write_response = ', '.join(i + (str(tdelta),))
                    print(write_response)
                    response_file.write(write_response + '\n')
                    active_alarm.remove(i)
    response_file.close()
    print('RESPONSE_FILE: ', response_file)
    write_to_xl(response_file)


# DELETE RESPONSE_FILE


'''
---------------------------GUI------------------------
'''


class CsvToExcel:

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
                                    text='Det spretter opp en melding når den er ferdig å lese filene. '
                                         'Vær tålmodig det kan ta litt tid',
                                    fg='Red')

        # Buttons
        self.convert_button = Button(self.f,
                                     text='Åpne',
                                     command=self.open_file)
        self.display_button = Button(self.f,
                                     text='Cleanup',
                                     command=self.clean_up_file)
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



    def open_file(self):
        try:
            self.file_name = filedialog.askopenfilename(initialdir='/Desktop',
                                                        title='Select a CSV file',
                                                        filetypes=(('CSV file', '*.csv'),
                                                                   ('Text file', '*.txt'),
                                                                   ('All files', '*.*')))

            df = pd.read_csv(self.file_name)
            global file_name
            file_name = self.file_name
            create_filename()
            create_database()
            write_to_db()
            if len(df) == 0:
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:
                print('open_file(): File opened, show table')
            show_table(self, df)

        except FileNotFoundError as e:
            msg.showerror('Error in opening file', e)

    def clean_up_file(self):
        self.table.close()
        clean_csv()
        print('clean_up_file(): clean_csv() kjørt')
        try:
            csv_file_name = dbname + "_output.csv"
            df = pd.read_csv(csv_file_name)
            if len(df) == 0:
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:

                # saves in the current directory
                write_to_xl(csv_file_name)
            os.rename('{}.xlsx'.format(csv_file_name), '{}_output.xlsx'.format(dbname))
            print('Renamed file: {}.xlsx'.format(csv_file_name), 'to: {}_output.xlsx'.format(dbname))
            self.file_name = dbname + '_output.xlsx'
            df = pd.read_excel(self.file_name)

            if len(df) == 0:
                msg.showinfo('No records', 'No records')
            else:
                pass

            show_table(self, df)

        except FileNotFoundError as e:
            print(e)
            msg.showerror('Error in opening file', e)

# Driver Code
root = Tk()
root.title('CSV converter')

obj = CsvToExcel(root)
root.geometry('800x600')
root.mainloop()
