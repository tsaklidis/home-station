import os
import time
import datetime
import RPi.GPIO as GPIO

start_tmp = 45


class FanControl:
    pin = 23
    status_led = 24
    spinning = False

    def _prepare(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.setup(self.status_led, GPIO.OUT)
            GPIO.setwarnings(False)
        except Exception as e:
            exit(e)

    def _power_led(self, power):
        GPIO.output(self.status_led, power)

    def log(self, s):
        fileLog = open('/home/pi/Desktop/sensors/fan.log', 'a+', 0)
        t = time.time()
        stamp = datetime.datetime.fromtimestamp(
            t).strftime('%Y/%m/%d %H:%M:%S - ')
        fileLog.write(stamp + s + "\n")
        fileLog.close()

    # Resets all GPIO ports used by this program
    def exitPin(self):
        GPIO.cleanup()

    def spin(self, power):
        self._prepare()
        # Inverting passed power, check circuit to investigate
        # LOW starts the fan and HIGH stops fan
        GPIO.output(self.pin, not power)
        self.log("Fan:" + str(power) + " CPU: " + str(cpu_temp))

        self._power_led(power)
        self.spinning = power


fan = FanControl()
fan.log("######### Cooler initialized #########")
while True:
    # res has "temp=46.2'C\n"
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    cpu_temp = float((res.replace("temp=", "").replace("'C\n", "")))

    if cpu_temp > start_tmp:
        if not fan.spinning:
            fan.spin(True)
    elif fan.spinning:
        fan.spin(False)
        fan.exitPin()

    if cpu_temp > 50:
        # take some time to cool the cpu
        time.sleep(40)
    else:
        time.sleep(15)
