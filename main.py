import asyncio
from utils import clock
from sensor import PicoThermometer
from microdot.microdot import Response
from microdot.microdot_asyncio import Microdot
from utils.connect import connect_to_network


# Workaround to allow pico to access the serial port, run the following command:
# sudo chmod a+rw /dev/ttyACM0

# Server -------------------------------------------------------------------- #
server = Microdot()
Response.default_content_type = 'text/html'

with open('static/index.html', 'r') as f:
    html_string = f.read()
    
# with open('style.css', 'r') as f:
#     css_string = f.read()

with open('static/script.js', 'r') as f:
    js_string = f.read()

# Webserver routes
@server.route('/')
async def index(request):
    # serve the index.html file with javascript
    return html_string


# Static CSS/JSS
@server.route("/static/<path:path>")
def static(request, path):
    if ".." in path:
        # directory traversal is not allowed
        return "Not found", 404
    return js_string#send_file("static/" + path)


@server.route('/data/current')
async def api_current(request, methods = ['GET']):
    print('Client requested data current static data')
    return Thermo.get_current_data()


@server.route('/data/stream')
async def api_stream_all(request, methods = ['GET']):
    print('Client requested data stream')
    return Thermo.get_data_stream()


@server.route('/data/stream/<from_timestamp>', methods = ['GET'])
async def api_stream(request, from_timestamp):
    
    # Parse URL string, %20 is a space in hexadecimal
    from_timestamp = from_timestamp.replace('%20', ' ')
    
    if from_timestamp.isdigit():
        print('Converting timestamp to epoch int')
        from_timestamp = int(from_timestamp)
    else:
        from_timestamp = clock.string_to_datetime(from_timestamp)
    
    timestamp_str = clock.datetime_to_string(from_timestamp)
    
    n_readings = len(Thermo.stack)
    
    print(f'Client requested data stream since {timestamp_str} ({n_readings:.0f} readings)')
    
    return Thermo.get_data_stream(from_timestamp)

async def main():
    
    print('Connecting to Network...')
    netinfo = connect_to_network()
    
    
    # Instantiate the webserver class
    global Thermo
    Thermo = PicoThermometer(netinfo)
            
    # Sync the clock
    clock.sync_time()
    
    # Start the sensor reading task
    sensor_task = asyncio.create_task(Thermo.read_sensors())
    server_task = asyncio.create_task(server.start_server("0.0.0.0", port=80))
    
    print('Setting up webserver...')
    
    await asyncio.gather(sensor_task, server_task)


# --------------------------------------------------------------------------- #

# Run the webserver asynchronously
try:
    asyncio.run(main())
    
finally:
    asyncio.new_event_loop()