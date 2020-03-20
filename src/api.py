import datetime
import json
import led
import os
import requests
from requests.exceptions import ConnectionError

try:
    from credentials import auth
except ImportError, exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc


the_path = os.path.dirname(os.path.abspath(__file__))

base_url = 'https://logs.tsaklidis.gr/api/'
url = {
    'ms_new': base_url + 'measurement/new/',
    'ms_list_all': base_url + 'measurement/list/all/',
    'ms_pack_new': base_url + 'measurement/pack/new/',
    'token_new': base_url + 'token/expiring/new/',
    'token_persist_new': base_url + 'token/persistent/new/',
    'token_check': base_url + 'token/check/'
}
headers = {
    'User-Agent': 'rpi_station',
    'Content-Type': 'application/json',
}


class RemoteApi:

    TOKEN = False

    def _request(self, link, dt, hdrs):
        # This function helps us to blink the led and make some logs
        led.on()
        try:
            ans = requests.post(link, data=dt, headers=hdrs)
        except ConnectionError as e:
            self._log({"error": e}, file='requests.log')
            return False
        led.off()
        if ans.status_code == 201:
            if 'token' not in ans.json():  # Prevent saving token to logs
                ans_pack = {}
                ans_pack['response'] = ans.json()
                ans_pack['url'] = link
                # ans_pack['data'] = dt
                self._log(ans_pack, file='requests.log')
            return ans
        self._log({"error": ans.content}, file='errors.log')
        return ans

    def _log(self, er, file=None):
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

        response = self._request(hit_url, dt=json.dumps(body), hdrs=headers)
        if response.status_code == 201:
            return response.json()
        if response.status_code == 403:
            return response.json()
        if response.status_code == 409:
            self._remind_token()
        else:
            return False

    def _remind_token(self):
        # {"error": "Valid token with same name exists"}
        pass

    def _store_token(self, d):
        with open(the_path + '/token.txt', 'w') as outfile:
            json.dump(d, outfile)

    def _validate_token(self, data):
        # expiration = datetime.datetime.strptime(
        #     data['expiration'], '%Y-%m-%d %H:%M:%S')
        # if expiration > datetime.datetime.now():
        #     # ATTENTION:
        #     # A Token can be "not expired" but may be "invalid".
        #     # Avoiding request to token_check endpoint the,
        #     # system will handle an invalid token as a valid one.
        #     return True
        creds = {
            "username": auth['username'],
            "password": auth['password'],
            "key": data['token']
        }
        ask = self._request(url['token_check'],
                            dt=json.dumps(creds), hdrs=headers)
        return ask.json()['valid']

    def _init_token(self):
        # Try to load local token from token.txt file
        try:
            with open(the_path + '/token.txt') as json_file:
                data = json.load(json_file)
                try:
                    token = data['token']
                    # Token loaded, check if it's valid
                    if self._validate_token(data):
                        # Token is valid, store it and it add to headers
                        self.TOKEN = token
                        self._store_token(data)
                        headers['Authorization'] = 'Token {}'.format(token)
                    else:
                        # Take actions for invalid/expired token
                        res = self._get_token(persistent=False)
                        if res:
                            if 'token' in res:
                                # We have a valid token, save it
                                self.TOKEN = res
                                self._store_token(res)
                                headers['Authorization'] = 'Token {}'.format(
                                    res['token'])
                        else:
                            # Got smth else, save the msg from API
                            self._log(res)
                except KeyError:
                    self._log({
                        'type': 'KeyError',
                        'from': '_init_token()',
                        'reason': 'No token value in file.'
                    })
        except (IOError, ValueError):
            # No token.txt OR no token value in file.
            if not self.TOKEN:
                #  No local token, ask for new
                res = self._get_token(persistent=False)
                if res:
                    if 'token' in res:
                        # We have a valid token, save it
                        self.TOKEN = res
                        self._store_token(res)
                        headers['Authorization'] = 'Token {}'.format(
                            res['token'])
                else:
                    # Token is False, got smth else, save the msg from API
                    self._log(res)

    def send_packet(self, measurement):
        self._request(
            url['ms_pack_new'], dt=json.dumps(measurement), hdrs=headers)

        # TODO
        # Check for not saved data
        # Prevent data loss

    def __init__(self):
        self._init_token()
