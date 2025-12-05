from fastapi import HTTPException, status

class DuplicatedUsernameError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate account ID"
        )

class DuplicatedEmailError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate email"
        )