from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserAuthSchema(BaseModel):
    login: Annotated[str, Field(max_length=255)]
    password: Annotated[str, Field(max_length=255)]


class UserInfoResponseSchema(BaseModel):
    id: int
    login: Annotated[str, Field(max_length=255)]
    money_balance: Annotated[
        Decimal,
        Field(
            gt=0,
            decimal_places=10,
            max_digits=30,
        ),
    ]


class UserSchema(UserInfoResponseSchema, UserAuthSchema):
    model_config = ConfigDict(from_attributes=True)
    token_version: Annotated[int, Field(ge=0)]


class AccessTokenSchema(BaseModel):
    access_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenObtainPairSchema(AccessTokenSchema, RefreshTokenSchema):
    pass


class TokenPayloadSchema(BaseModel):
    id: int
    token_version: int
    token_type: TokenType
    exp: int


class TokenSchema(BaseModel):
    token: str


class AddMoneySchema(BaseModel):
    amount: Annotated[
        Decimal,
        Field(
            gt=0,
            decimal_places=10,
            max_digits=30,
            example=100.50,
            description="Positive decimal amount",
        ),
    ]
