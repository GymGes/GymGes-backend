from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.booking_model import Booking
from schema.booking_schema import BookingCreate, BookingUpdate


def get_all_bookings(db: Session, skip: int = 0, limit: int = 100) -> List[Booking]:
    try:
        return db.query(Booking).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching bookings {str(error)}"
        )


def get_booking_by_id(db: Session, booking_id: int) -> Booking:
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id {booking_id} not found"
            )
        return booking
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching booking {str(error)}"
        )


def create_booking(db: Session, booking_data: BookingCreate) -> Booking:
    new_booking = Booking(
        member_code=booking_data.member_code,
        class_id=booking_data.class_id,
        booking_date=booking_data.booking_date
    )
    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in creating booking {str(error)}"
        )


def update_booking(db: Session, booking_id: int, booking_data: BookingUpdate) -> Booking:
    booking = get_booking_by_id(db, booking_id)
    try:
        if booking_data.member_code is not None:
            booking.member_code = booking_data.member_code
        if booking_data.class_id is not None:
            booking.class_id = booking_data.class_id
        if booking_data.booking_date is not None:
            booking.booking_date = booking_data.booking_date
        db.commit()
        db.refresh(booking)
        return booking
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in updating booking {str(error)}"
        )


def delete_booking(db: Session, booking_id: int) -> None:
    booking = get_booking_by_id(db, booking_id)
    try:
        db.delete(booking)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting booking {str(error)}"
        )

    