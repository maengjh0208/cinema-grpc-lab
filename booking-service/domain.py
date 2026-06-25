# =============================
# 순수 Pydantic 도메인 객체 (비즈니스 레이어)
# =============================

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MovieDomain:
    id: int
    title: str
    description: str | None
    runtime_minutes: int


@dataclass
class ScreeningDomain:
    id: int
    movie_id: int
    hall_id: int
    start_time: datetime


@dataclass
class BookingDomain:
    id: int
    screening_id: int
    seat_id: int
    user_id: int
    created_at: datetime


@dataclass
class SeatDomain:
    id: int
    hall_id: int
    seat_name: str
