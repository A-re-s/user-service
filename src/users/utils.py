from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from config import Settings


def encode_jwt(
    payload: dict[str, Any],
    key: str,
    algorithm: str,
    expire_time_delta: int | None = None,
) -> str:
    to_encode = payload.copy()
    if expire_time_delta is not None:
        to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
            minutes=expire_time_delta
        )
    encoded = jwt.encode(to_encode, key, algorithm)
    return encoded


def create_access_token(user_id: int, user_token_version: int, settings: Settings):
    token_payload = {
        "id": user_id,
        "token_version": user_token_version,
        "token_type": "access",
    }
    return encode_jwt(
        token_payload,
        expire_time_delta=settings.auth_jwt.access_token_expire_minutes,
        algorithm=settings.auth_jwt.algorithm,
        key=settings.auth_jwt.secret_key,
    )


def create_refresh_token(user_id: int, user_token_version: int, settings: Settings):
    token_payload = {
        "id": user_id,
        "token_version": user_token_version,
        "token_type": "refresh",
    }
    return encode_jwt(
        token_payload,
        expire_time_delta=settings.auth_jwt.refresh_token_expire_minutes,
        algorithm=settings.auth_jwt.algorithm,
        key=settings.auth_jwt.secret_key,
    )


def decode_jwt(
    token: str,
    key: str,
    algorithm: str,
) -> Any:
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
