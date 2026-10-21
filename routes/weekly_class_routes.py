from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.weekly_class_schema import (
    WeeklyClassCreate,
    WeeklyClassUpdate,
    WeeklyClassResponse
)
import controller.weekly_class_controller as weekly_class_controller


router = APIRouter(
    prefix="/weekly-classes",
    tags=["Weekly Classes"]
)


@router.get(
    "/",
    response_model=List[WeeklyClassResponse],
    summary="Get all weekly classes",
    description="Retrieve a list of weekly classes with optional pagination."
)
def read_weekly_classes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    return weekly_class_controller.get_all_weekly_classes(db=db, skip=skip, limit=limit)


@router.get(
    "/{weekly_class_id}",
    response_model=WeeklyClassResponse,
    summary="Get a weekly class by ID",
    description="Retrieve specific details of a single weekly class by its ID."
)
def read_weekly_class(
    weekly_class_id: int,
    db: Session = Depends(get_db)
):
    weekly_class = weekly_class_controller.get_weekly_class_by_id(db=db, weekly_class_id=weekly_class_id)
    if not weekly_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado la clase con id {weekly_class_id}"
        )
    return weekly_class


@router.post(
    "/",
    response_model=WeeklyClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new weekly class",
    description="Add a new weekly class and validate the teacher's schedule availability."
)
def create_new_weekly_class(
    weekly_class_data: WeeklyClassCreate,
    db: Session = Depends(get_db)
):
    return weekly_class_controller.create_weekly_class(db=db, data=weekly_class_data)


# @router.put(
#     "/{weekly_class_id}",
#     response_model=WeeklyClassResponse,
#     summary="Update an existing weekly class",
#     description="Update teacher, start time or duration (activity type cannot be changed)."
# )
# def update_existing_weekly_class(
#     weekly_class_id: int,
#     weekly_class_data: WeeklyClassUpdate,
#     db: Session = Depends(get_db)
# ):
#     updated = weekly_class_controller.update_weekly_class(
#         db=db, weekly_class_id=weekly_class_id, data=weekly_class_data
#     )
#     if not updated:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No se ha encontrado la clase con id {weekly_class_id}"
#         )
#     return updated


@router.delete(
    "/{weekly_class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a weekly class",
    description="Permanently remove a weekly class by ID."
)
def remove_weekly_class(
    weekly_class_id: int,
    db: Session = Depends(get_db)
):
    deleted = weekly_class_controller.delete_weekly_class(db=db, weekly_class_id=weekly_class_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado la clase con id {weekly_class_id}"
        )
    return None
