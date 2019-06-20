import Adafruit_DHT

# Physical pin 11 BCM pin 17
dht_pin = 17
sensor = Adafruit_DHT.DHT22


# humidity, temperature = 65, 20
def read_humidity():
    data = Adafruit_DHT.read_retry(sensor, dht_pin)
    return data[0]


def read_temp():
    data = Adafruit_DHT.read_retry(sensor, dht_pin)
    return data[1]
