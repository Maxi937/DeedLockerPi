# Description

Python scripts to read and write to an RFID Tag.
Uses UART interface to communicate.
Pi serial interface needs to be configured if re-imaged.

## Warning

DO NOT write the blocks of 4N+3 (3, 7, 11, ..., 63)
or else you will change the password for blocks 4N ~ 4N+2.

Note:

1.  The first 6 bytes (KEY A) of the 4N+3 blocks are always shown as 0x00,
    since 'KEY A' is unreadable. In contrast, the last 6 bytes (KEY B) of the
    4N+3 blocks are readable.
2.  Block 0 is unwritable.

<br>

## Resources

| Description                   | Source                                                                                    |
| ----------------------------- | ----------------------------------------------------------------------------------------- |
| package requirements overview | <https://www.raspberrypi.com/newread-rfid-and-nfc-tokens-with-raspberry-pi-hackspace-37/> |
| code examples                 | <https://www.waveshare.com/wiki/PN532_NFC_HAT#Raspberry_Pi_examples>                      |
| layout of Mifare Blocks/Bytes | <https://www.waveshare.com/w/upload/c/c7/MF1S50YYX_V1.pdf>                                |
