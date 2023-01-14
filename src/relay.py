import RPi.GPIO as GPIO
import time
import pins


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pins.RELAY, GPIO.OUT)


def on():
    GPIO.output(pins.RELAY, GPIO.HIGH)
    return True


def off():
    GPIO.output(pins.RELAY, GPIO.LOW)
    return True
