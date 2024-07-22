# import the python pandas package
import pandas as pd
from db.dataAccess import retrieve_all
from pathlib import Path
import datetime
import xlsxwriter

def build_table_header(initial_column, worksheet):
    row = 1 
    col = initial_column
    columns = ["Name", "Age", "Team", "Seed Time", "Seed Date", "Last Official Time", "Last Official Time Date"]
    for h in columns:
        worksheet.write(row, col, h)
        col += 1



def export_swim_times(path, swim_times):
    
    # Create a workbook and add a worksheet.
        
    date = datetime.datetime.now()
    data_folder = Path(path)
    file_to_save = data_folder / f"Swim_Results_{date.year}_{date.month}_{date.day}.xlsx"
    workbook = xlsxwriter.Workbook(file_to_save)
    cell_format = workbook.add_format({'bold': True, 'font_color': 'blue'})
    times_by_age_and_gender = {}
    for x in swim_times:
        group = f"{x.event.gender}, {x.event.age_group}"
        if group in times_by_age_and_gender:
            times_by_age_and_gender[group].append(x)
        else: 
            times_by_age_and_gender[group] = [x]
        
        
    # for k, g in itertools.groupby(swim_times , lambda x: x.event):
    #     times_by_age_and_gender.append((k, list(g)))
    print(times_by_age_and_gender.keys())

    for gender_age_times in times_by_age_and_gender:
        print(gender_age_times)
        worksheet = workbook.add_worksheet(str(gender_age_times))
        # columns = ["Name", "Age", "Team", "Seed Time", "Seed Date", "Last Official Time", "Last Official Time Date"]
        times = times_by_age_and_gender[gender_age_times]
        times_by_races = {}
        
        for s in times: 
            race = str(s.event.race)
            if race in times_by_races:
                times_by_races[race].append(s)
            else: 
                times_by_races[race] = [s]
                
        print(times_by_races.keys())
                
        initial_column = 0
        for race in times_by_races:
            worksheet.merge_range(0,initial_column, 0, initial_column+7, str(race)) # title for Race
            build_table_header(initial_column, worksheet) # header for time Data
            row = 2
            for time in times_by_races[race]: 
                for index, rowData in enumerate(time.get_excel_row()):
                    if time.racer.team == "HOW": #special format for Hills of Walden 
                        worksheet.write(row, initial_column+index, rowData, cell_format)  # time entries
                    else:
                        worksheet.write(row, initial_column+index, rowData)  # time entries
                row += 1                     

            initial_column += 9
            
    workbook.close()


    
    