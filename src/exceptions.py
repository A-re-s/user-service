from fastapi import HTTPException, status


SelfActionRequired = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="This action can only be performed on your own account",
)

DatabaseError = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred"
)
