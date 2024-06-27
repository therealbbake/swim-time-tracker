# import tkinter as tk

import tkinter as tk
from tkinter import filedialog
from main import load_race_data, update_swim_times, backup_db
import itertools

def open_secondary_window():
    # Create secondary (or popup) window.
    secondary_window = tk.Toplevel()
    secondary_window.title("Secondary Window")
    secondary_window.config(width=300, height=200)
    # Create a button to close (destroy) this window.
    button_close = tk.Button(
        secondary_window,
        text="Close window",
        command=secondary_window.destroy
    )
    button_close.place(x=75, y=75)
    




class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

    
        self.file_path = tk.Label(text="No File Selected")
        self.file_path.pack()
        self.import_button = tk.Button(root, text="Import File", command=self.import_file)
        self.import_button.pack()

        
        
        # self.load_times_button = tk.Button(root, text="Submit", command=self.load_swim_times)
        # self.load_times_button.pack(pady=25)
        
        # This will create a LabelFrame
        # export_frame = tk.LabelFrame(root, text='Export Swim Data')
        # self.frame = export_frame.pack(expand='yes', fill='both')
        # chkbtn1 = tk.Checkbutton(self.frame, text='Checkbutton 1')
        # chkbtn1.place(x=30, y=50)
        # chkbtn2 = tk.Checkbutton(self.frame, text='Checkbutton 2')
        # chkbtn2.place(x=30, y=80)
        # export_time_button = tk.Button(self.frame, text="Export", command=open_secondary_window)
        # export_time_button.place(x=30, y=100)
        
        
    def import_file(self):
        path = filedialog.askopenfilename(title="Select a file", filetypes=[("pdf files", "*.pdf"), ("cvs files", "*.csv*")])
        
        self.file_path.config(text = path.split('/').pop())
        data = load_race_data(path)
        self.times_by_event = []
        for k, g in itertools.groupby(data , lambda x: x.event):
           self.times_by_event.append((k, list(g)))
        self.open_import_window()
        
    def open_import_window(self):
        # Create secondary (or popup) window.
        secondary_window = tk.Toplevel()
        secondary_window.title("Import Times")
        secondary_window.geometry('450x400')
        
        # Create a button to close (destroy) this window            
        x = self.times_by_event[0]
        
        event = tk.Label(secondary_window, text="{} - {} times recorded".format(str(x[0]), len(x[1])))
        event.grid(row=0, column=0, columnspan=4)
        yScroll = tk.Scrollbar(secondary_window, orient=tk.VERTICAL)
        yScroll.grid(row=1, column=2, sticky=tk.N+tk.S)
        listbox = tk.Listbox(secondary_window, width=65, height=20,
            yscrollcommand=yScroll.set)
        listbox.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        yScroll.config(command = listbox.yview) 
        
        # Insert elements into the listbox'
        # listbox.insert(tk.END, "Name --- Age --- Team --- Seed --- Official") 
        for time in x[1]: 
             listbox.insert(tk.END, str(time))
            # listbox.insert(tk.END, f"{time.swimmer.name} --- {time.swimmer.age} --- {time.swimmer.team} --- {time.seed_time} --- {time.most_recent_time}") 
        
            
            
        button_close = tk.Button(
            secondary_window,
            text="upload",
            command=self.update_times
        )
        button_close.grid(row=5,column=1)
        
    def update_times(self):
        self.times_by_event.pop(0)
        

root = tk.Tk()
root.title("Swim Time Tracker")
root.geometry('500x500')
myapp = App(root)
myapp.mainloop()

backup_db()