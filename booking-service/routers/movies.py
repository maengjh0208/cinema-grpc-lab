from database import get_db
from fastapi import APIRouter, Depends
from models import Movie
from schemas import MovieResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# GET /movies
@router.get("/movies", response_model=list[MovieResponse])
async def get_movies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Movie))
    movies = result.scalars().all()
    return movies
