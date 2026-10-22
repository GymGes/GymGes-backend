from datetime import timedelta
from typing import List, Optional
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.config import now_local
from models.activity_type_model import ActivityType
from models.weekly_class_model import WeeklyClass
from schema.activity_type_schema import ActivityTypeCreate, ActivityTypeUpdate
from service import cloudinary_service


def get_all_activity_types(db: Session, skip: int = 0, limit: int = 100) -> List[ActivityType]:
    try:
        return db.query(ActivityType).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error de base de datos al obtener los tipos de actividad: {str(error)}")


def get_activity_type_by_id(db: Session, activity_type_id: int) -> Optional[ActivityType]:
    try:
        return db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error de base de datos al obtener el tipo de actividad {activity_type_id}: {str(error)}")


def create_activity_type(db: Session, data: ActivityTypeCreate, image: UploadFile | None = None) -> ActivityType:
    if (
        data.name is None or not str(data.name).strip()
        or data.duration is None
        or data.max_students is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    image_url = None
    image_public_id = None

    if image is not None:
        result = cloudinary_service.upload_image(
            image.file,
            folder="gymges/activities"
        )
        image_url = result["secure_url"]
        image_public_id = result["public_id"]

    new_activity_type = ActivityType(
        name=data.name,
        duration=data.duration,
        max_students=data.max_students,
        description=data.description,
        image_url=image_url,
        image_public_id=image_public_id
    )

    try:
        db.add(new_activity_type)
        db.commit()
        db.refresh(new_activity_type)
        return new_activity_type
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al crear el tipo de actividad: {str(error)}"
        )


def update_activity_type(db: Session, activity_type_id: int, data: ActivityTypeUpdate,
                        image: UploadFile | None = None) -> Optional[ActivityType]:
    existing = get_activity_type_by_id(db, activity_type_id)

    if not existing:
        return None

    raw_update_data = data.model_dump(exclude_unset=True)

    if "name" in raw_update_data and (
        raw_update_data["name"] is None
        or not str(raw_update_data["name"]).strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    if "duration" in raw_update_data and raw_update_data["duration"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    if "max_students" in raw_update_data and raw_update_data["max_students"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    update_data = {
        field: value
        for field, value in raw_update_data.items()
        if value is not None
    }

    for field, value in update_data.items():
        setattr(existing, field, value)

    if image is not None:
        if existing.image_public_id:
            cloudinary_service.delete_image(existing.image_public_id)

        result = cloudinary_service.upload_image(
            image.file,
            folder="gymges/activities"
        )

        existing.image_url = result["secure_url"]
        existing.image_public_id = result["public_id"]

    try:
        db.commit()
        db.refresh(existing)
        return existing
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al actualizar el tipo de actividad {activity_type_id}: {str(error)}"
        )

def delete_activity_type(db: Session, activity_type_id: int) -> bool:
    existing = get_activity_type_by_id(db, activity_type_id)
    if not existing:
        return False

    now = now_local()

    blocking_class = (
        db.query(WeeklyClass)
        .filter(
            WeeklyClass.activity_type_id == activity_type_id,
            WeeklyClass.activity_date >= now,
            WeeklyClass.activity_date < now + timedelta(hours=2),
        )
        .order_by(WeeklyClass.activity_date)
        .first()
    )

    if blocking_class:
        classDate = blocking_class.activity_date.strftime("%d/%m/%Y")
        classTime = blocking_class.activity_date.strftime("%H:%M")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar el tipo de actividad: hay una clase "
                f"programada para el {classDate} a las {classTime}, dentro "
                f"de las próximas dos horas."
            ),
        )

    try:
        if existing.image_public_id:
            cloudinary_service.delete_image(existing.image_public_id)
        db.delete(existing)
        db.commit()
        return True
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error de base de datos al eliminar el tipo de actividad {activity_type_id}: {str(error)}")