# 진행 상황

## 2026-06-16
- 프로젝트 초기 세팅
  - CLAUDE.md 작성 (Claude Code 컨텍스트)
  - docs/ 구조 생성 (plan, progress, architecture, decisions)
  - 전체 아키텍처 설계 완료
- 기술 스택 결정 업데이트: SQLite → PostgreSQL (서비스별 독립 DB), Docker Compose 도입 확정
- Phase 1 완료
  - 디렉토리 구조 생성 (`auth-service/app/`, `booking-service/app/`, `proto/`)
  - `docker-compose.yml` — 4개 서비스, healthcheck + `condition: service_healthy`, named volumes, `.env` 변수 주입
  - 각 서비스 `Dockerfile`, `requirements.txt`
  - `.env`, `.env.example`, `.gitignore` (`*_pb2.py` 추가)
- **다음 할 일**: Phase 2 — auth-service Flask 앱 구현 (Application Factory 패턴부터)

## 2026-06-17
- Phase 2 진행 중
  - `app/__init__.py` Application Factory 패턴 구현 완료 (`create_app`, `db = SQLAlchemy()`, Blueprint 등록)
  - ORM 전략을 DB-first(SQLAlchemy Reflection)로 변경 결정 — SQL 초기화 스크립트가 스키마 소스 오브 트루스
  - docs 업데이트: decisions.md에 ORM 전략 결정 기록, plan.md Phase 2 태스크 갱신, architecture.md 디렉토리 구조 반영

## 2026-06-18
- Phase 2 계속
  - `postgres/auth-init/01_create_users.sql` 작성 (참고용으로 보존, 실제 미사용)
  - `docker-compose.yml` — `env_file: .env`로 환경변수 주입, auth-db init 스크립트 볼륨 마운트 제거
  - `app/__init__.py` — DB URI PostgreSQL로 교체, 환경변수 기반으로 수정
  - ORM 전략 재결정: DB-first + Reflection → **Code-first + Alembic 마이그레이션**으로 변경
  - `requirements.txt` — Flask-Migrate 추가
  - `app/__init__.py` — Flask-Migrate 연동, models import 추가
  - `app/blueprints/auth.py` — Blueprint 선언
  - `app.py` — 엔트리포인트 작성
  - `docker-compose.yml` — auth-service 볼륨 마운트 추가 (코드 변경 즉시 반영)
  - `Makefile` — auth-migrate, auth-migrate-create, auth-migrate-init 명령 추가
  - Alembic 초기화 (`flask db init`) 및 첫 마이그레이션 생성/적용 완료 (`users` 테이블)
- **다음 할 일**: 회원가입 API `POST /register` → 로그인 API `POST /login` + JWT 발급

## 2026-06-19
- Phase 2 계속
  - `requirements.txt` — `bcrypt` 추가
  - `app/blueprints/auth.py` — `POST /auth/register` 구현 (이메일 중복 확인, bcrypt 해싱, DB 저장, try/rollback)
  - `app/blueprints/auth.py` — `POST /auth/login` 구현 (bcrypt 검증, PyJWT 토큰 발급)
  - `Dockerfile` — `flask run --reload` 추가 (볼륨 마운트 + 자동 재시작)
  - `docker-compose.yml` — auth-service 포트 `5001:5000`으로 변경 (macOS AirPlay 포트 충돌 해결)
  - `docker-compose.yml` — healthcheck에 `-d ${AUTH_DB_NAME}` 추가 (FATAL 노이즈 제거)
  - `CLAUDE.md` — SQLAlchemy v2 스타일 규칙 추가
  - Docker 볼륨 재생성 (`docker compose down -v`) — 초기화 누락 문제 해결
  - `/register`, `/login` API 테스트 완료
- **다음 할 일**: JWT 검증 유틸 함수 → gRPC 서버 구현 (Phase 3 시작)

## 2026-06-22
- Phase 2 완료
  - `app/utils/jwt.py` — `verify_token()` 구현 (B 방식: 예외 bubble up, gRPC 핸들러에서 catch)
  - `.gitignore` — `data/` 추가 (Claude Code 상태 파일 제외)
  - `docs/decisions.md` — gRPC 핸들러 Flask app context 명시 필요 기록
