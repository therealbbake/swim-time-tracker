
import csv
from models.mod import *
import helpers.Utility as Utility
from datetime import datetime

# PL,LastName,FirstName,AGE,Team,Seed,Official,Points,Gender,AGE_GROUP,EVENT,Date
# 2, Rossbach, Hannah, 8, TOST,21.71, 20.52, Girls,5, 8 & Under, 25m Freestyle,05/12/2024

def build_swim_entry(row, score):
    row.pop(0) # remove place
    
    race = row[10].split(' ')
                          
    distance = Utility.get_race_distance(race[0])
    race_type = Utility.get_race_type(race[1])
    meet_date = datetime.strptime(race[11], '%b/%d/%Y')
    age_group = row[9] if "8 & Under" not in row[9] else '8&U'
    team = row[4]
    if not any(reason in row[6] for reason in  Utility.skip_reasons):
        result = "Finished"
        time_in_milis = Utility.convert_time_to_seconds(row[6])
    else:
        result = row[6]
        time_in_milis = None
                  
    g = Utility.get_gender(row.pop())
    entry = IndividualSwimEntry(
        row[2], #first_name
        row[1], #last_name
        row[3], # age
        team, # team
        row[0], # placement
        row[8], # points
        result, #
        time_in_milis, 
        meet_date, 
        race_type, 
        age_group,
        g, 
        distance)
        
    if team in score: 
        score[team] += row[8]
    else:
        score[team] = row[8]
    return entry
    
    
def load_race_data(path):
    raceTimes = []
    score = {}
    with open(path, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        next(datareader, None)  # skip the headers
        for row in datareader:
            raceTimes.append(build_swim_entry(row, score))
    returnValue = {
        "times": raceTimes,
        "score": score
    }   
    return returnValue