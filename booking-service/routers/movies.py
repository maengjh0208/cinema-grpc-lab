from typing import Annotated

from core.database import get_db
from fastapi import APIRouter, Depends
from schemas import MovieResponse, ScreeningResponse
from services import movie_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# GET /movies - 전체 영화 조회
@router.get("/movies", response_model=list[MovieResponse])
async def get_movies(session: Annotated[AsyncSession, Depends(get_db)]):
    movies = await movie_service.get_movies(session)

    return [
        MovieResponse(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            runtime_minutes=movie.runtime_minutes,
        )
        for movie in movies
    ]


# GET /movies/{movie_id}/screenings - movie_id 영화의 상영 목록 조회
@router.get("/movies/{movie_id}/screenings", response_model=list[ScreeningResponse])
async def get_screenings(movie_id: int, session: Annotated[AsyncSession, Depends(get_db)]):
    screenings = await movie_service.get_screenings(session, movie_id)

    return [
        ScreeningResponse(
            id=screening.id,
            movie_id=screening.movie_id,
            hall_id=screening.hall_id,
            start_time=screening.start_time,
        )
        for screening in screenings
    ]
