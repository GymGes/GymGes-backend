from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.booking_schema import BookingCreate, BookingResponse, BookingUpdate
import controller.booking_controller as controller

router = APIRouter(
    prefix="/booking",
    tags=["Booking"]
)


@router.get(
    "/",
    response_model=List[BookingResponse],
    summary="Read all bookings",
    description="Return all bookings"
)
def read_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_all_bookings(db=db, skip=skip, limit=limit)


@router.get(
    "/member/{member_code}",
    response_model=List[BookingResponse],
    summary="Get bookings by member",
    description="Return all bookings for a specific member"
)
def read_bookings_by_member(
    member_code: str,
    db: Session = Depends(get_db)
):
    return controller.get_bookings_by_member(
        db=db,
        member_code=member_code
    )


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description="Add a new booking"
)
def create_new_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    return controller.create_booking(db=db, booking_data=booking_data)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get a booking by ID",
    description="Return a single booking"
)
def read_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_booking_by_id(db=db, booking_id=booking_id)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a booking",
    description="Delete an existing booking"
)
def delete_existing_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_booking(db=db, booking_id=booking_id)
    return None