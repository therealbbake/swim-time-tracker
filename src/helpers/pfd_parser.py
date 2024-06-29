
import pypdfium2 as pdfium
import uuid 
from models import *

skip_reasons = ['DQ', 'DNF', 'DFS', 'NS']
# convert race times to a common format
def format_time(time):
    if(time == "NT"):
        return time
    elif(":" in time): 
        d = time.split(":")
        int_min = int(d[0])
        sec =d[1]
    else:
        d = time.split(".")
        mil = d[1]
        v = d[0]
        sec = "{}.{}".format(v[-2:],mil)
        min = v[:-2]
        int_min = 0 if min == "" else int(min)
    return"{}:{}".format(int_min,sec)     

def build_race_name(race_info):
    return ' '.join(str(r) for r in race_info).replace('Swim-off' , '').replace(' Meter', 'm').replace('Individual Medley', 'IM').replace('Freestyle', 'Free').replace('Breaststroke', 'Breast').replace('Backstroke', 'Back').replace('Butterfly', 'Fly').strip()

def get_gender(gender):
    val = gender.lower()
    if val ==  "women" or "girl" in val:
        return "Girls"
    elif val ==  "men" or "boy" in val:
        return "Boys"
    else:
        return gender
def parse_conference_PDF(pages):
    race_times = []
    meet_date = ''
    meet_info = ''
    for page in pages: 
        textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None, errors='ignore')
        page_lines = textpage.split('\n')
        # retieve data of the meet
        title = page_lines.pop(0).split(' ')
        meet_date = title[len(title) - 3]
        # remove unneeded lines
        meet_info = page_lines.pop(0).split(' ')[:4]
        page_lines.pop(0)
        page_lines.pop(0)
        # loop through pages
        for x in page_lines:
            x.replace('\\n', '')
            if(x.startswith('#')): # retrieves Event Data
                is_relay = 'Relay' in x
                race_info = x.split(' ')
                race_info.pop(0) #remove race info 
                gender = get_gender(race_info.pop(0))
                age_group = race_info.pop(0)
                race = build_race_name(race_info)
                current_event = Event(race, age_group, gender)
            elif('Preliminaries' in x or 'Final' in x or 'Team' in x or 'Swim-Off' in x or 'Swim-off' in x): # un needed lines
                continue
            elif(is_relay):
                swimmer_time = x.split(' ')
                if(len(swimmer_time) > 4):
                    continue
                swimmer_time.pop(0) # remove placement
                time = swimmer_time.pop().strip() # grab official time
                if any(reason in time for reason in skip_reasons): # skip storing events
                    continue
                group = swimmer_time.pop()
                team = swimmer_time.pop()
                swim_entry = SwimerEventTimes(str(uuid.uuid1()), 
                    RelayTeam(team, group, current_event.age_group), # swimmer info
                    format_time(time), # seed time (best)
                    meet_date,  # date seed time recorded
                    format_time(time), # most recent swim time
                    meet_date, # last time swam event
                    current_event) # current Event
    
                race_times.append(swim_entry)
            else:
                swimmer_time = x.split(' ')
                swimmer_time.pop(0) # remove placement
                time = swimmer_time.pop().strip() # grab official time
                if any(reason in time for reason in skip_reasons): # skip storing events
                    continue
                team = swimmer_time.pop()
                age = swimmer_time.pop()
                name = ' '.join(swimmer_time)
                # create new Swimmer Event time entry 
                swim_entry = SwimerEventTimes(str(uuid.uuid1()), 
                    Swimmer(name, age, team), # swimmer info
                    format_time(time), # seed time (best)
                    meet_date,  # date seed time recorded
                    format_time(time), # most recent swim time
                    meet_date, # last time swam event
                    current_event) # current Event
    
                race_times.append(swim_entry)
                
    return {
        "meet_info": meet_info,
        "times": race_times,
        "date": meet_date,
    }

def parse_meet_PDF(pages):
    race_times = []
    meet_date = ''
    meet_info = ''
    for page in pages: 
        textpage = page.get_textpage().get_text_bounded(left=None, bottom=None, right=None, top=None, errors='ignore')
        page_lines = textpage.split('\n')
        # retieve data of the meet
        title = page_lines[len(page_lines) -2].split(' ')
        meet_date = title.pop(0).strip(',')
        del title[:2]
        del title[-4:]
        meet_info = ' '.join(title)
        del page_lines[-3:]
        page_lines.pop(0)
        # loop through pages
        for x in page_lines:
            x.replace('\\n', '')
            if(x.startswith('#')): # retrieves Event Data
                print(x)
                is_relay = 'Relay' in x
                
                race_info = x.split(' ')
                race_info.pop(0) #remove race info 
                gender = get_gender(race_info.pop(0))
                if "8 & Under" not in x: 
                    age_group = race_info.pop(0)  
                else: 
                    age_group = '8&U'
                    del race_info[:3]
                    
                race = build_race_name(race_info)
                current_event = Event(race, age_group, gender)
            elif('Preliminaries' in x or 'Final' in x or 'Team' in x or 'Swim-Off' in x or 'Swim-off' in x): # un needed lines
                continue
            elif(is_relay):
                swimmer_time = x.split(' ')
                if( swimmer_time[0] == '1)' or swimmer_time[0] == '3)'):
                    continue
                placement = swimmer_time.pop(0) # remove placement
                if( placement.isnumeric() and int(placement) == 1): # remove points scored
                    swimmer_time.pop()
                time = swimmer_time.pop().strip() # grab official time\
                if any(reason in time for reason in skip_reasons): # skip storing events
                    continue
                seed_time = swimmer_time.pop().strip()
                team = swimmer_time.pop()
                group = swimmer_time.pop()
                swim_entry = SwimerEventTimes(str(uuid.uuid1()), 
                    RelayTeam(team, group, current_event.age_group), # swimmer info
                    format_time(seed_time), # seed time (best)
                    None,  # date seed time recorded
                    format_time(time), # most recent swim time
                    meet_date, # last time swam event
                    current_event) # current Event
    
                race_times.append(swim_entry)
            else:
                swimmer_time = x.split(' ')
                placement = swimmer_time.pop(0) # remove placement
                if( placement.isnumeric() and int(placement) < 7): # remove points scored
                    swimmer_time.pop()
                official_time = swimmer_time.pop().strip() # grab official time
                if any(reason in official_time for reason in skip_reasons): # skip storing events
                    continue
                seed_time = swimmer_time.pop().strip()
                team = swimmer_time.pop()
                age = swimmer_time.pop()
                name = ' '.join(swimmer_time)
                # create new Swimmer Event time entry 
                swim_entry = SwimerEventTimes(str(uuid.uuid1()), 
                    Swimmer(name, age, team), # swimmer info
                    format_time(seed_time), # seed time (best)
                    None,  # date seed time recorded
                    format_time(official_time), # most recent swim time
                    meet_date, # last time swam event
                    current_event) # current Event
    
                race_times.append(swim_entry)
                
    return {
        "meet_info": meet_info,
        "times": race_times,
        "date": meet_date,
    }


def load_race_data(pdf):
    pages = pdfium.PdfDocument(pdf)
    searcher = pages[0].get_textpage().search("Northland Conference Championships", match_case=False, match_whole_word=False)
    if(searcher.get_next() != None): 
        return parse_conference_PDF(pages)
    else:
        return parse_meet_PDF(pages)
    