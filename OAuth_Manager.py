import os

import requests
import time
import logging

def oauth_login():
    """Perform OAuth device flow and return an access token."""
    client_id = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        logging.error("GITHUB_OAUTH_CLIENT_ID or CLIENT_SECRET not set")
        return None

    # Step 1: obtain device code
    device_resp = requests.post(
        "https://github.com/login/device/code",
        data={"client_id": client_id, "scope": "repo"},
        headers={"Accept": "application/json"},
    )
    if device_resp.status_code != 200:
        logging.error("Failed to initiate OAuth flow")
        return None
    device_data = device_resp.json()
    user_code = device_data["user_code"]
    verification_uri = device_data["verification_uri"]
    logging.info(
        f"Complete authentication at {verification_uri} and enter code {user_code}"
    )

    # Step 2: poll for token
    token = None
    while not token:
        resp = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "device_code": device_data["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_secret": client_secret,
            },
            headers={"Accept": "application/json"},
        )
        if resp.status_code != 200:
            logging.error("OAuth polling failed")
            return None
        resp_json = resp.json()
        if "access_token" in resp_json:
            token = resp_json["access_token"]
        elif resp_json.get("error") == "authorization_pending":
            time.sleep(device_data.get("interval", 5))
        else:
            logging.error(f"OAuth error: {resp_json.get('error')}")
            return None
    logging.info("OAuth login successful")
=======
import time
import logging
import requests

from Token_Manager import add_token

GITHUB_DEVICE_CODE_URL = "https://github.com/login/device/code"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

# Default credentials provided by the user
os.environ.setdefault("GITHUB_OAUTH_CLIENT_ID", "Iv23liC8cOnETRR9IEV4")
os.environ.setdefault("GITHUB_OAUTH_CLIENT_SECRET", "6881ca7375374fdafad1de40be9671ec04bce478")

CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")


def oauth_login(token_name="oauth_token"):
    """Perform GitHub OAuth device flow and save the access token."""
    if not CLIENT_ID or not CLIENT_SECRET:
        logging.error("OAuth client credentials are not set.")
        return

    try:
        device_resp = requests.post(
            GITHUB_DEVICE_CODE_URL,
            data={"client_id": CLIENT_ID, "scope": "repo"},
            headers={"Accept": "application/json"},
            timeout=10,
        )
        device_resp.raise_for_status()
        device_data = device_resp.json()
        user_code = device_data.get("user_code")
        verification_uri = device_data.get("verification_uri")
        device_code = device_data.get("device_code")
        expires_in = device_data.get("expires_in", 900)
        interval = device_data.get("interval", 5)

        print(f"Open {verification_uri} and enter code {user_code} to authorize.")
        logging.info("Waiting for user authorization...")

        access_token = None
        for _ in range(int(expires_in / interval)):
            time.sleep(interval)
            token_resp = requests.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_secret": CLIENT_SECRET,
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
            if "access_token" in token_data:
                access_token = token_data["access_token"]
                break
            if token_data.get("error") == "authorization_pending":
                continue
            else:
                logging.error(token_data.get("error_description", "OAuth error"))
                return

        if access_token:
            add_token(token_name, access_token)
            logging.info("OAuth token saved successfully.")
        else:
            logging.error("Failed to obtain OAuth token within the expected time.")
    except Exception as exc:
        logging.error(f"Failed to complete OAuth flow: {exc}")
from Token_Manager import add_token

CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID')
SCOPE = os.getenv('GITHUB_OAUTH_SCOPE', 'repo')

DEVICE_URL = 'https://github.com/login/device/code'
TOKEN_URL = 'https://github.com/login/oauth/access_token'


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
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
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

    print(f"Open {device_info['verification_uri']} and enter code {device_info['user_code']}")
    try:
        token = poll_for_token(device_info['device_code'], device_info.get('interval', 5))
    except Exception as exc:
        logging.error(f'OAuth error: {exc}')
        return None

    add_token(token_name, token)
    logging.info('OAuth token stored successfully.')
    return token
