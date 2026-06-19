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
