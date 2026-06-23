import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Authorization: Bearer xxx 헤더를 자동으로 파싱
security = HTTPBearer()


def get_current_user_id(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> int:
    # Bearer 뒤의 토큰 문자열만 꺼냄
    token = credentials.credentials

    # TODO: auth-service 에서 gRPC 호출로 변경 예정
    try:
        payload = jwt.decode(
            jwt=token,
            key=os.environ["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
        return int(payload["user_id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰 만료됨")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
