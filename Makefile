# migrations/versions/ 에 있는 마이그레이션 파일들 중 아직 적용 안 된 것들을 DB에 순서대로 적용한다.
# Alembic 이 내부적으로 alembic_version 테이블을 관리해서 어디까지 적용했는지 추적한다.
auth-migrate:
	docker compose run --rm auth-service flask db upgrade

# 현재 models.py를 읽고 DB 현재 상태와 비교해서 차이점을 마이그레이션 파일로 자동 생성한다.
# migrations/versions/ 안에 xxxx_설명.py 파일이 만들어지며, 아직 DB에 적용된 상태는 아니다.
auth-migrate-create:
	docker compose run --rm auth-service flask db migrate -m "${message}"

# Alembic 을 처음 세팅할 때 딱 한 번 실행함.
# migrations/ 폴더와 alembic.ini, env.py 등 Alembic 설정 파일들을 생성한다. 이미 migrations/ 가 있으면 다시 실행할 필요 없다.
auth-migrate-init:
	docker compose run --rm auth-service flask db init