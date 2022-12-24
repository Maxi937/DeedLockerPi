import requests
from dotenv import load_dotenv
import os

def buildPacket(code, data, message):
  packet = {
    'code' : code,
    'data' : data,
    'message' : message
  }
  return packet

def sendMessageToServer(packet):
  route = '/deedlockerPi/rpiMessage'
  url = f'{os.environ.get("DEEDLOCKERNODESERVERURL")}{route}'

  try:
    requests.post(url, json=packet)
  except BaseException as e:
    print(e)

def sendLocationUpdateToServer(packet):
  route = '/deedlockerPi/updateLocation'
  url = f'{os.environ.get("DEEDLOCKERNODESERVERURL")}{route}'

  try:
    requests.post(url, json=packet)
  except BaseException as e:
    print(e)

def sendRfidUpdateToServer(packet):
  route = '/deedlockerPi/updateRfid'
  url = f'{os.environ.get("DEEDLOCKERNODESERVERURL")}{route}'

  try:
    requests.post(url, json=packet)
  except BaseException as e:
    print(e)
