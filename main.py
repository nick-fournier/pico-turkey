import json
import asyncio
from machine import Pin
from connect import wifi_connect
from clock import get_datetime_string, sync_time
from max6675 import MAX6675
from machine import Pin, I2C
from i2c_lcd import I2cLcd
from regression import best_fit
from webpage import webpage
import gc

# The Thermocouple sensor
sck = Pin(2, Pin.OUT)
cs = Pin(3, Pin.OUT)
so = Pin(4, Pin.IN)

sensor = MAX6675(sck, cs, so)

# The LCD display
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

heartbeat = 5  # Seconds
led = Pin("LED", Pin.OUT, value=0)

class PicoThermometer:
    
    rate = 0            # Rate of temperature change
    current = {}        # Current temperature reading    
    tempstack = []      # Data stack of temperature readings
    maxshort = int(60 / heartbeat)  # Rolling average over 1 minute of data
    maxlong = 60 * 60 * (60 / heartbeat)  # 1 hour of data
    
    def connect_to_network(self):
        self.netinfo = wifi_connect()
        

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
            temp = sensor.read() * (9/5) + 32
            self.current = {'timestamp': time, 'temperature': temp}
                
            # Add to the web data stack
            self.tempstack.append(self.current)
            
            # # Drop first if > maxlen (FIFO)
            # if len(self.tempstack) > self.maxlong:
            #     self.tempstack.pop(0)
                
            # Extract last 1 minute of data
            shortstack = [t['temperature'] for t in self.tempstack[-self.maxshort:]]
                                        
            # If at least 2 readings readings, calculate a rate
            slope = 0
            if len(shortstack) >= 2:
                x = range(len(shortstack))
                y = shortstack
                # Regression, intercept, slope per heartbeat
                _, slope = best_fit(x, y)
            
            # Calculate rate per 10 minutes
            self.rate = slope * (60 / heartbeat)
            
            # Print to console
            mem_free = gc.mem_free() / 1024
            print(f'Heartbeat -- {time}, Temp: {temp:.2f}F, Rate: {self.rate:.1f}F/min, mem free {mem_free:.0f} kb')
            
            # Dynamically delete data if memory is low
            if mem_free < 50:                
                print('Memory low, deleting data.')
                while gc.mem_free() < 100:
                    self.tempstack.pop(0)
            
            # print to LCD
            lcd.clear()
                        
            msg = (
                f"{temp:.1f}F {self.rate:+.1f}/min\n" +
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
        asyncio.create_task(asyncio.start_server(self.serve_client, "0.0.0.0", 80))
        
                
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