# cinema-grpc-lab

Flask + FastAPI 마이크로서비스를 gRPC로 연동하는 영화 예매 실습 프로젝트.

## 학습 목표

- Flask로 REST API + JWT 인증 구현
- FastAPI로 비동기 REST API 구현 (Pydantic, 의존성 주입)
- `.proto` 파일 작성 및 Python 코드 생성 (protoc)
- gRPC 서버(Flask 측)와 클라이언트(FastAPI 측) 구현
- 두 서비스가 gRPC로 실제 통신하는 흐름 이해

---

## gRPC란?

### REST와 gRPC 비교

서비스 간 통신 방식으로 REST가 가장 익숙하지만, 마이크로서비스 환경에서는 gRPC도 널리 쓰인다.

| | REST | gRPC |
|---|---|---|
| 프로토콜 | HTTP/1.1 | HTTP/2 |
| 데이터 형식 | JSON (텍스트) | Protocol Buffers (바이너리) |
| 인터페이스 정의 | 암묵적 (문서로 관리) | `.proto` 파일로 명시적 정의 |
| 코드 생성 | 없음 | protoc가 서버/클라이언트 코드 자동 생성 |
| 성능 | 상대적으로 느림 | 바이너리 직렬화로 빠름 |
| 주요 사용처 | 외부 API, 브라우저 통신 | 내부 서비스 간 통신 |

### Protocol Buffers (.proto)

gRPC의 인터페이스 정의 언어(IDL). 어떤 언어로 구현하든 `.proto` 파일이 계약서 역할을 한다.

```protobuf
// proto/auth.proto
service AuthService {
    rpc ValidateToken (ValidateTokenRequest) returns (ValidateTokenResponse);
}

message ValidateTokenRequest {
    string token = 1;   // 필드 번호(= 1)는 이름이 아닌 바이너리 식별자
}

message ValidateTokenResponse {
    bool is_valid = 1;
    int32 user_id = 2;
}
```

`.proto`를 작성한 뒤 `protoc`로 컴파일하면 Python 코드가 자동 생성된다:

```bash
# Makefile의 auth-proto-gen 태스크
python -m grpc_tools.protoc \
    -I ./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    ./proto/auth.proto
```

생성된 파일:
- `auth_pb2.py` — 메시지 클래스 (`ValidateTokenRequest`, `ValidateTokenResponse`)
- `auth_pb2_grpc.py` — 서버 베이스 클래스(`AuthServiceServicer`)와 클라이언트 스텁(`AuthServiceStub`)

### gRPC 서버 (auth-service)

생성된 `AuthServiceServicer`를 상속해서 실제 로직을 구현한다.

```python
# auth-service/grpc_server.py
class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    def ValidateToken(self, request, context):
        try:
            payload = verify_token(request.token)
            return auth_pb2.ValidateTokenResponse(is_valid=True, user_id=payload["user_id"])
        except Exception:
            return auth_pb2.ValidateTokenResponse(is_valid=False, user_id=0)
```

### gRPC 클라이언트 (booking-service)

생성된 `AuthServiceStub`으로 서버를 원격 호출한다. 로컬 함수를 호출하는 것처럼 쓸 수 있다.

```python
# booking-service/dependencies.py
with grpc.insecure_channel("auth-grpc:50051") as channel:
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    response = stub.ValidateToken(auth_pb2.ValidateTokenRequest(token=token))
```

### 이 프로젝트에서의 흐름

```
Client
  │  POST /bookings
  │  Authorization: Bearer <JWT>
  ▼
booking-service (FastAPI :8000)
  │  1. Bearer 토큰 추출
  │  2. gRPC 호출 → ValidateToken(token)
  ▼
auth-grpc (gRPC :50051)
  │  3. JWT 서명 검증
  │  4. ValidateTokenResponse(is_valid=True, user_id=1) 반환
  ▼
booking-service
  │  5. user_id로 예매 처리
  ▼
Client  ← 201 Created
```

### 컨테이너 분리 설계

gRPC 서버는 Flask HTTP 서버와 같은 이미지를 사용하지만, 별도 컨테이너(`auth-grpc`)로 분리해 실행한다.

```yaml
auth-service:
  command: (Dockerfile 기본값) flask run ...  # HTTP 전담

auth-grpc:
  build: ./auth-service   # 같은 이미지 재사용
  command: python grpc_server.py  # gRPC 전담
```

분리 이유:
- HTTP와 gRPC 트래픽을 독립적으로 스케일링 가능
- 한쪽 장애가 다른 쪽에 영향 없음
- Flask reloader와 gRPC 스레드 간 프로세스 충돌 제거

---

## 서비스 구성

| 서비스 | 프레임워크 | 역할 | 포트 |
|--------|-----------|------|------|
| auth-service | Flask | 회원가입 / 로그인 / JWT 발급 | 5001 (호스트) → 5000 (컨테이너) |
| auth-grpc | Flask (same image) | gRPC 토큰 검증 서버 | 50051 |
| booking-service | FastAPI | 영화 조회 / 좌석 예매 / gRPC 클라이언트 | 8000 |
| auth-db | PostgreSQL | auth-service 전용 DB | 5432 |
| booking-db | PostgreSQL | booking-service 전용 DB | 5433 |

---

## 실행 방법

```bash
cp .env.example .env   # 환경변수 설정
docker compose up --build
```

---

## API

### auth-service (`:5001`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/register` | 회원가입 (이메일, 비밀번호) |
| POST | `/auth/login` | 로그인 → JWT 발급 |

### booking-service (`:8000`)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| GET | `/movies` | 불필요 | 전체 영화 목록 조회 |
| GET | `/movies/{id}/screenings` | 불필요 | 특정 영화의 상영 일정 조회 |
| POST | `/bookings` | Bearer JWT | 좌석 예매 |
| GET | `/healthcheck` | 불필요 | 헬스체크 |

`POST /bookings` 요청 예시:
```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"screening_id": 1, "seat_id": 3}'
```

---

## 프로젝트 구조

```
cinema-grpc-lab/
├── docker-compose.yml
├── .env.example
├── Makefile
├── proto/
│   └── auth.proto               # gRPC 인터페이스 정의
│
├── auth-service/                # Flask 회원 서비스
│   ├── Dockerfile
│   ├── wsgi.py                  # Flask 엔트리포인트
│   ├── grpc_server.py           # gRPC 서버 (auth-grpc 컨테이너용)
│   └── app/
│       ├── __init__.py          # Application Factory
│       ├── models.py            # User ORM 모델
│       ├── utils/jwt.py         # JWT 발급/검증
│       └── blueprints/auth.py  # /register, /login 라우트
│
└── booking-service/             # FastAPI 예매 서비스
    ├── Dockerfile
    ├── main.py                  # FastAPI 앱 엔트리포인트
    ├── dependencies.py          # gRPC 토큰 검증 의존성
    ├── domain.py                # 레이어 간 전달용 dataclass
    ├── models.py                # SQLAlchemy ORM 모델
    ├── schemas.py               # Pydantic 요청/응답 스키마
    ├── core/
    │   ├── database.py          # DB 엔진, 세션, Base
    │   ├── exceptions.py        # 커스텀 예외 클래스
    │   └── exception_handlers.py
    ├── repositories/            # DB 접근 레이어
    ├── services/                # 비즈니스 로직 레이어
    └── routers/                 # API 엔드포인트
```

---

## Makefile 주요 명령어

```bash
make auth-proto-gen        # .proto → Python 코드 생성
make auth-migrate          # auth-service DB 마이그레이션 실행
make booking-migrate       # booking-service DB 마이그레이션 실행
```
