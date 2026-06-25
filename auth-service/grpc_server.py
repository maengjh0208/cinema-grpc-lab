from concurrent import futures

import auth_pb2
import auth_pb2_grpc
import grpc
from app.utils.jwt import verify_token


# auth_pb2_grpc 의 AuthServiceServicer 를 상속받고, ValidateToken 를 오버라이드 - 실제 로직 구현
class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    def ValidateToken(self, request, context):
        try:
            # request.token - proto 에서 정의한 ValidateTokenRequest.token 필드
            payload = verify_token(request.token)
            return auth_pb2.ValidateTokenResponse(is_valid=True, user_id=payload["user_id"])
        except Exception:
            return auth_pb2.ValidateTokenResponse(is_valid=False, user_id=0)


def serve():
    # futures.ThreadPoolExecutor(max_workers=10) - gRPC 요청을 처리할 스레드풀
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()

    print("========================================")
    print("gRPC server started on port 50051")
    print("========================================")

    # 서버를 계속 실행 상태로 유지
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
