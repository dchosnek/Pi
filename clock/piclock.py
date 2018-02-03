# Raspberry Pi Clock
# for the Pi Zero W and OLED Bonnet from Adafruit:
# https://www.adafruit.com/product/3400
# https://www.adafruit.com/product/3192

# external dependencies

import time
import urllib2
import json
import subprocess
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

WEATHER_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%3D12791571&format=json'
FONT_FAMILY_CLOCK = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_FAMILY_DATE = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FONT_FAMILY_TEMP = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
SLEEP_TIMER = 0.2
WEATHER_TIMER = int(300 / SLEEP_TIMER)

# Input pins:
L_pin = 27 
R_pin = 23 
C_pin = 4 
U_pin = 17 
D_pin = 22 

A_pin = 5 
B_pin = 6 

GPIO.setmode(GPIO.BCM) 

GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up


# Raspberry Pi pin configuration
# 128x64 display with hardware I2C:
RST = None     # on the PiOLED this pin isn't used
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
WIDTH = disp.width
HEIGHT = disp.height

# Initialize library and clear display
disp.begin()
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)

# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = HEIGHT-padding

def biggest_font(screen_width, screen_height, family, message):
    """
    Return the largest font size a message can be displayed given the screen
    dimensions and the font family.
    """
    size = 1
    while True:
        font = ImageFont.truetype(family, size)
        dimensions = font.getsize(message)
        if dimensions[0] >= screen_width or dimensions[1] >= screen_height:
            break
        size += 1
    return size - 1

timer = 0
temp_current = 0
temp_hi = 0
temp_lo = 0
screen_number = 0

while True:

    if GPIO.input(U_pin):   # up button released
        btn_up = False
    else:
        btn_up = True
    
    if GPIO.input(D_pin):   # button is released
        btn_down = False
    else:
        btn_down = True


    if pressed_up:
        if btn_up:
            timer_up += 1
        else:
            timer_up = 0
    
    if pressed_down:
        pass

    # ===============================================================
    # Get data to diplay on screen
    # ---------------------------------------------------------------

    # clock is always displayed
    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "date +\"%_I:%M\""
    clock_text = subprocess.check_output(cmd, shell=True)

    if screen_number == 0:
        cmd = "date +\"%A %b %d\""
        line2_text = subprocess.check_output(cmd, shell=True)
    elif screen_number == 1:
        if timer == 0:
            result = urllib2.urlopen(WEATHER_URL).read()
            data = json.loads(result)
            temp_current = data['query']['results']['channel']['item']['condition']['temp']
            temp_hi = data['query']['results']['channel']['item']['forecast'][0]['high']
            temp_lo = data['query']['results']['channel']['item']['forecast'][0]['low']
        line2_text = "{} deg, Lo:{}, Hi:{}".format(temp_current, temp_lo, temp_hi)
    elif screen_number == 2:
        line2_text = "IP address"
        pass

    timer += 1
    timer = 0 if timer >= WEATHER_TIMER else timer

    clock_font_size = biggest_font(WIDTH, HEIGHT, FONT_FAMILY_CLOCK, str(clock_text)) + 1
    clock_font = ImageFont.truetype(FONT_FAMILY_CLOCK, clock_font_size)

    voffset = clock_font.getsize(str(clock_text))[1]

    line2_size = biggest_font(WIDTH, HEIGHT, FONT_FAMILY_DATE, line2_text)
    line2_font = ImageFont.truetype(FONT_FAMILY_DATE, line2_size)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    draw.text((0, top), str(clock_text), font=clock_font, fill=255)
    draw.text((0, voffset), line2_text, font=line2_font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(SLEEP_TIMER)
