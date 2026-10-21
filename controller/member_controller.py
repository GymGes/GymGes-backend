from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.member_model import Member
from models.plan_model import Plan
from schema.member_schema import MemberCreate, MemberUpdate

def get_all_members(db: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    try:
        return db.query(Member).order_by(Member.code).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al obtener los socios: {str(error)}"
        )


def get_member_by_id(db: Session, code: str) -> Member:
    try:
        member = db.query(Member).filter(Member.code == code).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se ha encontrado el socio con código {code}"
            )
        return member
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al obtener el socio: {str(error)}"
        )


def create_member(db: Session, member_data: MemberCreate) -> Member:
    plan = db.query(Plan).filter(Plan.id == member_data.plan_id).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha encontrado el plan"
        )
    new_member = Member(
        code=member_data.code,
        first_name=member_data.first_name,
        last_name=member_data.last_name,
        age=member_data.age,
        city=member_data.city,
        address=member_data.address,
        plan_id=member_data.plan_id,
        remaining_credits=plan.credits
    )

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        return new_member

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al crear el socio: {str(error)}"
        )


def update_member(
    db: Session,
    code: str,
    member_data: MemberUpdate
) -> Member:
    member = get_member_by_id(db, code)

    try:
        member.first_name = member_data.first_name
        member.last_name = member_data.last_name
        member.age = member_data.age
        member.city = member_data.city
        member.address = member_data.address
        member.plan_id = member_data.plan_id

        db.commit()
        db.refresh(member)
        return member

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al actualizar el socio: {str(error)}"
        )


def delete_member(db: Session, code: str) -> None:
    member = get_member_by_id(db, code)

    try:
        db.delete(member)
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos al eliminar el socio: {str(error)}"
        )