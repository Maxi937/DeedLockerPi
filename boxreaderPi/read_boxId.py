"""
Connecting to the PN532 and reading an M1
"""

import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *


def configurePN532():
  pn532 = PN532_UART(debug=False, reset=20)
  pn532.SAM_configuration()

  ic, ver, rev, support = pn532.get_firmware_version()
  print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

  return pn532

def awaitRFID(pn532):
  print('Waiting for RFID/NFC card to write to!')
  while True:
      # Check if a card is available to read
      uid = pn532.read_passive_target(timeout=0.5)
      print('.', end="")
      # Try again if no card is available.
      if uid is not None:
          break
  print('Found card with UID:', [hex(i) for i in uid])

  return uid

def readBlock(uid, block_number):
  key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

  try:
    pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
    print("Block:", block_number, pn532.mifare_classic_read_block(block_number).decode())
    return pn532.mifare_classic_read_block(block_number).decode()
  except nfc.PN532Error as e:
    print(e.errmsg)
  finally:
    GPIO.cleanup()

    
# Main
if __name__ =="__main__":
  pn532 = configurePN532()
  uid = awaitRFID(pn532)

  data = readBlock(uid, 6) + readBlock(uid, 8)

  print(data)

