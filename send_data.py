import json
import time
import DHT11
import DS18B20
import led
import requests
import datetime

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

    # print response.content
    led.off()
    # samples every 5 minutes
    time.sleep(300)
