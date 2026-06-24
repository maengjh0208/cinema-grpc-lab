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

## [2026-06-22] booking-service DB 드라이버: 비동기 스택 선택

**결정**: `psycopg2-binary` 대신 `asyncpg` + SQLAlchemy 비동기 스택 사용

**이유**
- FastAPI는 비동기 프레임워크이므로 동기 드라이버를 쓰면 `async def` 라우터 안에서 이벤트 루프를 blocking
- `asyncpg` + `AsyncSession`을 쓰면 I/O 대기 중 다른 요청을 처리할 수 있어 FastAPI 본래 성능을 활용 가능
- 비동기 DB 연동 패턴을 직접 경험하는 것 자체가 학습 목표 중 하나

**변경 범위**
- `requirements.txt`: `psycopg2-binary` → `asyncpg`
- `database.py`: `create_engine` → `create_async_engine`, `sessionmaker` → `async_sessionmaker`, `Session` → `AsyncSession`
- `get_db()`: `async def` + `async with`로 변경
- 라우터 핸들러: `def` → `async def`, 쿼리에 `await` 추가

**주의사항**
- DB URL 스킴 변경 필요: `postgresql://` → `postgresql+asyncpg://`
- `await db.execute(...)`, `await db.commit()` 등 모든 DB 호출에 `await` 필요

**대안**: `def` + `psycopg2-binary` — FastAPI가 스레드풀에서 실행해 이벤트 루프는 막지 않으나, 비동기 패턴을 배우는 기회를 놓침

---

## [2026-06-22] booking-service 좌석 모델 설계: Seat 테이블 별도 분리

**결정**: `Seat` 테이블을 별도로 두고 예매 시 특정 좌석을 점유하는 방식

**이유**
- gRPC 학습이 주 목표이지만, 좌석 예매 시스템을 설계하면서 생기는 고민도 충분히 경험하고자 함
- `available_seats` 카운트만 줄이는 방식은 현실과 거리가 있고, 중복 예매 방지 등 실질적인 문제를 다루지 못함

**테이블 구조**
```
Movie (1) ──< Screening (1) ──< Seat (0..1) ──< Booking
```
- `Screening` 생성 시 `Seat`도 함께 생성 (총 좌석 수만큼)
- 예매 시 특정 `Seat`를 점유 (`is_booked = True`)
- `Booking`은 `Seat`를 FK로 참조

**이 설계에서 생기는 고민들**
- 상영 생성 시 좌석을 어떻게 자동 생성할 것인가 (DB 트리거 vs 애플리케이션 로직)
- 동시에 같은 좌석을 예매하려는 요청이 들어올 때 race condition 처리
- 좌석 번호 체계 (A1, B3 vs 단순 정수)

**대안**
- A: `available_seats` 카운트만 감소 — 단순하지만 좌석 식별 불가
- B: `Booking.seat_number` 추가 — 중간 수준이나 좌석 목록의 소스가 불명확

---

## [2026-06-24] gRPC 서버 실행 방식: 스레드 → 별도 컨테이너 전환 예정

**현재 결정**: auth-service 컨테이너 안에서 Flask HTTP + gRPC 서버를 스레드로 함께 실행

**이유**
- 학습 초기에는 구조를 단순하게 유지해 gRPC 흐름 자체에 집중
- 스레드 방식이 동작 원리를 이해하기에 더 직관적

**다음 단계 (이해 후 리팩토링 예정)**
같은 이미지를 두 컨테이너로 나눠 실행하는 방식으로 전환:
```yaml
auth-service:
  command: flask run ...          # HTTP만 담당

auth-grpc-service:
  build: ./auth-service           # 같은 이미지 재사용
  command: python grpc_server.py  # gRPC만 담당
```

**이렇게 분리하는 이유**
- HTTP와 gRPC를 독립적으로 스케일링 가능 (gRPC 트래픽이 많으면 gRPC 컨테이너만 늘림)
- 한 쪽 장애가 다른 쪽에 영향 없음
- Flask reloader와 gRPC 스레드 간 프로세스 충돌 문제 원천 제거

---

## [2026-06-22] gRPC 핸들러에서 Flask app context 명시 필요

**결정**: gRPC 서버 핸들러에서 `verify_token` 등 Flask context가 필요한 함수를 호출할 때 `app.app_context()`를 명시적으로 감싸야 함

**이유**
- gRPC 서버는 Flask HTTP 서버와 **별도 스레드**로 실행됨
- Flask의 `current_app`, `g` 등은 요청 컨텍스트(request context) 또는 앱 컨텍스트(app context) 안에서만 동작함
- 별도 스레드에는 Flask가 자동으로 context를 주입하지 않으므로 직접 열어줘야 함

**구현 방식**
```python
# gRPC 핸들러 안에서
with app.app_context():
    payload = verify_token(token)
```
또는 gRPC 서버 시작 시 `app` 인스턴스를 핸들러 클래스에 주입해서 사용

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
