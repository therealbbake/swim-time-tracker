import pypdfium2 as pdfiumss
import sqlite3
import pandas
import datetime
from models import *
from pathlib import Path


# initializing the DB 
conn = sqlite3.connect(':memory:')
data_folder = Path("src/db")
file_to_open = data_folder / "database.csv"
df = pandas.read_csv(file_to_open)
df.to_sql('swim_times', conn, if_exists='append', index=False)

def backup_db():
    db_df = pandas.read_sql_query("SELECT * FROM swim_times", conn)
    db_df.to_csv(data_folder / "database.csv", index=False)

def retrieve_all():
    res = cur.execute("SELECT * FROM swim_times")
    swim_times = []
    for row in res.fetchall():
        # record_id, racer, seed_time, seed_date, most_recent_time, most_recent_date, event):
        entry = SwimerEventTimes(row[0], # record id
                         Swimmer(row[1], row[2], row[3]), # swimmer
                         row[4],
                         row[5],
                         row[6],
                         row[7],
                         Event(row[8], row[10], row[9]))
        swim_times.append(entry)

    return swim_times
    
cur = conn.cursor()
sql = "INSERT INTO swim_times VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

def retrieve_row_count():
    res = cur.execute("SELECT Count(*) FROM swim_times")
    return res.fetchall()[0][0]

def convert_time_to_milis(time):
    if (time == "NT" or time == None):
        return  99999.9999
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
     
    
def update_swim_times(times):
    rows_to_insert = []
    for time_entry in times: 
        if str(time_entry.event) == '200m Medley Relay': 
            print(time_entry)
            print(time_entry.event)
        res = cur.execute(f"SELECT * FROM swim_times WHERE Name = \"{time_entry.racer.name}\" AND TEAM = \"{time_entry.racer.team}\"AND Event = \"{time_entry.event.race}\" AND Gender = \"{time_entry.event.gender}\" ")
        rows = res.fetchall()
        if(len(rows) > 0): # update Row
            current_row = rows[0]
            record_id = current_row[0]
            seed_data = get_new_seed_time((current_row[4], current_row[5]), time_entry)
            cur.execute(""" UPDATE swim_times
            SET Last_Time = ?, Last_Update_Time= ?, Age = ?, Age_Group = ?, Seed_Time = ?, Seed_Update_Time = ?
            WHERE Id = ?;""",(time_entry.most_recent_time, time_entry.most_recent_date, time_entry.racer.age, time_entry.event.age_group, seed_data[0], seed_data[1], record_id))
        else: # create Brand new Swimmer Event time entry 
            rows_to_insert.append((time_entry.record_id, 
                time_entry.racer.name, 
                time_entry.racer.age, 
                time_entry.racer.team, 
                time_entry.seed_time, 
                time_entry.seed_date, 
                time_entry.most_recent_time, 
                time_entry.most_recent_date, 
                time_entry.event.race, 
                time_entry.event.gender, 
                time_entry.event.age_group))
    print(rows_to_insert)
    cur.executemany(sql, rows_to_insert)
        
def get_new_seed_time(existing_seed, time_entry):
    lowest_time = existing_seed
    for time in [(time_entry.most_recent_time, time_entry.most_recent_date), (time_entry.seed_time, time_entry.seed_date)]:
          if convert_time_to_milis(time[0]) < convert_time_to_milis(lowest_time[0]):
              lowest_time = time
              
    return lowest_time