from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str | None
    runtime_minutes: int

    # SQLAlchemy ORM 객체를 Pydnatic 모델로 변환
    model_config = {"from_attributes": True}
