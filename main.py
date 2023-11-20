import json
import asyncio
from collections import deque
from machine import Pin
from connect import wifi_connect
from clock import get_datetime_string, sync_time
from max6675 import MAX6675
from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from regression import linear_regression, best_fit

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

heartbeat = 2  # Seconds
led = Pin("LED", Pin.OUT, value=0)

class PicoThermometer:
    
    # tempstack = deque((), int(10 * 60 / heartbeat))
    tempstack = []
    maxlen = 5 * int(60 / heartbeat)  # Rolling average over 5 minute of data
    # maxlen = 5
    
    def connect_to_network(self):        
        self.netinfo = wifi_connect()
        

    async def serve_client(self, reader, writer):
        print("Client connected")
        request_line = await reader.readline()
        print("Request:", request_line)
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass
                
        payload = json.dumps(self.current_reading)
        writer.write('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        writer.write(payload)

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")
        
            
    async def read_sensors(self, period = heartbeat):
        while True:
            
            # Get temp reading
            time = get_datetime_string()
            temp = sensor.read() * (9/5) + 32
            
            # Add to the temperature stack
            self.tempstack.append(temp)
            
            # Drop first if maxlen (FIFO)
            if len(self.tempstack) > self.maxlen:
                self.tempstack.pop(0)
                            
            # If at least 10 sec of readings, calculate a rate
            rate = 0
            intercept = 0
            if len(self.tempstack) >= int(10 / heartbeat):
                x = range(len(self.tempstack))
                y = self.tempstack
                # intercept, rate = linear_regression(x, y)
                intercept, rate = best_fit(x, y)
            
            macid = self.netinfo['mac']
            
            self.current_reading = {
                'timestamp': time,
                'temperature': temp,
                'fit': [intercept, rate],
                'macid': macid
            }
            
            print(f'Heartbeat -- {time}, {temp:.2f} F, fit (b, m) {intercept:.2f}, {rate:.2f}')
            
            # print to LCD   
            lcd.clear()
            
            # temp10 = intercept + 10 * 60 * rate / heartbeat
            msg = (
                f"Temp: {temp:.2f}F\n" + 
                f"Rate: {rate / heartbeat:.2f}/min"
            )
            
            # lcd.putstr("Temperature\n{:>2}C".format(int(temperature)))
            
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

# Instantiate the webserver class
WebServer = PicoThermometer()

# Run the webserver asynchronously
try:
    asyncio.run(WebServer.main())
    
finally:
    asyncio.new_event_loop()