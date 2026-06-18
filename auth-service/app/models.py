from datetime import datetime

from app import db

class User(db.Model):
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(256), nullable=False)
    created_at: datetime = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())  # timezone=True -> TIMESTAMPTZ
    updated_at: datetime = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now(), onupdate=db.func.now())  # onupdate는 python(SQLAlchemy) 레벨에서만 동작한다. 즉, SQLAlchemy 를 통한 UPDATE 에만 적용되고, DB에서 직접 SQL을 날리면 적용 안된다.

    def __repr__(self) -> str:
        return f"<User {self.email}>"