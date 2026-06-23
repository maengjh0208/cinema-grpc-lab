from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Movie, Screening
from schemas import MovieResponse, ScreeningResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# GET /movies - 전체 영화 조회
@router.get("/movies", response_model=list[MovieResponse])
async def get_movies(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Movie))
    movies = result.scalars().all()
    return movies


# GET /movies/{movie_id}/screenings - movie_id 영화의 상영 목록 조회
@router.get("/movies/{movie_id}/screenings", response_model=list[ScreeningResponse])
async def get_screenings(movie_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    movie = await db.execute(select(Movie).where(Movie.id == movie_id))
    if not movie.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"영화를 찾을 수 없음 | movie_id:{movie_id}")

    screenings = await db.execute(select(Screening).where(Screening.movie_id == movie_id))
    return screenings.scalars().all()
