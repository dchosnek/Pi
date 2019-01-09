
# Raspberry Pi Clock
# for the Pi Zero W and OLED Bonnet from Adafruit:
# https://www.adafruit.com/product/3400
# https://www.adafruit.com/product/3192

# external dependencies

# import time
# import urllib2
# import json
# import subprocess
from PIL import Image, ImageDraw, ImageFont

# import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

# =============================================================================
# Globals
# -----------------------------------------------------------------------------

FONT_FAMILY = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"

# Raspberry Pi pin configuration
# 128x64 display with hardware I2C:
RST = None     # on the PiOLED this pin isn't used
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
WIDTH = disp.width
HEIGHT = disp.height


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

# Draw a black filled box to clear the image.
msg_font = ImageFont.truetype(FONT_FAMILY, 18)
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
draw.text((0, 0), "Hello World!", font=msg_font, fill=255)

# Display image.
disp.image(image)
disp.display()
