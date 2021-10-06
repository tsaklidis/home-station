import RPi.GPIO as GPIO
import time
import pins


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pins.LED, GPIO.OUT)


def on():
    GPIO.output(pins.LED, GPIO.HIGH)
    return True


def off():
    GPIO.output(pins.LED, GPIO.LOW)
    return True


def blink(times):
    for x in range(times):
        on()
        time.sleep(0.2)
        off()
        time.sleep(0.2)
