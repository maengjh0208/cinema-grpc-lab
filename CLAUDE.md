# Cinema gRPC Lab — Claude Code Context

## 프로젝트 목적
Flask(회원 서비스) + FastAPI(영화 예매 서비스) + gRPC 연동을 학습하는 실습 프로젝트.
코드만 짜는 게 아니라 **왜 이렇게 설계하는지** 이해하는 게 목표.

## 작업 전 필수 확인
- `docs/plan.md` — 전체 구현 계획 및 현재 TODO
- `docs/progress.md` — 날짜별 진행 기록
- `docs/architecture.md` — 시스템 구조 설계

## 서비스 구성
| 서비스 | 프레임워크 | 역할 | 포트 |
|--------|-----------|------|------|
| auth-service | Flask | 회원가입/로그인/JWT 발급, gRPC 토큰 검증 서버 | HTTP:5000, gRPC:50051 |
| auth-db | PostgreSQL | auth-service 전용 DB | 5432 |
| booking-service | FastAPI | 영화/상영 조회, 좌석 예매, gRPC 클라이언트 | HTTP:8000 |
| booking-db | PostgreSQL | booking-service 전용 DB | 5433 |
| proto/ | — | 공통 .proto 파일 | — |

## 실행 방법
```bash
docker compose up --build
```
전체 스택(서비스 2개 + DB 2개)이 한 번에 실행됨.

## 핵심 학습 흐름
```
Client → booking-service(FastAPI) → gRPC → auth-service(Flask)
                                             └─ JWT 검증 후 사용자 정보 반환
```

## 코드 작성 규칙
- Python 3.12, 타입 힌트 적극 사용
- 각 서비스는 독립 venv (서비스별 requirements.txt)
- proto 파일에서 생성된 코드는 `*_pb2.py`, `*_pb2_grpc.py` — 직접 수정 금지
- 새 기능 추가 전에 반드시 `docs/plan.md`의 TODO를 확인
- SQLAlchemy는 **v2 스타일만 사용** — `User.query.filter_by()` 같은 v1 스타일(deprecated) 금지
  ```python
  # 올바른 예시
  from sqlalchemy import select
  stmt = select(User).where(User.email == email)
  user = db.session.execute(stmt).scalar_one_or_none()
  ```

## 진행 상황 업데이트 규칙
작업 완료 시 `docs/progress.md`에 날짜와 함께 기록 추가.
의사결정이 생기면 `docs/decisions.md`에 이유와 함께 기록.

## 협업 방식
- **직접 코딩 실습**: 사용자가 직접 코드를 작성하며 학습. Claude는 코드를 대신 짜주는 게 아니라 가이드 역할.
- **설명 중심**: 무엇을 만들어야 하는지, 왜 이렇게 설계하는지, 각 개념이 무엇인지 설명하며 진행.
- **단계별 진행**: 한 번에 한 파일/기능씩 안내. 사용자가 직접 구현한 후 다음 단계로.
- **질문 환영**: 막히거나 이해 안 되는 부분은 언제든 질문하면 상세 설명 제공.
