# Import Libraries
import time
import DHT22
import DS18B20
import led


while True:
    try:
        led.on()
        print 'DS18B20:', DS18B20.read_temp(), '*C'
        print 'DHT22: {0}*C, {1}%'.format(DHT22.read_temp(), DHT22.read_humidity())
        led.off()
        time.sleep(2)
    except KeyboardInterrupt:
        print '\nStoped by user'
        break
