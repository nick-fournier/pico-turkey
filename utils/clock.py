import utime
import ntptime

UTC_OFFSET = -8 # Pacific Standard Time (PST)
ntptime.host = "0.us.pool.ntp.org"

def get_datetime():
    # Get the current time
    return utime.time() + UTC_OFFSET * 3600


def datetime_to_string(datetime_seconds):    
    # Convert to a string
    dt = utime.localtime(datetime_seconds)
    date_string = f"{dt[0]}-{dt[1]:02d}-{dt[2]:02d} {dt[3]:02d}:{dt[4]:02d}:{dt[5]:02d} {UTC_OFFSET:+03d}:00"

    return date_string


def get_datetime_string():
    return datetime_to_string(utime.time() + UTC_OFFSET * 3600)


def string_to_datetime(datetime_string):
    # Convert to a datetime object assuming format: "mm/dd/yyyy hh:mm:ss-UTC_OFFSET"
    try:
        strings = datetime_string.split(' ')
        date = strings[0].split('-')
        time = strings[1].split(':')
        # utc = int(strings[2].split(':')[0]) * 3600 + int(strings[2].split(':')[1])
        
        # Make time [year, month, day, hour, minute, second]
        dt = tuple([int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]), 0, 0])                
        dt = utime.mktime(dt)
        
    except:
        print(f"Error converting string {datetime_string} to datetime object")
        dt = datetime_string
    
    return dt


def adjust_dst_utc():
    
    global UTC_OFFSET
    
    current_time = utime.time()
    year = utime.localtime(current_time)[0]
    
    # DST begins on the second Sunday in March and ends on the first Sunday in November.
    day_start = (14 - (int(5 * year / 4 + 1)) % 7)
    day_end = (7 - (int(5 * year / 4 + 1)) % 7)
    
    # Format tuple for mktime
    dst_start_tuple = tuple((year, 3, day_start, 1, 0, 0, 0, 0, 0))
    dst_end_tuple = tuple((year, 11, day_end, 1, 0, 0, 0, 0, 0))
    
    # Calculate the start and end of daylight savings time for the given year
    dst_start = utime.mktime(dst_start_tuple)
    dst_end = utime.mktime(dst_end_tuple)
        
    # Check if the current time is between the start and end of daylight savings time
    if dst_start <= current_time <= dst_end:
        print("Daylight savings time is in effect")
        UTC_OFFSET += 1
    

def sync_time():
    
    print("Synchronizing time. Local time before synchronization: %s" %get_datetime_string())
    
    # Attempt to sync the time, try 3 times
    attempts = 1
    max_attempts = 3
    
    while attempts < max_attempts:
        try:
            # Sync the time with the ntp server            
            ntptime.settime()
            
            # Adjust for daylight savings time
            adjust_dst_utc()
            print("Time synchronized. Local time after synchronization: %s" %get_datetime_string())
            
            return
            
        except Exception as e:
            print(f"Error syncing time, retrying {attempts}/{max_attempts}...")
            utime.sleep(1)
        
        attempts += 1
        
    print(f"Failed to sync time after {attempts} attempts. Using existing local time")
    print("Local time: %s" %get_datetime_string())
        
    return

if __name__ == '__main__':
    sync_time()
    