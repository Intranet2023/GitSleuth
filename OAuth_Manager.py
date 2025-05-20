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
    return token
