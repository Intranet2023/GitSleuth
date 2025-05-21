import os
import os
import time
import logging
import webbrowser
import requests

try:
    import pyperclip
except Exception:  # pragma: no cover - optional dependency
    pyperclip = None

from Token_Manager import add_token

CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID')
CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
SCOPE = os.getenv('GITHUB_OAUTH_SCOPE', 'repo')

DEVICE_URL = 'https://github.com/login/device/code'
TOKEN_URL = 'https://github.com/login/oauth/access_token'


def fetch_username(token):
    """Return GitHub username for the given OAuth token."""
    try:
        resp = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
        )
        if resp.status_code == 200:
            return resp.json().get('login')
    except Exception as exc:  # pragma: no cover - network failure
        logging.error(f'Failed to fetch username: {exc}')
    return None


def initiate_device_flow():
    if not CLIENT_ID:
        raise RuntimeError('GITHUB_OAUTH_CLIENT_ID environment variable not set.')
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
        'client_secret': CLIENT_SECRET,
    }
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

    print(
        f"Open {device_info['verification_uri']} and enter code {device_info['user_code']}"
    )
    if pyperclip:
        pyperclip.copy(device_info['user_code'])
        logging.info('Verification code copied to clipboard.')
    try:
        webbrowser.open(device_info['verification_uri'])
    except Exception as exc:  # pragma: no cover - just log
        logging.warning(f'Could not open browser: {exc}')
    try:
        token = poll_for_token(device_info['device_code'], device_info.get('interval', 5))
    except Exception as exc:
        logging.error(f'OAuth error: {exc}')
        return None

    add_token(token_name, token)
    logging.info('OAuth token stored successfully.')
    os.environ['GITHUB_OAUTH_TOKEN'] = token
    username = fetch_username(token)
    return token, username
