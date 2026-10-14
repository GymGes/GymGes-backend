
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from controller.weekly_class_controller import (
    get_all_weekly_classes,
    get_weekly_class_by_id,
    create_weekly_class,
    update_weekly_class,
    delete_weekly_class
)
from schema.weekly_class_schema import WeeklyClassBase


router = APIRouter(
    prefix="/weekly-classes",
    tags=["Weekly Classes"]
)


@router.get("/")
def read_weekly_classes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_all_weekly_classes(db, skip=skip, limit=limit)


@router.get("/{teacher_id}/{activity_type_id}")
def read_weekly_class(
    teacher_id: int,
    activity_type_id: int,
    db: Session = Depends(get_db)
):
    weekly_class = get_weekly_class_by_id(
        db,
        teacher_id,
        activity_type_id
    )

    if weekly_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly class not found"
        )

    return weekly_class


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_weekly_class(
    data: WeeklyClassBase,
    db: Session = Depends(get_db)
):
    return create_weekly_class(db, data)


@router.put("/{teacher_id}/{activity_type_id}")
def update_existing_weekly_class(
    teacher_id: int,
    activity_type_id: int,
    data: WeeklyClassBase,
    db: Session = Depends(get_db)
):
    weekly_class = update_weekly_class(
        db,
        teacher_id,
        activity_type_id,
        data
    )

    if weekly_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly class not found"
        )

    return weekly_class


@router.delete(
    "/{teacher_id}/{activity_type_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_existing_weekly_class(
    teacher_id: int,
    activity_type_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_weekly_class(
        db,
        teacher_id,
        activity_type_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly class not found"
        )

    return None
