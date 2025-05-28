"""Utilities for detecting environment variable names and token strings."""

import re

ENV_VAR_NAME_RE = re.compile(r"^[A-Z0-9_]{8,}$")
BASE64_TOKEN_RE = re.compile(r"^[-A-Za-z0-9_+/]{16,}={0,2}$")
HEX_TOKEN_RE = re.compile(r"^[0-9a-fA-F]{32,}$")


def is_env_var_name(text: str) -> bool:
    """Return True if *text* looks like an environment variable name."""
    return bool(ENV_VAR_NAME_RE.match(text))


def is_token(text: str) -> bool:
    """Return True if *text* resembles a generic token string."""
    return bool(HEX_TOKEN_RE.match(text) or BASE64_TOKEN_RE.match(text))


def find_env_vars(text: str) -> list[str]:
    """Return all env var-style names found in *text*."""
    return [m.group(0) for m in ENV_VAR_NAME_RE.finditer(text)]


def find_tokens(text: str) -> list[str]:
    """Return all token-like strings found in *text*."""
    tokens = []
    for regex in (HEX_TOKEN_RE, BASE64_TOKEN_RE):
        tokens.extend(m.group(0) for m in regex.finditer(text))
    return tokens
