from bluepy import btle
from time import sleep
import binascii





def get_all_data():
  address = "A4:C1:38:AB:CA:21"
  sensor = ReadXiaoMi()
  p = btle.Peripheral( )
  p.setDelegate( sensor )

  try:
    p.connect(address)
    p.waitForNotifications(30.0)
  except Exception as e:
    print(e)
  finally:
    p.disconnect()
    return sensor.temp, sensor.humid, sensor.battery


class ReadXiaoMi(btle.DefaultDelegate):
    temp = 0
    humid = 0
    battery = 0
    databytes = ''

    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        self.databytes = bytearray(data)
        self.temp = int.from_bytes(self.databytes[0:2],"little")/100
        self.humid = int.from_bytes(self.databytes[2:3],"little")
        self.battery = int.from_bytes(self.databytes[3:5],"little")/1000

    def get_temp(self):
      return self.temp

    def get_humid(self):
      return self.humid

    def get_batt(self):
      return self.battery

    def get_databytes(self):
      return self.databytes

    def print_data(self):
        print('Databytes: {0}'.format(binascii.hexlify(self.databytes)))
        print('Temperature: {0}'.format(self.temp))
        print('Humidity: {0}'.format(self.humid))
        print('Battery: {0}'.format(self.battery))
