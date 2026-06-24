from domain import BookingDomain
from exceptions import ErrorCode, NotFoundError
from repositories import booking_repository
from sqlalchemy.ext.asyncio import AsyncSession


async def create_booking(session: AsyncSession, screening_id: int, seat_id: int, user_id: int) -> BookingDomain:
    screening = await booking_repository.get_screening(session, screening_id)
    if not screening:
        raise NotFoundError(ErrorCode.SCREENING_NOT_FOUND)

    seat = await booking_repository.get_seat(session, seat_id)
    if not seat:
        raise NotFoundError(ErrorCode.SEAT_NOT_FOUND)

    if seat.hall_id != screening.hall_id:
        raise NotFoundError(
            error_code=ErrorCode.SEAT_NOT_FOUND,
            detail=(
                f"해당 상영관의 좌석이 아님 | "
                f"seat_id:{seat_id} && seat's hall_id:{seat.hall_id} && screening's hall_id:{screening.hall_id}"
            ),
        )

    return await booking_repository.create_booking(
        session=session,
        screening_id=screening_id,
        seat_id=seat_id,
        user_id=user_id,
    )
