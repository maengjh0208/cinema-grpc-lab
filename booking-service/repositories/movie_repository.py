from domain import MovieDomain, ScreeningDomain
from models import Movie, Screening
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_movie(session: AsyncSession, movie_id: int) -> MovieDomain | None:
    result = await session.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none()

    # 이런식으로 pydantic 모델 인스턴스를 만들수도 있고
    # return MovieDomain.model_validate(movie, from_attributes=True) if movie else None

    # 혹은 좀 더 명시적으로 하고 싶으면 이렇게 하면 됨
    # 필드가 많아지면 번거롭지만, 매핑이 명확하게 보여서 좋음
    return (
        MovieDomain(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            runtime_minutes=movie.runtime_minutes,
        )
        if movie
        else None
    )


async def get_all_movies(session: AsyncSession) -> list[MovieDomain]:
    result = await session.execute(select(Movie))
    movies = result.scalars().all()

    return [
        MovieDomain(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            runtime_minutes=movie.runtime_minutes,
        )
        for movie in movies
    ]


async def get_screenings_by_movie(session: AsyncSession, movie_id: int) -> list[ScreeningDomain]:
    result = await session.execute(select(Screening).where(Screening.movie_id == movie_id))
    screenings = result.scalars().all()

    return [
        ScreeningDomain(
            id=screening.id,
            movie_id=screening.movie_id,
            hall_id=screening.hall_id,
            start_time=screening.start_time,
        )
        for screening in screenings
    ]
