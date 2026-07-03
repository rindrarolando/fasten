from fastapi import HTTPException, status


# TODO: rename and add error classes for each domain entity.


class ExampleModelNotFound(HTTPException):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{identifier}' not found.",
        )


class ExampleModelConflict(HTTPException):
    def __init__(self, detail: str = "Conflict.") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
