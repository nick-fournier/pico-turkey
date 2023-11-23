import json
import asyncio
import network
import ubinascii
import time
import machine
from env import SSID, PASSWORD
from clock import get_datetime_string, sync_time
from max6675 import MAX6675
from machine import Pin, I2C
from i2c_lcd import I2cLcd
from regression import best_fit
from webpage import webpage
import gc

# Settings ------------------------------------------------------------------ #

# Heartbeat rate
heartbeat = 5  # Seconds

# Calibration
CAL_OFFSET = -2.25  # The calibration offset in degrees Celcius
CAL_FACTOR = 1.0    # The calibration factor

# The LCD display
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# The Thermocouple sensor
sck = Pin(2, Pin.OUT)
cs = Pin(3, Pin.OUT)
so = Pin(4, Pin.IN)

# Initialize --------------------------------------------------------------- #
led = Pin("LED", Pin.OUT, value=0)

# Wifi connection
network.hostname('jive.turkey')
wlan = network.WLAN(network.STA_IF)

# Thermocouple sensor
sensor = MAX6675(sck, cs, so)


# Calibration --------------------------------------------------------------- #
def calibrate(temp):
    return temp * CAL_FACTOR + CAL_OFFSET


# Webserver ----------------------------------------------------------------- #
class PicoThermometer:
    
    rate = 0            # Rate of temperature change
    stdev = 0           # Standard deviation of the last minute of data
    current = {}        # Current temperature reading    
    tempstack = []      # Data stack of temperature readings
    maxshort = 2 * int(60 / heartbeat)  # Rolling average over 1 minute of data
    maxlong = 60 * 60 * (60 / heartbeat)  # 1 hour of data
    
    def connect_to_network(self):
            
        # Connect to the network
        wlan.active(True)
        wlan.config(pm = 0xa11140)  # Disable power-save mode
        wlan.connect(ssid=SSID, key=PASSWORD)
        mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
        
        # Wait for connect or fail
        wait = 10
        lcd.clear()
        while wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            wait -= 1
            print('waiting for connection...')
            lcd.putstr(f'Connecting to\n{SSID[:15]}')
            time.sleep(2)
        
        lcd.clear()
        # Handle connection error
        if wlan.status() != 3:
            print('wifi connection failed')
            lcd.putstr('Wifi connection\nfailed')
            raise RuntimeError('wifi connection failed')
        
        else:            
            ip = wlan.ifconfig()[0]
            print('Connected')
            
            lcd.putstr(f'Connected as\n{ip}')
            self.netinfo = {'ip': ip, 'mac': mac}
            
            time.sleep(2)
            print('IP: ', ip, 'MAC: ', mac)
        
        lcd.clear()
        

    async def serve_client(self, reader, writer):
        print("Client connected")
        request_line = await reader.readline()
        print("Request:", request_line)
        
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass
        
        # Create data for the web page
        data = {
            'rate': self.rate, 
            'stdev': self.stdev,
            'data': self.tempstack
        }
                
        # Format the data for the web page
        payload = json.dumps(data).encode('utf-8')
                
        # If request header is /json, return JSON data
        if "GET /data" in request_line:      
            writer.write('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            writer.write(payload)
            
        else:
            # Otherwise return the webpage
            webhost = '/data'
            html = webpage(webhost)
            
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(html)

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")
        
            
    async def read_sensors(self, period = heartbeat):
        while True:
            
            # Get temp reading
            time = get_datetime_string()
            temp = sensor.read()
            
            # Calibrate
            temp = calibrate(temp)
            
            # Temp C to F
            temp = temp * (9/5) + 32
            
            self.current = {'timestamp': time, 'temperature': temp}
                
            # Add to the web data stack
            self.tempstack.append(self.current)
                                        
            # If at least 2 readings readings, calculate a rate
            slope = 0
            if len(self.tempstack) >= 4:
                # Extract last 1 minute of data
                shortstack = [t['temperature'] for t in self.tempstack[-self.maxshort:]]
            
                x = range(len(shortstack))
                y = shortstack
                
                # Standard deviation of the last minute of data
                self.stdev = sum([(i - sum(y) / len(y)) ** 2 for i in y]) / len(y)                
               
                # Regression, intercept, slope per heartbeat
                _, slope = best_fit(x, y)
            
            # Calculate rate per 10 minutes
            self.rate = slope * (60 / heartbeat)
            
            # Print to console
            mem_free = gc.mem_free() / 1024 # type: ignore
            print((
                f'Heartbeat -- {time}, Temp: {temp:.2f}F, Stdev: {self.stdev:.1f}, Rate: {self.rate:+.1f}F/min, mem free {mem_free:.0f} kb'
            ))
            
            # Dynamically delete data if memory is low
            if mem_free < 50:                
                print('Memory low, deleting data.')
                while gc.mem_free() < 100: # type: ignore
                    self.tempstack.pop(0)
            
            # print to LCD
            lcd.clear()
            
            # Printing stdev capped at 99F/min
            if abs(self.rate) > 9:
                prate = f'{self.rate:+.0f}'
            elif abs(self.rate) > 99:
                prate = 99 * self.rate / abs(self.rate)                
                prate = f'{prate:+.0f}'
            else:
                prate = f'{self.rate:+.1f}'
                        
            msg = (
                f"{temp:.1f}F {prate}/min\n" +
                f"{self.netinfo['ip']}"
            )
                        
            lcd.putstr(msg)
            
            await asyncio.sleep(period)
                

    async def main(self):
        
        print('Connecting to Network...')
        self.connect_to_network()
                
        # Sync the clock
        sync_time()
        
        # Start the sensor reading task
        asyncio.create_task(self.read_sensors())
        
        print('Setting up webserver...')
        try:
            asyncio.create_task(asyncio.start_server(self.serve_client, "0.0.0.0", 80))
        except OSError:
            print('Failed to start webserver')
            lcd.clear()
            lcd.putstr('Webserver failed,\nrestarting...')
            time.sleep(2)
            machine.reset()
        
                
        # Heartbeat LED
        while True:
            led.on()
            await asyncio.sleep(0.25)
            led.off()
            await asyncio.sleep(heartbeat - 0.25)
            
            gc.collect()


# --------------------------------------------------------------------------- #
# Instantiate the webserver class
WebServer = PicoThermometer()

# Run the webserver asynchronously
try:
    asyncio.run(WebServer.main())
    
finally:
    asyncio.new_event_loop()