#!/usr/bin/python3
"""
send_data_DHT.py - Reads DHT22 sensor (temperature & humidity)
and sends to the gateway API.

The relay module ensures the sensor is powered ON at import time.
If reading fails, the relay power-cycles the sensor and retries.
"""

import api
import relay  # noqa: F401 - import ensures relay is ON before reading

try:
    from credentials import balkoni
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

try:
    import DHT22
    dht_available = True
except Exception:
    print("DHT22 sensor not available")
    dht_available = False

pack = []

if dht_available:
    temperature = DHT22.read_temp()
    humidity = DHT22.read_humidity()

    if temperature:
        pack.append({
            "sensor_id": balkoni['DHT22_T'],
            "data": {"temperature": temperature}
        })

    if humidity:
        pack.append({
            "sensor_id": balkoni['DHT22_H'],
            "data": {"humidity": humidity}
        })

if pack:
    station = api.RemoteApi()
    station.send_packet(pack)

