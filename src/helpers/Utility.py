
def convert_time_to_seconds(time):
    if (time == "NT" or time == None):
        return  None
    if(":" in time): 
        d = time.split(":")
        int_min = int(d[0])
        sec = float(d[1])
    else:
        d = time.split(".")
        mil = d[1]
        v = d[0]
        sec = float("{}.{}".format(v[-2:],mil))
        min = v[:-2]
        int_min = 0 if min == "" else int(min)
    return round((sec + (int_min * 60 )),2)

def format_time(time):
    if not time:
        return  None
    t = str(time).split('.')
    m, s = divmod(int(t[0]), 60)
    return f'{m:02}:{s:02}.{t[1]}'

def get_race_distance(distance):
    return int(distance.strip('m'))


skip_reasons = ['DQ', 'DNF', 'DFS', 'NS', 'SCR']