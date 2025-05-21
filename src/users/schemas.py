from typing import Annotated
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal


class UserAuthSchema(BaseModel):
    login: Annotated[str, Field(max_length=255)]
    password: Annotated[str, Field(max_length=255)]

class UserInfoResponseSchema(BaseModel):
    id: int
    login: Annotated[str, Field(max_length=255)]
    money_balance: Annotated[Decimal, condecimal(decimal_places=10, max_digits=30)]

class UserSchema(UserInfoResponseSchema, UserAuthSchema):
    token_version: Annotated[int, Field(ge=0)]

class AccessTokenSchema(BaseModel):
    access_token: str

class RefreshTokenSchema(BaseModel):
    refresh_token: str

class TokenObtainPairSchema(AccessTokenSchema, RefreshTokenSchema):
    pass

class TokenSchema(BaseModel):
    token: str
