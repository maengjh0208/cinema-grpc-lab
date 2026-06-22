import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ['BOOKING_DB_USER']}:{os.environ['BOOKING_DB_PASSWORD']}"
    f"@{os.environ['BOOKING_DB_HOST']}:{os.environ['BOOKING_DB_PORT']}/{os.environ['BOOKING_DB_NAME']}"
)


engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    # autocommit 은 이제 default False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # context manager 가 자동으로 db.close() 해줌
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:  # # except: 만 하면 프로그램 종료 신호(KeyboardInterrupt, SystemExit 등)까지 가로챔.
            await db.rollback()
