from enum import StrEnum


class ErrorCode(StrEnum):
    # 400
    DUPLICATE_BOOKING = "DUPLICATE_BOOKING"
    # 401
    UNAUTHORIZED = "UNAUTHORIZED"
    # 404
    MOVIE_NOT_FOUND = "MOVIE_NOT_FOUND"
    SCREENING_NOT_FOUND = "SCREENING_NOT_FOUND"
    SEAT_NOT_FOUND = "SEAT_NOT_FOUND"
    # 500
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class BadRequestError(Exception):
    def __init__(self, error_code: ErrorCode, detail: str | None = None, status_code: int = 400):
        self.error_code = error_code
        self.detail = detail
        self.status_code = status_code


class UnAuthorizedError(BadRequestError):
    def __init__(self, error_code: ErrorCode, detail: str | None = None, status_code: int = 401):
        super().__init__(
            error_code=error_code,
            detail=detail,
            status_code=status_code,
        )


class NotFoundError(BadRequestError):
    def __init__(self, error_code: ErrorCode, detail: str | None = None, status_code: int = 404):
        super().__init__(
            error_code=error_code,
            detail=detail,
            status_code=status_code,
        )


class InternalServerError(BadRequestError):
    def __init__(self, error_code: ErrorCode, detail: str | None = None, status_code: int = 500):
        super().__init__(
            error_code=error_code,
            detail=detail,
            status_code=status_code,
        )
