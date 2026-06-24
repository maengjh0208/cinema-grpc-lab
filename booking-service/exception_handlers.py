from exceptions import BadRequestError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(BadRequestError)
    async def app_error_handler(request: Request, exc: BadRequestError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )
