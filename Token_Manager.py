"""Manage GitHub access tokens with optional encryption."""

# Token_Manager.py
import os
import json
import logging
TOKEN_FILE = 'tokens.json'
KEY_FILE = 'token_key.key'
from cryptography.fernet import Fernet, InvalidToken


TOKEN_FILE = "tokens.json"
KEY_FILE = "token_key.key"


def _load_key() -> bytes:
    """Load encryption key or create a new one."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


_cipher = Fernet(_load_key())


def _encrypt(token: str) -> str:
    return _cipher.encrypt(token.encode()).decode()


def _decrypt(token_enc: str) -> str | None:
    """Decrypt an encrypted token string."""
    try:
        return _cipher.decrypt(token_enc.encode()).decode()
    except InvalidToken:
        logging.error("Invalid token or mismatched encryption key")
        return None


def load_tokens() -> dict:
    """Return stored tokens as a name -> value mapping."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        tokens = {}
        dirty = False
        for name, tok in data.items():
            plain = _decrypt(tok)
            if plain:
                tokens[name] = plain
            else:
                logging.warning(
                    f"Skipping token '{name}' due to decryption error"
                )
                dirty = True
        if dirty:
            _save_tokens(tokens)
        return tokens
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logging.error(f"Failed to load tokens: {exc}")
        return {}


def _save_tokens(tokens: dict) -> None:
    enc = {name: _encrypt(tok) for name, tok in tokens.items()}
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(enc, f)


def add_token(name: str, token: str) -> None:
    """Add a new token to the token store."""
    tokens = load_tokens()
    tokens[name] = token
    _save_tokens(tokens)    



def delete_token(name: str) -> None:
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



