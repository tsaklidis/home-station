import api
import json
import paho.mqtt.client as mqtt
from credentials import mosq

# runing from /etc/systemd/system/listen.service
# sudo service listen stop | start | status

try:
    from credentials import balkoni
except ImportError, exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc


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


def on_message_from_temperature(client, userdata, message):
    # print("house/balkoni/temperature: " + message.payload.decode())
    data = json.loads(message.payload.decode())

    DS18B20 = {
        "space_uuid": balkoni['space'],
        "sensor_uuid": balkoni['DS18B20'],
        "value": data['value'],
        "volt": data['volt']
    }
    pack = [DS18B20, ]

    esp32.send_packet(pack)


def on_message_from_presure(client, userdata, message):
    # print("house/balkoni/presure: " + message.payload.decode())

    BMP280 = {
        "space_uuid": balkoni['space'],
        "sensor_uuid": balkoni['BMP280'],
        "value": message.payload.decode()
    }
    pack = [BMP280, ]

    esp32.send_packet(pack)


def on_message(client, userdata, message):
    print("Message Recieved from Others: " + message.payload.decode())


broker_url = "192.168.1.251"
broker_port = 1883

client = mqtt.Client()

client.username_pw_set(mosq['username'], mosq['password'])

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message


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

# subscribe to single topic:
# client.subscribe('house/balkoni/temperature', qos=1)

topics = [('house/balkoni/temperature', 1), ('house/balkoni/presure', 1)]
client.subscribe(topics)

client.message_callback_add(
    'house/balkoni/temperature', on_message_from_temperature)

client.message_callback_add(
    'house/balkoni/presure', on_message_from_presure)

client.loop_forever()
