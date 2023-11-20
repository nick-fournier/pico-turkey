
import network
import ubinascii
import time
from env import SSID, PASSWORD

wlan = network.WLAN(network.STA_IF)

def wifi_connect():
        
    # Connect to the network
    wlan.active(True)        
    wlan.config(pm = 0xa11140)  # Disable power-save mode
    wlan.connect(ssid=SSID, key=PASSWORD)
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    
    # Wait for connect or fail
    wait = 10
    while wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        wait -= 1
        print('waiting for connection...')
        time.sleep(2)
    
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('wifi connection failed')
    else:
        print('connected')
        
        ip = wlan.ifconfig()[0]
        netinfo = {'ip': ip, 'mac': mac}
        
        print('IP: ', ip, 'MAC: ', mac)
    
    return netinfo