import api
import DHT22
import wifi
import system_tempr
try:
    from BMP280 import get_temp as bmp_tmp, get_presure
except IOError:
    # Temp hack for broken sensor
    bmp_tmp = lambda x: 0
    get_presure = lambda x: 0

try:
    from credentials import balkoni
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
    "value": get_presure()
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

SYS_TEMPR = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['SYS_TEMPR'],
    "value": system_tempr.get_tempr()
}

# Some values overwrite the imports
pack = [DHT22_tmpr, DHT22_hum, WIFI, BMP280, BMP280_TMP, SYS_TEMPR]

station.send_packet(pack)
