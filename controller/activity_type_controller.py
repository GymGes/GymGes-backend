from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.activity_type_model import ActivityType
from schema.activity_type_schema import ActivityTypeCreate, ActivityTypeUpdate


def get_all_activity_types(db: Session, skip: int = 0, limit: int = 100) -> List[ActivityType]:
    try:
        return db.query(ActivityType).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error while retrieving activity types: {str(error)}")


def get_activity_type_by_id(db: Session, activity_type_id: int) -> Optional[ActivityType]:
    try:
        return db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error while retrieving activity type {activity_type_id}: {str(error)}")


def create_activity_type(db: Session, data: ActivityTypeCreate) -> ActivityType:
    new_activity_type = ActivityType(
        name=data.name,
        duration=data.duration,
        max_students=data.max_students,
        description=data.description
    )
    try:
        db.add(new_activity_type)
        db.commit()
        db.refresh(new_activity_type)
        return new_activity_type
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error while creating activity type: {str(error)}")


def update_activity_type(db: Session, activity_type_id: int, data: ActivityTypeUpdate) -> Optional[ActivityType]:
    existing = get_activity_type_by_id(db, activity_type_id)
    if not existing:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    try:
        db.commit()
        db.refresh(existing)
        return existing
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error while updating activity type {activity_type_id}: {str(error)}")


def delete_activity_type(db: Session, activity_type_id: int) -> bool:
    existing = get_activity_type_by_id(db, activity_type_id)
    if not existing:
        return False
    try:
        db.delete(existing)
        db.commit()
        return True
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error while deleting activity type {activity_type_id}: {str(error)}")