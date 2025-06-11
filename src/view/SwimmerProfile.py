

from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from db.DataAccess import DataAccess
from helpers.Logger import LOGGER


class SwimmerProfile(CTkToplevel):
    def __init__(self, swimmer: Racer, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.geometry("950x550")
        
        self.dataAccess: DataAccess = self.master.dataAccess
        
        LOGGER.info("Entering SwimmerProfile for swimmer: %s", swimmer.record_id)        
        self.title(f'Swimmer Profile for {swimmer}')

        self.label = CTkLabel(self, text=f'{swimmer.first_name} {swimmer.last_name}')
        self.label.pack(padx=20, pady=20)

        self.relay_label = CTkLabel(self, text=f'Relay Reams')
        self.relay_label.pack(padx=20, pady=20)
        # associated_relays = self.dataAccess.get_relay_teams_for_swimmer(swimmer_id=swimmer.record_id)
        self.times_breakdown = {}
        times = self.dataAccess.get_times_for_swimmer(swimmer_id=swimmer.record_id)
        t: RaceTime
        for t in times: 
            if t.event_id in self.times_breakdown: 
                self.times_breakdown[t.event_id]['event_times'].append(t)
            else: 
                event = self.dataAccess.get_event_by_id(t.event_id)
                self.times_breakdown[t.event_id] = {
                    'event': event,
                    'event_times': [t],
                }
            
        self.swimmer_results = CTkFrame(self, width=800, height=500, fg_color="transparent")
        self.swimmer_results.pack()
        self.show_division_results()
    
    def show_division_results(self):
        try: 
            if hasattr(self, 'tabview'):
                self.tabview.destroy()
                
            self.tabview = CTkTabview(master=self.swimmer_results, width=500)
            self.tabview.pack()
            
            for breakdown in self.times_breakdown.values():
                event: RaceEvent = breakdown['event']
                tab = self.tabview.add(str(event)) 
                
                points_earned = sum([t.points_scored for t in breakdown['event_times']])
                event_label = CTkLabel(tab,font=('helvetica', 24), text="{} times recorded and {} points scored".format(len(breakdown['event_times']), points_earned))        
                event_label.pack(side=TOP)
                times_by_results= breakdown['event_times']
                times_by_results.sort(key=lambda x: x.result_time, reverse=False)
                best_time: RaceTime = times_by_results[0] if len(times_by_results) > 0 else ''
                best_label = CTkLabel(tab,font=('helvetica', 24), text=str(best_time))   
                best_label.pack(side=TOP)
                # Insert elements into the listbox'
                # listbox.insert(tk.END, "Name --- Age --- Team --- Seed --- Official") 
                columns = ['Pl', 'Racer', 'Result', 'Points']
                
                treeview = ttk.Treeview(tab, height=12, show='tree', displaycolumns='', columns=columns)
                treeview.pack(side=LEFT, ipadx=200, ipady=20)

                # create CTk scrollbar
                ctk_textbox_scrollbar = CTkScrollbar(tab, command=treeview.yview)
                ctk_textbox_scrollbar.pack(side=RIGHT)
                treeview.configure(yscrollcommand=ctk_textbox_scrollbar.set)
                times_by_date = breakdown['event_times']
                times_by_date.sort(key=lambda x: x.date, reverse=True)
                time: RaceTime
                for time in times_by_date: 
                    treeview.insert("", END, text=str(time), values=time.result_time)
        except Exception as e:
            LOGGER.error("Exception occurred while rendering swimmer results: %s", str(e))