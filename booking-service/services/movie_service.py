from domain import MovieDomain, ScreeningDomain
from exceptions import ErrorCode, NotFoundError
from repositories import movie_repository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_movies(session: AsyncSession) -> list[MovieDomain]:
    return await movie_repository.get_all_movies(session)


async def get_screenings(session: AsyncSession, movie_id: int) -> list[ScreeningDomain]:
    movie = await movie_repository.get_movie(session, movie_id)
    if not movie:
        raise NotFoundError(ErrorCode.MOVIE_NOT_FOUND)

    return await movie_repository.get_screenings_by_movie(session, movie_id)
