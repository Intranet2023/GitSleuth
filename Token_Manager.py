#Token_Manager.py
import json
from cryptography.fernet import Fernet

TOKEN_FILE = 'tokens.json'
KEY_FILE = 'token_key.key'

def load_key():
    try:
        with open(KEY_FILE, 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
        return key

key = load_key()
cipher_suite = Fernet(key)

def encrypt_token(token):
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted):
    return cipher_suite.decrypt(token_encrypted.encode()).decode()

def load_tokens():
    try:
        with open(TOKEN_FILE, 'r') as file:
            encrypted_tokens = json.load(file)
        return {name: decrypt_token(token) for name, token in encrypted_tokens.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_tokens(tokens):
    encrypted_tokens = {name: encrypt_token(token) for name, token in tokens.items()}
    with open(TOKEN_FILE, 'w') as file:
        json.dump(encrypted_tokens, file)

def add_token(name, token):
    tokens = load_tokens()
    tokens[name] = token
    save_tokens(tokens)

def delete_token(name):
    tokens = load_tokens()
    if name in tokens:
        del tokens[name]
        save_tokens(tokens)
