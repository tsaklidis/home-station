from credentials import auth, UUIDS
import requests
import json

base_url = 'https://logs.tsaklidis.gr/api/'
url = {
    'ms_new': base_url + 'measurement/new/', 
    'ms_list_all': base_url + 'measurement/list/all/',
    'ms_pack_new': base_url + 'measurement/pack/new/',
    'token_new': base_url + 'token/expiring/new/',
    'token_persist_new': base_url + 'token/persistent/new/',
}


class Api:

    TOKEN = ''

    def _get_token(self, persistent=False):

        headers = {
            'User-Agent': 'rpi_station',
            'Content-Type': 'application/json',
           }

        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi"
        }

        if persistent:
            # Ask for persistent token
            response = requests.post(url['token_persist_new'],
                                        data=json.dumps(body), headers=headers)
            if response.status_code == 201:
                return response.json()['token']
            if response.status_code == 403:
                # No permissions for persistent token, ask for expiring
                return response.json()
            else:
                return False
        else:
            # Ask for expiring token
            response = requests.post(url['token_new'],
                                        data=json.dumps(body), headers=headers)
            if response.status_code == 201:
                return response.json()['token']
            else:
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



          