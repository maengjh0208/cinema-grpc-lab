# 기술 의사결정 기록

의사결정마다 **무엇을**, **왜**, **어떤 대안을 고려했는지** 기록.

---

## [2026-06-16] Flask vs Django (회원 서비스)

**결정**: Flask 선택

**이유**
- 학습 목적이므로 최소한의 마법(magic) 없이 명시적으로 작동하는 프레임워크가 좋음
- JWT 인증, Blueprint 라우팅을 직접 구현하면서 HTTP 흐름을 이해하기 적합
- Django는 ORM/Admin/Form 등 부가 기능이 많아 gRPC 학습에 집중하기 어려움

**대안**: Django REST Framework — 프로덕션 수준 기능이 많지만 학습 목적에는 과함

---

## [2026-06-16] FastAPI (예매 서비스)

**결정**: FastAPI 선택

**이유**
- Pydantic으로 요청/응답 타입 검증을 선언적으로 할 수 있음
- `/docs` 자동 생성 → 수동 테스트 편리
- async 지원 → gRPC 클라이언트 호출 패턴 학습에 좋음
- Flask와 다른 프레임워크를 같이 써보며 차이점 이해

---

## [2026-06-16] gRPC 통신 방향 (단방향)

**결정**: booking-service(클라이언트) → auth-service(서버)

**이유**
- 예매 요청 시 토큰 검증이 필요하므로 booking이 auth를 호출하는 방향이 자연스러움
- auth-service는 Flask HTTP 서버 + gRPC 서버를 별도 스레드로 함께 실행
- 단방향 단순 패턴으로 시작해 gRPC 기본을 익힌 뒤 streaming 등 확장 가능

---

## [2026-06-18] ORM 전략 변경: Code-first + Alembic 마이그레이션

**결정**: SQLAlchemy ORM 모델을 코드로 정의하고, Alembic(Flask-Migrate)으로 스키마 변경을 관리

**이유**
- Alembic이 Python 마이크로서비스 생태계에서 가장 널리 쓰이는 마이그레이션 도구
- 스키마 변경 이력이 마이그레이션 파일로 남아 추적 가능
- DB를 날리지 않고 `flask db upgrade`만으로 스키마 변경 적용 가능
- 이전에 경험한 적 있어 러닝 커브 낮음

**구현 방식**
- `app/models.py` — SQLAlchemy ORM 모델로 테이블 구조 정의 (소스 오브 트루스)
- `Flask-Migrate` — Alembic 래퍼, `flask db init/migrate/upgrade` 명령 제공
- Docker 컨테이너 시작 시 `flask db upgrade` 실행으로 마이그레이션 자동 적용
- `postgres/auth-init/01_create_users.sql` — 참고용으로 보존, 실제 사용 안 함

**대안**: DB-first + SQLAlchemy Reflection — DB 스키마가 소스 오브 트루스이나, Flask 앱 컨텍스트와의 연동이 복잡하고 이 프로젝트 규모에서 오버스펙

---

## [2026-06-16] DB: PostgreSQL (서비스별 독립 DB)

**결정**: 서비스마다 별도 PostgreSQL 인스턴스 사용

**이유**
- 마이크로서비스의 핵심 원칙인 "Database per Service" 패턴 적용
- auth-service와 booking-service가 서로의 DB에 직접 접근하지 않음 → 서비스 간 결합도 낮춤
- 나중에 서비스별로 다른 DB 종류로 교체하거나 독립 스케일링이 가능한 구조
- Docker로 실행하므로 PostgreSQL 컨테이너 띄우는 비용이 낮음

**구성**
- `auth-db`: auth-service 전용 PostgreSQL
- `booking-db`: booking-service 전용 PostgreSQL

**대안**: 단일 공유 DB — 설정이 단순하지만 마이크로서비스 취지에 맞지 않음

---

## [2026-06-16] 실행 환경: Docker Compose

**결정**: Docker Compose로 전체 서비스 묶어서 실행

**이유**
- 로컬 환경에 Python, PostgreSQL 등을 직접 설치하지 않아도 됨
- `docker compose up` 한 번으로 전체 스택(auth, booking, 두 DB) 실행 가능
- 서비스 간 네트워크(gRPC 포함)를 docker network로 격리해서 실제 마이크로서비스 환경과 유사하게 구성

**구성 서비스**
```
docker-compose.yml
  ├── auth-service   (Flask + gRPC 서버)
  ├── auth-db        (PostgreSQL)
  ├── booking-service (FastAPI + gRPC 클라이언트)
  └── booking-db     (PostgreSQL)
```
