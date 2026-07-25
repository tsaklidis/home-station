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

# Build gateway ingest readings — each reading has sensor_id and data dict
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
        "sensor_id": saloni['sys_tmp'],
        "data": {"temperature": system_tempr.get_tempr()}
    },
]

station.send_packet(pack)
