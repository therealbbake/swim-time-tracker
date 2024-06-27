
   
class Event: 
    def __init__(self, race, age_group, gender):
        self.race = race
        self.age_group = age_group
        self.gender = gender
    
    def __str__(self):
        return f"{self.race} ({self.gender} - {self.age_group})"

class Swimmer:
    def __init__(self, name, age, team, ):
        self.name = name
        self.age = age
        self.team = team
        
    def __str__(self):
        return f"{self.name} ({self.age})({self.team})"
        

class SwimerEventTimes:
  def __init__(self, record_id, swimmer, seed_time, seed_date, most_recent_time, most_recent_date, event):
    self.record_id = record_id
    self.swimmer = swimmer
    self.seed_time = seed_time
    self.seed_date = seed_date
    self.most_recent_time = most_recent_time
    self.most_recent_date = most_recent_date  
    self.event = event   
  def __str__(self):
    return f"{self.swimmer} -- seed: \"{self.seed_time}\" latest: \"{self.most_recent_time}\""
    
    
# timeEntry = SwimerEventTimes(str(uuid.uuid1()), Swimmer("name", "age", "team"), "1:11.11", '1/1/24', "1:11.11", '1/1/24', Event("50 Free", "11-12", "Boys")))
# rows_to_insert.append((timeEntry.record_id, 
#                        timeEntry.swimmer.name, 
#                        timeEntry.swimmer.age, 
#                        timeEntry.swimmer.team, 
#                        timeEntry.seed_time, 
#                        timeEntry.seed_date, 
#                        timeEntry.most_recent_time, 
#                        timeEntry.most_recent_date, 
#                        timeEntry.event.race, 
#                        timeEntry.event.gender, 
#                        timeEntry.event.age_group))