
import pypdfium2 as pdfium
import uuid 
import helpers.Utility as Utils
from models.mod import *
from datetime import datetime
from db.DataAccess import DataAccess
import traceback
from helpers.Logger import LOGGER

def process_individual_swimmer(swimmer_time, containsSeedTime, meet_date, race_type, age_group, gender, distance, score, isConference):
    placement = swimmer_time.pop(0) # remove placement
    if(not (placement == 'X' or placement == '--' or placement.isnumeric())):
        return None
    points = 0
            
    if isConference and int(placement) == 1:
        points = 9
    elif isConference:
        points = 9 - int(placement) if placement.isnumeric() and int(placement) < 9 else 0
    elif(placement.isnumeric() and int(placement) < 7):
        points = int(swimmer_time.pop())
        
    official_time = swimmer_time.pop().strip() # grab official time
    seed_time = swimmer_time.pop().strip() if containsSeedTime else None
    team = swimmer_time.pop()
    age = swimmer_time.pop()
    full_name = ' '.join(swimmer_time)
    # create new Swimmer Event time entry 
    name_arr = full_name.split(',') 
    result = "Finished" if not any(reason in official_time for reason in Utils.skip_reasons) else official_time
    time_in_milis = Utils.convert_time_to_seconds(official_time) if not any(reason in official_time for reason in Utils.skip_reasons) else None

            
    swim_entry = IndividualSwimEntry(
        name_arr[1].strip(), #first_name
        name_arr[0].strip(), #last_name
        age, 
        team, 
        placement, 
        points, 
        result, 
        time_in_milis, 
        meet_date, 
        race_type, 
        age_group, 
        gender, 
        distance)
        
    if team in score: 
        score[team] += points
    else:
        score[team] = points
    return swim_entry


def parse_conference_PDF(pages):
    LOGGER.info("Entering PDFParser.parse_conference_PDF")  
    database = DataAccess()
    try:
        meet_date = ''
        meet_info = ''
        score = {}
        individual_race_times = []
        relay_race_times = []
        relay_teams={}
        partial_swimmer_time = [] # for building out swimmers that take up multiple lines
        for page in pages: 
            textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None, errors='ignore')
            page_lines = textpage.split('\n')
            # retieve data of the meet
            title = page_lines.pop(0).split(' ')
            date = title[len(title) - 3].split('/')
            meet_date = datetime(int(date[2]), int(date[0]), int(date[1]))
            # remove unneeded lines
            meet_info = ' '.join(page_lines.pop(0).split(' ')[:4])
            page_lines.pop(0)
            page_lines.pop(0)
            # loop through pages
            for x in page_lines:
                x = x.strip('\n').strip('\r')
                if(x.startswith('#')): # retrieves Event Data
                    is_relay = 'Relay' in x
                    race_info = x.split(' ')
                    race_info.pop(0) #remove race info 
                    gender = get_gender(race_info.pop(0))
                    if "8 & Under" not in x: 
                        age_group = race_info.pop(0)  
                    else: 
                        age_group = '8&U'
                        del race_info[:3]
                        
                    distance = Utils.get_race_distance(race_info.pop(0))
                    race_type = get_race_type(race_info)
                elif('Preliminaries' in x or 'Final' in x or 'Team' in x or 'Swim-Off' in x or 'Swim-off' in x or '(#' in x ): # un needed lines
                    continue
                elif(is_relay):
                    swimmer_time = x.split(' ')
                    if(not (swimmer_time[0] == 'X' or swimmer_time[0] == '--'  or swimmer_time[0] == '---' or swimmer_time[0].isnumeric())):

                        swimmer_name = ''
                        for s in swimmer_time:
                            if s.isnumeric():
                                swimmer_name += f" {s}" 
                                relay_teams[current_relay_id].append(swimmer_name)
                                swimmer_name = ''
                            elif any(char.isdigit() for char in s):
                                age = ''
                                next_name = ''
                                for char in s:
                                    if char.isdigit():
                                        age += char
                                    else:
                                        next_name += char   
                                swimmer_name += f" {age}" 
                                relay_teams[current_relay_id].append(swimmer_name.strip())
                                swimmer_name = f'{next_name}'
                            else:
                                swimmer_name += f" {s}"                    
                        continue
                        
                    
                    placement = swimmer_time.pop(0) # remove placement
                    points = 0 
                    if placement.isnumeric() and int(placement) < 9:
                        points = 9 - int(placement) if int(placement) > 1 else 9
                    time = swimmer_time.pop().strip() # grab official time
                    group = swimmer_time.pop()
                    team = swimmer_time.pop()
                    result = "Finished" if not any(reason in time for reason in Utils.skip_reasons) else time
                    time_in_milis = Utils.convert_time_to_seconds(time) if not any(reason in time for reason in Utils.skip_reasons) else None
                    current_relay_id = str(uuid.uuid1())
                    relay_teams[current_relay_id] = []
                    swim_entry = RelaySwimEntry(current_relay_id, group, team, placement,points,result, time_in_milis, meet_date, race_type, age_group, gender, distance)
                    
                    if team in score: 
                        score[team] += points
                    else:
                        score[team] = points
                    relay_race_times.append(swim_entry)
                else:
                    
                    swimmer_time = x.split(' ')
                    if (len(swimmer_time) < 5):
                        # logic to combine times that come on multiple lines
                        if( swimmer_time[0] not in partial_swimmer_time[1:]):
                            partial_swimmer_time.extend(swimmer_time)
                        if(len(partial_swimmer_time) > 5):
                            swim_entry = process_individual_swimmer(partial_swimmer_time, False, meet_date, race_type, age_group, gender, distance, score, True)
                            partial_swimmer_time = []
                    else:
                        swim_entry = process_individual_swimmer(swimmer_time, False, meet_date, race_type, age_group, gender, distance, score, True)
                    if swim_entry: 
                        individual_race_times.append(swim_entry)
                    
        meet_id = database.get_meet_id(str(meet_info), meet_date.timestamp())
        meet = Meet(
            meet_id,
            meet_date, 
            str(meet_info), 
            score
        )   
        
        return {
            "isAlreadySaved": meet.record_id != None,
            "meet": meet,
            "individual_race_times": individual_race_times, 
            "relay_race_times": relay_race_times,
            "relay_teams": relay_teams
        }
    except Exception as e:
        LOGGER.error("Error occurred in PDFParser.parse_conference_PDF: %s", str(e))
    finally:
        database.close_connection()
        LOGGER.info("Exiting PDFParser.parse_conference_PDF")  



