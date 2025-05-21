import json
import os
import logging

TOKEN_FILE = 'tokens.json'

def load_tokens():
    """Load saved GitHub tokens from TOKEN_FILE."""
    if not os.path.exists(TOKEN_FILE):
        return {}
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as exc:
        logging.error(f"Failed to load tokens: {exc}")
        return {}

def _save_tokens(tokens):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f)

def add_token(name, token):
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

def switch_token(_config=None):
    """Rotate the GITHUB_OAUTH_TOKEN environment variable among saved tokens."""
    tokens = list(load_tokens().values())
    if not tokens:
        logging.error("No tokens available for rotation.")
        return False
    current = os.environ.get('GITHUB_OAUTH_TOKEN')
    if current in tokens:
        idx = tokens.index(current)
        new_token = tokens[(idx + 1) % len(tokens)]
    else:
        new_token = tokens[0]
    os.environ['GITHUB_OAUTH_TOKEN'] = new_token
    logging.info("Switched GitHub token")
    return True
