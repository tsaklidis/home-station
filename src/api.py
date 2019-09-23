from credentials import auth
import requests
import json
import led

base_url = 'https://logs.tsaklidis.gr/api/'
url = {
    'ms_new': base_url + 'measurement/new/', 
    'ms_list_all': base_url + 'measurement/list/all/',
    'ms_pack_new': base_url + 'measurement/pack/new/',
    'token_new': base_url + 'token/expiring/new/',
    'token_persist_new': base_url + 'token/persistent/new/',
}
headers = {
    'User-Agent': 'rpi_station',
    'Content-Type': 'application/json',
}

class RemoteApi:

    TOKEN = ''

    def _get_token(self, persistent=False):


        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi"
        }

        led.on()
        if persistent:
            # Ask for persistent token
            response = requests.post(url['token_persist_new'],
                                        data=json.dumps(body), headers=headers)
            if response.status_code == 201:
                led.off()
                return response.json()['token']
            if response.status_code == 403:
                # No permissions for persistent token, ask for expiring
                led.off()
                return response.json()
            else:
                led.off()
                return False
        else:
            # Ask for expiring token
            response = requests.post(url['token_new'],
                                        data=json.dumps(body), headers=headers)
            if response.status_code == 201:
                led.off()
                return response.json()['token']
            else:
                led.off()
                return response.json()

    def _store_token(self, token):
        with open('token.txt', 'w') as outfile:
            d = {"token":token}
            json.dump(d, outfile)

    def _load_token(self):
        try:
            with open('token.txt') as json_file:
                data = json.load(json_file)
                try:
                    return data['token']
                except KeyError:
                    return False
        except IOError, ValueError:
            return False

    def send_packet(self, measurement):
        # measurement = [
        #     {"space_uuid":"97db","sensor_uuid":"6a41", "value":26},
        #     {"space_uuid":"ff3","sensor_uuid":"836f", "value":266}
        # ]
        led.on()
        response = requests.post(url['ms_pack_new'],
                                data=json.dumps(measurement), headers=headers)
        led.off()
        
        # TODO
        # Prevent data loss


    def __init__(self):
        # Try to load local token
        self.TOKEN = self._load_token()
        
        if not self.TOKEN:
            #  No local token, ask for new
            res = self._get_token(persistent=False)
            if isinstance(res, basestring):
                # We have a valid token, save it
                self.TOKEN = res
                self._store_token(res)
            else:
                # Got smth else, save the msg from API
                with open('errors.txt', 'a+') as outfile:
                    json.dump(res, outfile)
                    outfile.write('\n')



          