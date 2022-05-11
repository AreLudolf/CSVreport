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
conn=''
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
	conn = sqlite3.connect(dateandtime.strftime(dbname)+".db")
	print("create_database: Opened database successfully")

	#lager metadata av første linje i fila
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
	if (len(df) == 0):
		msg.showinfo('No Rows Selected', 'CSV has no rows')
	else:

		# saves in the current directory
		with pd.ExcelWriter('{}.xlsx'.format(file_name)) as writer:
			df.to_excel(writer, 'Alarm')
			writer.save()
			msg.showinfo('Excel file ceated', 'Excel File created and database created')
			print('Excel file ceated', 'Excel File created and database created')


def clean_csv():
	global cursor
	cursor.execute(cleanup_query)
	queryResult = cursor.fetchall()
	print('Clean_csv, DB queried successfully')
	#skriver til fil
	print('Clean_csv: opening file')
	outputFile = open(dbname + "_output.csv", "a")
	for row in queryResult:
		outputFile.write(', '.join(row) + '\n')
		print(', '.join(row) + '\n')
	print("Cleaned up csv written to file: " + dbname + "_output.csv")
	
	write_to_xl(dbname + "_output.csv")
#DELETE DBNAME + OUTPUT.CSV
	outputFile.close()

	
def response_time():
	global file_name
	global dbname
	cursor.execute(response_query)
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
	write_to_xl(response_file)
#DELETE RESPONSE_FILE


'''
---------------------------GUI------------------------
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
                                    text='Det spretter opp en melding når den er ferdig å lese filene. Vær tålmodig det kan ta litt tid',
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
            create_filename()
            create_database()
            write_to_db()
            if (len(df) == 0):
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:
                write_to_xl(file_name)

            self.f2 = Frame(self.root, height=200, width=300)
            self.f2.pack(fill=BOTH, expand=1)
            self.table = Table(self.f2, dataframe=df, read_only=True)
            self.table.show()

        except FileNotFoundError as e:
            msg.showerror('Error in opening file', e)


    def display_xls_file(self):
        self.table.close()
        clean_csv()
        try:
            csv_file_name = dbname + "_output.csv"
            df = pd.read_csv(csv_file_name)
            if (len(df) == 0):
                msg.showinfo('No Rows Selected', 'CSV has no rows')
            else:

                # saves in the current directory
                write_to_xl(csv_file_name)

            self.file_name = dbname + '_output.xlsx'
            df = pd.read_excel(self.file_name)

            if (len(df) == 0):
                msg.showinfo('No records', 'No records')
            else:
                pass

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
