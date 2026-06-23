from typing import Annotated

from database import get_db
from dependencies import get_current_user_id
from fastapi import APIRouter, Depends, HTTPException
from models import Booking, Screening, Seat
from schemas import BookingRequest, BookingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    body: BookingRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    screening = (await db.execute(select(Screening).where(Screening.id == body.screening_id))).scalar_one_or_none()
    if not screening:
        raise HTTPException(status_code=404, detail=f"상영을 찾을 수 없음 | screening_id:{body.screening_id}")

    seat = (
        await db.execute(select(Seat).where(Seat.id == body.seat_id, Seat.hall_id == screening.hall_id))
    ).scalar_one_or_none()
    if not seat:
        raise HTTPException(status_code=404, detail=f"좌석을 찾을 수 없음 | seat_id:{body.seat_id}")

    booking = Booking(
        screening_id=body.screening_id,
        seat_id=body.seat_id,
        user_id=user_id,
    )
    db.add(booking)

    try:
        # DB에 실제로 INSERT를 날리되, 아직 커밋은 안함
        await db.flush()
    # UniqueConstraint 위반 시 SQLAlchemyr가 발생시키는 예외
    except IntegrityError:
        raise HTTPException(status_code=409, detail="이미 예약된 좌석")

    return booking
