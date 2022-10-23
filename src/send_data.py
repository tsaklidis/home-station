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

x_tmpr = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['tempr'],
    "value": tempr
}


x_hum = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['humid'],
    "value": humid
}

x_batt = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['battery'],
    "value": batt
}

x_batt_lvl = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['battery_lvl'],
    "value": batt_lvl
}

x_signal = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['signal'],
    "value": signal
}



# Some values overwrite the imports
pack = [x_tmpr, x_hum, x_batt, x_batt_lvl, x_signal]

station.send_packet(pack)
