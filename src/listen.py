import api
import json
import paho.mqtt.client as mqtt
from credentials import mosq

import datetime
import os

# runing from /etc/systemd/system/listen.service
# sudo service listen stop | start | status

try:
    from credentials import balkoni
except ImportError, exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc


def _log(er, file=None):
    the_path = os.path.dirname(os.path.abspath(__file__))
    if file:
        the_file = the_path + '/logs/' + file
    else:
        the_file = the_path + '/logs/errors.log'
    with open(the_file, 'a+') as outfile:
        log_time = datetime.datetime.now()
        outfile.write(log_time.strftime('%Y-%m-%d %H:%M:%S'))
        outfile.write('\n')
        json.dump(er, outfile)
        outfile.write('\n\n')


rc_map = {
    "0": "Connection successful",
    "1": "Connection refused - incorrect protocol version",
    "2": "Connection refused - invalid client identifier",
    "3": "Connection refused - server unavailable",
    "4": "Connection refused - bad username or password",
    "5": "Connection refused - not authorised",
    # 6-255: Currently unused
}

esp32 = api.RemoteApi()


def on_connect(client, userdata, flags, rc):
    print("Connected With Result Code " (rc))


def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected, reason:{}".format(rc_map[rc]))


def on_message_from_pack(client, userdata, message):
    # print("house/balkoni/temperature: " + message.payload.decode())
    # Example data is:
    # data = {
    #   "BATTERY": 100,
    #   "DS18B20": 22.9375,
    #   "DHTXX": 62,
    #   "WIFI": -64
    # }
    try:
        data = json.loads(message.payload.decode())
    except KeyError:
        data = None

    # DS18B20 = {
    #     "space_uuid": balkoni['space'],
    #     "sensor_uuid": balkoni['DS18B20'],
    #     "value": data['value'],
    #     "volt": data['volt']
    # }
    if data:
        pack = []
        for sensor, value in data.items():
            try:
                _log({"data: ": '{}'.format(value)}, file='errors.log')
                tmp = {
                    "space_uuid": balkoni['space'],
                    "sensor_uuid": balkoni[sensor],
                    "value": round(float(value), 2) if value else 0,
                }
                pack.append(tmp)
            except Exception as e:
                _log({"listen_error": '{}'.format(e.message)}, file='errors.log')

        esp32.send_packet(pack)
    else:
        print("Wrong data:")
        print(message.payload.decode())


# def on_message_from_humidity(client, userdata, message):
#     # print("house/balkoni/presure: " + message.payload.decode())

#     DHT11 = {
#         "space_uuid": balkoni['space'],
#         "sensor_uuid": balkoni['DHT11'],
#         "value": message.payload.decode()
#     }
#     pack = [DHT11, ]

#     esp32.send_packet(pack)


# def on_message(client, userdata, message):
#     print("Message Recieved from Others: " + message.payload.decode())


broker_url = "192.168.1.251"
broker_port = 1883

client = mqtt.Client()

client.username_pw_set(mosq['username'], mosq['password'])

client.on_connect = on_connect
client.on_disconnect = on_disconnect
# client.on_message = on_message


client.connect(broker_url, broker_port)
# sudo service listen restart has a 10sec delay,
# in order to avoid that use this try/except or use [Unit] Before After Wants
# try:
#     client.connect(broker_url, broker_port)
# except Exception as e:
#     import time
#     time.sleep(5)
#     client.connect(broker_url, broker_port)

# to publish use:
# client.publish(topic="house/balkoni", payload="TestingPayload", qos=0, retain=False) # noqa


# subscribe to multiple topics:
# topics = [('house/balkoni/pack', 1), ('house/balkoni/humidity', 1)]
# client.subscribe(topics)

client.subscribe('house/balkoni/pack', qos=1)

client.message_callback_add(
    'house/balkoni/pack', on_message_from_pack)

# client.message_callback_add(
#     'house/balkoni/humidity', on_message_from_humidity)

client.loop_forever()
