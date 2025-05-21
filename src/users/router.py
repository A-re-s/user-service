from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from database import get_session
from users.models import UserModel
from users.utils import hash_password, encode_jwt
from users.schemas import AccessTokenSchema, UserAuthSchema, UserSchema, UserInfoResponseSchema
from users.dependencies import get_current_user, authenticate_user
from users.exceptions import UserAlreadyExist


users_router = APIRouter()



@users_router.post("/register")
async def register_user_jwt(
    user: UserAuthSchema,
    session: Annotated[AsyncSession, Depends(get_session)]
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
    user: Annotated[UserSchema, Depends(authenticate_user)]
) -> AccessTokenSchema:
    token_payload = {
        "id" : user.id,
        "token_version" : user.token_version
    }

    token = encode_jwt(token_payload)
    return {"access_token" : token}

@users_router.post("/users/me")
async def get_user_info(
    current_user: Annotated[UserSchema, Depends(get_current_user)]
) -> UserInfoResponseSchema:
    return current_user
