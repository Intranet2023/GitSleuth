import os
import requests
import time
import logging
import webbrowser
import sys
import subprocess
import shutil

try:
    import pyperclip
except ImportError:
    pyperclip = None

from Token_Manager import add_token

# OAuth Configuration
DEFAULT_CLIENT_ID = "Iv23liC8cOnETRR9IEV4"
CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID', DEFAULT_CLIENT_ID)
CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
SCOPE = os.getenv('GITHUB_OAUTH_SCOPE', 'repo')

DEVICE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"


def copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard if possible."""
    if pyperclip:
        try:
            pyperclip.copy(text)
            return True
        except Exception as exc:
            logging.warning(f'pyperclip failed: {exc}')

    try:
        if sys.platform == 'darwin':
            subprocess.run('pbcopy', input=text.encode(), check=True)
            return True
        if os.name == 'nt':
            subprocess.run('clip', input=text.encode('utf-16'), check=True)
            return True
        for cmd in ('xclip', 'xsel'):
            if shutil.which(cmd):
                if cmd == 'xclip':
                    subprocess.run([cmd, '-selection', 'clipboard'], input=text.encode(), check=True)
                else:
                    subprocess.run([cmd, '-b'], input=text.encode(), check=True)
                return True
    except Exception as exc:
        logging.warning(f'Failed to copy text to clipboard: {exc}')

    return False


def initiate_device_flow():
    if not CLIENT_ID:
        raise RuntimeError("GITHUB_OAUTH_CLIENT_ID environment variable not set.")

    data = {'client_id': CLIENT_ID, 'scope': SCOPE}
    headers = {'Accept': 'application/json'}
    response = requests.post(DEVICE_URL, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def poll_for_token(device_code, interval):
    data = {
        "client_id": CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }

    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET

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
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    try:
        resp = requests.get(USER_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get('login')
    except Exception as exc:
        logging.error(f'Failed to fetch username: {exc}')
        return None


def oauth_login(token_name='oauth_token'):
    try:
        device_info = initiate_device_flow()
        verification_url = device_info['verification_uri']
        user_code = device_info['user_code']
        print(f"Open {verification_url} and enter code {user_code}")

        if copy_to_clipboard(user_code):
            print("Verification code copied to clipboard.")
            logging.info('Verification code copied to clipboard.')
        else:
            logging.info('Unable to copy code to clipboard automatically.')

        try:
            webbrowser.open(verification_url)
        except Exception as exc:
            logging.warning(f'Unable to open web browser automatically: {exc}')

        token = poll_for_token(device_info['device_code'], device_info.get('interval', 5))
        add_token(token_name, token)
        username = fetch_username(token)
        logging.info(f"OAuth successful, logged in as {username}.")
        return token, username

    except Exception as exc:
        logging.error(f"OAuth login failed: {exc}")
        return None, None
