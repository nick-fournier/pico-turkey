import gc
import asyncio
from machine import Pin
from utils.clock import get_datetime_string
from utils.regression import best_fit
from apparatus.max6675 import MAX6675
from apparatus.lcd import LCD


# Settings ------------------------------------------------------------------ #

# Heartbeat rate
heartbeat = 5  # Seconds

# Initialize --------------------------------------------------------------- #
# The Thermocouple sensor
sensor = MAX6675(
    sck = Pin(17, Pin.OUT), 
    cs = Pin(16, Pin.OUT),
    so = Pin(18, Pin.IN)
    )

# Webserver ----------------------------------------------------------------- #
class PicoThermometer:
    
    target = 165        # Target temperature
    rate = 0            # Rate of temperature change
    stdev = 0           # Standard deviation of the last minute of data
    timestamp = ''      # Current timestamp
    temperature = 0     # Current temperature
    tempstack = []      # Data stack of temperature readings
    stacklength = 2 * int(60 / heartbeat)  # Rolling average over 2 minute of data        
    
    def __init__(self, netinfo) -> None:
        self.netinfo = netinfo
        
    def update_target(self, target):
        self.target = target
        
        
    def get_current_data(self):
        data = {
            'rate': self.rate, 
            'stdev': self.stdev,
            'timestamp': self.timestamp,
            'temperature': self.temperature
        }
        return data

            
    async def read_sensors(self, period = heartbeat, loop = True):
        while True:
            
            # Get temp reading & convert to Fahrenheit
            self.temperature = sensor.read_fahrenheit()
            self.timestamp = get_datetime_string()            
            
            # Add to the web data stack
            self.tempstack.append(self.temperature)            
                        
            # Fixed length stack
            if len(self.tempstack) > self.stacklength:
                self.tempstack.pop(0)
                                        
            # If at least 2 readings readings, calculate a rate
            slope = 0
            if len(self.tempstack) >= 4:
                x = range(len(self.tempstack))
                y = self.tempstack
                
                # Standard deviation of the last minute of data
                self.stdev = sum([(i - sum(y) / len(y)) ** 2 for i in y]) / len(y)                
               
                # Regression, intercept, slope per heartbeat
                _, slope = best_fit(x, y)
            
            # Calculate rate per 10 minutes
            self.rate = slope * (60 / heartbeat)
            
            # If single reading requested, return
            if not loop:
                return
            
            # Print to console
            mem_free = gc.mem_free() / 1024 # type: ignore
            
            msg = [
                'Heartbeat',
                f'{self.timestamp}',
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
            
            await asyncio.sleep(period)
                
