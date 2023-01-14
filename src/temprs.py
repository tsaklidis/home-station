# Import Libraries
import time
import DHT22
import DS18B20
import led
import BMP280


# while True:
#     try:
#         # led.on()
#         print 'DS18B20:', DS18B20.read_temp(), '*C'
#         print 'DHT22: {0}*C'.format(DHT22.read_temp())
#         time.sleep(2)
#         print 'DHT22: {}%'.format(DHT22.read_humidity())
#         print 'BMP280: {}\n'.format(BMP280.print_all_data())
#         led.off()
#         time.sleep(2)
#     except KeyboardInterrupt:
#         print '\nStoped by user'
#         break


while True:
    try:
        print '######################'
        print 'DS18B20 | DHT22 | BMP280 \n'
        ds = DS18B20.read_temp()
        time.sleep(1)

        dh = DHT22.read_temp()
        time.sleep(1)

        bm = round(BMP280.get_temp(), 2)
        time.sleep(1)

        print '{}*C , {}*C, {}*C \n'.format(ds ,dh, bm)
        print '######################\n\n'
        time.sleep(1)
    except KeyboardInterrupt:
        print '\nStoped by user'
        break
    except Exception as e:
        print e.message
