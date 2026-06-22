import jwt
from flask import current_app


def verify_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )
