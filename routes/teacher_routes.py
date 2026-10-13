
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.teacher_model import Teacher
from schema.teacher_schema import TeacherCreate, TeacherUpdate


def get_all_teachers(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Teacher]:
    try:
        return db.query(Teacher).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while retrieving teachers: {str(error)}"
        )


def get_teacher_by_id(
    db: Session,
    teacher_id: int
) -> Optional[Teacher]:
    try:
        return db.query(Teacher).filter(Teacher.id == teacher_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while retrieving teacher {teacher_id}: {str(error)}"
        )


def create_teacher(
    db: Session,
    data: TeacherCreate
) -> Teacher:
    new_teacher = Teacher(
        name=data.name
    )

    try:
        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        return new_teacher
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating teacher: {str(error)}"
        )


def update_teacher(
    db: Session,
    teacher_id: int,
    data: TeacherUpdate
) -> Optional[Teacher]:
    existing = get_teacher_by_id(db, teacher_id)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating teacher {teacher_id}: {str(error)}"
        )


def delete_teacher(
    db: Session,
    teacher_id: int
) -> bool:
    existing = get_teacher_by_id(db, teacher_id)

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
            detail=f"Database error while deleting teacher {teacher_id}: {str(error)}"
        )
