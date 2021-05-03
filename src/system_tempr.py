import os
import re


def get_tempr():
    result = os.popen("cat /sys/class/thermal/thermal_zone0/temp")
    result = result.readlines()
    try:
        value = int(
            re.search(r'-?\d+', result[0].strip().split("=")[0]).group())
        return round((value / 1000.0), 2)
    except Exception as e:
        return 0
