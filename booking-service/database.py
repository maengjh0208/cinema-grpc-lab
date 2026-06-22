import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = (
    f"postgresql://{os.environ['BOOKING_DB_USER']}:{os.environ['BOOKING_DB_PASSWORD']}"
    f"@{os.environ['BOOKING_DB_HOST']}:{os.environ['BOOKING_DB_PORT']}/{os.environ['BOOKING_DB_NAME']}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        # except: 만 하면 프로그램 종료 신호(KeyboardInterrupt, SystemExit 등)까지 가로챔.
        db.rollback()
    finally:
        db.close()
