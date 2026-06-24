from domain import BookingDomain, ScreeningDomain, SeatDomain
from exceptions import BadRequestError, ErrorCode
from models import Booking, Screening, Seat
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_screening(session: AsyncSession, screening_id: int) -> ScreeningDomain | None:
    result = await session.execute(select(Screening).where(Screening.id == screening_id))
    screening = result.scalar_one_or_none()

    return (
        ScreeningDomain(
            id=screening.id,
            movie_id=screening.movie_id,
            hall_id=screening.hall_id,
            start_time=screening.start_time,
        )
        if screening
        else None
    )


async def get_seat(session: AsyncSession, seat_id: int) -> SeatDomain | None:
    result = await session.execute(select(Seat).where(Seat.id == seat_id))
    seat = result.scalar_one_or_none()

    return (
        SeatDomain(
            id=seat.id,
            hall_id=seat.hall_id,
            seat_name=seat.seat_name,
        )
        if seat
        else None
    )


async def create_booking(session: AsyncSession, screening_id: int, seat_id: int, user_id: int) -> BookingDomain:
    booking = Booking(
        screening_id=screening_id,
        seat_id=seat_id,
        user_id=user_id,
    )

    session.add(booking)

    try:
        # DB에 실제로 INSERT를 날리되, 아직 커밋은 안함
        await session.flush()
    # UniqueConstraint 위반 시 SQLAlchemyr가 발생시키는 예외
    except IntegrityError:
        raise BadRequestError(error_code=ErrorCode.DUPLICATE_BOOKING)

    return BookingDomain(
        id=booking.id,
        screening_id=booking.screening_id,
        seat_id=booking.seat_id,
        user_id=booking.user_id,
        created_at=booking.created_at,
    )