- Phase 3 시작
  - `booking-service/main.py` — FastAPI 앱 기본 구조, `/healthcheck` 엔드포인트
  - `booking-service/Dockerfile` — uvicorn 실행으로 변경
  - `booking-service/database.py` — asyncpg + create_async_engine + async_sessionmaker + get_db 비동기 제너레이터
  - `booking-service/requirements.txt` — asyncpg, alembic 추가 (psycopg2-binary 제거)
  - `booking-service/models.py` — Movie, Hall, Screening, Seat, Booking ORM 모델 정의
  - `booking-service/routers/` — movies.py, bookings.py 라우터 구조 생성
  - `booking-service/README.md` — DB 관계도 (Mermaid ERD) 작성
  - Alembic async 템플릿으로 마이그레이션 설정, 초기 테이블 생성 완료
  - `Makefile` — booking-migrate-init, booking-migrate-create, booking-migrate 명령 추가
  - `GET /movies` 구현 + `MovieResponse` 스키마
  - `GET /movies/{movie_id}/screenings` 구현 + `ScreeningResponse` 스키마
  - `docs/decisions.md` — 비동기 DB 스택 선택, 좌석 모델 설계(Hall/Seat 분리), Hall 테이블 추가 결정 기록
- **다음 할 일**: `POST /bookings` 구현 + JWT Bearer 의존성 주입 → 레이어 분리

## 2026-06-23
- Phase 3 계속
  - `GET /movies/{movie_id}/screenings` f-string 버그 수정
  - `booking-service/dependencies.py` — `get_current_user_id` JWT Bearer 의존성 구현
  - `booking-service/schemas.py` — `BookingRequest`, `BookingResponse` 추가
  - `booking-service/routers/bookings.py` — `POST /bookings` 구현 (screening/seat 존재 확인, UniqueConstraint 위반 시 409)
  - `booking-service/seeds/seed.sql` — 초기 seed 데이터 저장
  - `booking-service/database.py` — `get_db` except 블록에 `raise` 추가 (yield 의존성 예외 소멸 버그 수정)
  - `POST /bookings` 테스트 완료 (정상 예매 201, 중복 예매 409)
- **다음 할 일**: repository/service 레이어 분리 또는 Phase 4 gRPC 연동

## 2026-06-24
- Phase 4 완료
  - `proto/auth.proto` — `ValidateToken` RPC 정의
  - `proto/auth_pb2.py`, `proto/auth_pb2_grpc.py` — `make auth-proto-gen`으로 생성
  - `auth-service/grpc_server.py` — gRPC 서버 구현 (`AuthServiceServicer.ValidateToken`)
  - `auth-service/wsgi.py` — Flask 엔트리포인트 (`app.py` → `wsgi.py` 이름 변경, 패키지 충돌 해결)
  - `auth-service/app/utils/jwt.py` — `current_app.config` → `os.environ` 변경 (gRPC 스레드는 Flask context 밖)
  - `booking-service/dependencies.py` — JWT 로컬 검증 → gRPC 호출로 교체
  - `booking-service/exceptions.py` — `UNAUTHORIZED` ErrorCode, `UnAuthorizedError` 추가
  - `docker-compose.yml` — proto 볼륨 마운트, `FLASK_APP=wsgi.py` 환경변수 추가
  - `Makefile` — `auth-proto-gen` 태스크 추가
  - booking-service에서 gRPC 호출 성공 확인
- gRPC 서버 컨테이너 분리 리팩토링
  - `auth-service/grpc_server.py` — `if __name__ == "__main__": serve()` 추가
  - `auth-service/wsgi.py` — gRPC 스레드 코드 제거, Flask만 남김
  - `docker-compose.yml` — `auth-grpc` 서비스 분리 (`command: python grpc_server.py`, 같은 이미지 재사용)
  - `booking-service/dependencies.py` — `auth-service:50051` → `auth-grpc:50051`
  - 테스트 완료
- **다음 할 일**: Phase 5 — 전체 흐름 통합 테스트 (회원가입 → 로그인 → 토큰 → 예매)
