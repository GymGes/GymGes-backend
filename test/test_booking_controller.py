from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

import controller.booking_controller as controller
from models.booking_model import Booking
from models.member_model import Member
from models.weekly_class_model import WeeklyClass
from schema.booking_schema import BookingCreate


BOOKING_ID = 1
MEMBER_CODE = "12345678A"
NOW = datetime(2030, 1, 1, 8, 0, 0)


def build_booking_data() -> BookingCreate:
    return BookingCreate(member_code=MEMBER_CODE, class_id=1)


def make_weekly_class(activity_date=None, available_spots=5, class_id=1):
    weekly_class = MagicMock(spec=WeeklyClass)
    weekly_class.id = class_id
    weekly_class.activity_date = activity_date or NOW + timedelta(hours=4)
    weekly_class.available_spots = available_spots
    weekly_class.activity_type = MagicMock()
    weekly_class.activity_type.duration = 60
    return weekly_class


def make_member(credits=5):
    member = MagicMock(spec=Member)
    member.code = MEMBER_CODE
    member.remaining_credits = credits
    return member


def configure_create_booking_queries(
    db_mock,
    weekly_class,
    member,
    duplicate=None,
    member_bookings=None,
    existing_class=None,
):
    class_query = MagicMock()
    class_query.filter.return_value.first.return_value = weekly_class
    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = member
    duplicate_query = MagicMock()
    duplicate_query.filter.return_value.first.return_value = duplicate
    bookings_query = MagicMock()
    bookings_query.filter.return_value.all.return_value = member_bookings or []
    queries = [class_query, member_query, duplicate_query, bookings_query]
    if existing_class is not None:
        existing_class_query = MagicMock()
        existing_class_query.filter.return_value.first.return_value = existing_class
        queries.append(existing_class_query)
    db_mock.query.side_effect = queries


def test_get_all_bookings_success():
    """Arrange"""
    db_mock = MagicMock()
    bookings = [MagicMock(spec=Booking), MagicMock(spec=Booking)]
    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = bookings

    """Act"""
    result = controller.get_all_bookings(db=db_mock, skip=0, limit=100)

    """Assert"""
    assert result == bookings
    db_mock.query.assert_called_once_with(Booking)


