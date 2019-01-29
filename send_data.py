import DHT11
import DS18B20
import datetime
# import pickle
import json
import led
import requests
import time
# import os


# url = 'http://192.168.1.2/sensors/catch.php'
url = 'https://tsaklidis.gr/home/catch.php'

# wait for wifi after reboot
# and show I am waiting
for i in xrange(0, 9):
    led.on()
    time.sleep(.500)
    led.off()
    time.sleep(.500)

while True:

    data = {}
    data['DHT11'] = []
    data['DS18B20'] = []

    dt = datetime.datetime.now()
    data['DHT11'].append({
        'date': dt.strftime('%d-%b-%Y'),
        'time': dt.strftime('%H:%M'),
        'tempr': DHT11.read_temp(),
        'humidity': DHT11.read_humidity()
    })

    data['DS18B20'].append({
        'date': dt.strftime('%d-%b-%Y'),
        'time': dt.strftime('%H:%M'),
        'tempr': DS18B20.read_temp()
    })

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive',
               'content-type': 'application/json'
               }

    led.on()
    response = requests.post(
        url, data=json.dumps(data), headers=headers)

    # Prevent data lose
    # if response.status_code == 201:
    #     led.off()
    # else:
    #     with open('/home/pi/Desktop/sensors/not_sent.pkl', 'a+') as handle:
    #         pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # if os.stat("/home/pi/Desktop/sensors/not_sent.pkl").st_size > 0:  # check if file is not empty
    #     with open('/home/pi/Desktop/sensors/not_sent.pkl', 'rb') as f:
    #         loaded_data = pickle.load(f)

    #     response = requests.post(
    #         url, data=json.dumps(loaded_data), headers=headers)

    #     if response.status_code == 201:
    #         led.off()
    #         # overwrite it with emptyness
    #         open('/home/pi/Desktop/sensors/not_sent.pkl', 'w').close()
    led.off()
    # print response.content
    # samples every 5 minutes
    time.sleep(300)