"""
Raspberry Pi Clock for the Pi Zero W and OLED Bonnet from Adafruit:
https://www.adafruit.com/product/3400
https://www.adafruit.com/product/3192

This clock relies on the accuracy of the Pi system clock (via NTP). It
also retrieves the weather from the OpenWeather API every 5 minutes.

written by Doron Chosnek
"""

# external dependencies
import time
import urllib2
import json
import subprocess
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from argparse import ArgumentParser

# import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

# =============================================================================
# Globals
# -----------------------------------------------------------------------------

FONT_FAMILY_PRIMARY = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_FAMILY_SECONDARY = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
SLEEP_TIMER = 0.2
WEATHER_TIMER = int(300 / SLEEP_TIMER)
MINIMUM_SIZE = 1

# pull personalization (zip code and appid) in order to read the appropriate
# weather data

parser = ArgumentParser()
parser.add_argument("--settings", required=True, help="JSON file containing zip code and appid")
args = parser.parse_args()

with open(args.settings) as f:
    data = json.load(f)
ZIP = data['zip']
APPID = data['appid']
OPENWEATHER_CURRENT_URL = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&units=imperial&appid={}'.format(ZIP, APPID)
OPENWEATHER_FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast?zip={},us&units=imperial&cnt=8&appid={}'.format(ZIP, APPID)


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

# =============================================================================
# Classes and functions
# -----------------------------------------------------------------------------

def biggest_font(screen_width, screen_height, family, message):
    """
    Return the largest font size a message can be displayed given the screen
    dimensions and the font family.
    """
    size = MINIMUM_SIZE
    while True:
        font = ImageFont.truetype(family, size)
        dimensions = font.getsize(message)
        if dimensions[0] >= screen_width or dimensions[1] >= screen_height:
            break
        size += 1
    return size - 1

def convert_to_integer(dec):
    """Rounds a float and returns it as an integer
    """
    return int(round(dec))

def get_weather_openweathermap():
    """Retrieves the weather from Open Weather map using their free API
    """
    (current, lo, hi) = (None, None, None)

    # get current temperature
    try:
        result = urllib2.urlopen(OPENWEATHER_CURRENT_URL).read()
        data = json.loads(result)
        current = convert_to_integer(data['main']['temp'])
    except:
        return (None, None, None)

    # Get forecast high and low for the day; this API endpoint returns the
    # multi-day forecast, so first we have to just look at today.
    # The other strange anomaly is that this forecast shows the high and low
    # for the rest of the current day, but shows no forecast if it is late in
    # the day.
    today = time.strftime("%Y-%m-%d")
    try:
        result = urllib2.urlopen(OPENWEATHER_FORECAST_URL).read()
        data = json.loads(result)
    except:
        return (None, None, None)
    
    for entry in data['list']:
        if today in entry['dt_txt']:
            if lo is None or lo > entry['main']['temp_min']:
                lo = entry['main']['temp_min']
            if hi is None or hi < entry['main']['temp_max']:
                hi = entry['main']['temp_max']
            lo = convert_to_integer(lo)
            hi = convert_to_integer(hi)
    
    return (current, lo, hi)

def network_ready():
    """
    To test for network readiness, we make sure that the IP address string is
    greater than 3 characters long. The following shell command will display
    the host IP address: hostname -I | wc -m
    If the network isn't ready yet, the IP address will be blank and the length
    of that string will be one.
    """
    cmd = 'hostname -I | wc -m'
    length = int(subprocess.check_output(cmd, shell=True))
    if length > 3:
        return True
    else:
        return False

