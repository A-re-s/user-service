from fastapi import HTTPException, status


def already_exist(subject: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{subject} with this name already exists",
    )


def not_found(subject: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{subject} not found")
