import hashlib
import secrets
import time

token_store = {}
TOKEN_EXPIRE_SECONDS = 24 * 3600

def md5(text: str):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def generate_token(user_name: str) -> str:
    token = secrets.token_urlsafe(32)
    expire_time = time.time() + TOKEN_EXPIRE_SECONDS
    token_store[token] = {
        "user_name": user_name,
        "expire": expire_time
    }
    return token

def verify_token(token: str) -> str | None:
    if token not in token_store:
        return None
    data = token_store[token]
    if time.time() > data["expire"]:
        del token_store[token]
        return None
    return data["user_name"]