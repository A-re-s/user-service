from fastapi import HTTPException, status


InvalidCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid login or password"
)
UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)
InvalidToken = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
)
InvalidTokenType = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
)

TokenRevoked = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
)

TokenExpired = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
)

UserAlreadyExist = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="User with this login already exists"
)

SelfActionRequired = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="This action can only be performed on your own account",
)

DatabaseError = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred"
)
