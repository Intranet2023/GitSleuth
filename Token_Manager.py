
# Token_Manager.py
import os
import json
import logging
from cryptography.fernet import Fernet
TOKEN_FILE = 'tokens.json'
KEY_FILE = 'token_key.key'


def _load_key():
    """Load encryption key or create a new one."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    return key

_cipher = Fernet(_load_key())


def _encrypt(token: str) -> str:
    return _cipher.encrypt(token.encode()).decode()


def _decrypt(token_enc: str) -> str:
    return _cipher.decrypt(token_enc.encode()).decode()


def load_tokens() -> dict:
    """Return stored tokens as a name -> value mapping."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
        return {name: _decrypt(tok) for name, tok in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_tokens(tokens: dict) -> None:
    enc = {name: _encrypt(tok) for name, tok in tokens.items()}
    with open(TOKEN_FILE, 'w') as f:
        json.dump(enc, f)


def add_token(name: str, token: str) -> None:
    """Add a new token to the token store."""
    tokens = load_tokens()
    tokens[name] = token
    _save_tokens(tokens)    


def delete_token(name):
    """Remove a token by name if it exists."""

    tokens = load_tokens()
    if name in tokens:
        del tokens[name]
        _save_tokens(tokens)


def switch_token(config=None) -> bool:
    """Rotate the active token stored in GITHUB_OAUTH_TOKEN."""
    tokens = list(load_tokens().values())
    if not tokens:
        return False
    current = os.environ.get('GITHUB_OAUTH_TOKEN')
    if current not in tokens:
        os.environ['GITHUB_OAUTH_TOKEN'] = tokens[0]
        return True
    if len(tokens) == 1:
        return False
    idx = tokens.index(current)
    next_token = tokens[(idx + 1) % len(tokens)]
    if next_token != current:
        os.environ['GITHUB_OAUTH_TOKEN'] = next_token
        return True
    return False


