from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.teacher_model import Teacher
from schema.teacher_schema import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse
)
from controller.teacher_controller import (
    get_all_teachers,
    get_teacher_by_id,
    create_teacher,
    update_teacher,
    delete_teacher
)

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


@router.get("/", response_model=List[TeacherResponse])
def read_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_all_teachers(db, skip, limit)


@router.get("/{teacher_id}", response_model=TeacherResponse)
def read_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    teacher = get_teacher_by_id(db, teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.post(
    "/",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_teacher(
    data: TeacherCreate,
    db: Session = Depends(get_db)
):
    return create_teacher(db, data)


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_existing_teacher(
    teacher_id: int,
    data: TeacherUpdate,
    db: Session = Depends(get_db)
):
    teacher = update_teacher(db, teacher_id, data)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_teacher(db, teacher_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return None
