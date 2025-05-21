from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import DecodeError
from database import get_session
from users.models import UserModel
from users.utils import validate_password, decode_jwt
from users.schemas import UserAuthSchema, UserSchema
from users.exceptions import InvalidCredentials, UserNotFound, InvalidToken

http_bearer = HTTPBearer()


async def get_user_from_db(
    user_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> UserModel:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound
    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserSchema:
    try:
        token = credentials.credentials
        payload = decode_jwt(token)
        current_user = await get_user_from_db(payload["id"], session)
    except DecodeError as exc:
        raise InvalidToken from exc
    return current_user


async def authenticate_user(
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
