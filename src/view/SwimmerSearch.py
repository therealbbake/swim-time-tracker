from customtkinter import *
from tkinter import *
from models.mod import *
from db.db import DataAccess

class SwimmerSearch(CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataAccess: DataAccess = self.master.dataAccess
        # self.handle_swimmer_search = handle_swimmer_search
        self.geometry("500x300")
        self.title("Swimmer Lookup")
        self.name_frame = CTkFrame(self, fg_color="transparent")
        self.name_frame.pack(side=TOP)
        self.first_name = CTkLabel(self.name_frame, text="First Name")
        self.first_name.pack(side=LEFT, padx=10)
        self.first_name_entry = CTkEntry(self.name_frame )
        self.first_name_entry.pack(side=LEFT, pady=10)
        self.last_name = CTkLabel(self.name_frame , text="Last Name")
        self.last_name.pack(side=LEFT, padx=10, pady=10)
        self.last_name_entry = CTkEntry(self.name_frame )
        self.last_name_entry.pack(side=LEFT)
        
        self.age_team_frame = CTkFrame(self, fg_color="transparent")
        self.age_team_frame.pack(side=TOP)
        self.age = CTkLabel(self.age_team_frame , text="Age")
        self.age.pack(side=LEFT, padx=5, pady=10)
        self.age_value = StringVar(value="")
        self.age_entry = CTkComboBox(self.age_team_frame, variable=self.age_value, values=['4','5','6','7','8','9','10','11','12','13','14','15','16','17','18'])
        self.age_entry.pack(side=LEFT, pady=10)
        self.team = CTkLabel(self.age_team_frame , text="Team")
        self.team.pack(side=LEFT, padx=5, pady=10)
        self.team_value = StringVar(value="")
        self.team_entry = CTkComboBox(self.age_team_frame, variable=self.team_value, values=team_names)
        self.team_entry.pack(side=LEFT)
        self.gender = CTkLabel(self.age_team_frame , text="Gender")
        self.gender.pack(side=LEFT, padx=5, pady=10)
        self.gender_value = StringVar(value="")
        self.gender_entry = CTkComboBox(self.age_team_frame, variable=self.gender_value, values=[Gender.BOYS.name, Gender.GIRLS.name])
        self.gender_entry.pack(side=LEFT)
        self.search_button = CTkButton(self, text="Search", command=self.search_swimmer )
        self.search_button.pack(pady=30)
        
        
        
        
        
    
    def search_swimmer(self):
        
        search_params = {
            'first_name': self.first_name_entry.get(), 
            'last_name': self.last_name_entry.get(), 
            'team': self.team_value.get(), 
            'age': self.age_value.get(), 
            'gender': self.gender_value.get()
        }
        swimmer_results = self.dataAccess.get_swimmers_by_query(search_params)
        
        
        
        
        
        
        # self.master.handle_swimmer_search("Bryan", "Baker")
        # self.destroy()
        
    def callback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
