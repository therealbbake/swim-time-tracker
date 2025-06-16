from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from db.DataAccess import DataAccess
import helpers.PDFParser as PDFParser
import traceback
import itertools
import uuid
import re
from helpers.Logger import LOGGER
class PDFImport(CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path = self.master.import_path
        self.dataAccess: DataAccess = self.master.dataAccess 
        self.geometry("950x750")
        self.title('Meet Results')
        self.resizable(False, True)
        
        LOGGER.info("Entering PDFImport with path: %s", path)   
        try:
            self.data = PDFParser.load_race_data(path)
            # print(self.data)
            self.meet: Meet = self.data['meet']
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
            if ('needs_attention' in self.data and len(self.data['needs_attention'])> 0):
                self.textbox = CTkTextbox(master=self, width=900, corner_radius=0)
                self.textbox.pack()
                self.update_incor = CTkButton(master=self, text="Update Incorrect Entries", state='normal',  command=self.update_bad)
                self.update_incor.pack()
                
                for i, x in enumerate(self.data['needs_attention']): 
                    self.textbox.insert("0.0", f"{x}\n")
                self.textbox.insert("0.0", f"---------------------------------------------------------------------------------------------------\n")
                self.textbox.insert("0.0", f"Pl | LastName | FirstName | Age | TEAM | OfficialTime(xx.xx) | Pts(0 if none awarded) | GENDER | AGE_GROUP | Distance | Stroke\n")
                self.textbox.insert("0.0", f"Swim Times needing Correction\n")
            
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
            LOGGER.error("Exception occurred while parsing Meet data: %s \n %s", str(error), traceback.format_exc())
            self.error_loading = CTkLabel(self, text=f"Failed to build out meet data from PDF \n Failure Reason: \n {error}")
            self.error_loading.pack(pady=30)
           
    def show_division_results(self, key):        
        if hasattr(self, 'tabview'):
            self.tabview.destroy()
            
        self.tabview = CTkTabview(master=self.division_result, width=500)
        self.tabview.pack()
        
        
        times_by_event = {}
        
        for x in self.times_by_age_and_gender[key]['individual_race_times']:
            print(x)
            event_key = f"{x.distance}M {x.event_race_type.name}"
            if event_key in times_by_event:
                    times_by_event[event_key].append(x)
            else: 
                    times_by_event[event_key] = [x]
               
        if 'relay_race_times' in self.times_by_age_and_gender[key]:
            for k, g in itertools.groupby(self.times_by_age_and_gender[key]['relay_race_times'], lambda x: f"{x.distance}M {x.event_race_type.name} Relay"):
                    times_by_event[k] = list(g)
        for event in times_by_event.keys():
            tab = self.tabview.add(event) 
            times = times_by_event[event]
            event_label = CTkLabel(tab,font=('helvetica', 24), text="{} - {} times recorded".format(str(event), len(times)))        
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
            for time in times: 
                time_item = treeview.insert("", END, text=str(time), values=time.get_result())
                # CTkLabel(self.resultSection, anchor=W, text=str(time), font=('helvetica', 18), justify='left').pack()
                if isinstance(time, RelaySwimEntry):
                    team_breakdown = self.relay_teams[time.relay_id]
                    # team = f"1) {team_breakdown[0]} 2) {team_breakdown[1]}\n 3) {team_breakdown[2]} 4) {team_breakdown[3]}"
                    treeview.insert(time_item, END, text=f"1) {team_breakdown[0]} 2) {team_breakdown[1]}") 
                    treeview.insert(time_item, END, text=f"3) {team_breakdown[2]} 4) {team_breakdown[3]}") 
                    # CTkLabel(self.resultSection, justify='left', text=team).pack()
                # listbox.insert(tk.END, f"{time.swimmer.name} --- {time.swimmer.age} --- {time.swimmer.team} --- {time.seed_time} --- {time.most_recent_time}") 
    
    def update_bad(self):
        still_wrong = []
        for f in self.textbox.get('4.0', 'end').split('\n'):
            if not f:
                continue
            try:
                entry = f.replace('  ', ' ').split(' ')
                if len(entry) != 11:
                    raise Exception
                official_time = entry[5] # time 
                result = "Finished" if not any(reason in official_time for reason in Utils.skip_reasons) else official_time
                time_in_milis = Utils.convert_time_to_seconds(official_time) if not any(reason in official_time for reason in Utils.skip_reasons) else None
                
                new_entry = IndividualSwimEntry(entry[1],entry[2],entry[3],entry[4],entry[0],entry[6],result,time_in_milis,"",Stroke[entry[10]], entry[8],Gender[entry[7]], int(entry[9]))
                group = f"{new_entry.gender.name}, {new_entry.age_group}"
                if group in self.times_by_age_and_gender:
                    self.times_by_age_and_gender[group]["individual_race_times"].append(new_entry)
                else: 
                    self.times_by_age_and_gender[group] = {
                        "individual_race_times": [new_entry],
                        "relay_race_times": []
                    }               
            except Exception as e:
                print(f"worng {f} cause {e}")
                still_wrong.append(f)
                
        self.textbox.delete('0.0', 'end')
        if(len(still_wrong) > 0):
            for x in still_wrong:
                self.textbox.insert("0.0", f"{x}\n")
            self.textbox.insert("0.0", f"Pl LastName FirstName Age TEAM OfficialTime Pts(0 if none awarded) GENDER AGE_GROUP Distance Stroke\n")
        else:
             self.textbox.insert("0.0", f"All Incorrect Entries Resolved\n")
   
   
    def save_results(self):
        try:                
            LOGGER.info("entering PDFImportWindow.save_results")
            meet_id = str(uuid.uuid1())
            self.meet.record_id = meet_id
            self.dataAccess.add_meet_relation(self.meet.score.keys(), meet_id)
            events_by_id = self.dataAccess.get_all_events()
            swimmers_by_id = self.dataAccess.get_swimmers_for_teams(list(self.meet.score.keys()))
            new_swimmers = []
            aged_swimmers = []
            race_times = []
            relay_teams = []
            for key, value in self.times_by_age_and_gender.items():
                splitKey = key.split(', ')
                gender = Gender[splitKey[0]]
                age_group = splitKey[1]
                times_by_event = {}
                for x in value['individual_race_times']:
                    event_key = (x.distance, x.event_race_type.name)
                    if event_key in times_by_event:
                            times_by_event[event_key].append(x)
                    else: 
                            times_by_event[event_key] = [x]
                print(times_by_event)
                for k in times_by_event.keys():
                    event = RaceEvent(None, Stroke[k[1]], age_group, gender, k[0], False)
                    event_id = list(events_by_id.keys())[list(events_by_id.values()).index(event)] if event in list(events_by_id.values()) else None
                    if not event_id:
                        print(event)
                        event_id = self.dataAccess.create_event(event)
                        events_by_id[event_id] = event
                        
                    for race_entry in list(times_by_event[k]):
                        race_entry: IndividualSwimEntry = race_entry 
                        swimmer = Racer(None,race_entry.racer_fname, race_entry.racer_lname, race_entry.racer_age, race_entry.racer_team, race_entry.gender, False)
                        racer_id = list(swimmers_by_id.keys())[list(swimmers_by_id.values()).index(swimmer)] if swimmer in list(swimmers_by_id.values()) else None
                      
                        
                        # add in swimmer entry
                        if not racer_id:
                            racer_id = str(uuid.uuid1())
                            swimmer.record_id = racer_id
                            swimmers_by_id[racer_id] = swimmer
                            new_swimmers.append(swimmer)
                        else:
                            existing_swimmer = swimmers_by_id[racer_id]
                            if (abs(int(swimmer.age) - int(existing_swimmer.age)) == 1 and int(swimmer.age) > int(existing_swimmer.age)):
                                print(f"updating swimmer age for {swimmer} - {existing_swimmer} ")
                                swimmer.record_id = racer_id
                                swimmers_by_id[racer_id] = swimmer
                                aged_swimmers.append(swimmer)
                        
                        race_times.append(RaceTime(str(uuid.uuid1()), racer_id, event_id, meet_id, race_entry.result, race_entry.time, race_entry.placement, race_entry.points, self.meet.meet_date))
                 
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
                        # create Relay
                        if not relay_id:
                            relay_id = str(uuid.uuid1())
                            relay_racer.record_id = relay_id
                            swimmers_by_id[relay_id] = relay_racer
                            new_swimmers.append(relay_racer)
                        
                        
                        race_id = str(uuid.uuid1())
                        race_times.append(RaceTime(race_id, relay_id, event_id, meet_id, relay_entry.result, relay_entry.time, relay_entry.placement, relay_entry.points, self.meet.meet_date))
                        
                        team_breakdown = self.relay_teams[relay_entry.relay_id]
                        relay_swimmers = []
                        # Saves entry unique entry for specific relay teams and swimmer apart of it 
                        for s in team_breakdown: 
                            s = re.sub("[()]", "",str(s))
                            s_racer = str(s).strip().split(' ')
                            age = s_racer.pop()
                            s_racer_name = ' '.join(s_racer).split(', ')
                            relay_swimmer = Racer(None, str(s_racer_name[1]).strip(), str(s_racer_name[0]).strip(), age, relay_entry.relay_team, race_entry.gender, False)
                            swimmer_id = list(swimmers_by_id.keys())[list(swimmers_by_id.values()).index(relay_swimmer)] if relay_swimmer in list(swimmers_by_id.values()) else None
                            # add swimmers that havent been found
                            if not swimmer_id:
                                swimmer_id = str(uuid.uuid1())
                                relay_swimmer.record_id = swimmer_id
                                swimmers_by_id[swimmer_id] = relay_swimmer
                                new_swimmers.append(relay_swimmer)
                            else:
                                existing_swimmer = swimmers_by_id[swimmer_id]
                                if (abs(int(relay_swimmer.age) - int(existing_swimmer.age)) == 1 and int(relay_swimmer.age) > int(existing_swimmer.age)):
                                    print(f"updating swimmer age for {relay_swimmer} - {existing_swimmer} ")
                                    relay_swimmer.record_id = swimmer_id
                                    swimmers_by_id[swimmer_id] = relay_swimmer
                                    aged_swimmers.append(relay_swimmer)

                            relay_swimmers.append(swimmer_id)
                        if(len(relay_swimmers) == 4):
                            relay_teams.append(RelayTeamBreakDown(str(uuid.uuid1()), race_id, relay_id, relay_swimmers[0],relay_swimmers[1], relay_swimmers[2], relay_swimmers[3]))

            self.dataAccess.create_swimmers(new_swimmers)
            # updating swimmers who have aged up by one 
            self.dataAccess.replace_swimmers(aged_swimmers)
            self.dataAccess.create_race_times(race_times)
            self.dataAccess.create_relay_breakdowns(relay_teams)
            self.dataAccess.create_meet(self.meet)
            self.master.create_teams_list()
            self.destroy()
            
        except Exception as error:
            LOGGER.error("Exception occurred while saving Meet data: %s \n %s", str(error), traceback.format_exc())
            print("Exception occurred while saving Meet data: %s \n %s", str(error), traceback.format_exc())
            self.error_loading = CTkLabel(self.bottom_frame, text=f"Failed to Save Meet Data \n Failure Reason: \n {error}")
            self.error_loading.pack(pady=30)
            self.save_time_button.pack(pady=10)
        finally:
            LOGGER.info("exiting PDFImportWindow.save_results")