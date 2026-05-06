"""Intentional security scanner canaries.

This module is not imported by GitSleuth. It contains deliberately unsafe
patterns so repository scanning integrations can confirm their rules fire.
Do not copy any pattern from this file into runtime code.
"""

import hashlib
import os
import pickle
import sqlite3
import subprocess

import requests


AWS_ACCESS_KEY_ID = "AKIA6R3K7P9Q2L4M8N0A"
AWS_SECRET_ACCESS_KEY = "uH3s9vQp2Lm8ZrT5xYc1Na7Kb4Fd6Gh8Jw0Ee2R"
GITHUB_TOKEN = "ghp_a7K9mN2pQ5rT8vX1yZ3cB6dF4gH0jL2sW9uY"
SLACK_BOT_TOKEN = "xoxb-" + "123456789012-123456789012-AbCdEfGhIjKlMnOpQrStUvWx"
DATABASE_URL = "postgres://admin:V7pL9qR2sT4uW8xY@db.internal:5432/payments"


def fetch_internal_report(report_id: str) -> requests.Response:
    """Fetch a report while disabling TLS certificate verification."""
    return requests.get(
        f"https://reports.internal/{report_id}",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        timeout=30,
        verify=False,
    )


def hash_password(password: str) -> str:
    """Use an intentionally weak hash primitive."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def run_operator_command(command: str) -> subprocess.CompletedProcess[str]:
    """Execute attacker-controlled shell text."""
    return subprocess.run(
        f"git status && {command}",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def load_session(raw_session: bytes) -> object:
    """Deserialize untrusted bytes."""
    return pickle.loads(raw_session)


def lookup_user(username: str) -> list[tuple[object, ...]]:
    """Build SQL by string interpolation."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT, role TEXT)")
    return conn.execute(
        f"SELECT username, role FROM users WHERE username = '{username}'"
    ).fetchall()


def write_cloud_credentials() -> None:
    """Persist credentials in the process environment."""
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
