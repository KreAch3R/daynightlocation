#!/usr/bin/env python3
# Author: Justin DuBois
# Modified by: KreAch3R
# Required libraries - astral, geocoder, gps, tzwhere -
# If missing, execute 'pip3 install astral/geocoder/gps/tzwhere'
# Also required: sudo apt-get install libgeos-dev
# REQUIRES internet for some functions: geocoder and sunrise-sunset.org API

import os
import datetime
import geocoder
import requests
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, date
from gps import *
from tzwhere import tzwhere

inifile="/home/pi/.openauto/config/openauto_system.ini"

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

# --------- Find today's sunrise and sunset hour and minute in location ----------------
# METHOD 1: Get longitude and latitude by right-clicking on Google Maps
# Set this to 'True'
manual=False
# UNCOMMENT and input manually
#lat=
#long=
if manual :
    print ("Setting coordinates manually")
else :
    # METHOD 2 (Default): Get latitude and longitude from GPS
    # https://ozzmaker.com/using-python-with-a-gps-receiver-on-a-raspberry-pi/
    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
    # 10 is a random repetition number that I've found produces valid results with a connected GPS
    for i in range(10):
        report = gpsd.next() #
        if report['class'] == 'TPV':
            lat = getattr(report,'lat',0.0)
            long = getattr(report,'lon',0.0)

            print ("Getting coordinates from the connected GPS device:")
            break
    else :
        print ("GPS not found")
        # METHOD 2: Get info from IP
        iplocation = geocoder.ip('me')
        print ("Getting coordinates from geocoder (device's IP):")
        lat = iplocation.latlng[0]
        long = iplocation.latlng[1]

print ("latitude", str(lat))
print ("longitude", str(long))

# Empty line
print ()

#---------- Search for sunrise and sunset values using Astral module or sunrise-sunset.org API------------------

# METHOD 1: Search for sunrise/sunset values using the Astral module
# Change this to 'False' if you want to use sunrise-sunset.org
astral=True

if astral :
    print ("Using Astral module...")
    # Find timezone from lat/long
    # https://stackoverflow.com/a/39457871/4008886
    tzwhere = tzwhere.tzwhere()
    local_tz = tzwhere.tzNameAt(lat, long)
    print ("Timezone:", local_tz)

    # City names not necessary: https://stackoverflow.com/a/65433512/4008886
    location = LocationInfo(timezone=local_tz, latitude=lat, longitude=long)
    s = sun(location.observer, date=date.today(), tzinfo=location.timezone)

    truncated_rise = (s["sunrise"]).strftime('%H:%M')
    truncated_set = (s["sunset"]).strftime('%H:%M')
else :
    # METHOD 2: Search for sunrise/sunset values using the sunrise-sunset.org API
    print ("Using sunrise-sunset.org API...")
    r = requests.get('https://api.sunrise-sunset.org/json', params={'lat': float(lat), 'lng': float(long)}).json()['results']

    # API uses UTC time!
    rise_utc = datetime.strptime(r['sunrise'], '%I:%M:%S %p')
    rise_local = datetime_from_utc_to_local(rise_utc)

    set_utc = datetime.strptime(r['sunset'], '%I:%M:%S %p')
    set_local = datetime_from_utc_to_local(set_utc)

    truncated_rise = rise_local.strftime('%H:%M')
    truncated_set = set_local.strftime('%H:%M')

print ("Sunrise (local, to be installed):", truncated_rise)
print ("Sunset (local, to be installed):", truncated_set)
print ()

#---------- Search in OAP system file for sunrise and sunset values ------------------
with open(inifile, 'r',encoding = 'utf-8') as f:
    for line in f:
        keyword = 'SunriseTime'
        if line.startswith(keyword):
            try:
                inirise = (line.split('=')[1].rstrip())
            except:
                print ("Error finding SunriseTime in openauto_system.ini")

        keyword = 'SunsetTime'
        if line.startswith(keyword):
            try:
                iniset = (line.split('=')[1].rstrip())
            except:
                print ("Error reading SunsetTime in openauto_system.ini")


# ----------- Update ini file ------------
# Read in the file
with open(inifile, 'r',encoding = 'utf-8') as file :
  filedata = file.read()

print ("Current values:")
print ('inirise =',inirise)
print ('iniset =',iniset)
print ()
print ("Changed values:")
print ('truncated_rise =',truncated_rise)
print ('truncated_set =',truncated_set)
print ()

# Replace the target string
filedata = filedata.replace('SunriseTime='+inirise, 'SunriseTime='+truncated_rise)
filedata = filedata.replace('SunsetTime='+iniset, 'SunsetTime='+truncated_set)

# Write the file out again
with open(inifile, 'w',encoding = 'utf-8') as file:
  file.write(filedata)
  print ("inifile updated successfully")
