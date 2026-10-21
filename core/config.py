import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Zona horaria oficial del gimnasio. Se usa para calcular la hora "actual"
# de forma coherente con las fechas naive almacenadas (activity_date), de
# modo que el servidor no dependa de su TZ (Render corre en UTC).
GYM_TIMEZONE: str = os.getenv("GYM_TIMEZONE", "Europe/Madrid")


def now_local() -> datetime:
    """Devuelve la hora actual del gimnasio como datetime naive.

    Se elimina el tzinfo para poder compararla con las columnas
    ``activity_date`` (naive) de la base de datos.
    """
    return datetime.now(ZoneInfo(GYM_TIMEZONE)).replace(tzinfo=None)

# Application configuration
APP_TITLE: str = os.getenv("APP_TITLE", "GymGes API")
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION: str = os.getenv(
    "APP_DESCRIPTION",
    "REST API for managing a gym: activity types, weekly classes, teachers, members and bookings, built with FastAPI, SQLAlchemy and SQLite."
)

# Database configuration
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "gymges.sqlite3")
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///./{DATABASE_NAME}")

# Cloudinary configuration
CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")