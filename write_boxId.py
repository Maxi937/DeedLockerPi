import RPi.GPIO as GPIO
import pn532.pn532 as nfc
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

  #print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
  sendMessageToServer(buildPacket(200, "", successMessage))
  return pn532

def awaitRFID(pn532):
  #print('Waiting for RFID to Write To!')
  sendMessageToServer(buildPacket(200, "", 'Waiting for RFID to Write To!'))

  while True:
      # Check if a card is available to read
      uid = pn532.read_passive_target(timeout=0.5)

      # Try again if no card is available.
      if uid is not None:
          break
  #print('Found card with UID:', [hex(i) for i in uid])
  return uid


# Write to block - data must be 16 bytes !! do not write to 4N+3 (3, 7, 11, ..., 63) or else passwords will be changed
def writeToBlock(uid, block_number, data):
  sendMessageToServer(buildPacket(200, "", f'Writing {data.decode()} to block {block_number}'))
  #print("Writing to Block", block_number, "on", uid.decode())
  key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
  
  try:
    pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
    pn532.mifare_classic_write_block(block_number, data)
    if pn532.mifare_classic_read_block(block_number) == data:
      sendMessageToServer(buildPacket(200, "", 'write block %d successfully' % block_number))
      #print('write block %d successfully' % block_number)
  except nfc.PN532Error as e:
      print(e.errmsg)
  finally:
    GPIO.cleanup()
  

# Main
if __name__ =="__main__":
  boxId = sys.argv[1]
 
  sendMessageToServer(buildPacket(200, "", f'Writing {boxId} to RFID'))

  pn532 = configurePN532()
  payload = parseBytes(boxId)

  # Write Loop
  while True:
    uid = awaitRFID(pn532)

    try:
      writeToBlock(uid, 6, payload['frame1'])
      writeToBlock(uid, 8, payload['frame2'])

      # Compile data for server
      rfidData = {
        'status' : 'OK',
        'rfid' : uid.decode(),
        'boxId' : boxId
      }
      sendRfidUpdateToServer(buildPacket(200, rfidData, f'Successfully Wrote {boxId} to RFID'))
      break
    except BaseException as e: 
      errorMessage = str(e)
      print(e)
      sendMessageToServer(buildPacket(500, errorMessage, 'Error'))
      continue
    finally:
      GPIO.cleanup()
  
  exit(0)


      

 



