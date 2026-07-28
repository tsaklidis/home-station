import RPi.GPIO as GPIO
import time
import pins


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pins.RELAY, GPIO.OUT)

# Ensure the relay starts in the ON state so the sensor
# is powered before any data reading takes place.
GPIO.output(pins.RELAY, GPIO.HIGH)


def on():
    GPIO.output(pins.RELAY, GPIO.HIGH)
    return True


def off():
    GPIO.output(pins.RELAY, GPIO.LOW)
    return True


def restart(pause=2):
    """Power-cycle the sensor: turn relay off, wait, turn back on."""
    off()
    time.sleep(pause)
    on()
