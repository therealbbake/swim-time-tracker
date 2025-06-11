
import xlsxwriter.worksheet
from db.DataAccess import DataAccess
from models.mod import *
import helpers.Utility as util
import itertools
import pandas as pd
from pathlib import Path
from datetime import datetime
import xlsxwriter

    
    


def build_table_header(initial_column, worksheet: xlsxwriter.worksheet):
    row = 1 
    col = initial_column
    columns = ["Name", "Age", "Team", "Last Official Time", "Last Official Time Date", "Seed Time", "Seed Date",]
    for h in columns:
        worksheet.write(row, col, h)
        col += 1

def export_all_swimdata(dataAccess: DataAccess, path):
    events_by_id: dict = dataAccess.get_all_events()
    
    date = datetime.now()
    data_folder = Path(path)
    file_to_save = data_folder / f"Swim_Results_{date.year}_{date.month}_{date.day}.xlsx"
    workbook = xlsxwriter.Workbook(file_to_save)

    cell_format = workbook.add_format({'bold': True, 'font_color': 'blue'})
    for k, g in itertools.groupby(events_by_id.values(), lambda x: f"({x.age_group}) {x.gender.name}"):
        worksheet = workbook.add_worksheet(k)
        event: RaceEvent
        
        
        initial_column = 0
        for event in list(g):
            event_results = dataAccess.get_swimmer_result_by_event(event.record_id)
            
            
            worksheet.merge_range(0,initial_column, 0, initial_column+7, str(event)) # title for Race
            build_table_header(initial_column, worksheet) # header for time Data
            row = 2
            for time in event_results: 
                for index, rowData in enumerate(time):
                    value = rowData
                    if index == 3 or index == 5: 
                        value = util.format_time(rowData)
                    elif index == 4 or index == 6:
                        value = datetime.fromtimestamp(int(rowData)/ 1000).strftime('%m/%d/%Y')
                    
                    if time[2] == "HOW": #special format for Hills of Walden // change to allow user to pick team to highlight 
                        worksheet.write(row, initial_column+index, value, cell_format)  # time entries
                    else:
                        worksheet.write(row, initial_column+index, value)  # time entries
                row += 1                     

            initial_column += 9
    
    workbook.close()