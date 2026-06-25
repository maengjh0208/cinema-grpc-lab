# 전체 구현 계획

## 학습 목표
1. Flask로 REST API + JWT 인증 구현
2. FastAPI로 REST API 구현 (Pydantic, 의존성 주입)
3. protobuf `.proto` 파일 작성 및 Python 코드 생성
4. gRPC 서버(Flask 쪽)와 클라이언트(FastAPI 쪽) 구현
5. 두 서비스가 실제로 통신하는 흐름 이해

---

## Phase 1: 기반 구조 세팅 ✅
- [x] 디렉토리 구조 생성 (`auth-service/`, `booking-service/`, `proto/`)
- [x] 각 서비스 `requirements.txt` 작성
- [x] 각 서비스 `Dockerfile` 작성
- [x] `docker-compose.yml` 작성 (auth-service, booking-service, auth-db, booking-db)
- [x] `.gitignore` 확인 (`*_pb2.py`, `.env` 등)
- [x] `.env.example` 작성 (DB 접속 정보 등)

## Phase 2: auth-service (Flask) ✅
- [x] Flask Application Factory 구조 (`app/__init__.py`, `app/blueprints/`)
- [x] `app/__init__.py` — DB URI를 PostgreSQL로 교체, 환경변수로 관리
- [x] `docker-compose.yml` — `env_file` 로 환경변수 주입
- [x] `app/models.py` — SQLAlchemy ORM으로 User 모델 정의 (Code-first)
- [x] `requirements.txt` — `Flask-Migrate`, `bcrypt` 추가
- [x] `app/__init__.py` — `Flask-Migrate` 연동
- [x] Alembic 초기화 및 첫 마이그레이션 생성/적용 (`flask db init/migrate/upgrade`)
- [x] 마이그레이션은 자동 실행 대신 `Makefile`로 수동 실행 (결정: race condition 방지)
- [x] `app.py` 엔트리포인트 작성
- [x] 회원가입 API `POST /auth/register`
- [x] 로그인 API `POST /auth/login` → JWT 발급
- [x] JWT 검증 유틸 함수 (`app/utils/jwt.py`)

## Phase 3: booking-service (FastAPI) ✅
- [x] FastAPI 앱 기본 구조 (`main.py`, `routers/`)
- [x] DB 설정 (`database.py`) — asyncpg + AsyncSession + Alembic async 마이그레이션
- [x] ORM 모델 정의 (`models.py`) — Movie, Hall, Screening, Seat, Booking
- [x] 영화 목록 조회 `GET /movies`
- [x] 상영 일정 조회 `GET /movies/{id}/screenings`
- [x] 좌석 예매 `POST /bookings` (인증 필요)
- [x] JWT Bearer 토큰 의존성 주입
- [x] repository/service 레이어 분리 (domain, repository, service, exception 계층 분리)

## Phase 4: gRPC 연동 ✅
- [x] `proto/auth.proto` 작성 — `ValidateToken` RPC 정의
- [x] protoc로 Python 코드 생성 (`auth_pb2.py`, `auth_pb2_grpc.py`)
- [x] auth-service에 gRPC 서버 추가 (Flask HTTP과 별도 스레드)
- [x] booking-service에 gRPC 클라이언트 추가
- [x] 예매 요청 시 gRPC로 토큰 검증하는 흐름 완성

---

## 현재 단계
**전체 구현 완료**
