from typing import Annotated

import auth_pb2
import auth_pb2_grpc
import grpc
from core.exceptions import ErrorCode, UnAuthorizedError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Authorization: Bearer xxx 헤더를 자동으로 파싱
security = HTTPBearer()


def get_current_user_id(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> int:
    token = credentials.credentials

    # Docker 내부 네트워크에서 auth-service 의 50051 포트로 연결
    with grpc.insecure_channel("auth-grpc:50051") as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        response = stub.ValidateToken(auth_pb2.ValidateTokenRequest(token=token))

    if not response.is_valid:
        raise UnAuthorizedError(ErrorCode.UNAUTHORIZED, "유효하지 않은 토큰")

    return response.user_id
