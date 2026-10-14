
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schema.plan_schema import PlanCreate, PlanUpdate, PlanResponse
from controller.plan_controller import (
    create_plan,
    get_plans,
    get_plan,
    update_plan,
    delete_plan
)

router = APIRouter(
    prefix="/plans",
    tags=["Plans"]
)


@router.post(
    "/",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_plan_route(
    plan_data: PlanCreate,
    db: Session = Depends(get_db)
):
    return create_plan(db, plan_data)


@router.get(
    "/",
    response_model=List[PlanResponse]
)
def get_plans_route(
    db: Session = Depends(get_db)
):
    return get_plans(db)


@router.get(
    "/{plan_id}",
    response_model=PlanResponse
)
def get_plan_route(
    plan_id: int,
    db: Session = Depends(get_db)
):
    return get_plan(db, plan_id)


@router.put(
    "/{plan_id}",
    response_model=PlanResponse
)
def update_plan_route(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db)
):
    return update_plan(db, plan_id, plan_data)


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_200_OK
)
def delete_plan_route(
    plan_id: int,
    db: Session = Depends(get_db)
):
    return delete_plan(db, plan_id)
