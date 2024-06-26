# print("hello world!")
# # importing required modules 
# from pypdf import PdfReader 

# # creating a pdf reader object 
# reader = PdfReader('2023_prelim_results_day_1.pdf') 

# # printing number of pages in pdf file 
# print(len(reader.pages)) 

# # getting a specific page from the pdf file 
# page = reader.pages[3] 

# # extracting text from ppython -m pip install -U pypdfium2age 
# text = page.extract_text() 
# print(text) 

import pypdfium2 as pdfium
import csv
import sqlite3
import pandas
import uuid 
import datetime
from models import *


# initializing the DB 
conn = sqlite3.connect(':memory:')
df = pandas.read_csv('db\\times.csv')
df.to_sql('swim_times', conn, if_exists='append', index=False)

def backup_db():
    db_df = pandas.read_sql_query("SELECT * FROM swim_times", conn)
    db_df.to_csv('db\\updated_database.csv', index=False)

    
cur = conn.cursor()
sql = "INSERT INTO swim_times VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

# val = (str(uuid.uuid1()), "B Baker", "12", "BTST", "1:12.2", "01/04/2003", "1:32.2", "01/04/2013", "50 Free", "Girls", "12-13")
# data = [val]
# cur.executemany(sql, data)




basic = "1:11.11"
basic2 = "11:11.11"
bad = "111.11"
bad2 = "1111.11"

time_arr = [basic, bad, basic2, bad2]


    


def format_time(time):
    if(":" in time): 
        d = time.split(":")
        int_min = int(d[0])
        sec =d[1]
    else:
        print(time)
        d = time.split(".")
        mil = d[1]
        v = d[0]
        sec = "{}.{}".format(v[-2:],mil)
        min = v[:-2]
        int_min = 0 if min == "" else int(min)
    return"{}:{}".format(int_min,sec)

def convert_time_to_miliseconds(time):
    if(":" in time): 
        d = time.split(":")
        int_min = int(d[0])
        sec = float(d[1])
    else:
        d = time.split(".")
        mil = d[1]
        v = d[0]
        sec = float("{}.{}".format(v[-2:],mil))
        min = v[:-2]
        int_min = 0 if min == "" else int(min)
    return (sec + (int_min * 60 )) 
     

# for x in time_arr:
#     print(format_time(x))
#     print(convert_time_to_miliseconds(x))   
        
def load_race_data(pdf):
    
    current_date = datetime.datetime.now()
    isRelay = False
    rows_to_insert = []
    updateCount = 0
    
    for page in pdfium.PdfDocument(pdf): 
        textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None, errors='ignore')
        page_lines = textpage.split('\n')
        page_lines.pop(0)
        page_lines.pop(0)
        page_lines.pop(0)
        page_lines.pop(0)
        for x in page_lines:
            x.replace('\\n', '')
            if(x.startswith('#')):
                # print('loading swim times for')
                # print(x)
                isRelay = 'Relay' in x
                race_info = x.split(' ')
                race_info.pop(0) #remove race info 
                gender = race_info.pop()
                age_group = race_info.pop(0)
                race = ' '.join(str(r) for r in race_info).strip()
                current_event = Event(race, age_group, gender)
                print(race)
            elif('Preliminaries' in x or 'Final' in x or 'Team' in x or 'Swim-Off' in x or 'Swim-off' in x):
                continue
            elif(not isRelay):
                print(x)
                swimmer_time = x.split(' ')
                swimmer_time.pop(0)
                time = swimmer_time.pop().strip()
                if 'DQ' in time or 'DNF' in time or 'DFS' in time: 
                    continue
                team = swimmer_time.pop()
                age = swimmer_time.pop()
                name = ' '.join(swimmer_time)
                # print("SELECT * FROM swim_times WHERE Name = \"{}\" AND Event = \"{}\"".format(name, current_event))
                res = cur.execute("SELECT * FROM swim_times WHERE Name = \"{}\" AND Event = \"{}\"".format(name, current_event))
                rows = res.fetchall()
                if(len(rows) > 0):
                    current_row = rows[0]
                    record_id = current_row[0]
                    current_seed_time = current_row[4]
                    seed_time = format_time(time) if convert_time_to_miliseconds(time) < convert_time_to_miliseconds(current_seed_time) else current_seed_time
                    seed_update = current_date if convert_time_to_miliseconds(time) < convert_time_to_miliseconds(current_seed_time) else current_row[5]
                    cur.execute(""" UPDATE swim_times
                    SET Last_Time = ?, Last_Update_Time= ?, Age = ?, Age_Group = ?, Seed_Time = ?, Seed_Update_Time = ?
                    WHERE Id = ?;""",(format_time(time), current_date, age, current_event.age_group, seed_time, seed_update, record_id))
                    updateCount = updateCount+1
                else: # create Brand new Swimmer Event time entry 
                    swimEntry = SwimerEventTimes(str(uuid.uuid1()), 
                                                 Swimmer(name, age, team), # swimmer info
                                                 format_time(time), # seed time (best)
                                                 current_date,  # date seed time recorded
                                                 format_time(time), # most recent swim time
                                                 current_date, # last time swam event
                                                 current_event) # current Event
                    rows_to_insert.append(swimEntry)
   
   
    print("updated {} times".format(updateCount))
    print("inserted {} times".format(len(rows_to_insert)))
    return rows_to_insert
    # cur.executemany(sql, rows_to_insert)
    
    
