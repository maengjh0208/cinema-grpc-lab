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
