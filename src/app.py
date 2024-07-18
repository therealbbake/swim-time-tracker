# import tkinter as tk

import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog
from db.dataAccess import update_swim_times, backup_db, retrieve_row_count, retrieve_all
import helpers.pfd_parser  as pdf
import helpers.csv_parser  as csv
from helpers.xlxs_export import export_swim_times
import itertools

import sys; print(sys.executable)





class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        db_count = retrieve_row_count()
        self.welcome = tk.Label(root, text="Swim Time Tracker")
        self.file_path = tk.Label(root, text="No File Selected")
        self.file_path.pack()
        self.import_button = tk.Button(root, text="Import File", command=self.import_file)
        self.import_button.pack()
        self.export_time_button = tk.Button(root, text=f"Export {db_count} times", command=self.export_file)
        self.export_time_button.pack()
        
        
        # self.load_times_button = tk.Button(root, text="Submit", command=self.load_swim_times)
        # self.load_times_button.pack(pady=25)
        
        # This will create a LabelFrame
        self.meet_info = tk.LabelFrame(root)
        
        self.meet_date = tk.Label(self.meet_info, text="Date: ")
        self.meet_date.pack()
        self.save_time_button = tk.Button(self.meet_info, text="Save Event Data", command=self.save_data)
        self.save_time_button.pack()
 
    def export_file(self):
        path = filedialog.askdirectory()
        swim_times = retrieve_all()
        export_swim_times(path, swim_times)

    def save_data(self):
        update_swim_times(self.race_times)
        updated_db_count = retrieve_row_count()
        self.export_time_button.config(text = f"Export {updated_db_count} times")
        
    def import_file(self):
        path = filedialog.askopenfilename(title="Select a file", filetypes=[("pdf files", "*.pdf"), ("cvs files", "*.csv")])

        self.file_path.config(text = path.split('/').pop())
        
        data = pdf.load_race_data(path) if '.pdf' in path else csv.load_race_data(path)
        self.race_times = data['times']
        self.meet_info.config(text = data['meet_info'])
        self.meet_info.place(x=100, y=100)
        self.meet_info.pack(expand='yes', fill='both')
        self.meet_date.config(text = f"Event Date: {data['date']}")
        
        self.times_by_age_and_gender = {}
        for x in data['times']:
            print(x)
            group = f"{x.event.gender}, {x.event.age_group}"
            if group in self.times_by_age_and_gender:
                self.times_by_age_and_gender[group].append(x)
            else: 
                self.times_by_age_and_gender[group] = [x]
        for key in self.times_by_age_and_gender:
            def open_results(x = key):
                self.open_import_window(x)
                
            ttk.Button(self.meet_info, text=f"{key} Results", command=open_results ).pack()
            
        # self.times_by_event = []
        # for k, g in itertools.groupby(data['times'] , lambda x: x.event):
        #    self.times_by_event.append((k, list(g)))
        # self.event_count.config(text = f"Events Found: {len(self.times_by_event)}")
        
    #     {
    #     "meet_info": meet_info,
    #     "times": race_times,
    #     "date": meet_date,
    # }\
        
    def open_import_window(self, key):
        # Create secondary (or popup) window.
        secondary_window = tk.Toplevel()
        secondary_window.title("Import Times")
        secondary_window.geometry('450x400')
        
        tabControl = ttk.Notebook(secondary_window) 
        times_by_event = []
        for k, g in itertools.groupby(self.times_by_age_and_gender[key], lambda x: x.event):
                times_by_event.append((k, list(g)))
  
        for event in times_by_event:
            tab = tk.Frame(tabControl)
            tabControl.add(tab, text =event[0].race) 
            event_label = tk.Label(tab, text="{} - {} times recorded".format(str(event[0].race), len(event[1])))        
            event_label.grid(row=0, column=0, columnspan=4)
            yScroll = tk.Scrollbar(tab, orient=tk.VERTICAL)
            yScroll.grid(row=1, column=2, sticky=tk.N+tk.S)
            listbox = tk.Listbox(tab, width=65, height=20,
                yscrollcommand=yScroll.set)
            listbox.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
            yScroll.config(command = listbox.yview) 
            # Insert elements into the listbox'
            # listbox.insert(tk.END, "Name --- Age --- Team --- Seed --- Official") 
            for time in event[1]: 
                listbox.insert(tk.END, str(time))
                # listbox.insert(tk.END, f"{time.swimmer.name} --- {time.swimmer.age} --- {time.swimmer.team} --- {time.seed_time} --- {time.most_recent_time}") 
            
        
        tabControl.pack(expand = 1, fill ="both")   
        # tab2 = ttk.Frame(tabControl) 
        
        # tabControl.add(tab2, text ='Tab 2') 
        # tabControl.pack(expand = 1, fill ="both") 
        
        # ttk.Label(tab1,  
        #         text ="Welcome to \ 
        #         GeeksForGeeks").grid(column = 0,  
        #                             row = 0, 
        #                             padx = 30, 
        #                             pady = 30)   
        # ttk.Label(tab2, 
        #         text ="Lets dive into the\ 
        #         world of computers").grid(column = 0, 
        #                                     row = 0,  
        #                                     padx = 30, 
        #                                     pady = 30) 

        
       
            
            
        # button_close = tk.Button(
        #     secondary_window,
        #     text="upload",
        #     command=self.update_times
        # )
        # button_close.grid(row=5,column=1)
        
    def update_times(self):
        self.times_by_event.pop(0)
        

root = tk.Tk()
root.title("Swim Time Tracker")
root.geometry('500x500')
myapp = App(root)
myapp.mainloop()

backup_db()