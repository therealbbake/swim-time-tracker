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
        self.open_import_window(path)
        
    def open_import_window(self, path):
        print(path)
        self.data = load_race_data(path)
        # Create secondary (or popup) window.
        secondary_window = tk.Toplevel()
        secondary_window.title("Import Times")
        secondary_window.config(width=300, height=200)
        # Create a button to close (destroy) this window.
        times_by_event = {}
        for k, g in itertools.groupby(self.data , lambda x: x.event):
            times_by_event[k] = list(g)
            
        for x, y in times_by_event.items():
            event = tk.Label(secondary_window, text="event: {}".format(str(x)))
            event.pack()
            for time in y:
                time = tk.Label(secondary_window, text=str(time))
                time.pack()
            
            
            
        button_close = tk.Button(
            secondary_window,
            text="Close window",
            command=self.update_times
        )
        button_close.place(x=75, y=75)
        
    def update_times(self):
        update_swim_times(self.data)
        

root = tk.Tk()
root.title("Swim Time Tracker")
root.geometry('500x500')
myapp = App(root)
myapp.mainloop()

backup_db()