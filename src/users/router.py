from typing import Annotated
from fastapi import APIRouter, Depends, Path
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import get_session
from users.models import UserModel
from users.utils import hash_password, create_access_token, create_refresh_token
from users.schemas import (
    TokenObtainPairSchema,
    UserAuthSchema,
    UserSchema,
    UserInfoResponseSchema,
    TokenSchema,
    AddMoneySchema,
)
from users.dependencies import (
    get_user_from_access_token,
    get_user_from_credentials,
    get_user_from_refresh_token,
    validate_token_payload,
    get_token_validator,
)
from users.exceptions import UserAlreadyExist, SelfActionRequired, DatabaseError


users_router = APIRouter()


@users_router.post("/register")
async def register_user_jwt(
    user: UserAuthSchema, session: Annotated[AsyncSession, Depends(get_session)]
) -> UserInfoResponseSchema:
    hashed_password = hash_password(user.password)
    new_user: UserModel = UserModel(login=user.login, password=hashed_password)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError as exc:
        await session.rollback()
        raise UserAlreadyExist from exc

    return new_user


@users_router.post("/token")
async def get_user_token(
    user: Annotated[UserSchema, Depends(get_user_from_credentials)]
) -> TokenObtainPairSchema:

    access_token = create_access_token(user.id, user.token_version)
    refresh_token = create_refresh_token(user.id, user.token_version)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@users_router.post("/users/me")
async def get_user_info(
    current_user: Annotated[UserSchema, Depends(get_user_from_access_token)]
) -> UserInfoResponseSchema:
    return current_user


@users_router.post("/token/refresh")
async def refresh_tokens(
    user: Annotated[UserSchema, Depends(get_user_from_refresh_token)]
) -> TokenObtainPairSchema:
    access_token = create_access_token(user.id, user.token_version)
    refresh_token = create_refresh_token(user.id, user.token_version)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@users_router.post("/token/verify")
async def verify_token(
    payload: TokenSchema, session: Annotated[AsyncSession, Depends(get_session)]
):
    token = payload.token
    validator = get_token_validator()
    token_payload = validate_token_payload(token)
    user = await validator(token=token, session=session)
    return {
        "detail": "Token is valid",
        "user_id": user.id,
        "token_type": token_payload.token_type,
    }


@users_router.post("/users/{user_id}/revoke_tokens")
async def revoke_user_tokens(
    user_id: Annotated[int, Path(title="id of current user")],
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if user_id != user.id:
        raise SelfActionRequired
    try:
        await session.execute(
            update(UserModel)
            .values(token_version=UserModel.token_version + 1)
            .where(UserModel.id == user_id)
        )
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        raise DatabaseError from exc
    return {"detail": "Tokens revoked"}


@users_router.post("/users/{user_id}/add_money")
async def add_money(
    user_id: Annotated[int, Path(title="id of current user")],
    money_schema: AddMoneySchema,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if user_id != user.id:
        raise SelfActionRequired
    try:
        await session.execute(
            update(UserModel)
            .values(money_balance=UserModel.money_balance + money_schema.amount)
            .where(UserModel.id == user_id)
        )
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        raise DatabaseError from exc
    return {"detail": "Money added"}
