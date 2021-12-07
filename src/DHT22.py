import pins
import Adafruit_DHT
import relay
import time

# Physical pin 11 BCM pin 17
dht_pin = pins.DHT22
sensor = Adafruit_DHT.DHT22



def restart_relay():
    relay.off()
    time.sleep(2)
    relay.on()


# humidity, temperature = 65, 20
def read_humidity(attempts=0):
    data = Adafruit_DHT.read_retry(sensor, dht_pin)
    try:
        return round(data[0], 2)
    except Exception as e:
        if attempts < 3:
            restart_relay()
            read_humidity(attempts + 1)
        else:
            return 0


def read_temp(attempts=0):
    data = Adafruit_DHT.read_retry(sensor, dht_pin)
    try:
        return round(data[1], 2)
    except Exception as e:
        if attempts < 3:
            restart_relay()
            read_temp(attempts + 1)
        else:
            return 0

