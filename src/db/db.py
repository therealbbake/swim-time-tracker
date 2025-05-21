import sqlite3
from models.mod import *
from datetime import datetime
import uuid 
import shutil

meet_db = """
    CREATE TABLE IF NOT EXISTS "meet" (
        "record_id"	varchar(255),
        "meet_date"	int,
        "title"	varchar(255),
        "score"	BLOB,
        PRIMARY KEY("record_id")
    )
"""

meet_relations_db = """
    CREATE TABLE IF NOT EXISTS "meet_teams" (
        "team"	varchar(255),
        "meet_id"	varchar(255)
    )
"""

event_db = """
    CREATE TABLE IF NOT EXISTS "events" (
        "record_id "	varchar(255),
        "race_type"	varchar(255),
        "age_group"	varchar(255),
        "gender"	varchar(255),
        "distance" INT,
        "is_relay"	BOOL,
        PRIMARY KEY("record_id "),
        UNIQUE("race_type","gender","age_group","is_relay")
    )
"""
swimmer_db = """
    CREATE TABLE IF NOT EXISTS "swimmers" (
        "record_id"	varchar(255),
        "first_name"	varchar(255),
        "last_name"	varchar(255),
        "age"	varchar(255),
        "team"	varchar(255),
        "gender"	int,
        "is_relay"	BOOL,
        PRIMARY KEY("record_id"),
        CONSTRAINT "uniqueSwimmer" UNIQUE("first_name","last_name","team","gender","age")
    )
"""
raceTimes_db = """
    CREATE TABLE IF NOT EXISTS "times" (
        "record_id"	varchar(255),
        "racer_id"	varchar(255),
        "event_id"	varchar(255),
        "meet_id"	varchar(255),
        "result"	varchar(255),
        "result_time"	float,
        "placement"	varchar(255),
        "points_scored"	int,
        "date"	int,
        FOREIGN KEY("event_id") REFERENCES "events"("record_id "),
        FOREIGN KEY("racer_id") REFERENCES "swimmers"("record_id"),
        PRIMARY KEY("record_id")
    )
"""

relay_breakdown_db = """
    CREATE TABLE IF NOT EXISTS "relay_breakdown" (
        "record_id"	varchar(255),
        "race_id"	varchar(255),
        "relay_team_id"	varchar(255),
        "swimmer_1"	varchar(255),
        "swimmer_2"	varchar(255),
        "swimmer_3"	varchar(255),
        "swimmer_4"	varchar(255),
        PRIMARY KEY("record_id")
    )
"""


