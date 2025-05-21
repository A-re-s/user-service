from typing import Any
import jwt
import bcrypt
from config import settings


def encode_jwt(
    payload: dict[str, Any],
    key: str = settings.auth_jwt.secret_key,
    algorithm: str = settings.auth_jwt.algorithm
) -> str:
    encoded = jwt.encode(payload, key, algorithm)
    return encoded

def decode_jwt(
    token: str,
    key: str = settings.auth_jwt.secret_key,
    algorithm: str = settings.auth_jwt.algorithm
) -> Any:
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    return decoded

def hash_password(
    password: str
) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def validate_password(
    password: str,
    hashed_password: str
) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