def parse_meet_PDF(pages):
    
    LOGGER.info("Entering PDFParser.parse_meet_PDF")  
    database = DataAccess()
    try:
        individual_race_times = []
        relay_race_times = []
        partial_swimmer_time = [] # for building out swimmers that take up multiple lines
        meet_date = None
        meet_info = None
        score = {}
        relay_teams = {}
        isTimeSection = False
        containsSeedTime = False
        containsAchievements = False
        meet_info_retrieved = False
        current_swimmer_entry = {
                        'placement': None,
                        'possible_name': [],
                        'age': None,
                        'Team': None,
                        'seed': None,
                        'official': None,
                        'points': None,

                    }
        failed_to_read = []
        # columnsIndex = {}
        # columnsize = 0
        is_relay=False
        current_relay_id=''
        for page in pages: 
            textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None)
           
            page_lines = textpage.split('\n')
            
            for x in page_lines:
                x = x.strip('\n').strip('\r')
                print(x)
                if('Pl' in x and 'Pts' in x):
                    containsAchievements = 'Achv' in x
                    # columnsIndex = {}
                    # for i, c in enumerate(columns):
                    #     columnsIndex[c] = i
                    isTimeSection = True
                    containsSeedTime = 'Seed' in x
                    continue
                if('Maestro' in x or 'DQ:' in x or 'swimtopia' in x): # un needed lines
                    continue
                if('Team' in x and 'Scores' in x):
                    isTimeSection = False
                    continue
                if('Results' in x):
                    if (not meet_info_retrieved):
                        x.replace('Results' , '')
                        
                        if '-' in x: line_split = x.split('-') 
                        else: line_split = x.split('—')
                        meet_info = line_split[0]
                        date_split = line_split[1].split(' ')
                        del date_split[-4:]
                        month = date_split[1]
                        day = date_split[2].strip(',')
                        year = date_split[3]
                        meet_date = datetime.strptime(f"{month} {day}, {year}", '%b %d, %Y')
                        meet_info_retrieved = True
                elif(x.startswith('#')): # retrieves Event Data
                    is_relay = 'Relay' in x
                    
                    race_info = x.split(' ')
                    race_info.pop(0) #remove race info 
                    gender: Gender = get_gender(race_info.pop(0))
                    if "8 & Under" not in x: 
                        age_group = race_info.pop(0)  
                    else: 
                        age_group = '8&U'
                        del race_info[:3]
                        
                    distance = Utils.get_race_distance(race_info.pop(0))
                    race_type: Stroke = get_race_type(race_info)
                    isTimeSection = False
                    current_swimmer_entry = {
                                'placement': None,
                                'possible_name': [],
                                'age': None,
                                'Team': None,
                                'seed': None,
                                'official': None,
                                'points': None,
                            }
                elif(is_relay and isTimeSection):
                    swimmer_time = x.split(' ')
                    if(swimmer_time[0] == '1)' or swimmer_time[0] == '3)'):
                        swimmer_time.pop(0) # remove the order
                        swimmer_name = ''
                        for s in swimmer_time:
                            if s == '2)' or s == '4)':
                                relay_teams[current_relay_id].append(swimmer_name.strip())
                                swimmer_name = ''
                            else:
                                swimmer_name += f" {s}" 
                                 
                        relay_teams[current_relay_id].append(swimmer_name.strip())                   
                        continue

                    if(not (swimmer_time[0] == 'X' or swimmer_time[0] == 'X' or swimmer_time[0] == '--' or swimmer_time[0].isnumeric())):
                        continue
                    
                    if len(swimmer_time) < 5: 
                        continue
                    # testplacement = swimmer_time[columnsIndex['Pl']] # remove placement
                    # testpoints = int(swimmer_time[columnsIndex['Pts']]) if placement.isnumeric() and int(placement) == 1 else 0
                    # testtime = swimmer_time[columnsIndex['Official']] # grab official time
                    # testseed_time = swimmer_time[columnsIndex['Seed']] if containsSeedTime else None  
                    # testtime = swimmer_time[columnsIndex['Official']] # grab official time
                    
                    
                    placement = swimmer_time.pop(0) # remove placement
                    
                    points = int(swimmer_time.pop()) if placement.isnumeric() and int(placement) == 1 else 0
                    time = swimmer_time.pop().strip() # grab official time
                    
                    seed_time = swimmer_time.pop().strip() if containsSeedTime else None
                    team = swimmer_time.pop()
                    group = swimmer_time.pop()
                    result = "Finished" if not any(reason in time for reason in Utils.skip_reasons) else time
                    time_in_milis = Utils.convert_time_to_seconds(time) if not any(reason in time for reason in Utils.skip_reasons) else None
                    current_relay_id = str(uuid.uuid1())
                    relay_teams[current_relay_id] = []
                    swim_entry = RelaySwimEntry(current_relay_id, group, team, placement,points,result, time_in_milis, meet_date, race_type, age_group, gender, distance)
                    
                    if team in score: 
                        score[team] += points
                    else:
                        score[team] = points
                    relay_race_times.append(swim_entry)
                elif(isTimeSection): # individual swimmer
                    swimmer_time = x.split(' ')
                    
                    try: 
                        for entry in swimmer_time: 
                            if(entry == 'NC' or entry == 'TEAM'):
                                continue
                            elif(current_swimmer_entry['placement'] == None):
                                current_swimmer_entry['placement'] = entry
                            elif(entry in team_names):
                                current_swimmer_entry['Team'] = entry
                            elif(current_swimmer_entry['age'] == None and not entry.isnumeric()):
                                if (len(current_swimmer_entry['possible_name']) > 0 and current_swimmer_entry['possible_name'][0].strip(',') != entry): 
                                    current_swimmer_entry['possible_name'].append(entry)
                                elif(len(current_swimmer_entry['possible_name']) == 0):
                                    current_swimmer_entry['possible_name'].append(entry)
                            elif(current_swimmer_entry['age'] == None and entry.isnumeric()):
                                current_swimmer_entry['age'] = entry
                            elif(current_swimmer_entry['Team'] != None and containsSeedTime and current_swimmer_entry['seed'] == None):
                                current_swimmer_entry['seed'] = entry
                            elif(current_swimmer_entry['seed'] != None and current_swimmer_entry['official'] == None):
                                current_swimmer_entry['official'] = entry
                            elif(current_swimmer_entry['official'] != None and (current_swimmer_entry['placement'].isnumeric() and  int(current_swimmer_entry['placement']) < 7)):
                                current_swimmer_entry['points'] = int(entry)
                        print(current_swimmer_entry)
                        if (current_swimmer_entry['official'] != None):
                            full_name = ' '.join(current_swimmer_entry['possible_name'])

                            # create new Swimmer Event time entry 
                            name_arr = full_name.split(',') 
                            official_time = current_swimmer_entry['official'] 
                            result = "Finished" if not any(reason in official_time for reason in Utils.skip_reasons) else official_time
                            time_in_milis = Utils.convert_time_to_seconds(official_time) if not any(reason in official_time for reason in Utils.skip_reasons) else None
                            team = current_swimmer_entry['Team']
                            swim_entry = IndividualSwimEntry(
                                name_arr[1].strip(), #first_name
                                name_arr[0].strip(), #last_name
                                current_swimmer_entry['age'], 
                                team, 
                                current_swimmer_entry['placement'], 
                                current_swimmer_entry['points'] if current_swimmer_entry['points'] else 0, 
                                result, 
                                time_in_milis, 
                                meet_date, 
                                race_type, 
                                age_group, 
                                gender, 
                                distance)

                            if team in score: 
                                score[team] += current_swimmer_entry['points'] if current_swimmer_entry['points'] else 0
                            else:
                                score[team] = current_swimmer_entry['points'] if current_swimmer_entry['points'] else 0
                            # print(f"adding entry to list {swim_entry}")
                            individual_race_times.append(swim_entry)
                            current_swimmer_entry = {
                                'placement': None,
                                'possible_name': [],
                                'age': None,
                                'Team': None,
                                'seed': None,
                                'official': None,
                                'points': None,
                            }
                    except Exception as e:
                        print("Error occurred in PDFParser.parse_meet_PDF: %s \n %s", str(e), traceback.format_exc())
                        failed_to_read.append(f"{x} {gender.name} {age_group} {distance} {race_type.name}")
                        current_swimmer_entry = {
                                'placement': None,
                                'possible_name': [],
                                'age': None,
                                'Team': None,
                                'seed': None,
                                'official': None,
                                'points': None,

                        }
                        
                        
                        
                            

                    # if (containsAchievements and (swimmer_time[-1] == 'NC' or swimmer_time[-1] == 'TEAM')):
                    #     swimmer_time.pop()
                    # if(len(swimmer_time) == 0):
                    #     continue
                    # if (len(swimmer_time) < 5):
                    #     # logic to combine times that come on multiple lines blocks if value is already stored so we dont repeat
                    #     if(swimmer_time[0] not in partial_swimmer_time[1:] and ( not len(partial_swimmer_time) > 2 or partial_swimmer_time[1].strip(',') not in swimmer_time[0])):
                    #         partial_swimmer_time.extend(swimmer_time)
                    #     if(len(partial_swimmer_time) > 5):
                    #         swim_entry = process_individual_swimmer(partial_swimmer_time, containsSeedTime, meet_date, race_type, age_group, gender, distance, score, False)
                    #         partial_swimmer_time = []
                    # else:
                    #     swim_entry = process_individual_swimmer(swimmer_time, containsSeedTime, meet_date, race_type, age_group, gender, distance, score, False)
                    # if swim_entry: 
                    #     individual_race_times.append(swim_entry)
                # else: 
        meet_id = database.get_meet_id(str(meet_info), meet_date.timestamp())
        meet = Meet(
            meet_id,
            meet_date, 
            str(meet_info), 
            score
        )   
        
        return {
            "isAlreadySaved": meet.record_id != None,
            "meet": meet,
            "individual_race_times": individual_race_times, 
            "relay_race_times": relay_race_times,
            "relay_teams": relay_teams,
            "needs_attention": failed_to_read
        }
    except Exception as e:
        print("Error occurred in PDFParser.parse_meet_PDF: %s \n %s", str(e), traceback.format_exc())
        LOGGER.error("Error occurred in PDFParser.parse_meet_PDF: %s \n %s", str(e), traceback.format_exc())
    finally:
        database.close_connection()
        LOGGER.info("Exiting PDFParser.parse_meet_PDF")  


def load_race_data(pdf):
    LOGGER.info("Entering PDFParser.load_race_data with path: %s", pdf)  
    pages = pdfium.PdfDocument(pdf)
    
    searcher = pages[0].get_textpage().search("Northland Conference Championships", match_case=False, match_whole_word=False)
    if(searcher.get_next() != None): 

        return parse_conference_PDF(pages)
    else:
        return parse_meet_PDF(pages)
    