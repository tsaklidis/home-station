import api
import system_tempr



try:
    from credentials import saloni
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc

station = api.RemoteApi()


SYS_TEMPR = {
    "space_uuid": saloni['space'],
    "sensor_uuid": saloni['sys_tmp'],
    "value": system_tempr.get_tempr()
}

# Some values overwrite the imports
pack = [SYS_TEMPR]

station.send_packet(pack)

