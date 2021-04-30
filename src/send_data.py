import api
import BMP280
import DHT22
import wifi
from BMP280 import get_temp as bmp_tmp

try:
    from credentials import UUIDS, balkoni
except ImportError, exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

station = api.RemoteApi()

DHT22_tmpr = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['DHTXX_T'],
    "value": DHT22.read_temp()
}
DHT22_hum = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['DHTXX'],
    "value": DHT22.read_humidity()
}

BMP280 = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['BMP280'],
    "value": BMP280.get_presure()
}

BMP280_TMP = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['BMP280_T'],
    "value": bmp_tmp(rnd=2),
}

WIFI = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['WIFI'],
    "value": wifi.get_signal()
}

# Each value overwrites the imports
pack = [DHT22_tmpr, DHT22_hum, WIFI, BMP280, BMP280_TMP]

station.send_packet(pack)
