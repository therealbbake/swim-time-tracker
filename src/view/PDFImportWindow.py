from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from db.db import DataAccess
import helpers.PDFParser as PDFParser
import traceback
import itertools
import uuid
import re

class PDFImport(CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path = self.master.import_path
        self.dataAccess: DataAccess = self.master.dataAccess 
        self.geometry("950x950")
        self.title('Meet Results')
        self.resizable(False, True)
        try:
            self.data = PDFParser.load_race_data(path)
            self.meet: Meet = self.data['meet']
            print(self.meet.record_id)
            self.relay_teams = self.data['relay_teams'] 
            
            self.top_frame = CTkFrame(self, fg_color="transparent")
            self.top_frame.pack(side=TOP)
            self.meet_title = CTkLabel(self.top_frame, text= f"{self.meet.title}")
            self.meet_title.pack()
            self.meet_date = CTkLabel(self.top_frame, text=self.meet.meet_date.strftime("%m/%d/%Y"))
            self.meet_date.pack()

            CTkLabel(self.top_frame, text=f"Meet Results").pack()
            self.meet_score = CTkLabel(self.top_frame, justify='left', text=f"{self.meet.results()}")
            self.meet_score.pack()
            
            
            self.bottom_frame = CTkFrame(self, fg_color="transparent")
            self.bottom_frame.pack(side=BOTTOM)
            isAlreadySaved = self.data['isAlreadySaved']
            print(fr'{isAlreadySaved}')
            if self.data['isAlreadySaved']:
                save_button = 'Event Already Saved'
                button_state = 'disabled'
            else:
                save_button = 'Save Event Data'
                button_state = 'normal'
                
            self.save_time_button = CTkButton(self.bottom_frame, text=save_button, state=button_state,  command=self.save_results)
            self.save_time_button.pack()
            
            
            
            self.times_by_age_and_gender = {}
            for x in self.data['relay_race_times']:
                group = f"{x.gender.name}, {x.age_group}"
                if group in self.times_by_age_and_gender:
                    self.times_by_age_and_gender[group]["relay_race_times"].append(x)
                else: 
                    self.times_by_age_and_gender[group] = {
                        "relay_race_times": [x],
                        "individual_race_times": []
                    }
        
            for x in self.data['individual_race_times']:
                group = f"{x.gender.name}, {x.age_group}"
                if group in self.times_by_age_and_gender:
                    self.times_by_age_and_gender[group]["individual_race_times"].append(x)
                else: 
                    self.times_by_age_and_gender[group] = {
                        "individual_race_times": [x],
                        "relay_race_times": []
                    }               
                    
            self.division = CTkFrame(self, fg_color="transparent")
            self.division.pack(side=LEFT)
            CTkLabel(self.division, text=f"Swimming Divisions").pack(pady=5, padx=5)

            for key in self.times_by_age_and_gender:
                def open_results(x = key):
                    self.show_division_results(x)
                    pass
                CTkButton(self.division, text=f"{key} Results", command=open_results ).pack(pady=5, padx=5)
                
            self.division_result = CTkFrame(self, width=800, height=500, fg_color="transparent")
            self.division_result.pack(side=RIGHT)


                
        except Exception as error:
            print(traceback.format_exc())
            self.error_loading = CTkLabel(self, text=f"Failed to build out meet data from PDF \n Failure Reason: \n {error}")
            self.error_loading.pack(pady=30)
           
    def show_division_results(self, key):
        if hasattr(self, 'tabview'):
            self.tabview.destroy()
            
        self.tabview = CTkTabview(master=self.division_result, width=500)
        self.tabview.pack()
        
        
        times_by_event = []
        for k, g in itertools.groupby(self.times_by_age_and_gender[key]['individual_race_times'], lambda x: f"{x.distance}M {x.event_race_type.name}"):
                times_by_event.append((k, list(g)))
               
        if 'relay_race_times' in self.times_by_age_and_gender[key]:
            for k, g in itertools.groupby(self.times_by_age_and_gender[key]['relay_race_times'], lambda x: f"{x.distance}M {x.event_race_type.name} Relay"):
                    times_by_event.append((k, list(g)))
        for event in times_by_event:
            tab = self.tabview.add(event[0]) 
            event_label = CTkLabel(tab,font=('helvetica', 24), text="{} - {} times recorded".format(str(event[0]), len(event[1])))        
            event_label.pack(side=TOP)
            # Insert elements into the listbox'
            # listbox.insert(tk.END, "Name --- Age --- Team --- Seed --- Official") 
            columns = ['Pl', 'Racer', 'Result', 'Points']

            treeview = ttk.Treeview(tab, height=12, show='tree', displaycolumns='', columns=columns)
            treeview.pack(side=LEFT, ipadx=200, ipady=20)

            # create CTk scrollbar
            ctk_textbox_scrollbar = CTkScrollbar(tab, command=treeview.yview)
            ctk_textbox_scrollbar.pack(side=RIGHT)
            treeview.configure(yscrollcommand=ctk_textbox_scrollbar.set)
            for time in event[1]: 
                time_item = treeview.insert("", END, text=str(time), values=time.get_result())
                # CTkLabel(self.resultSection, anchor=W, text=str(time), font=('helvetica', 18), justify='left').pack()
                if isinstance(time, RelaySwimEntry):
                    team_breakdown = self.relay_teams[time.relay_id]
                    # team = f"1) {team_breakdown[0]} 2) {team_breakdown[1]}\n 3) {team_breakdown[2]} 4) {team_breakdown[3]}"
                    treeview.insert(time_item, END, text=f"1) {team_breakdown[0]} 2) {team_breakdown[1]}") 
                    treeview.insert(time_item, END, text=f"3) {team_breakdown[2]} 4) {team_breakdown[3]}") 
                    # CTkLabel(self.resultSection, justify='left', text=team).pack()
                # listbox.insert(tk.END, f"{time.swimmer.name} --- {time.swimmer.age} --- {time.swimmer.team} --- {time.seed_time} --- {time.most_recent_time}") 
    
    def save_results(self):
        try: 
            meet_id = self.dataAccess.create_meet(self.meet)
            self.dataAccess.add_meet_relation(self.meet.score.keys(), meet_id)
            events_by_id = self.dataAccess.get_all_events()
            swimmers_by_id = self.dataAccess.get_swimmers_for_teams(list(self.meet.score.keys()))
            new_swimmers = []
            race_times = []
            relay_teams = []
            for key, value in self.times_by_age_and_gender.items():
                splitKey = key.split(', ')
                gender = Gender[splitKey[0]]
                age_group = splitKey[1]
            
                for k, g in itertools.groupby(value['individual_race_times'], lambda x: (x.event_race_type.name, x.distance)):
                    event = RaceEvent(None, Stroke[k[0]], age_group, gender, k[1], False)
                    event_id = list(events_by_id.keys())[list(events_by_id.values()).index(event)] if event in list(events_by_id.values()) else None
                    if not event_id:
                        event_id = self.dataAccess.create_event(event)
                        events_by_id[event_id] = event
                        
                    for race_entry in list(g):
                        race_entry: IndividualSwimEntry = race_entry 
                        swimmer = Racer(None,race_entry.racer_fname, race_entry.racer_lname, race_entry.racer_age, race_entry.racer_team, race_entry.gender, False)
                        racer_id = list(swimmers_by_id.keys())[list(swimmers_by_id.values()).index(swimmer)] if swimmer in list(swimmers_by_id.values()) else None
                        if not racer_id:
                            racer_id = str(uuid.uuid1())
                            swimmer.record_id = racer_id
                            swimmers_by_id[racer_id] = swimmer
                            print(f'adding swimmer to db {swimmer}')
                            print(f'adding swimmer to db {swimmer}')
                            new_swimmers.append(swimmer)
                        
                        race_times.append(RaceTime(None, racer_id, event_id, meet_id, race_entry.result, race_entry.time, race_entry.placement, race_entry.points, self.meet.meet_date))
                 
                for k, g in itertools.groupby(value['relay_race_times'], lambda x: (x.event_race_type.name, x.distance)):
                    event = RaceEvent(None, Stroke[k[0]], age_group, gender, k[1], True)
                    
                    event_id = list(events_by_id.keys())[list(events_by_id.values()).index(event)] if event in list(events_by_id.values()) else None
                    if not event_id:
                        event_id = self.dataAccess.create_event(event)
                        events_by_id[event_id] = event
                
        
                    for relay in list(g):
                        relay_entry: RelaySwimEntry = relay 
                        relay_racer = Racer(None,relay_entry.relay_group, relay_entry.relay_team, relay_entry.age_group, relay_entry.relay_team, relay_entry.gender,True)
                        relay_id = list(swimmers_by_id.keys())[list(swimmers_by_id.values()).index(relay_racer)] if relay_racer in list(swimmers_by_id.values()) else None
                        if not relay_id:
                            relay_id = str(uuid.uuid1())
                            relay_racer.record_id = relay_id
                            swimmers_by_id[relay_id] = relay_racer
                            print(f'adding swimmer to db {relay_racer}')
                            new_swimmers.append(relay_racer)
                        
                        
                        race_id = str(uuid.uuid1())
                        race_times.append(RaceTime(race_id, relay_id, event_id, meet_id, relay_entry.result, relay_entry.time, relay_entry.placement, relay_entry.points, self.meet.meet_date))
                        
                        team_breakdown = self.relay_teams[relay_entry.relay_id]
                        relay_swimmers = []
                        print(team_breakdown)
                        for s in team_breakdown: 
                            s = re.sub("[()]", "",str(s))
                            s_racer = str(s).strip().split(' ')
                            age = s_racer.pop()
                            s_racer_name = ' '.join(s_racer).split(', ')
                            relay_swimmer = Racer(None, str(s_racer_name[1]).strip(), str(s_racer_name[0]).strip(), age, relay_entry.relay_team, race_entry.gender, False)
                            swimmer_id = list(swimmers_by_id.keys())[list(swimmers_by_id.values()).index(relay_swimmer)] if relay_swimmer in list(swimmers_by_id.values()) else None
                            if not swimmer_id:
                                print(f'not finding a swimmer id for {relay_swimmer}')
                            relay_swimmers.append(swimmer_id)
                            
                        relay_teams.append(RelayTeamBreakDown(str(uuid.uuid1()), race_id, relay_id, relay_swimmers[0],relay_swimmers[1], relay_swimmers[2], relay_swimmers[3]))
            
            
            self.dataAccess.create_swimmers(new_swimmers)
            self.dataAccess.create_race_times(race_times)
            self.dataAccess.create_relay_breakdowns(relay_teams)
            
            self.destroy()
            
        except Exception as error:
            print(traceback.format_exc())
            self.error_loading = CTkLabel(self.bottom_frame, text=f"Failed to Save Meet Data \n Failure Reason: \n {error}")
            self.error_loading.pack(pady=30)
            self.save_time_button.pack(pady=10)
            