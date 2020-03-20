# Import Libraries
import time
import DHT22
import DS18B20
import led
import BMP280


while True:
    try:
        led.on()
        print 'DS18B20:', DS18B20.read_temp(), '*C'
        print 'DHT22: {0}*C'.format(DHT22.read_temp())
        time.sleep(2)
        print 'DHT22: {}%'.format(DHT22.read_humidity())
        print 'BMP280: {}\n'.format(BMP280.print_all_data())
        led.off()
        time.sleep(2)
    except KeyboardInterrupt:
        print '\nStoped by user'
        break
