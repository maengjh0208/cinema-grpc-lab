import os

import jwt


# gRPC 에서 가져다 쓸 JWT 검증 로직
def verify_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        # Flask 컨텍스트 밖(gRPC 서버 스레드)에서는 flask 의 current_app 을 쓸 수 없음.
        # gRPC 에서 쓰려면 JWT_SECRET_KEY 를 환경변수에서 직접 읽도록 분리해야 함.
        key=os.environ["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )
