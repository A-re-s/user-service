from functools import lru_cache
from typing import Annotated, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database import get_session
from users.exceptions import (
    InvalidCredentials,
    InvalidToken,
    InvalidTokenType,
    TokenExpired,
    TokenRevoked,
    Usernot_found,
)
from users.models import UserModel
from users.schemas import (
    RefreshTokenSchema,
    TokenPayloadSchema,
    TokenType,
    UserAuthSchema,
    UserSchema,
)
from users.utils import decode_jwt, validate_password


http_bearer = HTTPBearer()


class TokenValidator:
    def __init__(self, expected_token_type: TokenType | None = None):
        self.expected_token_type = expected_token_type

    async def __call__(
        self, token: str, session: AsyncSession, settings: Settings
    ) -> UserSchema:
        token_payload = validate_token_payload(token, settings)

        if (
            self.expected_token_type is not None
            and token_payload.token_type != self.expected_token_type
        ):
            raise InvalidTokenType

        user_from_db = await get_user_from_db(token_payload.id, session)
        if user_from_db.token_version != token_payload.token_version:
            raise TokenRevoked

        return user_from_db


@lru_cache
def get_token_validator(expected_token_type: TokenType | None = None) -> TokenValidator:
    return TokenValidator(expected_token_type)


async def get_access_token_from_header(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> str:
    return credentials.credentials


async def get_refresh_token_from_schema(refresh_data: RefreshTokenSchema) -> str:
    return refresh_data.refresh_token


def get_token_validator_with_token(
    expected_token_type: TokenType, token_dependency: Callable[..., str]
) -> Callable[[AsyncSession], int]:
    async def dependency(
        token: Annotated[str, Depends(token_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> int:
        validator = get_token_validator(expected_token_type)
        return await validator(token=token, session=session, settings=settings)

    return dependency


async def get_user_from_access_token(
    user: Annotated[
        UserSchema,
        Depends(
            get_token_validator_with_token(
                TokenType.ACCESS, get_access_token_from_header
            )
        ),
    ],
) -> UserSchema:
    return user


async def get_user_from_refresh_token(
    user: Annotated[
        UserSchema,
        Depends(
            get_token_validator_with_token(
                TokenType.REFRESH, get_refresh_token_from_schema
            )
        ),
    ],
) -> UserSchema:
    return user


async def get_user_from_db(user_id: int, session: AsyncSession) -> UserSchema:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise Usernot_found
    return UserSchema.model_validate(user)


def validate_token_payload(token: str, settings: Settings) -> TokenPayloadSchema:
    try:
        raw_payload = decode_jwt(
            token, settings.auth_jwt.secret_key, settings.auth_jwt.algorithm
        )
        token_payload: TokenPayloadSchema = TokenPayloadSchema(**raw_payload)
        return token_payload
    except (DecodeError, ValidationError) as exc:
        raise InvalidToken from exc
    except ExpiredSignatureError as exc:
        raise TokenExpired from exc


async def get_user_from_credentials(
    user_creds: UserAuthSchema, session: Annotated[AsyncSession, Depends(get_session)]
) -> UserSchema:
    result = await session.execute(
        select(UserModel).where(UserModel.login == user_creds.login)
    )
    user_in_db = result.scalar_one_or_none()
    if user_in_db is None:
        raise InvalidCredentials
    if not validate_password(user_creds.password, user_in_db.password):
        raise InvalidCredentials
    return user_in_db
