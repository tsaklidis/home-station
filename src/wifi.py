import os
import re


def get_signal():
    result = os.popen("iwconfig wlan0 | grep level")
    result = result.readlines()
    return int(re.search(r'-?\d+', result[0].strip().split("Signal level=")[1]).group())
