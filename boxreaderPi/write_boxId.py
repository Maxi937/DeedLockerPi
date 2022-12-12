"""
Warning: DO NOT write the blocks of 4N+3 (3, 7, 11, ..., 63)
or else you will change the password for blocks 4N ~ 4N+2.

Note: 
1.  The first 6 bytes (KEY A) of the 4N+3 blocks are always shown as 0x00,
since 'KEY A' is unreadable. In contrast, the last 6 bytes (KEY B) of the 
4N+3 blocks are readable.
2.  Block 0 is unwritable. 
"""
import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import math
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

# Take in a string, parse to bytes - fill last 16 with empties
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

# Write to block - data must be 16 bytes !! do not write to 4N+3 (3, 7, 11, ..., 63) or else passwords will be changed
def writeToBlock(uid, block_number, data):
  print("Writing to Block", block_number, "on", uid.decode())
  key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
  
  try:
    pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
    pn532.mifare_classic_write_block(block_number, data)
    if pn532.mifare_classic_read_block(block_number) == data:
      print('write block %d successfully' % block_number)
  except nfc.PN532Error as e:
      print(e.errmsg)
  finally:
    GPIO.cleanup()
  

# Main
if __name__ =="__main__":
  #Cnvert String to Bytes
  pn532 = configurePN532()
  payload = parseBytes("6376ab5763848432ea56a1c6")
  
  uid = awaitRFID(pn532)

  writeToBlock(uid, 6, payload['frame1'])
  writeToBlock(uid, 8, payload['frame2'])

  GPIO.cleanup()

 



