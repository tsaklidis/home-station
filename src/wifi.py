import os
import re


def get_signal():
    result = os.popen("iwconfig wlan0 | grep level")
    result = result.readlines()
    try:
        value = int(
            re.search(r'-?\d+', result[0].strip().split("Signal level=")[1]).group())
        return value
    except Exception as e:
        return 0
