from typing import List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.member_schema import (
    MemberCreate,
    MemberResponse,
    MemberUpdate
)
import controller.member_controller as controller


router = APIRouter(
    prefix="/members",
    tags=["Members"]
)


@router.get(
    "/",
    response_model=List[MemberResponse],
    summary="Get all members"
)
def get_all_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return controller.get_all_members(
        db=db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{code}",
    response_model=MemberResponse,
    summary="Get a member by ID"
)
def get_member_by_id(
    code: str = Path(..., min_length=9, max_length=9),
    db: Session = Depends(get_db)
):
    return controller.get_member_by_id(
        db=db,
        code=code
    )


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member"
)
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db)
):
    return controller.create_member(
        db=db,
        member_data=member_data
    )


@router.put(
    "/{code}",
    response_model=MemberResponse,
    summary="Update a member"
)
def update_member(
    code: str = Path(..., min_length=9, max_length=9),
    member_data: MemberUpdate = ...,
    db: Session = Depends(get_db)
):
    return controller.update_member(
        db=db,
        code=code,
        member_data=member_data
    )


@router.delete(
    "/{code}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a member"
)
def delete_member(
    code: str = Path(..., min_length=9, max_length=9),
    db: Session = Depends(get_db)
):
    controller.delete_member(
        db=db,
        code=code
    )
    return None
