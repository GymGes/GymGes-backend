import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from controller.teacher_controller import (
    create_teacher,
    delete_teacher,
    get_all_teachers,
    get_teacher_by_id,
    update_teacher,
)
from models.teacher_model import Teacher
from schema.teacher_schema import TeacherCreate, TeacherUpdate


TEACHER_ID = 1


def build_teacher_data() -> TeacherCreate:
    return TeacherCreate(name="Luis Perales")


def test_get_all_teachers_success():
    """Arrange"""
    db_mock = MagicMock()
    teachers = [MagicMock(spec=Teacher), MagicMock(spec=Teacher)]
    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = teachers

    """Act"""
    result = get_all_teachers(db=db_mock, skip=0, limit=100)

    """Assert"""
    assert result == teachers
    db_mock.query.assert_called_once_with(Teacher)


def test_get_all_teachers_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.offset.return_value.limit.return_value.all.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_all_teachers(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener los profesores" in exc_info.value.detail


def test_get_teacher_by_id_success():
    """Arrange"""
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    db_mock.query.return_value.filter.return_value.first.return_value = teacher

    """Act"""
    result = get_teacher_by_id(db=db_mock, teacher_id=TEACHER_ID)

    """Assert"""
    assert result is teacher
    db_mock.query.assert_called_once_with(Teacher)


def test_get_teacher_by_id_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = get_teacher_by_id(db=db_mock, teacher_id=TEACHER_ID)

    """Assert"""
    assert result is None


def test_get_teacher_by_id_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        get_teacher_by_id(db=db_mock, teacher_id=TEACHER_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al obtener el profesor {TEACHER_ID}" in exc_info.value.detail


def test_create_teacher_success():
    """Arrange"""
    db_mock = MagicMock()
    teacher_data = build_teacher_data()

    """Act"""
    result = create_teacher(db=db_mock, data=teacher_data)

    """Assert"""
    assert isinstance(result, Teacher)
    assert result.name == "Luis Perales"
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_teacher_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        create_teacher(db=db_mock, data=build_teacher_data())

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al crear el profesor" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_update_teacher_success():
    """Arrange"""
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    teacher.name = "Luis Perales"
    db_mock.query.return_value.filter.return_value.first.return_value = teacher
    teacher_data = TeacherUpdate(name="Ana Garcia")

    """Act"""
    result = update_teacher(db=db_mock, teacher_id=TEACHER_ID, data=teacher_data)

    """Assert"""
    assert result is teacher
    assert teacher.name == "Ana Garcia"
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(teacher)


def test_update_teacher_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = update_teacher(
        db=db_mock,
        teacher_id=TEACHER_ID,
        data=TeacherUpdate(name="Ana Garcia"),
    )

    """Assert"""
    assert result is None
    db_mock.commit.assert_not_called()


def test_update_teacher_database_error():
    """Arrange"""
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    db_mock.query.return_value.filter.return_value.first.return_value = teacher
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        update_teacher(
            db=db_mock,
            teacher_id=TEACHER_ID,
            data=TeacherUpdate(name="Ana Garcia"),
        )

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al actualizar el profesor {TEACHER_ID}" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def test_delete_teacher_success():
    """Arrange"""
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    db_mock.query.return_value.filter.return_value.first.return_value = teacher

    """Act"""
    result = delete_teacher(db=db_mock, teacher_id=TEACHER_ID)

    """Assert"""
    assert result is True
    db_mock.delete.assert_called_once_with(teacher)
    db_mock.commit.assert_called_once()


def test_delete_teacher_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act"""
    result = delete_teacher(db=db_mock, teacher_id=TEACHER_ID)

    """Assert"""
    assert result is False
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_teacher_database_error():
    """Arrange"""
    db_mock = MagicMock()
    teacher = MagicMock(spec=Teacher)
    db_mock.query.return_value.filter.return_value.first.return_value = teacher
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        delete_teacher(db=db_mock, teacher_id=TEACHER_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert f"Error de base de datos al eliminar el profesor {TEACHER_ID}" in exc_info.value.detail
    db_mock.rollback.assert_called_once()
