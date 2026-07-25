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

if len(sys.argv) >= 8:
    # Called with arguments (e.g. from LYWSD03MMC.py callback)
    tempr = float(sys.argv[3])
    humid = float(sys.argv[4])
    batt = float(sys.argv[5])
    batt_lvl = float(sys.argv[6])
    signal = float(sys.argv[7])
else:
    # Called without arguments (e.g. from cron job) - read sensors directly
    import x_sense
    tempr, humid, batt = x_sense.get_all_data()
    batt_lvl = None
    signal = None

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
]

if batt_lvl is not None:
    pack.append({
        "sensor_id": saloni['battery_lvl'],
        "data": {"battery_level": batt_lvl}
    })

if signal is not None:
    pack.append({
        "sensor_id": saloni['signal'],
        "data": {"signal_strength": signal}
    })

# Add system temperature if available
if saloni.get('sys_tmp'):
    import system_tempr
    pack.append({
        "sensor_id": saloni['sys_tmp'],
        "data": {"temperature": system_tempr.get_tempr()}
    })

station.send_packet(pack)
