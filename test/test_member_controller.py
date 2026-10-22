import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from controller.member_controller import (
    create_member,
    delete_member,
    get_all_members,
    get_member_by_id,
    update_member,
)
from models.member_model import Member
from models.plan_model import Plan
from schema.member_schema import MemberCreate, MemberUpdate


MEMBER_CODE = "12345678A"


def build_member_data() -> MemberCreate:
    return MemberCreate(
        code=MEMBER_CODE,
        first_name="Lucia",
        last_name="Garcia",
        age=25,
        city="Madrid",
        address="Calle Mayor 10",
        plan_id=1,
    )


def build_member_update_data() -> MemberUpdate:
    return MemberUpdate(
        first_name="Lucia",
        last_name="Garcia",
        age=26,
        city="Toledo",
        address="Calle Nueva 5",
        plan_id=2,
    )


def test_get_all_members_success():
    """Arrange"""
    db_mock = MagicMock()
    members = [MagicMock(spec=Member), MagicMock(spec=Member)]
    db_mock.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = members

    """Act"""
    result = get_all_members(db=db_mock, skip=0, limit=100)

    """Assert"""
    assert result == members
    db_mock.query.assert_called_once_with(Member)
    db_mock.query.return_value.order_by.assert_called_once_with(Member.code)


def test_get_all_members_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_all_members(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener los socios" in exc_info.value.detail


def test_get_member_by_id_success():
    """Arrange"""
    db_mock = MagicMock()
    member = MagicMock(spec=Member)
    member.code = MEMBER_CODE
    db_mock.query.return_value.filter.return_value.first.return_value = member

    """Act"""
    result = get_member_by_id(db=db_mock, code=MEMBER_CODE)

    """Assert"""
    assert result is member
    db_mock.query.assert_called_once_with(Member)


def test_get_member_by_id_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_member_by_id(db=db_mock, code=MEMBER_CODE)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert MEMBER_CODE in exc_info.value.detail


def test_get_member_by_id_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_member_by_id(db=db_mock, code=MEMBER_CODE)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener el socio" in exc_info.value.detail


def test_create_member_success():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    plan.credits = 10
    db_mock.query.return_value.filter.return_value.first.return_value = plan
    member_data = build_member_data()

    """Act"""
    result = create_member(db=db_mock, member_data=member_data)

    """Assert"""
    assert isinstance(result, Member)
    assert result.code == MEMBER_CODE
    assert result.first_name == "Lucia"
    assert result.last_name == "Garcia"
    assert result.plan_id == 1
    assert result.remaining_credits == 10
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_member_plan_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        create_member(db=db_mock, member_data=build_member_data())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No se ha encontrado el plan"
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_member_database_error():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    plan.credits = 10
    db_mock.query.return_value.filter.return_value.first.return_value = plan
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        create_member(db=db_mock, member_data=build_member_data())

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al crear el socio" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_update_member_success():
    """Arrange"""
    db_mock = MagicMock()
    member = MagicMock(spec=Member)
    db_mock.query.return_value.filter.return_value.first.return_value = member
    member_data = build_member_update_data()

    """Act"""
    result = update_member(db=db_mock, code=MEMBER_CODE, member_data=member_data)

    """Assert"""
    assert result is member
    assert member.first_name == "Lucia"
    assert member.last_name == "Garcia"
    assert member.age == 26
    assert member.city == "Toledo"
    assert member.address == "Calle Nueva 5"
    assert member.plan_id == 2
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(member)


def test_update_member_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_member(
            db=db_mock,
            code=MEMBER_CODE,
            member_data=build_member_update_data(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    db_mock.commit.assert_not_called()


def test_update_member_database_error():
    """Arrange"""
    db_mock = MagicMock()
    member = MagicMock(spec=Member)
    db_mock.query.return_value.filter.return_value.first.return_value = member
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_member(
            db=db_mock,
            code=MEMBER_CODE,
            member_data=build_member_update_data(),
        )

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al actualizar el socio" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_delete_member_success():
    """Arrange"""
    db_mock = MagicMock()
    member = MagicMock(spec=Member)
    db_mock.query.return_value.filter.return_value.first.return_value = member

    """Act"""
    result = delete_member(db=db_mock, code=MEMBER_CODE)

    """Assert"""
    assert result is None
    db_mock.delete.assert_called_once_with(member)
    db_mock.commit.assert_called_once()


def test_delete_member_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        delete_member(db=db_mock, code=MEMBER_CODE)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_member_database_error():
    """Arrange"""
    db_mock = MagicMock()
    member = MagicMock(spec=Member)
    db_mock.query.return_value.filter.return_value.first.return_value = member
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        delete_member(db=db_mock, code=MEMBER_CODE)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al eliminar el socio" in exc_info.value.detail
    db_mock.rollback.assert_called_once()
