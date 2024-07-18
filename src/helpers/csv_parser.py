import pandas 
import csv
from models import *
import uuid

from datetime import datetime

def build_race_name(race_info):
    return str(race_info).replace(' Meter', 'm').replace('Individual Medley', 'IM').replace('Freestyle', 'Free').replace('Breaststroke', 'Breast').replace('Backstroke', 'Back').replace('Butterfly', 'Fly').strip()

def get_gender(gender):
    val = gender.lower()
    if val ==  "women" or "girl" in val:
        return "Girls"
    elif val ==  "men" or "boy" in val:
        return "Boys"
    else:
        return gender

swim_entries = [["Id","Name","Age","Team","Seed_Time","Seed_Update_Time","Last_Time","Last_Update_Time","Event","Gender","Age_Group"]]
    
def format_time(time):
    time = time.strip()
    print(time)
    if(time == "NT" or time ==  None):
        return time
    elif(":" in time): 
        d = time.split(":")
        int_min = int(d[0])
        sec =d[1]
    else:
        d = time.split(".")
        mil = d[1] if len(d) > 1 else "00"
        v = d[0]
        sec = "{}.{}".format(v[-2:],mil)
        min = v[:-2]
        int_min = 0 if min == "" else int(min)
    return"{}:{}".format(int_min,sec)   


# PL,LastName,FirstName,AGE,Team,Seed,Official,Gender,AGE_GROUP,EVENT
# 2, Rossbach, Hannah, 8, TOST,21.71, 20.52, Girls, 8 & Under, 25m Freestyle

def build_swim_entry(row):
    row.pop(0) # remove place
    
    r = build_race_name(row.pop())
    age_group = row.pop().strip()
    if "8 & Under" in age_group: 
        age_group = '8&U'
    g = get_gender(row.pop())
    entry = SwimerEventTimes(str(uuid.uuid1()), Swimmer(f"{row[0]} {row[1]}", row[2].strip(), row[3].strip()),format_time(row[4]),None,format_time(row[5]),None, Event(r,age_group,g))
    return entry

    
# xl = pandas.ExcelFile('little.xlsx')
# for sheet in xl.sheet_names:
#     filename = f"{sheet}.csv"
#     df = pandas.read_excel('little.xlsx', index_col=[0], sheet_name=sheet)
#     df.to_csv(filename, index=False)

#     with open(filename, 'r') as csvfile:
#         datareader = csv.reader(csvfile)
#         events = []

#         for x in next(datareader, None):
#             if "Unnamed" not in x: 
#                 events.append(x)
#         print(events)
#         next(datareader, None)  # remove headers

#         for row in datareader:
#             print(row)
#             event_counter = 0
#             while len(events)-1 > event_counter:
#                 entry = row[:7]
#                 if entry[0] != '' and entry[0] != 'NC' and entry[6] != 'DQ' and entry[6] != 'NS':
#                     swim_entries.append(build_swim_entry(events[event_counter], entry))
#                 del row[:8]
#                 event_counter += 1

        
        
# entrys = pandas.DataFrame(swim_entries)
# entrys.to_csv("seed2.csv", index=False)
    
    
skip_reasons = ['DQ', 'DNF', 'DFS', 'NS', 'SCR']
def load_race_data(path):
    raceTimes = []
    with open(path, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        next(datareader, None)  # skip the headers
        for row in datareader:
            raceTimes.append(build_swim_entry(row))
    returnValue = {
        "meet_info": 'CSV Import',
        "times": raceTimes,
        "date": datetime.now(),
    }
    print(returnValue)
    return returnValue