
from datetime import timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.weekly_class_model import WeeklyClass
from models.teacher_model import Teacher
from models.activity_type_model import ActivityType
from schema.weekly_class_schema import WeeklyClassCreate, WeeklyClassUpdate


def get_all_weekly_classes(db: Session, skip: int = 0, limit: int = 100) -> List[WeeklyClass]:
    try:
        return db.query(WeeklyClass).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while retrieving weekly classes: {str(error)}"
        )


def get_weekly_class_by_id(db: Session, weekly_class_id: int) -> Optional[WeeklyClass]:
    try:
        return db.query(WeeklyClass).filter(WeeklyClass.id == weekly_class_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while retrieving weekly class {weekly_class_id}: {str(error)}"
        )


def _ensure_teacher_exists(db: Session, teacher_id: int) -> None:
    if not db.query(Teacher).filter(Teacher.id == teacher_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )


def _ensure_activity_type_exists(db: Session, activity_type_id: int) -> ActivityType:
    activity_type = db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    if not activity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity type with id {activity_type_id} not found"
        )
    return activity_type


def _check_teacher_schedule_conflict(
    db: Session,
    teacher_id: int,
    activity_date,
    duration: int,
    exclude_id: Optional[int] = None
) -> None:
    new_start = activity_date
    new_end = new_start + timedelta(minutes=duration)

    query = db.query(WeeklyClass).filter(WeeklyClass.teacher_id == teacher_id)
    if exclude_id is not None:
        query = query.filter(WeeklyClass.id != exclude_id)

    for existing in query.all():
        existing_start = existing.activity_date
        existing_end = existing_start + timedelta(minutes=existing.activity_type.duration)
        if new_start < existing_end and existing_start < new_end:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"El profesor ya tiene una clase el "
                    f"{existing_start.strftime('%d/%m/%Y')}, "
                    f"de {existing_start.strftime('%H:%M')} "
                    f"a {existing_end.strftime('%H:%M')}. "
                    "El horario solicitado se solapa con esa clase."
                )
            )


def create_weekly_class(db: Session, data: WeeklyClassCreate) -> WeeklyClass:
    _ensure_teacher_exists(db, data.teacher_id)
    activity_type = _ensure_activity_type_exists(db, data.activity_type_id)
    _check_teacher_schedule_conflict(db, data.teacher_id, data.activity_date, activity_type.duration)

    new_weekly_class = WeeklyClass(
        teacher_id=data.teacher_id,
        activity_type_id=data.activity_type_id,
        activity_date=data.activity_date,
        available_spots=activity_type.max_students
    )
    try:
        db.add(new_weekly_class)
        db.commit()
        db.refresh(new_weekly_class)
        return new_weekly_class
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating weekly class: {str(error)}"
        )


# def update_weekly_class(db: Session, weekly_class_id: int, data: WeeklyClassUpdate) -> Optional[WeeklyClass]:
#     existing = get_weekly_class_by_id(db, weekly_class_id)
#     if not existing:
#         return None

#     update_fields = data.model_dump(exclude_unset=True)

#     new_teacher_id = update_fields.get("teacher_id", existing.teacher_id)
#     new_activity_date = update_fields.get("activity_date", existing.activity_date)

#     if "teacher_id" in update_fields:
#         _ensure_teacher_exists(db, new_teacher_id)

#     if update_fields:
#         _check_teacher_schedule_conflict(
#             db, new_teacher_id, new_activity_date,
#             existing.activity_type.duration, exclude_id=weekly_class_id
#         )

#     for field, value in update_fields.items():
#         setattr(existing, field, value)

#     try:
#         db.commit()
#         db.refresh(existing)
#         return existing
#     except SQLAlchemyError as error:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database error while updating weekly class {weekly_class_id}: {str(error)}"
#         )


def delete_weekly_class(db: Session, weekly_class_id: int) -> bool:
    existing = get_weekly_class_by_id(db, weekly_class_id)
    if not existing:
        return False
    try:
        db.delete(existing)
        db.commit()
        return True
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while deleting weekly class {weekly_class_id}: {str(error)}"
        )