#!/usr/bin/python

import api
import sys


try:
    from credentials import saloni
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

station = api.RemoteApi()

tempr, humid, batt, batt_lvl, signal = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])

# Build gateway ingest readings - each reading has sensor_id and data dict
pack = [
    {
        "sensor_id": saloni['tempr'],
        "data": {"temperature": tempr}
    },
    {
        "sensor_id": saloni['humid'],
        "data": {"humidity": humid}
    },
    {
        "sensor_id": saloni['battery'],
        "data": {"battery_voltage": batt}
    },
    {
        "sensor_id": saloni['battery_lvl'],
        "data": {"battery_level": batt_lvl}
    },
    {
        "sensor_id": saloni['signal'],
        "data": {"signal_strength": signal}
    },
]

station.send_packet(pack)
