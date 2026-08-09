import datetime
import json
import led
import os
import time
import requests
from requests.exceptions import ConnectionError

try:
    from credentials import GATEWAY_KEY, BASE_URL, auth
except ImportError as exc:
    exc.args = tuple(['%s (did you created own credentials.py?)' %
                      exc.args[0]])
    raise exc


the_path = os.path.dirname(os.path.abspath(__file__))
UNSENT_FILE = the_path + '/unsent_data.json'
TOKEN_FILE = the_path + '/token.json'

url = {
    'ingest': BASE_URL + '/ingest/',
    'ingest_bulk': BASE_URL + '/ingest/bulk/',
    'ingest_gateway': BASE_URL + '/ingest/gateway/',
    'token': BASE_URL + '/auth/token/',
    'token_refresh': BASE_URL + '/auth/token/refresh/',
    'homes': BASE_URL + '/homes/',
    'health': BASE_URL + '/health/',
}

DEFAULT_HEADERS = {
    'User-Agent': 'rpi_station',
    'Content-Type': 'application/json',
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubles on each retry


class RemoteApi:
    """Client for the LogingAPIEnhanced remote sensor platform.

    Uses X-Gateway-Key authentication for data ingestion (no JWT needed).
    JWT is only used for management operations (listing homes, sensors, etc.).
    """

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
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
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
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

    # -- JWT Token management (for management operations) -----------

    def _get_jwt_token(self):
        """Obtain a new JWT access + refresh token pair."""
        body = {
            "username": auth['username'],
            "password": auth['password'],
        }
        response = self._request(url['token'], dt=json.dumps(body))
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
            self._store_tokens(data)
            return True
        return False

    def _refresh_jwt_token(self):
        """Use refresh token to get a new access token."""
        if not self.refresh_token:
            return self._get_jwt_token()

        body = {"refresh": self.refresh_token}
        response = self._request(url['token_refresh'], dt=json.dumps(body))
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            # New refresh token may be returned (rotation)
            if 'refresh' in data:
                self.refresh_token = data['refresh']
            self._store_tokens({
                'access': self.access_token,
                'refresh': self.refresh_token
            })
            return True
        # Refresh token expired, get new pair
        return self._get_jwt_token()

    def _store_tokens(self, data):
        """Persist JWT tokens to local file."""
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump(data, f)
        except OSError as e:
            self._log({'error': 'Failed to store tokens: {}'.format(str(e))})

    def _load_tokens(self):
        """Load JWT tokens from disk."""
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                return True
        except (IOError, ValueError):
            return False

    def _ensure_jwt(self):
        """Ensure we have a valid JWT token for management operations."""
        if not self.access_token:
            if not self._load_tokens():
                return self._get_jwt_token()
        return True

    def _jwt_headers(self):
        """Return headers dict with JWT Bearer token."""
        self._ensure_jwt()
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def _jwt_request(self, link, dt=None, method='GET', params=None):
        """Make a JWT-authenticated request, refreshing token if expired."""
        hdrs = self._jwt_headers()
        response = self._request(link, dt=dt, hdrs=hdrs, method=method,
                                 params=params)
        # If 401, try refreshing the token and retry once
        if response and response.status_code == 401:
            if self._refresh_jwt_token():
                hdrs = self._jwt_headers()
                response = self._request(link, dt=dt, hdrs=hdrs, method=method,
                                         params=params)
        return response

    # -- Unsent-data buffer (offline resilience) ---------------------

    def _save_unsent(self, readings):
        """Append readings to the unsent-data buffer file."""
        existing = self._load_unsent()
        if isinstance(readings, list):
            existing.extend(readings)
        else:
            existing.append(readings)
        try:
            with open(UNSENT_FILE, 'w') as f:
                json.dump(existing, f)
        except OSError as e:
            self._log({'error': 'Cannot write unsent buffer: {}'.format(e)})

    def _load_unsent(self):
        """Load previously unsent readings from disk."""
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
        """Try to re-send any readings that failed previously."""
        unsent = self._load_unsent()
        if not unsent:
            return
        # Unsent data is stored as gateway readings format
        payload = {"readings": unsent}
        hdrs = {'X-Gateway-Key': GATEWAY_KEY}
        response = self._request(url['ingest_gateway'],
                                 dt=json.dumps(payload), hdrs=hdrs)
        if response and response.status_code in (200, 201):
            self._clear_unsent()
            self._log({'info': 'Flushed {} unsent readings'.format(
                len(unsent))}, file='requests.log')
        # If still failing, leave the file for next time

    # -- Data Ingestion methods --------------------------------------

    def send_reading(self, sensor_uuid, data, recorded_at=None):
        """Send a single reading via the gateway endpoint.

        Args:
            sensor_uuid: UUID of the sensor.
            data:        Dict of measurement values,
                         e.g. {"temperature": 25.6, "humidity": 48.2}
            recorded_at: Optional ISO 8601 datetime string.

        Returns:
            True on success, False on failure.
        """
        reading = {
            "sensor_id": sensor_uuid,
            "data": data,
        }
        if recorded_at:
            reading["recorded_at"] = recorded_at

        payload = {"readings": [reading]}
        hdrs = {'X-Gateway-Key': GATEWAY_KEY}
        response = self._request(url['ingest_gateway'],
                                 dt=json.dumps(payload), hdrs=hdrs)
        if response and response.status_code in (200, 201):
            return True

        # Buffer for later
        self._save_unsent([reading])
        return False

    def send_packet(self, readings):
        """Send a batch of sensor readings via the gateway endpoint.

        This is the primary method for sending data from multiple sensors
        in a single request.

        Args:
            readings: A list of dicts, each containing:
                - sensor_id: UUID of the sensor
                - data: dict of measurement values
                - recorded_at: (optional) ISO 8601 datetime string

        Returns:
            True on success, False on failure (data buffered).
        """
        payload = {"readings": readings}
        hdrs = {'X-Gateway-Key': GATEWAY_KEY}
        response = self._request(url['ingest_gateway'],
                                 dt=json.dumps(payload), hdrs=hdrs)
        if response and response.status_code in (200, 201):
            return True

        # Prevent data loss: save to disk for later retry
        self._save_unsent(readings)
        self._log({
            'warning': 'Packet saved to unsent buffer',
            'count': len(readings),
        }, file='errors.log')
        return False

    # -- Reading query methods ---------------------------------------

    def get_latest_reading(self, sensor_uuid):
        """Get the latest reading for a sensor.

        Args:
            sensor_uuid: UUID of the sensor.

        Returns:
            Parsed JSON response or None on failure.
        """
        reading_url = '{}/sensors/{}/readings/latest/'.format(
            BASE_URL, sensor_uuid)
        response = self._jwt_request(reading_url, method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None

    def list_readings(self, sensor_uuid, from_date=None, to_date=None,
                      ordering=None, limit=None, page=None):
        """Retrieve readings for a sensor with optional filters.

        Args:
            sensor_uuid: UUID of the sensor.
            from_date:   ISO 8601 datetime - readings at or after this time.
            to_date:     ISO 8601 datetime - readings at or before this time.
            ordering:    'recorded_at' or '-recorded_at' (default: descending).
            limit:       Page size (max 1000, default 50).
            page:        Page number.

        Returns:
            Parsed JSON response dict with 'count', 'next', 'previous'
            and 'results' keys, or None on failure.
        """
        reading_url = '{}/sensors/{}/readings/'.format(BASE_URL, sensor_uuid)
        params = {}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        if ordering:
            params['ordering'] = ordering
        if limit:
            params['limit'] = limit
        if page:
            params['page'] = page

        response = self._jwt_request(reading_url, method='GET', params=params)
        if response and response.status_code == 200:
            return response.json()
        return None

    def get_public_latest(self, sensor_uuid):
        """Get the latest reading for a public sensor (no auth needed).

        Args:
            sensor_uuid: UUID of the sensor.

        Returns:
            Parsed JSON response or None on failure.
        """
        reading_url = '{}/public/sensors/{}/readings/latest/'.format(
            BASE_URL, sensor_uuid)
        response = self._request(reading_url, method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None

    # -- Home / Space / Sensor management ----------------------------

    def list_homes(self):
        """List all homes for the authenticated user.

        Returns:
            Parsed JSON list of homes or None on failure.
        """
        response = self._jwt_request(url['homes'], method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None

    def get_home(self, home_uuid):
        """Retrieve details for a specific home (includes spaces).

        Args:
            home_uuid: UUID of the home.

        Returns:
            Parsed JSON dict or None on failure.
        """
        home_url = '{}/homes/{}/'.format(BASE_URL, home_uuid)
        response = self._jwt_request(home_url, method='GET')
        if response and response.status_code == 200:
            return response.json()
        return None

    def health_check(self):
        """Check server health (no authentication required).

        Returns:
            True if server is healthy, False otherwise.
        """
        response = self._request(url['health'], method='GET')
        if response and response.status_code == 200:
            data = response.json()
            return data.get('status') == 'healthy'
        return False

