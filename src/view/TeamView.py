
from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from db.DataAccess import DataAccess

import traceback

from helpers.Logger import LOGGER

class TeamView(CTkToplevel):
    def __init__(self, team_code, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.geometry("950x550")
        
        self.dataAccess: DataAccess = self.master.dataAccess
        
        LOGGER.info("Entering TeamView for team: %s", team_code)        
        self.title(f'Team: {team_code}')

        self.label = CTkLabel(self, text=f'{team_code}: Individual Swim Points earned')
        self.label.pack(padx=20, pady=20)
        self.times_breakdown = {}
        swimmers_individual_points = self.dataAccess.get_swimmer_points_by_team(team_code)
        self.swimmers_by_age_group = {
            '8&U Boys': [],
            '8&U Girls': [],
            '9-10 Boys': [],
            '9-10 Girls': [],
            '11-12 Boys': [],
            '11-12 Girls': [],
            '13-14 Boys': [],
            '13-14 Girls': [],
            '15-18 Boys': [],
            '15-18 Girls': [],
        }
        for swimmer in swimmers_individual_points: 
            age = int(swimmer[1])
            gen = swimmer[2]
            swimmer = {
                'name': swimmer[0],
                'points': swimmer[3],
            }
            if gen == "BOYS": 
                gender = "Boys" 
            else:
                gender = "Girls"
            
            if age <= 8: 
                self.swimmers_by_age_group[f'8&U {gender}'].append(swimmer)
            elif age <= 10:
                self.swimmers_by_age_group[f'9-10 {gender}'].append(swimmer)
            elif age <= 12:
                self.swimmers_by_age_group[f'11-12 {gender}'].append(swimmer)
            elif age <= 14:
                self.swimmers_by_age_group[f'13-14 {gender}'].append(swimmer)
            else:
                self.swimmers_by_age_group[f'15-18 {gender}'].append(swimmer)
            
        self.swimmer_results = CTkFrame(self, width=800, height=500, fg_color="transparent")
        self.swimmer_results.pack()
        self.show_point_breakdown()
    
    def show_point_breakdown(self):
        try: 
            if hasattr(self, 'tabview'):
                self.tabview.destroy()
                
            self.tabview = CTkTabview(master=self.swimmer_results, width=500)
            self.tabview.pack()
            
            for group in self.swimmers_by_age_group.keys():
                swimmers: list = self.swimmers_by_age_group[group]
                tab = self.tabview.add(str(group)) 
                
                columns = ['Swimmer Name', 'Point Total']
                
                treeview = ttk.Treeview(tab, height=12, show='tree', displaycolumns='', columns=columns)
                treeview.pack(side=LEFT, ipadx=200, ipady=20)

                # create CTk scrollbar
                ctk_textbox_scrollbar = CTkScrollbar(tab, command=treeview.yview)
                ctk_textbox_scrollbar.pack(side=RIGHT)
                treeview.configure(yscrollcommand=ctk_textbox_scrollbar.set)
                swimmers.sort(key=lambda x: x['points'], reverse=True)
                s: dict
                for s in swimmers: 
                    treeview.insert("", END, text=f"{s['name']} --- {s['points']}", values=s.values())
        except Exception as e:
            LOGGER.error("Exception occurred while rendering Team results: %s \n %s", str(e), traceback.format_exc())