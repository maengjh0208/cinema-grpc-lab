from typing import Annotated

from database import get_db
from dependencies import get_current_user_id
from fastapi import APIRouter, Depends
from schemas import BookingRequest, BookingResponse
from services import booking_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    body: BookingRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    book = await booking_service.create_booking(
        session=session,
        screening_id=body.screening_id,
        seat_id=body.seat_id,
        user_id=user_id,
    )

    return BookingResponse(
        id=book.id,
        screening_id=book.screening_id,
        seat_id=book.seat_id,
        user_id=book.user_id,
        created_at=book.created_at,
    )
