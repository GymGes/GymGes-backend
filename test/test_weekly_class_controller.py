from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

import controller.weekly_class_controller as controller
from models.activity_type_model import ActivityType
from models.teacher_model import Teacher
from models.weekly_class_model import WeeklyClass
from schema.weekly_class_schema import WeeklyClassCreate


WEEKLY_CLASS_ID = 1
NOW = datetime(2030, 1, 1, 8, 0, 0)


def build_weekly_class_data(activity_date=None) -> WeeklyClassCreate:
    return WeeklyClassCreate(
        activity_type_id=1,
        teacher_id=2,
        activity_date=activity_date or NOW + timedelta(hours=4),
    )


def build_create_queries(db_mock, teacher=None, activity_type=None, existing_classes=None):
    teacher_query = MagicMock()
    teacher_query.filter.return_value.first.return_value = teacher
    activity_query = MagicMock()
    activity_query.filter.return_value.first.return_value = activity_type
    schedule_query = MagicMock()
    schedule_query.filter.return_value.all.return_value = existing_classes or []
    db_mock.query.side_effect = [teacher_query, activity_query, schedule_query]


def test_get_all_weekly_classes_success():
    """Arrange"""
    db_mock = MagicMock()
    weekly_classes = [MagicMock(spec=WeeklyClass), MagicMock(spec=WeeklyClass)]
    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = weekly_classes

    """Act"""
    result = controller.get_all_weekly_classes(db=db_mock, skip=0, limit=100)

    """Assert"""
    assert result == weekly_classes
    db_mock.query.assert_called_once_with(WeeklyClass)


def test_get_all_weekly_classes_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.offset.return_value.limit.return_value.all.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_all_weekly_classes(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener las clases" in exc_info.value.detail


def test_get_weekly_class_by_id_success():
    """Arrange"""
    db_mock = MagicMock()
    weekly_class = MagicMock(spec=WeeklyClass)
    db_mock.query.return_value.filter.return_value.first.return_value = weekly_class

    """Act"""
    result = controller.get_weekly_class_by_id(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    """Assert"""
    assert result is weekly_class
    db_mock.query.assert_called_once_with(WeeklyClass)


def test_get_weekly_class_by_id_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = controller.get_weekly_class_by_id(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    """Assert"""
    assert result is None


def test_get_weekly_class_by_id_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_weekly_class_by_id(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al obtener la clase {WEEKLY_CLASS_ID}" in exc_info.value.detail


def test_create_weekly_class_success(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    activity_type = MagicMock(spec=ActivityType)
    activity_type.duration = 60
    activity_type.max_students = 20
    build_create_queries(db_mock, teacher, activity_type)
    data = build_weekly_class_data()

    """Act"""
    result = controller.create_weekly_class(db=db_mock, data=data)

    """Assert"""
    assert isinstance(result, WeeklyClass)
    assert result.teacher_id == 2
    assert result.activity_type_id == 1
    assert result.activity_date == data.activity_date
    assert result.available_spots == 20
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_weekly_class_past_date(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    data = build_weekly_class_data(NOW - timedelta(minutes=1))

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_weekly_class(db=db_mock, data=data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "fecha anterior a la actual" in exc_info.value.detail
    db_mock.query.assert_not_called()
    db_mock.add.assert_not_called()


def test_create_weekly_class_teacher_not_found(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    teacher_query = MagicMock()
    teacher_query.filter.return_value.first.return_value = None
    db_mock.query.side_effect = [teacher_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_weekly_class(db=db_mock, data=build_weekly_class_data())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "No se ha encontrado el profesor" in exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_weekly_class_activity_type_not_found(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    teacher_query = MagicMock()
    teacher_query.filter.return_value.first.return_value = MagicMock(spec=Teacher)
    activity_query = MagicMock()
    activity_query.filter.return_value.first.return_value = None
    db_mock.query.side_effect = [teacher_query, activity_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_weekly_class(db=db_mock, data=build_weekly_class_data())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "No se ha encontrado el tipo de actividad" in exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_weekly_class_teacher_schedule_conflict(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    activity_type = MagicMock(spec=ActivityType)
    activity_type.duration = 60
    activity_type.max_students = 20
    existing_class = MagicMock(spec=WeeklyClass)
    existing_class.activity_date = NOW + timedelta(hours=4, minutes=15)
    existing_class.activity_type = MagicMock()
    existing_class.activity_type.duration = 60
    build_create_queries(db_mock, teacher, activity_type, [existing_class])

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_weekly_class(db=db_mock, data=build_weekly_class_data())

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "El horario solicitado se solapa" in exc_info.value.detail
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_weekly_class_database_error(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    activity_type = MagicMock(spec=ActivityType)
    activity_type.duration = 60
    activity_type.max_students = 20
    build_create_queries(db_mock, teacher, activity_type)
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_weekly_class(db=db_mock, data=build_weekly_class_data())

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al crear la clase" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_delete_weekly_class_success(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    weekly_class = MagicMock(spec=WeeklyClass)
    weekly_class.activity_date = NOW - timedelta(days=1)
    db_mock.query.return_value.filter.return_value.first.return_value = weekly_class

    """Act"""
    result = controller.delete_weekly_class(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    """Assert"""
    assert result is True
    db_mock.delete.assert_called_once_with(weekly_class)
    db_mock.commit.assert_called_once()


def test_delete_weekly_class_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = controller.delete_weekly_class(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    """Assert"""
    assert result is False
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_weekly_class_blocked_within_two_hours(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    weekly_class = MagicMock(spec=WeeklyClass)
    weekly_class.activity_date = NOW + timedelta(hours=1)
    db_mock.query.return_value.filter.return_value.first.return_value = weekly_class

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_weekly_class(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "faltan menos de dos horas" in exc_info.value.detail
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_weekly_class_database_error(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    weekly_class = MagicMock(spec=WeeklyClass)
    weekly_class.activity_date = NOW - timedelta(days=1)
    db_mock.query.return_value.filter.return_value.first.return_value = weekly_class
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_weekly_class(db=db_mock, weekly_class_id=WEEKLY_CLASS_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al eliminar la clase {WEEKLY_CLASS_ID}" in exc_info.value.detail
    db_mock.rollback.assert_called_once()
