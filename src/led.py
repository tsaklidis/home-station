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


def blink(times, speed=0.2):
    for x in range(times):
        on()
        time.sleep(speed)
        off()
        time.sleep(speed)
