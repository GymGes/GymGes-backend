from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

import controller.activity_type_controller as controller
from models.activity_type_model import ActivityType
from models.weekly_class_model import WeeklyClass
from schema.activity_type_schema import ActivityTypeCreate, ActivityTypeUpdate


ACTIVITY_TYPE_ID = 1
NOW = datetime(2030, 1, 1, 8, 0, 0)


def build_activity_type_data() -> ActivityTypeCreate:
    return ActivityTypeCreate(
        name="Yoga",
        duration=60,
        max_students=20,
        description="Yoga session",
    )


def test_get_all_activity_types_success():
    """Arrange"""
    db_mock = MagicMock()
    activity_types = [MagicMock(spec=ActivityType), MagicMock(spec=ActivityType)]
    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = activity_types

    """Act"""
    result = controller.get_all_activity_types(db=db_mock, skip=0, limit=100)

    """Assert"""
    assert result == activity_types
    db_mock.query.assert_called_once_with(ActivityType)


def test_get_all_activity_types_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.offset.return_value.limit.return_value.all.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_all_activity_types(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener los tipos de actividad" in exc_info.value.detail


def test_get_activity_type_by_id_success():
    """Arrange"""
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    db_mock.query.return_value.filter.return_value.first.return_value = activity_type

    """Act"""
    result = controller.get_activity_type_by_id(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    """Assert"""
    assert result is activity_type
    db_mock.query.assert_called_once_with(ActivityType)


def test_get_activity_type_by_id_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_activity_type_by_id(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al obtener el tipo de actividad {ACTIVITY_TYPE_ID}" in exc_info.value.detail


def test_create_activity_type_success():
    """Arrange"""
    db_mock = MagicMock()
    data = build_activity_type_data()

    """Act"""
    result = controller.create_activity_type(db=db_mock, data=data)

    """Assert"""
    assert isinstance(result, ActivityType)
    assert result.name == "Yoga"
    assert result.duration == 60
    assert result.max_students == 20
    assert result.description == "Yoga session"
    assert result.image_url is None
    assert result.image_public_id is None
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_activity_type_incomplete_data():
    """Arrange"""
    db_mock = MagicMock()
    data = ActivityTypeCreate.model_construct(
        name=" ", duration=60, max_students=20, description=None
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_activity_type(db=db_mock, data=data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_activity_type_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_activity_type(db=db_mock, data=build_activity_type_data())

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al crear el tipo de actividad" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_update_activity_type_success():
    """Arrange"""
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    activity_type.name = "Yoga"
    activity_type.duration = 60
    activity_type.max_students = 20
    activity_type.description = None
    activity_type.image_public_id = None
    db_mock.query.return_value.filter.return_value.first.return_value = activity_type
    data = ActivityTypeUpdate(name="Pilates")

    """Act"""
    result = controller.update_activity_type(
        db=db_mock, activity_type_id=ACTIVITY_TYPE_ID, data=data
    )

    """Assert"""
    assert result is activity_type
    assert activity_type.name == "Pilates"
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(activity_type)


def test_update_activity_type_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = controller.update_activity_type(
        db=db_mock,
        activity_type_id=ACTIVITY_TYPE_ID,
        data=ActivityTypeUpdate(name="Pilates"),
    )

    """Assert"""
    assert result is None
    db_mock.commit.assert_not_called()


def test_update_activity_type_invalid_name():
    """Arrange"""
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    db_mock.query.return_value.filter.return_value.first.return_value = activity_type

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.update_activity_type(
            db=db_mock,
            activity_type_id=ACTIVITY_TYPE_ID,
            data=ActivityTypeUpdate(name=" "),
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.commit.assert_not_called()


def test_update_activity_type_database_error():
    """Arrange"""
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    activity_type.image_public_id = None
    db_mock.query.return_value.filter.return_value.first.return_value = activity_type
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.update_activity_type(
            db=db_mock,
            activity_type_id=ACTIVITY_TYPE_ID,
            data=ActivityTypeUpdate(name="Pilates"),
        )

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al actualizar el tipo de actividad {ACTIVITY_TYPE_ID}" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_delete_activity_type_success(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    activity_type.image_public_id = None

    activity_query = MagicMock()
    activity_query.filter.return_value.first.return_value = activity_type
    weekly_class_query = MagicMock()
    weekly_class_query.filter.return_value.order_by.return_value.first.return_value = None
    db_mock.query.side_effect = [activity_query, weekly_class_query]

    """Act"""
    result = controller.delete_activity_type(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    """Assert"""
    assert result is True
    db_mock.delete.assert_called_once_with(activity_type)
    db_mock.commit.assert_called_once()


def test_delete_activity_type_blocked_within_two_hours(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    activity_type.image_public_id = None

    blocking_class = MagicMock(spec=WeeklyClass)
    blocking_class.activity_date = NOW + timedelta(hours=1)

    activity_query = MagicMock()
    activity_query.filter.return_value.first.return_value = activity_type
    weekly_class_query = MagicMock()
    weekly_class_query.filter.return_value.order_by.return_value.first.return_value = blocking_class
    db_mock.query.side_effect = [activity_query, weekly_class_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_activity_type(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "dentro de las próximas dos horas" in exc_info.value.detail
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_activity_type_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = controller.delete_activity_type(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    """Assert"""
    assert result is False
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_activity_type_database_error(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    activity_type = MagicMock(spec=ActivityType)
    activity_type.image_public_id = None
    activity_query = MagicMock()
    activity_query.filter.return_value.first.return_value = activity_type
    weekly_class_query = MagicMock()
    weekly_class_query.filter.return_value.order_by.return_value.first.return_value = None
    db_mock.query.side_effect = [activity_query, weekly_class_query]
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_activity_type(db=db_mock, activity_type_id=ACTIVITY_TYPE_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al eliminar el tipo de actividad {ACTIVITY_TYPE_ID}" in exc_info.value.detail
    db_mock.rollback.assert_called_once()
