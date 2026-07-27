#!/usr/bin/python
"""
send_data.py - Reads wired sensors (BMP280, DS18B20, WiFi, system temp)
and sends to the gateway API.

BLE sensors (saloni/living room) are handled separately by pitoula's
LYWSD03MMC.py cron job - no need to duplicate here.
"""

import api

try:
    from credentials import balkoni
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

import system_tempr
import wifi

try:
    import BMP280
    bmp_available = True
except Exception:
    bmp_available = False

try:
    from DS18B20 import read_temp as ds_tmp
    ds_available = True
except (IOError, IndexError):
    print("No sensor found from DS18B20 module")
    ds_available = False

# Build readings from wired sensors only - all instant, no BLE wait
pack = []

if bmp_available:
    pack.append({
        "sensor_id": balkoni['BMP280'],
        "data": {"pressure": BMP280.get_presure()}
    })
    pack.append({
        "sensor_id": balkoni['BMP280_T'],
        "data": {"temperature": BMP280.get_temp(rnd=2)}
    })

if ds_available:
    pack.append({
        "sensor_id": balkoni['DS18B20'],
        "data": {"temperature": ds_tmp()}
    })

pack.append({
    "sensor_id": balkoni['WIFI'],
    "data": {"signal_strength": wifi.get_signal()}
})

pack.append({
    "sensor_id": balkoni['SYS_TEMPR'],
    "data": {"temperature": system_tempr.get_tempr()}
})

if pack:
    station = api.RemoteApi()
    station.send_packet(pack)
