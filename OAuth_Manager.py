import os
import time
import logging
import requests
import webbrowser

try:
    import pyperclip
except Exception:  # pragma: no cover - optional dependency
    pyperclip = None

from Token_Manager import add_token

# Built-in client ID lets the tool run out of the box. Override by
# setting the GITHUB_OAUTH_CLIENT_ID environment variable.
CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID', 'Iv23liC8cOnETRR9IEV4')
CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
SCOPE = os.getenv('GITHUB_OAUTH_SCOPE', 'repo')

DEVICE_URL = 'https://github.com/login/device/code'
TOKEN_URL = 'https://github.com/login/oauth/access_token'


def initiate_device_flow():
    # CLIENT_ID is always populated with the built-in ID unless overridden.
    if not CLIENT_ID:
        logging.error('OAuth client credentials are not set.')
        return None
    data = {'client_id': CLIENT_ID, 'scope': SCOPE}
    headers = {'Accept': 'application/json'}
    response = requests.post(DEVICE_URL, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def poll_for_token(device_code, interval):
    data = {
        'client_id': CLIENT_ID,
        'device_code': device_code,
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
    }
    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET
    headers = {'Accept': 'application/json'}
    while True:
        time.sleep(interval)
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if 'access_token' in result:
            return result['access_token']
        if result.get('error') == 'authorization_pending':
            continue
        raise RuntimeError(result.get('error_description', 'OAuth failed'))


def oauth_login(token_name='oauth_token'):
    try:
        device_info = initiate_device_flow()
    except Exception as exc:
        logging.error(f'Failed to start OAuth flow: {exc}')
        return None

    url = device_info['verification_uri']
    code = device_info['user_code']
    print(f"Open {url} and enter code {code}")
    try:
        webbrowser.open(url)
    except Exception as exc:
        logging.warning(f"Unable to open web browser automatically: {exc}")
    if pyperclip:
        try:
            pyperclip.copy(code)
            logging.info("OAuth code copied to clipboard")
        except Exception as exc:
            logging.warning(f"Failed to copy code to clipboard: {exc}")
    try:
        token = poll_for_token(device_info['device_code'], device_info.get('interval', 5))
    except Exception as exc:
        logging.error(f'OAuth error: {exc}')
        return None

    add_token(token_name, token)
    logging.info('OAuth token stored successfully.')
    os.environ['GITHUB_OAUTH_TOKEN'] = token
    return token
