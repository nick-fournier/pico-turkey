import gc
import asyncio
from machine import Pin
from utils import clock
from utils.kalman import KalmanFilter
from utils.ema import ExponentialMovingAverage
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
    
    heartbeat = 1       # Seconds between readings
    log_rate = 5        # Log to stack every nth reading
    target = 165        # Target temperature
    rate = 0            # Rate of temperature change
    stdev = 0           # Standard deviation of the last minute of data
    timestamp = ''      # Current timestamp
    temperature = 0     # Current temperature
    stack = []          # Data stack of readings tuple (timestamp and temperature)
    stacklength = 2 * int(60 / log_rate)  # Rolling average over 2 minute of data    
    
    def __init__(self, netinfo) -> None:
        self.netinfo = netinfo
        self.KF = KalmanFilter(dt=self.heartbeat, x0=68, x0_acc=0.25) # type: ignore
        self.EMA = ExponentialMovingAverage(alpha=0.01)

    def update_target(self, target):
        self.target = target
     
    def get_current_data(self):
        data = {
            'heartbeat': self.heartbeat,
            'rate': self.rate,
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
     
    async def read_sensors(self, period = heartbeat, loop = True):
        counter = 0
        while True:
            
            # Get temp reading & convert to Fahrenheit
            measurement = sensor.read_fahrenheit()
            
            # Update Kalman filter
            self.KF.update(measurement)
            
            # Update timestamp in Thermometer
            self.timestamp = clock.get_datetime()
                
            # Update temperature state in Thermometer
            self.temperature = self.KF.x[0]
            
            # Calculate instantaneous rate of change per minute
            inst_rate = self.KF.x[1] * (60 / self.heartbeat) # type: ignore
            
            # Update rate of change per min state in Thermometer as Exp. Moving Average
            self.rate = self.EMA.update(inst_rate)             

            # Log to stack every nth reading
            counter += 1
            if counter % self.log_rate == 0:

                # Add to the data stack for web data
                self.stack.append(
                    (self.timestamp, self.temperature)
                )

                # Fixed length stack
                if len(self.stack) > self.stacklength:
                    self.stack.pop(0)
                
                # Garbage collection
                mem_free = gc.mem_free() / 1024 # type: ignore
                
                # Print to console
                msg = [
                    f'Log rate ({self.log_rate:.0f}s)',
                    f'{clock.datetime_to_string(self.timestamp)}',
                    f'Temp: {self.temperature:.2f}F',
                    f'Rate: {self.rate:+.1f}F/min',
                    f'mem free {mem_free:.0f} kb'
                ]
                print(' '.join(msg))

            # If single reading requested, return
            if not loop:
                return            

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
                