def test_get_all_bookings_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.offset.return_value.limit.return_value.all.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_all_bookings(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener las reservas" in exc_info.value.detail


def test_get_booking_by_id_success():
    """Arrange"""
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    db_mock.query.return_value.filter.return_value.first.return_value = booking

    """Act"""
    result = controller.get_booking_by_id(db=db_mock, booking_id=BOOKING_ID)

    """Assert"""
    assert result is booking
    db_mock.query.assert_called_once_with(Booking)


def test_get_booking_by_id_not_found():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_booking_by_id(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"No se ha encontrado la reserva con id {BOOKING_ID}" == exc_info.value.detail


def test_get_booking_by_id_database_error():
    """Arrange"""
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.get_booking_by_id(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al obtener la reserva" in exc_info.value.detail


def test_get_bookings_by_member_success():
    """Arrange"""
    db_mock = MagicMock()
    bookings = [MagicMock(spec=Booking)]
    db_mock.query.return_value.filter.return_value.all.return_value = bookings

    """Act"""
    result = controller.get_bookings_by_member(db=db_mock, member_code=MEMBER_CODE)

    """Assert"""
    assert result == bookings
    db_mock.query.assert_called_once_with(Booking)


def test_create_booking_success(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    weekly_class = make_weekly_class()
    member = make_member(credits=5)
    configure_create_booking_queries(db_mock, weekly_class, member)

    """Act"""
    result = controller.create_booking(db=db_mock, booking_data=build_booking_data())

    """Assert"""
    assert isinstance(result, Booking)
    assert result.member_code == MEMBER_CODE
    assert result.class_id == 1
    assert member.remaining_credits == 4
    assert weekly_class.available_spots == 4
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)


def test_create_booking_incomplete_data():
    """Arrange"""
    db_mock = MagicMock()
    booking_data = BookingCreate.model_construct(member_code=" ", class_id=None)

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=booking_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Datos incompletos"
    db_mock.query.assert_not_called()
    db_mock.add.assert_not_called()


def test_create_booking_class_not_found(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()

    class_query = MagicMock()
    class_query.filter.return_value.first.return_value = None

    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = make_member()

    db_mock.query.side_effect = [class_query, member_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(
            db=db_mock,
            booking_data=build_booking_data()
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No se ha encontrado la clase"
    db_mock.add.assert_not_called()


def test_create_booking_class_already_started(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()

    class_query = MagicMock()
    class_query.filter.return_value.first.return_value = make_weekly_class(
        activity_date=NOW - timedelta(minutes=1)
    )

    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = make_member()

    db_mock.query.side_effect = [class_query, member_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(
            db=db_mock,
            booking_data=build_booking_data()
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == (
        "No se puede reservar una clase que ya ha comenzado"
    )
    db_mock.add.assert_not_called()


def test_create_booking_member_not_found(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    class_query = MagicMock()
    class_query.filter.return_value.first.return_value = make_weekly_class()
    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = None
    db_mock.query.side_effect = [class_query, member_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"No se ha encontrado el socio con código {MEMBER_CODE}" == exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_booking_duplicate(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    duplicate = MagicMock(spec=Booking)
    configure_create_booking_queries(
        db_mock, make_weekly_class(), make_member(), duplicate=duplicate
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "El socio ya tiene una reserva para esta clase" == exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_booking_member_without_credits(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    configure_create_booking_queries(db_mock, make_weekly_class(), make_member(credits=0))

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert "El socio no dispone de créditos suficientes" == exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_booking_class_full(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    configure_create_booking_queries(
        db_mock, make_weekly_class(available_spots=0), make_member(credits=5)
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert "La clase está completa" == exc_info.value.detail
    db_mock.add.assert_not_called()


def test_create_booking_member_schedule_conflict(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    weekly_class = make_weekly_class()
    member = make_member()
    existing_booking = MagicMock(spec=Booking)
    existing_booking.class_id = 2
    existing_class = make_weekly_class(class_id=2)
    existing_class.activity_date = weekly_class.activity_date + timedelta(minutes=15)
    configure_create_booking_queries(
        db_mock,
        weekly_class,
        member,
        member_bookings=[existing_booking],
        existing_class=existing_class,
    )

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "tienes una clase reservada a esa hora" in exc_info.value.detail
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_booking_database_error(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    configure_create_booking_queries(db_mock, make_weekly_class(), make_member())
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.create_booking(db=db_mock, booking_data=build_booking_data())

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al crear la reserva" in exc_info.value.detail
    db_mock.rollback.assert_called_once()


def configure_delete_booking_queries(db_mock, booking=None, member=None, weekly_class=None):
    booking_query = MagicMock()
    booking_query.filter.return_value.first.return_value = booking
    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = member
    class_query = MagicMock()
    class_query.filter.return_value.first.return_value = weekly_class
    db_mock.query.side_effect = [booking_query, member_query, class_query]


def test_delete_booking_success_for_future_class(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    booking.member_code = MEMBER_CODE
    booking.class_id = 1
    member = make_member()
    weekly_class = make_weekly_class(
        available_spots=4,
        activity_date=NOW + timedelta(hours=3)
    )
    configure_delete_booking_queries(db_mock, booking, member, weekly_class)

    """Act"""
    result = controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    """Assert"""
    assert result is None
    assert weekly_class.available_spots == 5
    db_mock.delete.assert_called_once_with(booking)
    db_mock.commit.assert_called_once()


def test_delete_booking_past_class_does_not_restore_spot(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    booking.member_code = MEMBER_CODE
    booking.class_id = 1
    member = make_member()
    weekly_class = make_weekly_class(
        activity_date=NOW - timedelta(days=1), available_spots=4
    )
    configure_delete_booking_queries(db_mock, booking, member, weekly_class)

    """Act"""
    result = controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    """Assert"""
    assert result is None
    assert weekly_class.available_spots == 4
    db_mock.delete.assert_called_once_with(booking)
    db_mock.commit.assert_called_once()


def test_delete_booking_not_found():
    """Arrange"""
    db_mock = MagicMock()
    booking_query = MagicMock()
    booking_query.filter.return_value.first.return_value = None
    db_mock.query.side_effect = [booking_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_booking_member_not_found():
    """Arrange"""
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    booking.member_code = MEMBER_CODE
    booking_query = MagicMock()
    booking_query.filter.return_value.first.return_value = booking
    member_query = MagicMock()
    member_query.filter.return_value.first.return_value = None
    db_mock.query.side_effect = [booking_query, member_query]

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No se ha encontrado el socio"
    db_mock.delete.assert_not_called()


def test_delete_booking_blocked_within_two_hours(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    booking.member_code = MEMBER_CODE
    booking.class_id = 1
    member = make_member()
    weekly_class = make_weekly_class(activity_date=NOW + timedelta(hours=1))
    configure_delete_booking_queries(db_mock, booking, member, weekly_class)

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "No se puede cancelar una reserva dentro de las 2 horas previas" in exc_info.value.detail
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_booking_database_error(monkeypatch):
    """Arrange"""
    monkeypatch.setattr(controller, "now_local", lambda: NOW)
    db_mock = MagicMock()
    booking = MagicMock(spec=Booking)
    booking.member_code = MEMBER_CODE
    booking.class_id = 1
    member = make_member()
    weekly_class = make_weekly_class(available_spots=4)
    configure_delete_booking_queries(db_mock, booking, member, weekly_class)
    db_mock.commit.side_effect = SQLAlchemyError("Database unavailable")

    """Act / Assert"""
    with pytest.raises(HTTPException) as exc_info:
        controller.delete_booking(db=db_mock, booking_id=BOOKING_ID)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error de base de datos al eliminar la reserva" in exc_info.value.detail
    db_mock.rollback.assert_called_once()
