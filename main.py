from max6675 import MAX6675
from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import time

sck = Pin(2, Pin.OUT)
cs = Pin(3, Pin.OUT)
so = Pin(4, Pin.IN)

sensor = MAX6675(sck, cs, so)

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


while True:
    lcd.clear()
    temperature = sensor.read()
    print(temperature)
    lcd.putstr("Temperature\n{:>2}C".format(int(temperature)))
    time.sleep(1)