from apparatus.i2c_lcd import I2cLcd
from machine import I2C, Pin

# The LCD display
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)

# Initialize
LCD = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
