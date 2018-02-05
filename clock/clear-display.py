"""
This script just clears the PiOLED screen. The screen does not clear on its
own unless cleared manually.
"""

import time
from PIL import Image, ImageDraw, ImageFont

# import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()
# Clear display.
disp.clear()
disp.display()
