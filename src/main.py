from customtkinter import *
from tkinter import *
from tkinter import ttk
from models.mod import *
from view.SwimmerSearch import SwimmerSearch
from view.PDFImportWindow import PDFImport
from view.TeamView import TeamView
from db.DataAccess import DataAccess
import helpers.Exporter as Exporter
from helpers.Logger import LOGGER

# Sets the appearance mode of the application
# "System" sets the appearance same as that of the system
set_appearance_mode("System")        
 
# Sets the color of the widgets
# Supported themes: green, dark-blue, blue
set_default_color_theme("green")    

class App(CTk):
    def shutdown(self):
        self.dataAccess.close_connection()
    
    def __init__(self):
        super().__init__()
        self.dataAccess = DataAccess()
        self.geometry("600x500")
        self.title("Swim Time Tracker")
        # self.iconbitmap('src/resources/swimmer.ico')
        LOGGER.info("Swim track starting up!")
        # add widgets to app
        
        self.header = CTkFrame(self, fg_color="transparent")
        self.header.pack(side=TOP)
        self.welcome = CTkLabel(self.header , text="Welcome to Swim Time Tracker")
        self.welcome.pack(side=LEFT, padx=100, pady=10)
        self.options = CTkButton(self.header ,text='Swimmer Lookup', command=self.open_toplevel )
        self.options.pack(side=LEFT, pady=10)
        
        
        # team_names
        self.teams = CTkFrame(self, fg_color="transparent")
        self.teams.pack(side=LEFT)
        
        self.team_buttons = []
        self.create_teams_list() 

        
        
        
        # bottom section
        self.section2 = CTkFrame(self, fg_color="transparent")
        self.section2.pack(side=BOTTOM)
        self.import_button = CTkButton(self.section2 , text="Import", command=self.import_file)
        self.export_button = CTkButton(self.section2 , text="Export", command=self.export_data)
        self.import_button.pack(side=LEFT, padx=15, pady=5)
        self.export_button.pack(side=RIGHT, padx=15, pady=5)

        self.team_profile = None
        self.swimmer_lookup_window = None
        self.import_window = None
        
    
        ###Treeview Customisation (theme colors are selected)
        bg_color = self._apply_appearance_mode(ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(ThemeManager.theme["CTkButton"]["fg_color"])
        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", background="transparent", foreground=text_color, fieldbackground=bg_color, borderwidth=0)
        treestyle.map('Treeview', background=[('selected', "transparent")], foreground=[('selected', selected_color)])
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())
        
        
        
        
    def create_teams_list(self):
        t: CTkButton
        for t in self.team_buttons:
            t.destroy()
            
        for team in self.dataAccess.get_swim_teams():
            def open_team_window(x = team):
                self.team_button(x)
            # () => team_button(team) 
            team_button = CTkButton(self.teams, text=team, command=open_team_window )
            team_button.pack(pady=5)
            self.team_buttons.append(team_button)
        
        

    def team_button(self, value):
        if self.team_profile is None or not self.team_profile.winfo_exists():
            self.team_profile = TeamView(team_code=value)  # create window if its None or destroyed
        else:
            self.team_profile.destroy()  # if window exists focus it   
            self.team_profile = TeamView(team_code=value)  # create window if its None or destroyed
            
            
    # add methods to app
    def export_data(self):
        path = filedialog.askdirectory()
        Exporter.export_all_swimdata(self.dataAccess, path)

    def open_toplevel(self):
        if self.swimmer_lookup_window is None or not self.swimmer_lookup_window.winfo_exists():
            self.swimmer_lookup_window = SwimmerSearch(self)  # create window if its None or destroyed
        else:
            self.swimmer_lookup_window.focus()  # if window exists focus it   

    # TODO add for CSV support
    def import_file(self):
        if self.import_window is None or not self.import_window.winfo_exists():
            self.import_path = filedialog.askopenfilename(title="Select a file", filetypes=[("pdf files", "*.pdf")])
            
            if '.pdf' in self.import_path: 
                self.import_window = PDFImport(self)
            # else:
            #     self.import_window = PDFImportWindow(self)
            # self.data = PDFParser.load_race_data(path) else csv.load_race_data(path)
        else:
            self.import_window.focus()  # if window exists focus it   


app = App()
app.mainloop()
app.shutdown()
