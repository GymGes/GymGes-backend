from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.booking_model import Booking
from models.weekly_class_model import WeeklyClass
from models.member_model import Member
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
    classvar= db.query(WeeklyClass).filter(WeeklyClass.id == booking_data.class_id).first()
    member = db.query(Member).filter(Member.code == booking_data.member_code).first()

    if classvar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="class not found"
        ) 
    
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="class not found"
        ) 
    if member.remaining_credits<=0:
        raise HTTPException(
            status_code= status.HTTP_406_NOT_ACCEPTABLE,
            detail="the member don't have enough credits" 
        )
    new_booking = Booking(
        member_code=booking_data.member_code,
        class_id=booking_data.class_id,
    )
    member.remaining_credits-=1
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
            member= db.query(Member).filter(Member.code == booking_data.class_id).first()
            if member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="member not found"
                ) 
            booking.member_code = booking_data.member_code
        if booking_data.class_id is not None:
            classvar= db.query(WeeklyClass).filter(WeeklyClass.id == booking_data.class_id).first()
            if classvar is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="class not found"
                ) 
            booking.class_id = booking_data.class_id
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
    member= db.query(Member).filter(Member.code == booking.member_code).first()
    if member is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="member not found"
        )
    member.remaining_credits+=1
        
    try:
        db.delete(booking)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting booking {str(error)}"
        )

    