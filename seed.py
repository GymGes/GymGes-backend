"""Datos de demostración de GymGes.

Se siembran automáticamente en el arranque (ver ``main.py``) solo si la
base de datos está vacía, de modo que sobreviven al disco efímero de
Render Free. Los datos son idénticos al fichero de referencia
``gymges.sqlite3`` más las dos actividades extra del catálogo del index
(Vinyasa Yoga y Kettlebell & Core).
"""

from datetime import datetime, timedelta

from core.database import SessionLocal
from models.activity_type_model import ActivityType
from models.booking_model import Booking
from models.member_model import Member
from models.plan_model import Plan
from models.teacher_model import Teacher
from models.weekly_class_model import WeeklyClass

CLOUDINARY = "https://res.cloudinary.com/u34rknur/image/upload"

# id, name, duration, max_students, description, image_url, image_public_id
ACTIVITY_TYPES = [
    (1, "Crossfit Studio", 50, 16,
     "Entrenamiento funcional de alta cadencia combinando halterofilia, "
     "ejercicios gimnásticos y acondicionamiento metabólico con técnica "
     "individualizada.",
     f"{CLOUDINARY}/v1792397400/gymges/activities/crossfit_studio.jpg",
     "gymges/activities/crossfit_studio"),
    (2, "Hyrox Conditioning", 50, 20,
     "Preparación atlética integral que fusiona tramos de carrera continua con "
     "estaciones de trineo de empuje, remo y movimientos de resistencia "
     "funcional.",
     f"{CLOUDINARY}/v1792397401/gymges/activities/hyrox_conditioning.jpg",
     "gymges/activities/hyrox_conditioning"),
    (3, "Pilates Reformer", 50, 12,
     "Precisión biomecánica y tonificación muscular profunda sobre camas "
     "reformer con resistencia de muelles para alinear y estilizar el cuerpo.",
     f"{CLOUDINARY}/v1792397402/gymges/activities/pilates_reformer.jpg",
     "gymges/activities/pilates_reformer"),
    (4, "HIIT Circuit", 50, 18,
     "Circuitos dinámicos por intervalos de alta intensidad diseñados para "
     "maximizar la quema calórica y potenciar la agilidad en tiempos cortos.",
     f"{CLOUDINARY}/v1792397402/gymges/activities/hiit_circuit.jpg",
     "gymges/activities/hiit_circuit"),
    (5, "Vinyasa Yoga", 50, 14,
     "Fluidez postural consciente y control respiratorio guiado para "
     "desarrollar flexibilidad, estabilidad central y calma mental profunda.",
     f"{CLOUDINARY}/v1792397403/gymges/activities/vinyasa_yoga.jpg",
     "gymges/activities/vinyasa_yoga"),
    (6, "Kettlebell & Core", 50, 16,
     "Trabajo de fuerza y potencia balística con pesas rusas centrado en la "
     "estabilidad lumbar, la activación del abdomen y el control postural.",
     f"{CLOUDINARY}/v1792397404/gymges/activities/kettlebell_core.jpg",
     "gymges/activities/kettlebell_core"),
]

# id, name, credits
PLANS = [
    (1, "Plan Ilimitado Pro", 30),
]

# id, name
TEACHERS = [
    (1, "Elena Gómez"),
    (2, "Marc Soler"),
    (3, "Clara Vega"),
    (4, "David Rivas"),
]

# code, first_name, last_name, age, city, address, plan_id, remaining_credits
MEMBERS = [
    ("12345678Z", "Sara", "Rodríguez", 28, "Toledo", "Av. Reconquista 12", 1, 28),
    ("48291034X", "Lucía", "García", 31, "Toledo", "Calle Comercio 5", 1, 30),
]

# teacher_id, activity_type_id, HH:MM, available_spots
# Patrón diario original del fichero de referencia.
BASE_SLOTS = [
    (2, 2, "07:30", 4),
    (1, 1, "09:00", 16),
    (3, 3, "09:30", 0),
    (4, 4, "10:00", 4),
    (1, 1, "11:30", 5),
    (2, 2, "12:00", 6),
    (4, 4, "13:30", 0),
    (1, 1, "18:00", 0),
    (3, 3, "18:00", 2),
    (4, 4, "19:00", 3),
    (2, 2, "19:15", 3),
    (1, 1, "20:15", 4),
]

# Clases extra para las dos actividades añadidas (Vinyasa Yoga y Kettlebell
# & Core), en el mismo estilo que el resto del horario.
EXTRA_SLOTS = [
    (1, 5, "08:15", 10),
    (2, 5, "17:00", 6),
    (3, 5, "20:45", 4),
    (2, 6, "08:45", 12),
    (3, 6, "17:30", 8),
    (4, 6, "21:00", 5),
]

FIRST_DAY = datetime(2026, 10, 12)
DAYS = 14

# member_code, activity_date, activity_type_id
BOOKINGS = [
    ("12345678Z", datetime(2026, 10, 16, 9, 0), 1),
    ("12345678Z", datetime(2026, 10, 17, 12, 0), 2),
]


def seed_if_empty() -> bool:
    """Carga los datos de demo solo si la base de datos está vacía.

    Devuelve ``True`` si siembra y ``False`` si ya había datos.
    """
    db = SessionLocal()
    try:
        if db.query(Plan).first() is not None:
            return False

        db.add_all(
            Plan(id=i, name=n, credits=c) for i, n, c in PLANS
        )
        db.add_all(
            Teacher(id=i, name=n) for i, n in TEACHERS
        )
        db.add_all(
            ActivityType(
                id=i, name=n, duration=d, max_students=m,
                description=desc, image_url=url, image_public_id=pid,
            )
            for i, n, d, m, desc, url, pid in ACTIVITY_TYPES
        )
        db.add_all(
            Member(
                code=c, first_name=fn, last_name=ln, age=a, city=city,
                address=addr, plan_id=p, remaining_credits=rc,
            )
            for c, fn, ln, a, city, addr, p, rc in MEMBERS
        )
        db.flush()

        classes = {}
        for day in range(DAYS):
            date = FIRST_DAY + timedelta(days=day)
            for teacher_id, activity_id, hhmm, spots in BASE_SLOTS + EXTRA_SLOTS:
                hour, minute = (int(part) for part in hhmm.split(":"))
                when = date.replace(hour=hour, minute=minute)
                weekly_class = WeeklyClass(
                    teacher_id=teacher_id,
                    activity_type_id=activity_id,
                    activity_date=when,
                    available_spots=spots,
                )
                db.add(weekly_class)
                classes[(when, activity_id)] = weekly_class

        db.flush()

        for code, when, activity_id in BOOKINGS:
            weekly_class = classes[(when, activity_id)]
            weekly_class.available_spots -= 1
            db.add(Booking(member_code=code, class_id=weekly_class.id))

        db.commit()
        return True
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
