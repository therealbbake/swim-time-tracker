from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from db.DataAccess import DataAccess
from view.SwimmerProfile import SwimmerProfile
from helpers.Logger import LOGGER
class SwimmerSearch(CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        LOGGER.info("Entering SwimmerSearch")
        self.bind("<<TreeviewSelect>>", self.handleSwimmerSelect)
        self.dataAccess: DataAccess = self.master.dataAccess
        
        self.swimmer_profile = None
        # self.handle_swimmer_search = handle_swimmer_search
        self.geometry("950x550")
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
        if hasattr(self, 'search_result'):
            self.search_result.destroy()
        
        
        self.search_result = CTkFrame(self, width=800, height=500, fg_color="transparent")
        self.search_result.pack()
        search_params = {
            'first_name': self.first_name_entry.get(), 
            'last_name': self.last_name_entry.get(), 
            'team': self.team_value.get(), 
            'age': self.age_value.get(), 
            'gender': self.gender_value.get()
        }
        swimmer_results = self.dataAccess.get_swimmers_by_query(search_params)
        
        event_label = CTkLabel(self.search_result,font=('helvetica', 24), text="Search Results")        
        event_label.pack(side=TOP)
        columns = ['Racer']

        self.treeview = ttk.Treeview(self.search_result, height=12, show='tree', displaycolumns='', columns=columns, selectmode='browse')
        self.treeview.pack(side=LEFT, ipadx=200, ipady=20)

        # create CTk scrollbar
        ctk_textbox_scrollbar = CTkScrollbar(self.search_result, command=self.treeview.yview)
        ctk_textbox_scrollbar.pack(side=RIGHT)
        self.treeview.configure(yscrollcommand=ctk_textbox_scrollbar.set)
        racer: Racer
        for racer in swimmer_results: 
            racer_item = self.treeview.insert("", END, text=racer, values=racer.get_db_row())
    

    def handleSwimmerSelect(self, arg):
        vals = self.treeview.item(self.treeview.focus())['values']
        selected_swimmer = Racer(vals[0],vals[1],vals[2],vals[3],vals[4],vals[5],vals[6])
        if self.swimmer_profile is None or not self.swimmer_profile.winfo_exists():
            self.swimmer_profile = SwimmerProfile(swimmer=selected_swimmer)  # create window if its None or destroyed
        else:
            self.swimmer_profile.focus()  # if window exists focus it   

    
    def callback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
