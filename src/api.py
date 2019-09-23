import json
import led
import os
import requests

from credentials import auth

the_path = os.path.dirname(os.path.abspath(__file__))

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

    def _log_error(self, er):
        with open(the_path + '/errors.txt', 'a+') as outfile:
            json.dump(er, outfile)
            outfile.write('\n')

    def _get_token(self, persistent=False):
        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi"
        }
        
        if persistent:
            hit_url = url['token_persist_new']
        else:
            hit_url = url['token_new']

        led.on()
        response = requests.post(hit_url,
                                    data=json.dumps(body), headers=headers)
        if response.status_code == 201:
            led.off()
            return response.json()['token']
        if response.status_code == 403:
            led.off()
            return response.json()
        if response.status_code == 409:
            self._remind_token()
        else:
            led.off()
            return False

    def _remind_token(self):
        # {"error": "Valid token with same name exists"}
        pass

    def _store_token(self, token):
        with open(the_path + '/token.txt', 'w') as outfile:
            d = {"token":token}
            json.dump(d, outfile)

    def _load_token(self):
        try:
            with open(the_path + '/token.txt') as json_file:
                data = json.load(json_file)
                try:
                    token = data['token']
                    # Token loaded, check if it's valid
                    if self._validate_token():
                        # Token is valid, return it, add to headers
                        headers['Authorization'] = 'Token {}'.format(self.TOKEN)
                        return token
                    else:
                        # Take actions for invalid/expired token
                        pass
                except KeyError:
                    return False
        except IOError, ValueError:
            return False

    def _validate_token(self, token):
        return True

    def _init_token(self):
        # Try to load local token from token.txt file
        try:
            with open(the_path + '/token.txt') as json_file:
                data = json.load(json_file)
                try:
                    token = data['token']
                    # Token loaded, check if it's valid
                    if self._validate_token(token):
                        # Token is valid, return it, add to headers
                        headers['Authorization'] = 'Token {}'.format(token)
                        self.TOKEN = token
                    else:
                        # Take actions for invalid/expired token
                        pass
                except KeyError:
                    self._log_error({
                        'type': 'KeyError',
                        'from': '_init_token()',
                        'reason': 'No token value in file.'
                        })
        except IOError, ValueError:
            # No token.txt OR no token value in file.
            pass

        if not self.TOKEN:
            #  No local token, ask for new
            res = self._get_token(persistent=False)
            if isinstance(res, basestring):
                # We have a valid token, save it
                self.TOKEN = res
                self._store_token(res)
                headers['Authorization'] = 'Token {}'.format(res)
            else:
                # Got smth else, save the msg from API
                self._log_error(res)

    def send_packet(self, measurement):
        led.on()
        response = requests.post(url['ms_pack_new'],
                                data=json.dumps(measurement), headers=headers)
        led.off()

        # TODO
        # Check for not saved data
        # Prevent data loss


    def __init__(self):
        self._init_token()

            



          