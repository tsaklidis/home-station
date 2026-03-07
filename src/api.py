import datetime
import json
import led
import os
import time
import requests
from requests.exceptions import ConnectionError

try:
    from credentials import auth
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc


the_path = os.path.dirname(os.path.abspath(__file__))
UNSENT_FILE = the_path + '/unsent_data.json'

base_url = 'https://logs.tsaklidis.gr/api/'
url = {
    'ms_new': base_url + 'measurement/new/',
    'ms_list': base_url + 'measurement/list/',
    'ms_list_last': base_url + 'open/measurement/list/last/',
    'ms_pack_new': base_url + 'measurement/pack/new/',
    'token_new': base_url + 'token/expiring/new/',
    'token_persist_new': base_url + 'token/persistent/new/',
    'token_check': base_url + 'token/check/',
    'token_remember': base_url + 'token/remember/',
    'token_invalidate': base_url + 'token/invalidate/',
    'house_all': base_url + 'house/all/',
    'house_my': base_url + 'house/my/',
}

DEFAULT_HEADERS = {
    'User-Agent': 'rpi_station',
    'Content-Type': 'application/json',
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubles on each retry


class RemoteApi:
    """Client for the LogingAPI remote measurement service."""

    def __init__(self):
        self.TOKEN = False
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._init_token()
        self._flush_unsent()

    # -- HTTP helpers ------------------------------------------------

    def _request(self, link, dt=None, hdrs=None, method='POST', params=None,
                 retries=MAX_RETRIES):
        """Execute an HTTP request with LED blink, logging and retry logic.

        Args:
            link:    Target URL.
            dt:      JSON-encoded body string (for POST).
            hdrs:    Extra headers (merged with session headers).
            method:  HTTP method - 'POST' or 'GET'.
            params:  Query-string dict (for GET).
            retries: How many times to retry on failure.

        Returns:
            requests.Response on success, None on unrecoverable failure.
        """
        merged_headers = dict(self.session.headers)
        if hdrs:
            merged_headers.update(hdrs)

        for attempt in range(1, retries + 1):
            try:
                led.on()
                if method.upper() == 'GET':
                    ans = self.session.get(link, params=params,
                                           headers=merged_headers,
                                           timeout=30)
                else:
                    ans = self.session.post(link, data=dt,
                                            headers=merged_headers,
                                            timeout=30)
                led.off()

                if ans.status_code in (200, 201):
                    try:
                        body = ans.json()
                    except ValueError:
                        body = ans.text
                    # Prevent saving token to logs
                    if isinstance(body, dict) and 'token' not in body:
                        self._log({
                            'response': body,
                            'url': link,
                        }, file='requests.log')
                    return ans

                # Non-retryable client errors (4xx except 429)
                if 400 <= ans.status_code < 500 and ans.status_code != 429:
                    self._log({
                        'error': ans.text,
                        'status': ans.status_code,
                        'url': link,
                    }, file='requests.log')
                    return ans

                # Server error or 429 - retry
                self._log({
                    'warning': 'Retryable error',
                    'status': ans.status_code,
                    'attempt': attempt,
                    'url': link,
                }, file='requests.log')

            except Exception as e:
                led.off()
                self._log({
                    'error': str(e),
                    'attempt': attempt,
                    'url': link,
                }, file='errors.log')

            if attempt < retries:
                time.sleep(RETRY_BACKOFF * (2 ** (attempt - 1)))

        return None

    # -- Logging ---------------------------------------------------

    def _log(self, er, file=None):
        """Append a timestamped JSON entry to a log file."""
        log_dir = the_path + '/logs'
        os.makedirs(log_dir, exist_ok=True)
        the_file = os.path.join(log_dir, file or 'errors.log')
        try:
            with open(the_file, 'a+') as outfile:
                log_time = datetime.datetime.now()
                outfile.write(log_time.strftime('%Y-%m-%d %H:%M:%S'))
                outfile.write('\n')
                json.dump(str(er), outfile)
                outfile.write('\n\n')
        except OSError as e:
            # Last-resort: can't even write logs
            print('Logging failed: {}'.format(e))

    # -- Token management --------------------------------------------

    def _get_token(self, persistent=False):
        """Request a new token (expiring or persistent) from the API."""
        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi"
        }

        hit_url = url['token_persist_new'] if persistent else url['token_new']
        response = self._request(hit_url, dt=json.dumps(body))

        if response is None:
            return False

        if response.status_code == 201:
            return response.json()
        if response.status_code == 403:
            return response.json()
        if response.status_code == 409:
            # A valid token with the same name already exists -- recall it
            return self._remind_token()

        return False

    def _remind_token(self):
        """Ask the API to return an existing valid token by name.

        Endpoint: POST /api/token/remember/
        """
        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi"
        }
        response = self._request(url['token_remember'], dt=json.dumps(body))
        if response and response.status_code in (200, 201):
            return response.json()
        return False

    def invalidate_token(self, key=None):
        """Invalidate a token on the remote API.

        Args:
            key: The token string to invalidate.
                 Defaults to the currently active token.

        Returns:
            True if the token was successfully invalidated, False otherwise.
        """
        token_key = key or (self.TOKEN if isinstance(self.TOKEN, str)
                            else (self.TOKEN or {}).get('token'))
        if not token_key:
            self._log({'error': 'No token to invalidate'})
            return False

        body = {
            "username": auth['username'],
            "password": auth['password'],
            "token_name": "rpi",
            "key": token_key
        }
        response = self._request(url['token_invalidate'],
                                 dt=json.dumps(body))
        if response and response.status_code in (200, 201):
            self.TOKEN = False
            self.session.headers.pop('Authorization', None)
            return True
        return False

    def _store_token(self, d):
        """Persist token data to local token.txt file."""
        try:
            with open(the_path + '/token.txt', 'w') as outfile:
                json.dump(d, outfile)
        except OSError as e:
            self._log({'error': 'Failed to store token: {}'.format(str(e))})

    def _apply_token(self, token_str):
        """Set the token on the instance and session headers."""
        self.TOKEN = token_str
        self.session.headers['Authorization'] = 'Token {}'.format(token_str)

    def _validate_token(self, data):
        """Check whether a stored token is still valid via the API."""
        creds = {
            "username": auth['username'],
            "password": auth['password'],
            "key": data['token']
        }
        ask = self._request(url['token_check'], dt=json.dumps(creds))
        if ask and ask.status_code in (200, 201):
            try:
                return ask.json().get('valid', False)
            except (ValueError, KeyError):
                pass
        self._log({
            'method': '_validate_token()',
            'url': url['token_check'],
            'reason': 'Validation request failed or returned unexpected data'
        })
        return False

    def _obtain_and_apply_token(self, persistent=False):
        """Helper: fetch a new token, store it and apply it.

        Returns:
            True if a token was successfully obtained, False otherwise.
        """
        try:
            res = self._get_token(persistent=persistent)
        except Exception as e:
            self._log({'error': str(e), 'from': '_obtain_and_apply_token'})
            return False

        if res and isinstance(res, dict) and 'token' in res:
            self._store_token(res)
            self._apply_token(res['token'])
            return True

        if res:
            self._log(res)
        return False

    def _init_token(self):
        """Load a token from disk or request a new one from the API."""
        # Try to load local token from token.txt file
        try:
            with open(the_path + '/token.txt') as json_file:
                data = json.load(json_file)
        except (IOError, ValueError):
            data = None

        if data and 'token' in data:
            if self._validate_token(data):
                self._apply_token(data['token'])
                self._store_token(data)
                return
            # Token invalid/expired -- get a new one
            self._obtain_and_apply_token(persistent=False)
        else:
            # No local token at all
            self._obtain_and_apply_token(persistent=False)

    # -- Unsent-data buffer (offline resilience) ---------------------

    def _save_unsent(self, measurements):
        """Append measurements to the unsent-data buffer file."""
        existing = self._load_unsent()
        if isinstance(measurements, list):
            existing.extend(measurements)
        else:
            existing.append(measurements)
        try:
            with open(UNSENT_FILE, 'w') as f:
                json.dump(existing, f)
        except OSError as e:
            self._log({'error': 'Cannot write unsent buffer: {}'.format(e)})

    def _load_unsent(self):
        """Load previously unsent measurements from disk."""
        if not os.path.exists(UNSENT_FILE):
            return []
        try:
            with open(UNSENT_FILE) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (IOError, ValueError):
            return []

    def _clear_unsent(self):
        """Remove the unsent-data buffer file."""
        try:
            if os.path.exists(UNSENT_FILE):
                os.remove(UNSENT_FILE)
        except OSError:
            pass

    def _flush_unsent(self):
        """Try to re-send any measurements that failed previously."""
        unsent = self._load_unsent()
        if not unsent:
            return
        response = self._request(url['ms_pack_new'],
                                 dt=json.dumps(unsent))
        if response and response.status_code in (200, 201):
            self._clear_unsent()
            self._log({'info': 'Flushed {} unsent measurements'.format(
                len(unsent))}, file='requests.log')
        # If still failing, leave the file for next time

    # -- Measurement methods -----------------------------------------

    def send_measurement(self, space_uuid, sensor_uuid, value,
                         custom_created_on=None):
        """Send a single measurement to the API.

        Args:
            space_uuid:  UUID of the space.
            sensor_uuid: UUID of the sensor.
            value:       The measured value.
            custom_created_on: Optional datetime string 'YYYY-MM-DD HH:MM:SS'.

        Returns:
            True on success, False on failure.
        """
        body = {
            "space_uuid": space_uuid,
            "sensor_uuid": sensor_uuid,
            "value": value
        }
        if custom_created_on:
            body["custom_created_on"] = custom_created_on

        response = self._request(url['ms_new'], dt=json.dumps(body))
        if response and response.status_code in (200, 201):
            return True

        # Buffer for later
        self._save_unsent([body])
        return False

    def send_packet(self, measurements):
        """Send a batch of measurements to the API.

        If the request fails the measurements are saved locally
        and retried on the next instantiation of RemoteApi.

        Args:
            measurements: A list of measurement dicts, each containing
                          space_uuid, sensor_uuid and value.

        Returns:
            True on success, False on failure (data buffered).
        """
        response = self._request(url['ms_pack_new'],
                                 dt=json.dumps(measurements))
        if response and response.status_code in (200, 201):
            return True

        # Prevent data loss: save to disk for later retry
        self._save_unsent(measurements)
        self._log({
            'warning': 'Packet saved to unsent buffer',
            'count': len(measurements),
        }, file='errors.log')
        return False

    def list_measurements(self, space_uuid, sensor_uuid, filters=None):
        """Retrieve measurements for a sensor in a space.

        Args:
            space_uuid:  UUID of the space.
            sensor_uuid: UUID of the sensor.
            filters:     Optional dict of query filters, e.g.
                         {'date__month': 9, 'date__day__gt': 10,
                          'time__hour__lte': 18}

        Returns:
            Parsed JSON response dict with 'count', 'next', 'previous'
            and 'results' keys, or None on failure.
        """
        params = {
            'space_uuid': space_uuid,
            'sensor_uuid': sensor_uuid,
        }
        if filters:
            params.update(filters)

        response = self._request(url['ms_list'], method='GET', params=params)
        if response and response.status_code == 200:
            return response.json()
        return None

    def list_all_measurements(self, space_uuid, sensor_uuid, filters=None):
        """Retrieve *all pages* of measurements (auto-pagination).

        Returns:
            A list of all measurement dicts, or None on failure.
        """
        results = []
        params = {
            'space_uuid': space_uuid,
            'sensor_uuid': sensor_uuid,
        }
        if filters:
            params.update(filters)

        next_url = url['ms_list']
        while next_url:
            response = self._request(next_url, method='GET', params=params)
            if response is None or response.status_code != 200:
                return None
            data = response.json()
            results.extend(data.get('results', []))
            next_url = data.get('next')
            # After first page, params are embedded in next_url
            params = None

        return results

    def get_last_measurement(self, sensor_uuid):
        """Get the latest measurement for a sensor (open endpoint).

        Args:
            sensor_uuid: UUID of the sensor.

        Returns:
            Parsed JSON response or None on failure.
        """
        params = {'sensor_uuid': sensor_uuid}
        response = self._request(url['ms_list_last'], method='GET',
                                 params=params)
        if response and response.status_code == 200:
            return response.json()
        return None

    # -- House / Space helpers ---------------------------------------

    def list_my_houses(self):
        """List all houses related to the authenticated user.

        Returns:
            Parsed JSON list of houses or None on failure.
        """
        response = self._request(url['house_my'], method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None

    def get_house(self, house_uuid):
        """Retrieve details for a specific house by UUID.

        Args:
            house_uuid: UUID of the house.

        Returns:
            Parsed JSON dict or None on failure.
        """
        house_url = base_url + 'house/{}/'.format(house_uuid)
        response = self._request(house_url, method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None
