import asyncio
from utils.clock import sync_time
from sensor import PicoThermometer
from microdot.microdot import Response
from microdot.microdot_asyncio import Microdot
from utils.connect import connect_to_network

# Server
server = Microdot()
Response.default_content_type = 'text/html'


with open('index.html', 'r') as f:
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


@server.route('/data')
async def api(request):
    data = Thermo.get_current_data()
    print('Client requested data')
    return data


async def main():
    
    print('Connecting to Network...')
    netinfo = connect_to_network()
    
    # Instantiate the webserver class
    global Thermo
    Thermo = PicoThermometer(netinfo)
            
    # Sync the clock
    sync_time()
    
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