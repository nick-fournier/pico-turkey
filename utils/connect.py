import network
import time
import ubinascii
from env import CONNECTIONS
from apparatus.lcd import LCD

# Wifi connection
network.hostname('jive.turkey')
wlan = network.WLAN(network.STA_IF)

def connect_to_network():
        
    # Connect to the network
    wlan.active(True)
    wlan.config(pm = 0xa11140)      # Disable power-save mode
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    
    # Try each connection in the list 3 times
    retry = len(CONNECTIONS) * 3
    while retry > 0:
        # Try next SSID, PASSWORD pair
        SSID, PASSWORD = CONNECTIONS[retry % len(CONNECTIONS)]
        wlan.connect(ssid=SSID, key=PASSWORD)
        
        LCD.clear()
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        retry -= 1
        print('waiting for connection...')
        LCD.putstr(f'Connecting to\n{SSID[:14]}')
        time.sleep(2)
    
    LCD.clear()
    # Handle connection error
    if wlan.status() != 3:
        print('wifi connection failed')
        LCD.putstr('Wifi connection\nfailed')
        raise RuntimeError('wifi connection failed')
    
    else:            
        ip = wlan.ifconfig()[0]
        print('Connected')
        
        LCD.putstr(f'Connected as\n{ip}')
                
        time.sleep(2)
        print('IP: ', ip, 'MAC: ', mac)
    
    LCD.clear()
    
    return {'ip': ip, 'mac': mac}



