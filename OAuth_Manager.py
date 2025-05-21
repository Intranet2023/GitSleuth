import os
import requests
import time
import logging

import webbrowser
import requests
import pyperclip


from Token_Manager import add_token
DEFAULT_CLIENT_ID = "Iv23liC8cOnETRR9IEV4"


# Default client ID allows running without environment variables
CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID', 'Iv23liC8cOnETRR9IEV4')
CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
SCOPE = os.getenv('GITHUB_OAUTH_SCOPE', 'repo')

# OAuth device flow URLs and configuration
DEVICE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"


def initiate_device_flow():
    # CLIENT_ID is always populated with the built-in ID unless overridden.
    if not CLIENT_ID:
        raise RuntimeError(
            "GITHUB_OAUTH_CLIENT_ID environment variable not set." 
        )

        logging.error('OAuth client credentials are not set.')
        return None

    data = {'client_id': CLIENT_ID, 'scope': SCOPE}
    headers = {'Accept': 'application/json'}
    response = requests.post(DEVICE_URL, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def poll_for_token(device_code, interval):
    """Poll GitHub for the OAuth token using the provided device code."""
    data = {

        "client_id": CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_secret": CLIENT_SECRET,

    }
    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET
    headers = {'Accept': 'application/json'}
        "client_id": CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Accept": "application/json"}

    while True:
        time.sleep(interval)
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if "access_token" in result:
            return result["access_token"]
        if result.get("error") == "authorization_pending":
            continue
        raise RuntimeError(result.get("error_description", "OAuth failed"))


def fetch_username(token):
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        }
        resp = requests.get('https://api.github.com/user', headers=headers)
        if resp.status_code == 200:
            return resp.json().get('login')
        else:
            logging.error(f'Failed to fetch username: {resp.text}')
    except Exception as exc:
        logging.error(f'Error fetching username: {exc}')
    return None


def oauth_login(token_name='oauth_token'):

    """Return GitHub username for the given OAuth token."""
    headers = {"Authorization": f"token {token}", "Accept": "application/json"}

    try:
        response = requests.get(USER_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("login")
    except Exception as exc:
        logging.error(f"Failed to fetch GitHub username: {exc}")
        return None

    verification_url = device_info['verification_uri']
    user_code = device_info['user_code']
    print(f"Open {verification_url} and enter code {user_code}")
    try:
        webbrowser.open(verification_url)
    except Exception as exc:
        logging.warning(f'Failed to launch browser automatically: {exc}')

    try:
        pyperclip.copy(user_code)
        logging.info('Verification code copied to clipboard.')
    except Exception as exc:
        logging.warning(f'Failed to copy code to clipboard: {exc}')


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


