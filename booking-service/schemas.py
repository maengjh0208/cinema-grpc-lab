from datetime import datetime

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str | None
    runtime_minutes: int

    # SQLAlchemy ORM 객체를 Pydnatic 모델로 변환
    model_config = {"from_attributes": True}


class ScreeningResponse(BaseModel):
    id: int
    movie_id: int
    hall_id: int
    start_time: datetime

    model_config = {"from_attributes": True}


class BookingRequest(BaseModel):
    screening_id: int
    seat_id: int


class BookingResponse(BaseModel):
    id: int
    screening_id: int
    seat_id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