class DataAccess:
    def __init__(self):
        self.connection = sqlite3.connect('src/db/swimtracker.sqlite3')
        self.create_tables()
        
    def backup_db(self):
        self.connection.close()
        current_date = datetime.now().strftime("%m_%d_%Y")
        shutil.copyfile('src/db/swimtracker.sqlite3', f'src/db/swimtracker_backup_{current_date}.sqlite3')
        self.connection = sqlite3.connect('src/db/swimtracker.sqlite3')
        
    def close_connection(self):
        self.connection.close()
            
    def create_tables(self):
        cur = self.connection.cursor()
        cur.execute(event_db)
        cur.execute(meet_db)
        cur.execute(meet_relations_db)
        cur.execute(swimmer_db)
        cur.execute(raceTimes_db)
        cur.execute(relay_breakdown_db)
        cur.close()
        self.connection.commit()
       
    # Event DB 
    def get_all_events(self):
        cur = self.connection.cursor()
        rows = cur.execute("SELECT * FROM events").fetchall()
        events_by_id = {}
        for result in rows:
            events_by_id[result[0]] = RaceEvent(result[0], Stroke[result[1]], result[2], Gender[result[3]], result[4], result[5])
        cur.close()
        return events_by_id

    def get_event_by_id(self, event_id):
        cur = self.connection.cursor()
        result = cur.execute("SELECT * FROM events WHERE record_id = ?", (event_id)).fetchone()
        if result == None:
            return None
        cur.close()
        return RaceEvent(result[0], Stroke[result[1]], result[2], Gender[result[3]], result[4], result[5])
        
    def get_eventId(self, raceType, gender, distance, age_group, is_relay):
        cur = self.connection.cursor()
        row = cur.execute(
        """ SELECT record_id FROM events 
            WHERE raceType = ? 
            AND gender = ?
            AND distance = ?
            AND age_group = ? 
            AND is_relay = ?
        """,
        (raceType, gender, distance, age_group, is_relay, )).fetchone()
        cur.close()
        return row[0] if row != None else None

    def create_event(self, event: RaceEvent):
        try:
            event.record_id = str(uuid.uuid1())
            cur = self.connection.cursor()
            cur.execute("INSERT INTO events VALUES(?, ?, ?, ?, ?, ?)", event.get_db_row())
            return event.record_id
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()
        
    # Swimm DB 
    def get_swimmers_for_teams(self, teams: list):
        cur = self.connection.cursor()
        rows = cur.execute('SELECT * FROM swimmers WHERE team IN (%s)' % ','.join('?'*len(teams)), teams).fetchall()
        racers_by_id = {}
        for result in rows:
            racers_by_id[result[0]] = Racer(result[0], result[1], result[2], result[3], result[4], Gender[result[5]], result[6])
        cur.close()
        return racers_by_id
    
    def get_swimmer_by_id(self, swimmer_id):
        cur = self.connection.cursor()
        result = cur.execute("SELECT * FROM swimmers WHERE record_id = ?", (swimmer_id)).fetchone()
        if result == None:
            return None
        cur.close()
        return Racer(result[0], result[1], result[2], result[3], result[4], Gender[result[5]], result[6])

    def get_swimmer_id(self, swimmer_fname,  swimmer_lname, swimmer_team, swimmer_age, swimmer_gender):
        cur = self.connection.cursor()
        result = cur.execute("""SELECT record_id FROM swimmers 
                                WHERE first_name = ?  
                                AND last_name = ? 
                                AND team = ?
                                AND age = ? 
                                AND gender = ?""", (swimmer_fname,  swimmer_lname, swimmer_team, swimmer_age, swimmer_gender)).fetchone()
        return result[0] if result != None else None

    def get_swimmers_by_query(self, search_params: dict):
        cur = self.connection.cursor()
        query = 'SELECT * FROM swimmers'
        params = tuple()
        
        
        for p in search_params.items():
            if not p[1] or p[1] == '':
                continue
            query += f' AND {p[0]} = ?' if 'WHERE' in query else f' WHERE {p[0]} = ?'
            params += (p[1],)
            
        swimmers = []
        rows = cur.execute(query, params).fetchall()
        for result in rows:
            swimmers.append(Racer(result[0], result[1], result[2], result[3], result[4], Gender[result[5]], result[6]))
        return swimmers

    def create_swimmer(self, swimmer: Racer):
        cur = self.connection.cursor()
        try:
            swimmer.record_id = str(uuid.uuid1())
            #(record_id, self.first_name, self.last_name, self.age, self.team, self.gender.name, self.is_relay)
            cur.execute("INSERT INTO swimmers VALUES(?, ?, ?, ?, ?, ?)", swimmer.get_db_row())
            return swimmer.record_id
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close() 
            
    def create_swimmers(self, swimmers: list):
        cur = self.connection.cursor()
        try:
            newRows = []
            for s in swimmers: 
                newRows.append(s.get_db_row())
            #(record_id, self.first_name, self.last_name, self.age, self.team, self.gender.name, self.is_relay)
            cur.executemany("INSERT INTO swimmers VALUES(?, ?, ?, ?, ?, ?, ?)", newRows)
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()
     
    # Relay Breakdown DB      
    def create_relay_breakdowns(self, relay_teams: list):
        cur = self.connection.cursor()
        try:
            newRows = []
            for r in relay_teams: 
                newRows.append(r.get_db_row())
           
            cur.executemany("INSERT INTO relay_breakdown VALUES(?, ?, ?, ?, ?, ?, ?)", newRows)
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()
   
    # retrieve all relays the provided swimmer was apart of 
    def get_relay_teams_for_swimmer(self, swimmer_id):
        cur = self.connection.cursor()
        rows = cur.execute("""SELECT * FROM relay_breakdown 
                                WHERE swimmer_1 = ?  
                                OR swimmer_2 = ? 
                                OR swimmer_3 = ?
                                OR swimmer_4 = ?
                            """, (swimmer_id, swimmer_id, swimmer_id, swimmer_id)).fetchall()
        racers_by_id = []
        for result in rows:
            racers_by_id.append(RelayTeamBreakDown(result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
        cur.close()
        return racers_by_id
    
    # Meet DB     
    def create_meet(self, meet: Meet):
        cur = self.connection.cursor()
        try:
            meet.record_id = str(uuid.uuid1())
            # (record_id, meet_date, title, team_a, a_score, team_b, b_score) 
            cur.execute("INSERT INTO meet VALUES(?, ?, ?, ?)", meet.get_db_row())
            return meet.record_id
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()
            
    def get_meet_id(self, meet_title, meet_date):
        cur = self.connection.cursor()
        try:
            # (record_id, meet_date, title, team_a, a_score, team_b, b_score) 
            result = cur.execute("SELECT * FROM meet WHERE meet_date = ? and title = ?", (meet_date, meet_title)).fetchone()
            print(result)
            return result[0] if result != None else None
        finally:
            cur.close()
            
    # RaceTime
    def create_race_times(self, times: list):
        cur = self.connection.cursor()
        try:
            newRows = []
            for t in times: 
                newRows.append(t.get_db_row())
            # (record_id, racer_id, event_id, meet_id, result, result_time, placement, points_scored, date)
            cur.executemany("INSERT INTO times VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", newRows)
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()
            
    #datetime.fromtimestamp(ms/1000.0)
    
    
    def get_swim_teams(self):
        cur = self.connection.cursor()
        rows = cur.execute("SELECT  DISTINCT team from swimmers").fetchall()
        swim_teams = []
        for result in rows:
            swim_teams.append(result[0])
        cur.close()
        return swim_teams
    
    
    def add_meet_relation(self, teams: list, meet_id):
        cur = self.connection.cursor()
        try:
            newRows = []
            for t in teams: 
                newRows.append((t, meet_id))
            # (team, meet_id)
            cur.executemany("INSERT INTO meet_teams VALUES(?, ?)", newRows)
        except Exception as error:
            self.connection.rollback()
            raise error
        finally:
            self.connection.commit() 
            cur.close()