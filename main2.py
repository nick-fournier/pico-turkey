import json
import time
import asyncio
import network
import ubinascii
from machine import Pin
from connect import wifi_connect
from clock import get_datetime_string, sync_time
from reading import get_temperature, get_distance


heartbeat = 60
led = Pin("LED", Pin.OUT, value=0)

class PicoThermometer:
    
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
            self.current_reading = {
                'timestamp': get_datetime_string(),
                'temperature': get_temperature(),
                'distance': get_distance(),
                'macid': self.netinfo['mac']
            }
            
            time = self.current_reading['timestamp']
            temp = self.current_reading['temperature']
            dist = self.current_reading['distance']  
            
            print(f'Heartbeat -- {time}, {temp:.2f} C, {dist:.2f} cm')
            
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
WebServer = PicoSumpServer()

# Run the webserver asynchronously
try:
    asyncio.run(WebServer.main())
    
finally:
    asyncio.new_event_loop()