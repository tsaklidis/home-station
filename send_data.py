import DHT11
import DS18B20
import datetime
import json
import time
import led
import os
import requests


# url = 'http://192.168.1.2/sensors/catch.php'
url = 'https://tsaklidis.gr/home/catch.php'


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

    # headers = {'content-type': 'application/json'}

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
    if response.status_code == 201:
        led.off()
    else:
        with open('not_sent.json', 'a+') as file:
            file.write(json.dumps(data))

    if os.stat("not_sent.json").st_size == 0:  # check if file is empty
        with open('not_sent.json') as f:
            data = json.load(f)
            response = requests.post(
                url, data=json.dumps(data), headers=headers)

            if response.status_code == 201:
                led.off()
                # overwrite it with emptyness
                open('not_sent.json', 'w').close()

    # print response.content
    # samples every 5 minutes
    time.sleep(3)
