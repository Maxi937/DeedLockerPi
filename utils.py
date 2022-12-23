import sys
import requests
import time
from pn532 import *
from dotenv import load_dotenv
import os
import json
import googlemaps
import re
import math

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

# Take in a string, parse to bytes - fill remainder of last 16 with empties
def parseBytes(stringToParse):
  payload = {}
  frameSize = 16
  encodedString = stringToParse.encode('utf-8')
  numberOfFrames = math.ceil(len(encodedString) / 16)

  #print("String Length:", len(stringToParse))
  #print("Frame Size:", frameSize)
  #print("Frames Required:", numberOfFrames, "\n")

  for i in range(1, numberOfFrames+1):
    frameName = f"frame{i}"

    frame = bytearray(encodedString[(i-1)*frameSize:frameSize*i])

    while len(frame) < 16:
      frame.extend(bytes(1))

    payload.update({ frameName: frame})

  return payload