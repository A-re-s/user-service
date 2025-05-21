from fastapi import HTTPException, status

InvalidCredentials = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid login or password"
        )
UserNotFound = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
InvalidToken = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

UserAlreadyExist = HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this login already exists"
        )
