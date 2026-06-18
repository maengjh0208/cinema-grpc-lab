import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# 앱과 분리해서 선언하고 init_app(app) 으로 나중에 연결
db = SQLAlchemy()
migrate = Migrate()

# Application Factory 패턴 - 목적: 앱을 함수 호출 시점에 구성하는 것
def create_app() -> Flask:
    AUTH_DB_NAME = os.environ.get("AUTH_DB_NAME")
    AUTH_DB_USER = os.environ.get("AUTH_DB_USER")
    AUTH_DB_PASSWORD = os.environ.get("AUTH_DB_PASSWORD")
    AUTH_DB_HOST = os.environ.get("AUTH_DB_HOST")
    AUTH_DB_PORT = os.environ.get("AUTH_DB_PORT")

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{AUTH_DB_USER}:{AUTH_DB_PASSWORD}@{AUTH_DB_HOST}:{AUTH_DB_PORT}/{AUTH_DB_NAME}"
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    db.init_app(app)
    # Migrate는 db와 app을 둘 다 알아야 함. 어떤 DB 연결인지, 어떤 앱인지 파악해서 flask db 명령을 실행할때 씀.
    migrate.init_app(app, db)

    # Alembic 마이그레이션을 위해서 import
    from app import models

    # blueprint import 는 함수 안에서 - circular import 방지
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/")

    return app
