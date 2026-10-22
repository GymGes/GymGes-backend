import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

GYM_TIMEZONE: str = os.getenv("GYM_TIMEZONE", "Europe/Madrid")


def now_local() -> datetime:
    """Devuelve la hora actual del gimnasio como datetime naive.

    Se elimina el tzinfo para poder compararla con las columnas
    ``activity_date`` (naive) de la base de datos.
    """
    return datetime.now(ZoneInfo(GYM_TIMEZONE)).replace(tzinfo=None)


APP_TITLE: str = os.getenv("APP_TITLE", "GymGes API")
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION: str = os.getenv(
    "APP_DESCRIPTION",
    "REST API for managing a gym: activity types, weekly classes, teachers, members and bookings, built with FastAPI, SQLAlchemy and SQLite."
)

DATABASE_NAME: str = os.getenv("DATABASE_NAME", "gymges.sqlite3")
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///./{DATABASE_NAME}")


CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")