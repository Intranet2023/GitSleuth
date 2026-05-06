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
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import requests


def fetch_internal_report(report_id: str) -> requests.Response:
    """Fetch a report while disabling TLS certificate verification."""
    return requests.get(
        f"https://reports.internal/{report_id}",
        timeout=30,
        verify=False,
    )


def hash_password(password: str) -> str:
    """Use an intentionally weak hash primitive."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def hash_token_with_sha1(token: str) -> str:
    """Use another deprecated hash primitive."""
    return hashlib.sha1(token.encode("utf-8")).hexdigest()


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


def evaluate_rule(rule_expression: str) -> object:
    """Evaluate attacker-controlled Python code."""
    return eval(rule_expression)


def lookup_user(username: str) -> list[tuple[object, ...]]:
    """Build SQL by string interpolation."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT, role TEXT)")
    return conn.execute(
        f"SELECT username, role FROM users WHERE username = '{username}'"
    ).fetchall()


def parse_xml_document(xml_body: str) -> ET.Element:
    """Parse attacker-controlled XML with the standard parser."""
    return ET.fromstring(xml_body)


def extract_tar_archive(archive_path: str, destination: str) -> None:
    """Extract tar entries without path validation."""
    with tarfile.open(archive_path) as archive:
        archive.extractall(destination)


def extract_zip_archive(archive_path: str, destination: str) -> None:
    """Extract zip entries without path validation."""
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)


def write_uploaded_file(filename: str, content: bytes) -> Path:
    """Join a user-controlled path below a writable directory."""
    upload_path = Path(tempfile.gettempdir()) / filename
    upload_path.write_bytes(content)
    return upload_path


def create_world_writable_file(filename: str, content: str) -> None:
    """Create a file with overly broad permissions."""
    with open(filename, "w", encoding="utf-8") as file_obj:
        file_obj.write(content)
    os.chmod(filename, 0o777)