def update_swim_times(times): 
    times[0]
    for s in times: 
        print(s)
        
    
    
# def load_race_data(pdf):
#     current_date = datetime.datetime.now()
#     current_gender = ''
#     current_event = ''
#     current_age_group = ''
#     isRelay = False
#     rows_to_insert = []
#     updateCount = 0
#     for page in pdf: 
#         textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None, errors='ignore')
#         page_lines = textpage.split('\n')
#         page_lines.pop(0)
#         page_lines.pop(0)
#         page_lines.pop(0)
#         page_lines.pop(0)
#         for x in page_lines:
#             x.replace('\\n', '')
#             if(x.startswith('#')):
#                 # print('loading swim times for')
#                 # print(x)
#                 race_info = x.split(' ')
#                 race_info.pop(0) #remove race info 
#                 current_gender = race_info.pop(0)
#                 current_age_group = race_info.pop(0)
#                 current_event = ' '.join(str(r) for r in race_info).strip()
#                 isRelay = 'Relay' in current_event
#             elif('Preliminaries' in x or 'Final' in x or 'Team' in x or 'Swim-Off' in x or 'Swim-off' in x):
#                 continue
#             elif(not isRelay):
#                 swimmer_time = x.split(' ')
#                 swimmer_time.pop(0)
#                 time = swimmer_time.pop().strip()
#                 if 'DQ' in time or 'DNF' in time or 'DFS' in time: 
#                     continue
#                 team = swimmer_time.pop()
#                 age = swimmer_time.pop()
#                 name = ' '.join(swimmer_time)
#                 # print("SELECT * FROM swim_times WHERE Name = \"{}\" AND Event = \"{}\"".format(name, current_event))
#                 res = cur.execute("SELECT * FROM swim_times WHERE Name = \"{}\" AND Event = \"{}\"".format(name, current_event))
#                 rows = res.fetchall()
#                 if(len(rows) > 0):
#                     current_row = rows[0]
#                     record_id = current_row[0]
#                     current_seed_time = current_row[4]
#                     seed_time = format_time(time) if convert_time_to_miliseconds(time) < convert_time_to_miliseconds(current_seed_time) else current_seed_time
#                     seed_update = current_date if convert_time_to_miliseconds(time) < convert_time_to_miliseconds(current_seed_time) else current_row[5]
#                     cur.execute(""" UPDATE swim_times
#                     SET Last_Time = ?, Last_Update_Time= ?, Age = ?, Age_Group = ?, Seed_Time = ?, Seed_Update_Time = ?
#                     WHERE Id = ?;""",(format_time(time), current_date, age, current_age_group, seed_time, seed_update, record_id))
#                     updateCount = updateCount+1
#                 else:
#                     rows_to_insert.append((str(uuid.uuid1()), name, age, team, format_time(time), current_date, format_time(time), current_date, current_event, current_gender, current_age_group))
   
   
#     print("updated {} times".format(updateCount))
#     print("inserted {} times".format(len(rows_to_insert)))
#     cur.executemany(sql, rows_to_insert)




# print(textpage)
# print(len(textpage.split('\n')))
# print(textpage.split('\n')[1])

# remove first 4 lines

# load_race_data(pdfium.PdfDocument('./2023_prelim_results_day_1.pdf'))
# load_race_data(pdfium.PdfDocument('./2023_prelim_results_day_2.pdf'))
    
# db_df = pandas.read_sql_query("SELECT * FROM swim_times", conn)
# db_df.to_csv('database.csv', index=False)

# print("initial DB Generated")

# load_race_data(pdfium.PdfDocument('./2023_results_-_championship_finals.pdf'))