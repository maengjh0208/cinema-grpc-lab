# 전체 구현 계획

## 학습 목표
1. Flask로 REST API + JWT 인증 구현
2. FastAPI로 REST API 구현 (Pydantic, 의존성 주입)
3. protobuf `.proto` 파일 작성 및 Python 코드 생성
4. gRPC 서버(Flask 쪽)와 클라이언트(FastAPI 쪽) 구현
5. 두 서비스가 실제로 통신하는 흐름 이해

---

## Phase 1: 기반 구조 세팅
- [ ] 디렉토리 구조 생성 (`auth-service/`, `booking-service/`, `proto/`)
- [ ] 각 서비스 `requirements.txt` 작성
- [ ] 각 서비스 `Dockerfile` 작성
- [ ] `docker-compose.yml` 작성 (auth-service, booking-service, auth-db, booking-db)
- [ ] `.gitignore` 확인 (`*_pb2.py`, `.env` 등)
- [ ] `.env.example` 작성 (DB 접속 정보 등)

## Phase 2: auth-service (Flask)
- [ ] Flask 앱 기본 구조 (`app.py`, `blueprints/`)
- [ ] 사용자 모델 (SQLite or 인메모리)
- [ ] 회원가입 API `POST /register`
- [ ] 로그인 API `POST /login` → JWT 발급
- [ ] JWT 검증 유틸 함수

## Phase 3: booking-service (FastAPI)
- [ ] FastAPI 앱 기본 구조 (`main.py`, `routers/`)
- [ ] 영화 목록 조회 `GET /movies`
- [ ] 상영 일정 조회 `GET /movies/{id}/screenings`
- [ ] 좌석 예매 `POST /bookings` (인증 필요)
- [ ] JWT Bearer 토큰 의존성 주입

## Phase 4: gRPC 연동
- [ ] `proto/auth.proto` 작성 — `ValidateToken` RPC 정의
- [ ] protoc로 Python 코드 생성 (`auth_pb2.py`, `auth_pb2_grpc.py`)
- [ ] auth-service에 gRPC 서버 추가 (Flask HTTP과 별도 스레드)
- [ ] booking-service에 gRPC 클라이언트 추가
- [ ] 예매 요청 시 gRPC로 토큰 검증하는 흐름 완성

## Phase 5: 통합 테스트
- [ ] 전체 흐름 수동 테스트 (회원가입 → 로그인 → 토큰 받기 → 예매)
- [ ] `curl` 또는 `httpx`로 E2E 시나리오 작성
- [ ] gRPC 통신 로그 확인

## Phase 6: 마무리
- [ ] 환경 변수 정리 (`.env` 파일로 DB URL, JWT_SECRET 등 관리)
- [ ] 간단한 에러 핸들링 정리
- [ ] `docker compose up` 한 번으로 전체 흐름 동작 확인

---

## 현재 단계
**Phase 1 진행 중**
