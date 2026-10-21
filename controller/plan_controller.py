
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.plan_model import Plan
from schema.plan_schema import PlanCreate, PlanUpdate


def create_plan(db: Session, plan_data: PlanCreate):
    if (
        plan_data.name is None or not str(plan_data.name).strip()
        or plan_data.credits is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    db_plan = Plan(
        name=plan_data.name,
        credits=plan_data.credits
    )

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    return db_plan


def get_plans(db: Session):
    return db.query(Plan).all()


def get_plan(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha encontrado el plan"
        )

    return plan


def update_plan(db: Session, plan_id: int, plan_data: PlanUpdate):
    plan = get_plan(db, plan_id)

    update_data = plan_data.model_dump(exclude_unset=True)

    if "name" in update_data and (
        update_data["name"] is None or not str(update_data["name"]).strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    if "credits" in update_data and update_data["credits"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datos incompletos"
        )

    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)

    return plan

def delete_plan(db: Session, plan_id: int):
    plan = get_plan(db, plan_id)

    db.delete(plan)
    db.commit()

    return {
        "message": "Plan deleted successfully",
        "plan_id": plan_id
    }