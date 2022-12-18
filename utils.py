import sys
import requests
import time
from pn532 import *
from dotenv import load_dotenv
import os
import json
import googlemaps
import re

def findCoordFromIP(ipLookupApiKey):
  url = f'https://extreme-ip-lookup.com/json/?key={ipLookupApiKey}'
  r = requests.get(url)
  data = json.loads(r.content.decode())
  return f'{data["lat"]},{data["lon"]}'

def findLocation(googleMapsApiKey, latlng):
  gmaps = googlemaps.Client(key=googleMapsApiKey)
  reverse_geocode_result = gmaps.reverse_geocode(latlng)
  location = reverse_geocode_result[0]["formatted_address"]
  return location

def parseLocation(locationAsString):
  result = {}
  addressLineNumber = 0
  strAsList = locationAsString.split(', ')
  eircodePattern = "\w\d\d\s[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]|\w\d\d[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]"

  for i, line in enumerate(strAsList):
    if re.search(eircodePattern, line):
      result["eircode"] = line
    elif line == "Ireland":
      result["county"] = line
    else:
      addressLineNumber = addressLineNumber + 1
      addressLine = f'addressline{addressLineNumber}'
      result[addressLine] = line
  
  return result