def draw_text(lines):
    """
    This function handles sizing the text on the display. It sizes text
    differently depending on how many lines of text are passed to it.
    0 lines: nothing is displayed
    1 lines: the text is made as large as possible using the primary
             font family
    2 lines: the first line is sized as large as possible using the primary
             font family and the second line is sized as large as it can be
             in the remaining space using the secondary font family
    > lines: every line uses the same font family and size; the screen is
             divided evenly by the number of lines to display
    """
    if len(lines) == 0:
        pass
    elif len(lines) == 1:
        s = biggest_font(WIDTH, HEIGHT, FONT_FAMILY_PRIMARY, lines[0])
        f = ImageFont.truetype(FONT_FAMILY_PRIMARY, s)
        draw.text((0, 0), lines[0], font=f, fill=255)

    elif len(lines) == 2:
        s = biggest_font(WIDTH, HEIGHT, FONT_FAMILY_PRIMARY, lines[0])
        f = ImageFont.truetype(FONT_FAMILY_PRIMARY, s)
        draw.text((0, 0), lines[0], font=f, fill=255)
        voffset = f.getsize(lines[0])[1]
        s = biggest_font(WIDTH, HEIGHT-voffset, FONT_FAMILY_SECONDARY, lines[1])
        f = ImageFont.truetype(FONT_FAMILY_SECONDARY, s)
        draw.text((0, voffset), lines[1], font=f, fill=255)

    else:
        voffset = 0
        smallest = 1000
        # all lines should be sized the same so first step through all lines and determine
        # which one is the smallest font size so we can apply that to all of them
        for one_line in lines:
            s = biggest_font(WIDTH, HEIGHT / len(lines), FONT_FAMILY_SECONDARY, one_line)
            smallest = s if s < smallest else smallest
        # now draw all lines using the font size determined above
        for one_line in lines:
            f = ImageFont.truetype(FONT_FAMILY_SECONDARY, smallest)
            draw.text((0, voffset), one_line, font=f, fill=255)
            voffset += HEIGHT / len(lines)

# =============================================================================
# Main
# -----------------------------------------------------------------------------

# Initialize library and clear display
disp.begin()
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)

# create a welcome message while we wait for the network to be available
welcome_message_size = biggest_font(WIDTH, HEIGHT, FONT_FAMILY_PRIMARY, 'Please Wait')
welcome_font = ImageFont.truetype(FONT_FAMILY_PRIMARY, welcome_message_size)
lines = ["Please Wait"]
draw_text(lines)
disp.image(image)
disp.display()

timer = 0
screen_number = 1
screen_change = True

while not network_ready():
    time.sleep(2)

while True:

    # handle button presses

    if not GPIO.input(U_pin):
        screen_number += 1
    if not GPIO.input(D_pin):
        screen_number -= 1

    if screen_number < 0:
        screen_number = 2
    elif screen_number > 2:
        screen_number = 0

    # ===============================================================
    # Get data to diplay on screen
    # ---------------------------------------------------------------

    if timer == 0:
        temp_current, temp_lo, temp_hi = get_weather_openweathermap()
    timer += 1
    timer = 0 if timer >= WEATHER_TIMER else timer

    lines = []

    if screen_number == 0:
        cmd = "date +\"%_I:%M\""
        lines.append(subprocess.check_output(cmd, shell=True))
        cmd = "date +\"%A %b %d\""
        lines.append(subprocess.check_output(cmd, shell=True))
    elif screen_number == 1:
        cmd = "date +\"%_I:%M\""
        lines.append(subprocess.check_output(cmd, shell=True))
        if temp_current is None:
            lines.append("WEATHER UNAVAILABLE")
        if None in [temp_lo, temp_hi]:
            lines.append("{} degrees".format(temp_current))
        else:
            lines.append("{} deg, Lo:{}, Hi:{}".format(temp_current, temp_lo, temp_hi))
    elif screen_number == 2:
        cmd = "hostname"
        lines.append(subprocess.check_output(cmd, shell=True))
        cmd = "hostname -I"
        lines.append(subprocess.check_output(cmd, shell=True))
        cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
        lines.append(subprocess.check_output(cmd, shell=True))
        cmd = "free -m | awk 'NR==2{printf \"MEM: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        lines.append(subprocess.check_output(cmd, shell=True))

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    # display the text
    draw_text(lines)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(SLEEP_TIMER)
