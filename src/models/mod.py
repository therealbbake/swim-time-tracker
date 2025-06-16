from enum import Enum
import numpy as np
import helpers.Utility as Utils
from datetime import datetime 
import json


class Stroke(Enum):
    UNKNOWN = 0
    Freestyle = 1
    Breaststroke = 2
    Butterfly = 3
    Backstroke = 4
    Medley = 5
    
class Gender(Enum):
    UNKNOWN = 0
    BOYS = 1
    GIRLS = 2
    
    
class RaceEvent: 
    def __init__(self, record_id, raceType, age_group, gender, distance, is_relay):
         self.record_id = record_id
         self.raceType: Stroke = raceType # RaceType
         self.age_group = age_group # 8&U, 9-10, 11-12, 13-14, 15-18
         self.gender: Gender = gender # Gender
         self.distance = distance # 25M, 50M, 100M, 200M 
         self.is_relay = is_relay # if race is relay race
    
    def __eq__(self, other):
        return (self.raceType == other.raceType
                    and self.age_group == other.age_group
                    and self.gender == other.gender
                    and self.distance == other.distance
                    and self.is_relay == other.is_relay)

    def __hash__(self):
        return hash((self.raceType, self.age_group, self.gender, self.distance, self.is_relay))

    def get_db_row(self):
        return (self.record_id, self.raceType.name, self.age_group, self.gender.name, self.distance, self.is_relay)
    
    def __str__(self):
        if self.is_relay: 
            return  f"{self.distance}M {self.raceType.name} Relay ({self.age_group})"
        else:
            return f"{self.distance}M {self.raceType.name} ({self.age_group})"
    
         
class Racer:
    def __init__(self, record_id, first_name, last_name, age, team, gender, is_relay):
        self.record_id = record_id
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender: Gender = gender
        self.team = team
        self.is_relay = is_relay
        
    def __str__(self):
        if self.is_relay: 
            return f"{self.last_name} {self.age} Relay Team {self.first_name}"
        else:
            return f"{self.first_name} {self.last_name} ({self.age})({self.team})"
    
    def __eq__(self, other):
        
        if (self.first_name != other.first_name):
            return False
        if (self.last_name != other.last_name):
            return False
        # if (self.age != other.age):
        #     return False
        if (self.gender.value != other.gender.value):
            return False
        if (self.team != other.team):
            return False
        
        return (self.is_relay == other.is_relay)
        
    def __hash__(self):
        return hash((self.first_name, self.last_name, self.age, self.team, self.gender.value, self.is_relay))
    
    def get_db_row(self):
        return (self.record_id, self.first_name, self.last_name, self.age, self.team, self.gender.name, self.is_relay)
    
    
    
class RelayTeamBreakDown:
    def __init__(self, record_id, race_id, relay_id,  swimmer_1, swimmer_2, swimmer_3, swimmer_4):
        self.record_id = record_id
        self.relay_id = relay_id 
        self.race_id = race_id 
        self.swimmer_1 = swimmer_1 
        self.swimmer_2 = swimmer_2 
        self.swimmer_3 = swimmer_3 
        self.swimmer_4 = swimmer_4 
               
    def __str__(self):
        return f"1) {self.swimmer_1} 2) {self.swimmer_2}\n3) {self.swimmer_3} 4) {self.swimmer_4}"
    
    def get_db_row(self):
        return (self.record_id, self.race_id, self.relay_id,  self.swimmer_1, self.swimmer_2, self.swimmer_3, self.swimmer_4)


class RaceTime:
    def __init__(self, record_id, racer_id, event_id,meet_id, result, result_time, placement, points_scored, date):
        self.record_id = record_id 
        self.racer_id = racer_id # swimmer or relay team id
        self.event_id = event_id # event_id
        self.meet_id = meet_id # meet_id
        self.result = result # results (DQ, FINISHED)
        self.result_time = result_time # time in Seconds
        self.placement = placement # int 
        self.points_scored = points_scored # int  points scored for team 
        self.date: datetime = date # date Time was recorded
    def __str__(self):
        return f"{self.placement} - {Utils.format_time(self.result_time)} - {self.date.strftime('%m/%d/%Y')}"
    def get_db_row(self):
        return (self.record_id, self.racer_id, self.event_id, self.meet_id, self.result, self.result_time, self.placement, self.points_scored, int(self.date.timestamp() * 1000))
        
