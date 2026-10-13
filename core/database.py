from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config import DATABASE_URL

# Motor de conexión. 'check_same_thread: False' es obligatorio para SQLite en FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase Base de la que heredarán todos los modelos (estándar moderno SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# Dependencia para inyectar la sesión en las rutas/controladores de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()