import api
import BMP280
import DHT22
import DS18B20

try:
    from credentials import UUIDS
except ImportError, exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

station = api.RemoteApi()

DHT22_tmpr = {
    "space_uuid": UUIDS['space'],
    "sensor_uuid": UUIDS['DHT22_tmpr'],
    "value": DHT22.read_temp(),
}
DHT22_hum = {
    "space_uuid": UUIDS['space'],
    "sensor_uuid": UUIDS['DHT22_hum'],
    "value": DHT22.read_humidity()
}
DS18B20 = {
    "space_uuid": UUIDS['space'],
    "sensor_uuid": UUIDS['DS18B20'],
    "value": DS18B20.read_temp()
}

BMP280 = {
    "space_uuid": UUIDS['space'],
    "sensor_uuid": UUIDS['BMP280'],
    "value": BMP280.get_presure()
}
# Each value overwrites the imports
pack = [DHT22_tmpr, DHT22_hum, DS18B20, BMP280]

station.send_packet(pack)
