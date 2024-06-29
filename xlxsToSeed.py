import pandas 
import csv
from src.models import *
import uuid

def build_race_name(race_info):
    return ' '.join(str(r) for r in race_info).replace('Swim-off' , '').replace(' Meter', 'm').replace('Individual Medley', 'IM').replace('Freestyle', 'Free').replace('Breaststroke', 'Breast').replace('Backstroke', 'Back').replace('Butterfly', 'Fly').strip()

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
    print(time)
    if(time == "NT"):
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

def build_swim_entry(event, row):
    row.pop(0) 
    event_s = event.split(' ')
    event_s.pop()
    event_s.pop()
    g = get_gender(event_s.pop(0))
    a = event_s.pop(0)
    r = build_race_name(event_s)
    entry = SwimerEventTimes(str(uuid.uuid1()), Swimmer(f"{row[0]} {row[1]}", row[2], row[3]),format_time(row[4]),None,format_time(row[5]),None, Event(r,a,g))
    return entry.get_as_csv()

    
xl = pandas.ExcelFile('little.xlsx')
for sheet in xl.sheet_names:
    filename = f"{sheet}.csv"
    df = pandas.read_excel('little.xlsx', index_col=[0], sheet_name=sheet)
    df.to_csv(filename, index=False)

    with open(filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        events = []

        for x in next(datareader, None):
            if "Unnamed" not in x: 
                events.append(x)
        print(events)
        next(datareader, None)  # remove headers

        for row in datareader:
            print(row)
            event_counter = 0
            while len(events)-1 > event_counter:
                entry = row[:7]
                if entry[0] != '' and entry[0] != 'NC' and entry[6] != 'DQ' and entry[6] != 'NS':
                    swim_entries.append(build_swim_entry(events[event_counter], entry))
                del row[:8]
                event_counter += 1

        
        
entrys = pandas.DataFrame(swim_entries)
entrys.to_csv("seed2.csv", index=False)
    