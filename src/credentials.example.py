# Server base URL (no trailing slash)
BASE_URL = "https://logs.tsaklidis.gr/api/v1"

# Gateway key for your home (obtained from POST /homes/<uuid>/gateway-key/)
# This authenticates the Raspberry Pi as a gateway for all sensors in the home.
GATEWAY_KEY = "gw_YOUR_GATEWAY_KEY_HERE"

# JWT credentials (only needed for management operations, not for data ingestion)
auth = {
    "username": "your_username",
    "password": "your_pass"
}

# Sensor mappings: each room/space maps sensor names to their UUIDs
# The UUIDs are obtained when registering sensors via the API.
saloni = {
    "tempr": "sensor-uuid-for-temperature",
    "humid": "sensor-uuid-for-humidity",
    "battery": "sensor-uuid-for-battery-voltage",
    "battery_lvl": "sensor-uuid-for-battery-level",
    "signal": "sensor-uuid-for-signal-strength",
    "sys_tmp": "sensor-uuid-for-system-temperature",
}
