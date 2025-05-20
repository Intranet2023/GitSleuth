import os
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
