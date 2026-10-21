from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from schema.activity_type_schema import ActivityTypeCreate, ActivityTypeUpdate, ActivityTypeResponse
import controller.activity_type_controller as activity_type_controller

router = APIRouter(prefix="/activity-types", tags=["Activity Types"])


@router.get("/", response_model=List[ActivityTypeResponse],
            summary="Get all activity types",
            description="Retrieve a list of activity types with optional pagination.")
def read_activity_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    return activity_type_controller.get_all_activity_types(db=db, skip=skip, limit=limit)


@router.get("/{activity_type_id}", response_model=ActivityTypeResponse,
            summary="Get an activity type by ID",
            description="Retrieve specific details of a single activity type by its ID.")
def read_activity_type(activity_type_id: int, db: Session = Depends(get_db)):
    activity_type = activity_type_controller.get_activity_type_by_id(db=db, activity_type_id=activity_type_id)
    if not activity_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No se ha encontrado el tipo de actividad con id {activity_type_id}")
    return activity_type


@router.post("/", response_model=ActivityTypeResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new activity type",
             description="Add a new activity type entry to the database.")
def create_new_activity_type(
    name: str = Form(...),
    duration: int = Form(...),
    max_students: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    activity_type_data = ActivityTypeCreate(
        name=name,
        duration=duration,
        max_students=max_students,
        description=description
    )
    return activity_type_controller.create_activity_type(db=db, data=activity_type_data, image=image)


@router.put("/{activity_type_id}", response_model=ActivityTypeResponse,
            summary="Update an existing activity type",
            description="Update one or more attributes of an existing activity type.")
def update_existing_activity_type(
    activity_type_id: int,
    name: str | None = Form(None),
    duration: int | None = Form(None),
    max_students: int | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    activity_type_data = ActivityTypeUpdate(
        name=name,
        duration=duration,
        max_students=max_students,
        description=description
    )
    updated = activity_type_controller.update_activity_type(
        db=db, activity_type_id=activity_type_id, data=activity_type_data, image=image)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No se ha encontrado el tipo de actividad con id {activity_type_id}")
    return updated


@router.delete("/{activity_type_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete an activity type",
               description="Permanently remove an activity type by ID.")
def remove_activity_type(activity_type_id: int, db: Session = Depends(get_db)):
    deleted = activity_type_controller.delete_activity_type(db=db, activity_type_id=activity_type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No se ha encontrado el tipo de actividad con id {activity_type_id}")
    return None