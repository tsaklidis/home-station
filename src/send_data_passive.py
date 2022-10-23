import api
import x_sense
import system_tempr



try:
    from credentials import saloni
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

station = api.RemoteApi()

tempr, humid, batt = x_sense.get_all_data()

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

SYS_TEMPR = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['sys_tmp'],
    "value": system_tempr.get_tempr()
}

# Some values overwrite the imports
pack = [x_tmpr, x_hum, x_batt, SYS_TEMPR]

station.send_packet(pack)

