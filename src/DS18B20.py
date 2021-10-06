import glob
import time
# import os

# Initialize the GPIO Pins
# Add them to /etc/modules or uncomment
# w1_gpio
# w1_therm
# os.system('modprobe w1-gpio')  # Turns on the GPIO module
# os.system('modprobe w1-therm')  # Turns on the Temperature module

# Finds the correct device file that holds the temperature data
base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')[0]
except (ValueError, IndexError):
    print('No sensor found from DS18B20 module')

device_file = device_folder + '/w1_slave'

# A function that reads the sensors data


def read_temp_raw():
    f = open(device_file, 'r')  # Opens the temperature device file
    lines = f.readlines()  # Returns the text
    f.close()
    return lines


# Convert the value of the sensor into a temperature
def read_temp():
    lines = read_temp_raw()  # Read the temperature 'device file'

    # While the first line does not contain 'YES', wait for 0.2s
    # and then read the device file again.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # Look for the position of the '=' in the second line of the
    # device file.
    equals_pos = lines[1].find('t=')

    # If the '=' is found, convert the rest of the line after the
    # '=' into degrees Celsius, then degrees Fahrenheit
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return round(temp_c, 2)

