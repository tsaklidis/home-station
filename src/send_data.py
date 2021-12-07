import api
import DHT22
import DHT11
import wifi
import system_tempr
import led


try:
    from BMP280 import get_temp as bmp_tmp, get_presure
    from DS18B20 import read_temp as ds_tmp
except IOError:
    # Temp hack for broken sensor
    bmp_tmp = lambda rnd: 0
    get_presure = lambda: 0
    ds_tmp = lambda: 0

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
led.blink(3)


DHT22_hum = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['DHTXX'],
    "value": DHT22.read_humidity()
}
led.blink(3)

DHT11_hum = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['DHT11'],
    "value": DHT11.read_humidity()
}
led.blink(3)

BMP280 = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['BMP280'],
    "value": get_presure()
}
led.blink(3)

BMP280_TMP = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['BMP280_T'],
    "value": bmp_tmp(rnd=2),
}
led.blink(3)

WIFI = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['WIFI'],
    "value": wifi.get_signal()
}
led.blink(3)

SYS_TEMPR = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['SYS_TEMPR'],
    "value": system_tempr.get_tempr()
}
led.blink(4, 0.1)

DS18B20_tmpr = {
    "space_uuid": balkoni['space'],
    "sensor_uuid": balkoni['DS18B20'],
    "value": ds_tmp()
}
led.blink(4, 0.1)


if DS18B20_tmpr['value'] > 100:
    DS18B20_tmpr['value'] = 0

# Some values overwrite the imports
pack = [DHT22_tmpr, DHT11_hum, DHT22_hum, WIFI, BMP280,
        BMP280_TMP, SYS_TEMPR, DS18B20_tmpr]

station.send_packet(pack)