class RacerTimeInfo:
    def __init__(self, racer, best_time, latest_time):
        self.racer = racer
        self.best_time = best_time,
        self.latest_time = latest_time
        
class Meet:
    def __init__(self, record_id, meet_date, title, score):
          self.record_id = record_id 
          self.meet_date: datetime = meet_date 
          self.title = title 
          self.score: dict = score
    def results(self):
        result = []
        keys = list(self.score.keys())
        values = list(self.score.values())
        sorted_value_index = np.argsort(values)
        sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
        if(len(sorted_dict.items()) > 2):
            counter = len(sorted_dict.keys())
            for i in sorted_dict.items():
                result.insert(0, f'{counter}. {i[0]} -- {i[1]}\n')
                counter -= 1
        else:
            for i in sorted_dict.items():
                result.insert(0, f'{i[0]} -- {i[1]}\n')
        
        return ''.join(result)  # (BTST, 213), (HOW, 332)
    
    def get_db_row(self):
        return (self.record_id, self.meet_date.timestamp(), self.title, json.dumps(self.score))
    
class IndividualSwimEntry:
    def __init__(self,  
                 racer_fname, # Last, First
                 racer_lname, # Last, First
                 racer_age,
                 racer_team,
                 placement,
                 points,
                 result, # Finished or DQ 
                 time, # time in milis
                 date, 
                 event_race_type, 
                 age_group, 
                 gender, 
                 distance):
        self.racer_fname = racer_fname
        self.racer_lname = racer_lname
        self.racer_age = racer_age
        self.racer_team = racer_team
        self.placement = placement
        self.points = points
        self.result = result
        self.time = time
        self.date = date
        self.event_race_type: Stroke = event_race_type
        self.age_group = age_group
        self.gender: Gender = gender
        self.distance = distance
        
    def __str__(self):
        result = Utils.format_time(self.time) if self.result == "Finished" else self.result
        return f"{self.placement} {self.racer_lname}, {self.racer_fname} ({self.racer_age}) {self.racer_team} - {result} - {self.points}"

    def get_result(self):
        result = Utils.format_time(self.time) if self.result == "Finished" else self.result
        return [self.placement,f'{self.racer_lname}, {self.racer_fname} ({self.racer_age}) {self.racer_team} ', result, self.points]

class RelaySwimEntry:
    def __init__(self,
                    relay_id,  
                    relay_group, # (a)
                    relay_team, # (HOW)
                    placement,
                    points,
                    result, # Finished or DQ 
                    time, # time in milis
                    date, 
                    event_race_type, 
                    age_group, 
                    gender, 
                    distance):
        self.relay_id = relay_id
        self.relay_group = relay_group
        self.relay_team = relay_team
        self.placement = placement
        self.points = points
        self.result = result
        self.time = time
        self.date = date
        self.event_race_type: Stroke = event_race_type
        self.age_group = age_group
        self.gender: Gender = gender
        self.distance = distance
        
    def __str__(self):
        result = Utils.format_time(self.time) if self.result == "Finished" else self.result
        return f"{self.placement} {self.relay_team}, {self.relay_group} - {result} - {self.points}"

    def get_result(self):
        result = Utils.format_time(self.time)  if self.result == "Finished" else self.result
        return [self.placement, f"{self.relay_team} ({self.relay_group})", self.relay_group, result,self.points]

    
          
                    
team_names = [
    "WFST",
    "KSC",
    "BTST",
    "CO",
    "HOW",
    "TOST",
    "OP",
    "RL",
    "CL",
    "NM",
    "WC",
]


def get_gender(gender):
    val = gender.lower()
    if val == "women" or "girl" in val:
        return Gender.GIRLS
    elif val == "men" or "boy" in val:
        return Gender.BOYS
    else:
        return Gender.UNKNOWN
    
def get_race_type(event):
    race_info = ' '.join(str(r) for r in event).replace('Freestyle', 'Free').replace('Breaststroke', 'Breast').replace('Backstroke', 'Back').replace('Butterfly', 'Fly').strip()
    
    print(race_info)
    if 'Medley' in race_info or 'IM' in race_info:
        return Stroke.Medley
    if 'Free' in race_info:
        return Stroke.Freestyle
    if 'Breast' in race_info:
        return Stroke.Breaststroke
    if 'Back' in race_info:
        return Stroke.Backstroke
    if 'Fly' in race_info:
        return Stroke.Butterfly
    else:
        return Stroke.UNKNOWN
    