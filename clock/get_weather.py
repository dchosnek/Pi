"""Used to display weather data for troubleshooting purposes.
"""

import urllib2
import json
import datetime
from argparse import ArgumentParser

# =============================================================================
# Globals

parser = ArgumentParser()
parser.add_argument("--settings", required=True, help="JSON file containing zip code and appid")
args = parser.parse_args()

with open(args.settings) as f:
    data = json.load(f)
ZIP = data['zip']
APPID = data['appid']
OPENWEATHER_CURRENT_URL = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&units=imperial&appid={}'.format(ZIP, APPID)
OPENWEATHER_FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast?zip={},us&units=imperial&cnt=8&appid={}'.format(ZIP, APPID)


# =============================================================================
# Main

# get current weather
result = urllib2.urlopen(OPENWEATHER_CURRENT_URL).read()
data = json.loads(result)

print "Current temperature = {}".format(data['main']['temp'])

# get forecast
result = urllib2.urlopen(OPENWEATHER_FORECAST_URL).read()
data = json.loads(result)
today = datetime.datetime.now().strftime("%Y-%m-%d")

lo = None
hi = None

for i in data['list']:
    print i['dt_txt'], i['main']['temp_min'], i['main']['temp_max']
    if today in i['dt_txt']:
        if lo is None or lo > i['main']['temp_min']:
            lo = i['main']['temp_min']
        if hi is None or hi < i['main']['temp_max']:
            hi = i['main']['temp_max']
        # print i['dt_txt'], i['main']['temp_min'], i['main']['temp_max']

print "Low and High for today = {} and {}".format(lo, hi)
