import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led_pin = 27
GPIO.setup(led_pin, GPIO.OUT)


def on():
    GPIO.output(led_pin, GPIO.HIGH)
    return True


def off():
    GPIO.output(led_pin, GPIO.LOW)
    return True
