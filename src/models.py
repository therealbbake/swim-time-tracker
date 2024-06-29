class Event: 
    def __init__(self, race, age_group, gender):
        self.race = race
        self.age_group = age_group
        self.gender = gender
    
    def __str__(self):
        return f"{self.race} ({self.gender} - {self.age_group})"
    
    def __eq__(self, other):
        return self.race == other.race and self.gender == other.gender and self.age_group == other.age_group

#Brooktree A BTST 1:43.91 1:46.02

class RelayTeam:
    def __init__(self, team, name, age):
        self.team = team
        self.name = name
        self.age = age
        
    def __str__(self):
        return f"{self.team} ({self.name})({self.age})"  # BTST (A) (11-12)
    
class Swimmer:
    def __init__(self, name, age, team, ):
        self.name = name
        self.age = age
        self.team = team
        
    def __str__(self):
        return f"{self.name} ({self.age})({self.team})"
        

class SwimerEventTimes:
    def __init__(self, record_id, racer, seed_time, seed_date, most_recent_time, most_recent_date, event):
        self.record_id = record_id
        self.racer = racer
        self.seed_time = seed_time
        self.seed_date = seed_date
        self.most_recent_time = most_recent_time
        self.most_recent_date = most_recent_date  
        self.event = event   
    def __str__(self):
        return f"{self.racer} -- seed: \"{self.seed_time}\" latest: \"{self.most_recent_time}\""

    def get_excel_row(self):
        return [self.racer.name ,self.racer.age, self.racer.team, self.seed_time, self.seed_date, self.most_recent_time, self.most_recent_date]
    
    def get_as_csv(self):
        return [self.record_id, 
                    self.racer.name, 
                    self.racer.age, 
                    self.racer.team, 
                    self.seed_time, 
                    self.seed_date, 
                    self.most_recent_time, 
                    self.most_recent_date, 
                    self.event.race, 
                    self.event.gender, 
                    self.event.age_group
                ]
    
# timeEntry = SwimerEventTimes(str(uuid.uuid1()), Swimmer("name", "age", "team"), "1:11.11", '1/1/24', "1:11.11", '1/1/24', Event("50 Free", "11-12", "Boys")))
# rows_to_insert.append([timeEntry.record_id, 
#                        timeEntry.racer.name, 
#                        timeEntry.racer.age, 
#                        timeEntry.racer.team, 
#                        timeEntry.seed_time, 
#                        timeEntry.seed_date, 
#                        timeEntry.most_recent_time, 
#                        timeEntry.most_recent_date, 
#                        timeEntry.event.race, 
#                        timeEntry.event.gender, 
#                        timeEntry.event.age_group))