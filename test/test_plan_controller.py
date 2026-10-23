import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException, status

from controller.plan_controller import (
    create_plan,
    delete_plan,
    get_plan,
    get_plans,
    update_plan,
)
from models.plan_model import Plan
from schema.plan_schema import PlanCreate, PlanUpdate


PLAN_ID = 1


def build_plan_data() -> PlanCreate:
    return PlanCreate(name="Basic", credits=10)


def test_create_plan_success():
    """Arrange"""
    db_mock = MagicMock()
    plan_data = build_plan_data()

    """Act"""
    result = create_plan(db=db_mock, plan_data=plan_data)

    """Assert"""
    assert isinstance(result, Plan)
    assert result.name == "Basic"
    assert result.credits == 10
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_plan_incomplete_data():
    """Arrange"""
    db_mock = MagicMock()
    plan_data = PlanCreate.model_construct(name=" ", credits=10)

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        create_plan(db=db_mock, plan_data=plan_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_get_plans_success():
    """Arrange"""
    db_mock = MagicMock()
    plans = [MagicMock(spec=Plan), MagicMock(spec=Plan)]
    db_mock.query.return_value.all.return_value = plans

    """Act"""
    result = get_plans(db=db_mock)

    """Assert"""
    assert result == plans
    db_mock.query.assert_called_once_with(Plan)


def test_get_plan_success():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    plan.id = PLAN_ID
    db_mock.query.return_value.filter.return_value.first.return_value = plan

    """Act"""
    result = get_plan(db=db_mock, plan_id=PLAN_ID)

    """Assert"""
    assert result is plan
    db_mock.query.assert_called_once_with(Plan)


def test_get_plan_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_plan(db=db_mock, plan_id=PLAN_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No se ha encontrado el plan"


def test_update_plan_success():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    plan.name = "Basic"
    plan.credits = 10
    db_mock.query.return_value.filter.return_value.first.return_value = plan
    plan_data = PlanUpdate(name="Premium", credits=20)

    """Act"""
    result = update_plan(db=db_mock, plan_id=PLAN_ID, plan_data=plan_data)

    """Assert"""
    assert result is plan
    assert plan.name == "Premium"
    assert plan.credits == 20
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(plan)


def test_update_plan_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_plan(db=db_mock, plan_id=PLAN_ID, plan_data=PlanUpdate(name="Premium"))

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    db_mock.commit.assert_not_called()


def test_update_plan_invalid_name():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    db_mock.query.return_value.filter.return_value.first.return_value = plan

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_plan(db=db_mock, plan_id=PLAN_ID, plan_data=PlanUpdate(name=None))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.commit.assert_not_called()


def test_update_plan_invalid_credits():
    """Arrange"""
    db_mock = MagicMock()
    plan = MagicMock(spec=Plan)
    db_mock.query.return_value.filter.return_value.first.return_value = plan

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_plan(db=db_mock, plan_id=PLAN_ID, plan_data=PlanUpdate(credits=None))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.commit.assert_not_called()


def test_delete_plan_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        delete_plan(db=db_mock, plan_id=PLAN_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()
