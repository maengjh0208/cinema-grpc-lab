# 시스템 아키텍처

## 전체 흐름

```
┌─────────────┐        HTTP         ┌──────────────────────┐
│   Client    │ ─────────────────→  │  booking-service     │
│ (curl/앱)   │                     │  (FastAPI :8000)     │
└─────────────┘                     │                      │
                                    │  1. JWT 토큰 추출     │
                                    │  2. gRPC 호출        │
                                    └──────────┬───────────┘
                                               │  gRPC
                                               ▼
                                    ┌──────────────────────┐
                                    │  auth-service        │
                                    │  (Flask :5000)       │
                                    │  (gRPC server :50051)│
                                    │                      │
                                    │  3. 토큰 검증        │
                                    │  4. 사용자 정보 반환  │
                                    └──────────────────────┘
```

## 예매 요청 시퀀스

```
Client                booking-service           auth-service
  │                         │                        │
  │  POST /bookings         │                        │
  │  Authorization: Bearer  │                        │
  │  <JWT>                  │                        │
  │ ──────────────────────→ │                        │
  │                         │  ValidateToken(token)  │
  │                         │ ─────────────────────→ │
  │                         │                        │ JWT 검증
  │                         │  UserInfo(id, email)   │
  │                         │ ←───────────────────── │
  │                         │ 예매 처리              │
  │  200 OK (예매 결과)     │                        │
  │ ←────────────────────── │                        │
```

## 디렉토리 구조

```
cinema-grpc-lab/
├── CLAUDE.md                    # Claude Code 컨텍스트
├── README.md
├── docs/
│   ├── plan.md                  # 구현 계획 & TODO
│   ├── progress.md              # 날짜별 진행 기록
│   ├── architecture.md          # 이 파일
│   └── decisions.md             # 기술 의사결정 기록
│
├── postgres/                    # DB 초기화 스크립트 (DB-first 스키마 관리)
│   ├── auth-init/
│   │   └── 01_create_users.sql  # auth-db 테이블 정의
│   └── booking-init/            # (Phase 3에서 추가)
│
├── proto/
│   └── auth.proto               # ValidateToken RPC 정의
│
├── auth-service/                # Flask 회원 서비스
│   ├── requirements.txt
│   ├── app.py                   # Flask 앱 엔트리포인트
│   ├── app/
│   │   ├── __init__.py          # Application Factory (create_app)
│   │   ├── models.py            # SQLAlchemy Reflection으로 User 클래스 구성
│   │   └── blueprints/
│   │       └── auth.py          # /register, /login 라우트
│   ├── grpc_server.py           # gRPC 서버 (별도 스레드)
│   ├── auth_pb2.py              # protoc 생성 (수정 금지)
│   └── auth_pb2_grpc.py         # protoc 생성 (수정 금지)
│
└── booking-service/             # FastAPI 예매 서비스
    ├── requirements.txt
    ├── main.py                  # FastAPI 앱 엔트리포인트
    ├── grpc_client.py           # gRPC 클라이언트
    ├── auth_pb2.py              # protoc 생성 (수정 금지)
    ├── auth_pb2_grpc.py         # protoc 생성 (수정 금지)
    └── routers/
        ├── movies.py            # /movies 라우트
        └── bookings.py          # /bookings 라우트
```

## 기술 스택

| 항목 | 선택 | 이유 |
|------|------|------|
| 회원 서비스 | Flask | 가볍고 명시적. Blueprint로 구조화 |
| 예매 서비스 | FastAPI | async, Pydantic, OpenAPI 자동 생성 |
| RPC | gRPC (grpcio) | 강타입 인터페이스, 성능, 마이크로서비스 표준 |
| 직렬화 | Protocol Buffers | gRPC 기본 직렬화 형식 |
| 인증 | JWT (PyJWT) | Stateless 토큰 인증 |
| DB | PostgreSQL (서비스별 독립) | Database per Service 패턴 |
| 실행 환경 | Docker Compose | 단일 명령으로 전체 스택 실행 |

## 포트 정리

| 서비스 | 프로토콜 | 포트 |
|--------|---------|------|
| auth-service | HTTP (Flask) | 5000 |
| auth-service | gRPC | 50051 |
| booking-service | HTTP (FastAPI) | 8000 |
| auth-db | PostgreSQL | 5432 |
| booking-db | PostgreSQL | 5433 |

## Docker Compose 구성

```
┌─────────────────────────────────────────────────────┐
│                  docker network                     │
│                                                     │
│  ┌─────────────────┐      ┌──────────────────────┐  │
│  │  auth-service   │      │  booking-service     │  │
│  │  Flask :5000    │      │  FastAPI :8000       │  │
│  │  gRPC  :50051   │ ←─── │  gRPC client         │  │
│  └────────┬────────┘      └──────────┬───────────┘  │
│           │                          │              │
│  ┌────────▼────────┐      ┌──────────▼───────────┐  │
│  │    auth-db      │      │    booking-db        │  │
│  │  PostgreSQL     │      │  PostgreSQL          │  │
│  │  :5432          │      │  :5433               │  │
│  └─────────────────┘      └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

각 서비스는 자신의 DB에만 접근. 서비스 간 데이터 공유는 반드시 gRPC(또는 HTTP API)를 통해서만.
