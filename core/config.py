import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

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