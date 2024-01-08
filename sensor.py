import gc
import asyncio
from machine import Pin
from utils import clock
from apparatus.max6675 import MAX6675
from apparatus.lcd import LCD

# Initialize --------------------------------------------------------------- #
# The Thermocouple sensor
sensor = MAX6675(
    sck = Pin(19, Pin.OUT), 
    cs = Pin(20, Pin.OUT),
    so = Pin(18, Pin.IN)
    )

# Webserver ----------------------------------------------------------------- #
class PicoThermometer:
    
    heartbeat = 5       # Seconds between readings
    target = 165        # Target temperature
    rate = 0            # Rate of temperature change
    stdev = 0           # Standard deviation of the last minute of data
    timestamp = ''      # Current timestamp
    temperature = 0     # Current temperature
    stack = []      # Data stack of readings tuple (timestamp and temperature)
    stacklength = 2 * int(60 / heartbeat)  # Rolling average over 2 minute of data        
    
    def __init__(self, netinfo) -> None:
        self.netinfo = netinfo
        
    def update_target(self, target):
        self.target = target
        
        
    def get_current_data(self):
        data = {
            'heartbeat': self.heartbeat,
            'rate': self.rate, 
            'stdev': self.stdev,
            'timestamp': self.timestamp,
            'temperature': self.temperature
        }
        return data
    
    def get_data_stream(self, from_time = 0):
        
        assert isinstance(from_time, int), 'from_time must be an datetime epoch integer'
            
        # If last timestamp is < from_time,return nothing, i.e. no timestamps will meet the criteria
        if self.stack[-1][0] < from_time:
            return 'Invalid request, from_timestamp is in the future.', 400
        
        # Create a generator to stream the data
        def readings_generator():
            for time, temp in self.stack:
                if time > from_time:
                    timestamp = clock.datetime_to_string(time)
                    yield f"[{timestamp}, {temp}]" + "\n"
                else:
                    yield ''
        
        return readings_generator()
    
    @staticmethod
    def calc_stack_stats(stack):
        ave_x = (len(stack) - 1) / 2
        ave_y = 0
        
        m_numer = 0
        m_denom = 0    
        stdev = 0
        
        for _, y_i in stack:
            ave_y += y_i / len(stack)
                
        for x_i, (_, y_i) in enumerate(stack):
            stdev += (y_i - ave_y) ** 2 / len(stack)
            m_numer += x_i * (y_i - ave_y)
            m_denom += x_i * (x_i - ave_x)
        
        slope = m_numer / m_denom
        
        return stdev, slope

            
    async def read_sensors(self, period = heartbeat, loop = True):
        while True:
            
            # Get temp reading & convert to Fahrenheit
            self.temperature = sensor.read_fahrenheit()
            # self.timestamp = clock.get_datetime_string()
            self.timestamp = clock.get_datetime()
            
            # Add to the web data stack
            self.stack.append(
                (self.timestamp, self.temperature)
            )

            # Fixed length stack
            if len(self.stack) > self.stacklength:
                self.stack.pop(0)
                                        
            # If at least 2 readings readings, calculate a rate
            slope = 0
            if len(self.stack) >= 4:
                self.stdev, slope = self.calc_stack_stats(self.stack)                
            
            # Calculate rate per 10 minutes
            self.rate = slope * (60 / self.heartbeat)
            
            # If single reading requested, return
            if not loop:
                return
            
            # Print to console
            mem_free = gc.mem_free() / 1024 # type: ignore
            
            msg = [
                f'Heartbeat ({self.heartbeat:.0f}s)',
                f'{clock.datetime_to_string(self.timestamp)}',
                f'Temp: {self.temperature:.2f}F',
                f'Stdev: {self.stdev:.1f}',
                f'Rate: {self.rate:+.1f}F/min',
                f'mem free {mem_free:.0f} kb'
            ]
            print(' '.join(msg))
            

            # print to LCD
            LCD.clear()
            
            # Printing stdev capped at 99F/min, rounded to integer if > 9, else 1 decimal place
            if abs(self.rate) > 9:
                prate = f'{self.rate:+.0f}'
            elif abs(self.rate) > 99:
                prate = 99 * self.rate / abs(self.rate)                
                prate = f'{prate:+.0f}'
            else:
                prate = f'{self.rate:+.1f}'
                                    
            msg = (
                f"{self.temperature:.1f}F {prate}/min\n" +
                f"{self.netinfo['ip']}"
            )
                        
            LCD.putstr(msg)
            
            # Garbage collect
            gc.collect()
            
            await asyncio.sleep(period)
                
