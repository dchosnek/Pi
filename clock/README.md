# Pi Clock with NTP

This project uses a Raspberry Pi Zero with the Adafruit 128x64 OLED Bonnet to display the current time in large letters followed by a single line of text underneath. The buttons on the OLED Bonnet are used to scroll through various screens of information.

- clock and current day and date
- clock with current temperature and weather forecast (obtained from Yahoo weather)
- statistics like IP address and hostname (4 lines of stats are displayed)

Just add the following line to `\etc\rc.local` to start the clock on Pi startup:

``` Python
python /home/pi/piclock.py &
```

## Bill of materials

- Raspberry Pi Zero W
- Adafruit Pi Protector for Raspberry Pi Model Zero
- Break-away 0.1" 2x20-pin Strip Dual Male Header
- Adafruit 128x64 OLED Bonnet for Raspberry Pi
- 32GB micro-SD card (oversized for the application but it was inexpensive)

## Headless install of Raspberry Pi Zero W

The method for getting the Pi up and running are described in HEADLESS.md in this repository.

## Noteworthy

There were two challenges to solve: how to keep the script from accessing the internet before the network stack was fully operational and how to display text in a readable fashion.

### Wait for network

The script displays the text "Please Wait" on the PiOLED screen until the network is ready. Check for network availability by checking if the Pi has an IP address. Look for the output of `hostname -I` to have a length greater than one.

### Display text effectively

We have two different display modes in this script:
- show the clock in large digits and a secondary line of information below it
- show four lines of statistics with all four lines being the same font/size

I wanted to make the function that displays the text very flexible and simple.
- 1 line: The one line is displayed as large as possible without cutting off any of the text.
- 2 lines: The first line is displayed as large as possible and then the second line is displayed as large as possible in the space remaining after the first line is displayed.
- Greater than 2 lines: Each line is displayed with the same font family and size. The function looks for the line that takes the most space on the screen and then sizes all other lines to match.