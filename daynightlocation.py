#!/usr/bin/env python3
# Author: Justin DuBois
# Required library - astral -
# If missing, execute 'pip3 install astral'

import os
import datetime
from datetime import datetime
from datetime import date
from astral import LocationInfo
from astral.sun import sun

inifile="/home/pi/.openauto/config/openauto_system.ini"

# --------- Find today's sunise and sunset hour and minuet in city location ----------------
city = LocationInfo("San Francisco", "Pacific", "America/Los_Angeles", 37.77397, -122.431297)
#print((
#    f"Information for {city.name}/{city.region}\n"
#    f"Timezone: {city.timezone}\n"
#    f"Latitude: {city.latitude:.02f}; Longitude: {city.longitude:.02f}\n"
#))

s = sun(city.observer, date=date.today(), tzinfo=city.timezone)
csrise = (s["sunrise"]).strftime('%H:%M')
csset = (s["sunset"]).strftime('%H:%M')

#-- search in OAP system file for sunrise and sunset values --
with open(inifile, 'r',encoding = 'utf-8') as f:
    for line in f:
        keyword = 'SunriseTime'
        if line.startswith(keyword):
            try:
                inisunrise = (line.split('=')[1].rstrip())
            except:
                print ("Error finding SunriseTime in openauto_system.ini")
       
        keyword = 'SunsetTime'
        if line.startswith(keyword):
            try:
                inisunset = (line.split('=')[1].rstrip())
            except:
                print ("Error reading SunsetTime in openauto_system.ini")


# ----------- Update ini file ------------
# Read in the file
with open(inifile, 'r',encoding = 'utf-8') as file :
  filedata = file.read()

#print('inisunrise=',inisunrise)
#print('csrise=',csrise)
#print('inisunset=',inisunset)
#print('csset=',csset)

# Replace the target string
filedata = filedata.replace('SunriseTime='+inisunrise, 'SunriseTime='+csrise)
filedata = filedata.replace('SunsetTime='+inisunset, 'SunsetTime='+csset)

# Write the file out again
with open(inifile, 'w',encoding = 'utf-8') as file:
  file.write(filedata)