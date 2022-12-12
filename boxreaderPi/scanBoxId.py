"""
Connecting to the PN532 and reading an M1
"""

import RPi.GPIO as GPIO

import pn532.pn532 as nfc
from pn532 import *

# pn532 = PN532_SPI(cs=4, reset=20, debug=False)
# pn532 = PN532_I2C(debug=False, reset=20, req=16)
pn532 = PN532_UART(debug=False, reset=20)

ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

print('Waiting for RFID/NFC card to read from!')
while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print('.', end="")
    # Try again if no card is available.
    if uid is not None:
        break
print('Found card with UID:', [hex(i) for i in uid])

key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

try:
  pn532.mifare_classic_authenticate_block(uid, block_number=6, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
  print("Box ID:", pn532.mifare_classic_read_block(6).decode())
except nfc.PN532Error as e:
  print(e.errmsg)
finally:
  GPIO.cleanup()
