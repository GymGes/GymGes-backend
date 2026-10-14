from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.member_model import Member
from models.plan_model import Plan
from schema.member_schema import MemberCreate, MemberUpdate

def get_all_members(db: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    try:
        return db.query(Member).offset(skip).limit(limit).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching members {str(error)}"
        )


def get_member_by_id(db: Session, member_id: int) -> Member:
    try:
        member = db.query(Member).filter(member.id == member_id).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"member with id {member_id} not found"
            )
        return member
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in fetching member {str(error)}"
        )


def create_member(db: Session, member_data: MemberCreate) -> Member:
    plan = db.query(Plan).filter(Plan.id == member_data.plan_id).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    new_member = Member(
        member_code=member_data.member_code,
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
            detail=f"Database error in creating member: {str(error)}"
        )


def update_member(
    db: Session,
    member_id: str,
    member_data: MemberUpdate
) -> Member:
    member = get_member_by_id(db, member_id)

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
            detail=f"Database error in updating member: {str(error)}"
        )


def delete_member(db: Session, member_id: str) -> None:
    member = get_member_by_id(db, member_id)

    try:
        db.delete(member)
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error in deleting member: {str(error)}"
        )