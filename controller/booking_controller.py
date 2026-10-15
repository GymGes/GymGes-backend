from datetime import timedelta
from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.booking_model import Booking
from models.weekly_class_model import WeeklyClass
from models.member_model import Member
from schema.booking_schema import BookingCreate, BookingUpdate


def _get_class_interval(weekly_class: WeeklyClass) -> Tuple[datetime, datetime]:
    start = weekly_class.activity_date
    duration = weekly_class.activity_type.duration if weekly_class.activity_type else 0
    return start, start + timedelta(minutes=duration)


def _ensure_member_exists(db: Session, member_code: str) -> None:
    if not db.query(Member).filter(Member.code == member_code).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with code {member_code} not found"
        )


def _ensure_class_exists(db: Session, class_id: int) -> WeeklyClass:
    weekly_class = db.query(WeeklyClass).filter(WeeklyClass.id == class_id).first()
    if not weekly_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly class with id {class_id} not found"
        )
    # Asegurar que la relación activity_type está cargada para calcular el fin
    if weekly_class.activity_type is None:
        # Recarga por si la sesión expiró la relación
        db.refresh(weekly_class, attribute_names=["activity_type"])
    return weekly_class


def _check_member_schedule_conflict(
    db: Session,
    member_code: str,
    new_class: WeeklyClass,
    exclude_booking_id: Optional[int] = None,
) -> None:
    """
    Lanza 409 si el socio ya tiene otra reserva cuyo intervalo
    [activity_date, activity_date + duration) solapa con new_class.
    Las clases adyacentes (fin == inicio) SÍ están permitidas.
    """
    new_start, new_end = _get_class_interval(new_class)

    query = db.query(Booking).filter(Booking.member_code == member_code)
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    for existing_booking in query.all():
        # Misma clase -> se gestiona como duplicada en otro chequeo, aquí se ignora
        # para dar un mensaje más claro de "reserva duplicada".
        if existing_booking.class_id == new_class.id:
            continue
        existing_class = db.query(WeeklyClass).filter(
            WeeklyClass.id == existing_booking.class_id
        ).first()
        if not existing_class:
            continue
        existing_start, existing_end = _get_class_interval(existing_class)
        if new_start < existing_end and existing_start < new_end:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Revisa tu horario: tienes una clase reservada a esa hora"                   
                )
            )


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
    _check_member_schedule_conflict(db, booking_data.member_code, new_class)
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
        new_member_code = booking_data.member_code if booking_data.member_code is not None else booking.member_code
        new_class_id = booking_data.class_id if booking_data.class_id is not None else booking.class_id

        if (new_member_code != booking.member_code) or (new_class_id != booking.class_id):
            _ensure_member_exists(db, new_member_code)
            new_class = _ensure_class_exists(db, new_class_id)

            duplicate = db.query(Booking).filter(
                Booking.member_code == new_member_code,
                Booking.class_id == new_class_id,
                Booking.id != booking_id
            ).first()
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Member {new_member_code} already booked class {new_class_id}"
                )

            _check_member_schedule_conflict(
                db, new_member_code, new_class, exclude_booking_id=booking_id
            )

            booking.member_code = new_member_code
            booking.class_id = new_class_id
        db.commit()
        db.refresh(booking)
        return booking
    except HTTPException:
        raise
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

    