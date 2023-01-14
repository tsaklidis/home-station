import time

DS18B20="/sys/bus/w1/devices/28-3c01a816c7f4/w1_slave"


def read_temp():
    r = 0
    while True:

       r += 1

       f = open(DS18B20, "r")
       data = f.read()
       f.close()

       (discard, sep, reading) = data.partition(' t=')

       return float(reading) / 1000.0
