#!/usr/bin/python


"""
Connecting to the PN532 and reading an M1
"""

import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import time
import sys
from pn532 import *
import os
from serverUtils import *
from utils import *


def configurePN532():
  pn532 = PN532_UART(debug=False, reset=20)
  pn532.SAM_configuration()
  ic, ver, rev, support = pn532.get_firmware_version()
  successMessage = 'Configuration Success - Found PN532 with firmware version: {0}.{1}'.format(ver, rev) 

  print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
  sendMessageToServer(buildPacket(200, "", successMessage))
  return pn532

def awaitRFID(pn532):
  print('Waiting for RFID to read from!')
  sendMessageToServer(buildPacket(200, "", 'Waiting for RFID to read from!'))

  while True:
      # Check if a card is available to read
      uid = pn532.read_passive_target(timeout=0.5)

      # Try again if no card is available.
      if uid is not None:
          break
  print('Found card with UID:', [hex(i) for i in uid])
  return uid

def readBlock(uid, block_number):
  key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

  try:
    pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
    # decode the bytes and remove any empties at the end
    return pn532.mifare_classic_read_block(block_number).decode().rstrip('\x00')
  except nfc.PN532Error as e:
    print(e.errmsg)
  finally:
    GPIO.cleanup()
     
# Main
if __name__ =="__main__":
  
  # Configure pn532
  pn532 = configurePN532()

  # RFID loop
  while True:
    try:
      # Await an RFID and read blocks once presented
      uid = awaitRFID(pn532)
      boxId = readBlock(uid, 6) + readBlock(uid, 8)

      # Find Location
      latlng = findCoordFromIP(os.environ.get("IPLOOKUPKEY"))
      location = findLocation(os.environ.get("GOOGLEMAPSKEY"), latlng)
      
      # Compile data for server
      locationData = {
        'boxId' : boxId,
        'location' : parseLocation(location)
      }

      
      # Data as Json to server
      sendLocationUpdateToServer(buildPacket(200, locationData, 'Successful Read'))
      sendMessageToServer(buildPacket(200, locationData, 'Sent Location Update to Server'))
    except BaseException as e:
      errorMessage = str(e)
      print(errorMessage)
      sendMessageToServer(buildPacket(500, errorMessage, 'Error'))
    
    print('cooldown')
    GPIO.cleanup()
    time.sleep(3)
