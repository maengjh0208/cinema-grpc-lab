# =============================
# 순수 Pydantic 도메인 객체 (비즈니스 레이어)
# =============================

from datetime import datetime

from pydantic import BaseModel


class MovieDomain(BaseModel):
    id: int
    title: str
    description: str | None
    runtime_minutes: int


class ScreeningDomain(BaseModel):
    id: int
    movie_id: int
    hall_id: int
    start_time: datetime


class BookingDomain(BaseModel):
    id: int
    screening_id: int
    seat_id: int
    user_id: int
    created_at: datetime


class SeatDomain(BaseModel):
    id: int
    hall_id: int
    seat_name: str
