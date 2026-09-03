from fastapi import HTTPException, status


class InvalidClientSecret(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Client-Secret header.",
        )


class InvalidAdminCredentials(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )


class AdminUserNotFound(HTTPException):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin user '{identifier}' not found.",
        )


class AdminUserConflict(HTTPException):
    def __init__(self, detail: str = "Admin user already exists.") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
