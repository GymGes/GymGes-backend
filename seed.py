from datetime import timedelta

from core.config import now_local
from core.database import SessionLocal
from models.activity_type_model import ActivityType
from models.booking_model import Booking
from models.member_model import Member
from models.plan_model import Plan
from models.teacher_model import Teacher
from models.weekly_class_model import WeeklyClass

CLOUDINARY = "https://res.cloudinary.com/u34rknur/image/upload"

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

PLANS = [
    (1, "Plan Ilimitado Pro", 30),
]

TEACHERS = [
    (1, "Elena Gómez"),
    (2, "Marc Soler"),
    (3, "Clara Vega"),
    (4, "David Rivas"),
]

MEMBERS = [
    ("12345678Z", "Sara", "Rodríguez", 28, "Toledo", "Av. Reconquista 12", 1, 28),
    ("48291034X", "Lucía", "García", 31, "Toledo", "Calle Comercio 5", 1, 30),
    ("51928374T", "Pablo", "Núñez", 24, "Toledo", "Calle Nueva 3", 1, 0),
]

BASE_DAY = now_local().replace(hour=0, minute=0, second=0, microsecond=0)
FIRST_DAY = BASE_DAY
PAST_DAY = BASE_DAY - timedelta(days=1)

SCHEDULE = [
    (0, 2, 2, "07:30", 4),
    (0, 1, 1, "09:00", 16),
    (0, 3, 3, "09:30", 0),
    (0, 4, 4, "10:00", 4),
    (0, 1, 1, "11:30", 5),
    (0, 2, 2, "12:00", 6),
    (0, 2, 5, "17:00", 6),
    (0, 3, 3, "18:00", 2),
    (0, 1, 1, "20:15", 4),
    (0, 4, 6, "21:00", 5),
    (1, 2, 6, "08:45", 12),
    (1, 1, 1, "09:00", 16),
    (1, 3, 6, "17:30", 8),
    (1, 3, 3, "18:00", 2),
    (1, 3, 5, "20:45", 4),
    (2, 1, 5, "08:15", 10),
    (2, 1, 1, "09:00", 16),
    (2, 2, 2, "12:00", 6),
    (2, 2, 2, "19:15", 3),
    (3, 1, 2, "08:00", 20),
    (3, 2, 4, "10:30", 15),
    (3, 4, 1, "18:00", 16),
    (3, 3, 5, "20:00", 12),
]

PAST_SLOT = (1, 1, "10:00", 16)

BOOKINGS = [
    ("12345678Z", FIRST_DAY + timedelta(days=2, hours=9), 1),
    ("12345678Z", FIRST_DAY + timedelta(hours=20, minutes=15), 1),
    ("48291034X", FIRST_DAY + timedelta(hours=11, minutes=30), 1),
    ("12345678Z", PAST_DAY + timedelta(hours=10), 1),
]

def seed_if_empty() -> bool:
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

        past_hour, past_minute = (int(part) for part in PAST_SLOT[2].split(":"))
        past_when = PAST_DAY.replace(hour=past_hour, minute=past_minute)
        past_class = WeeklyClass(
            teacher_id=PAST_SLOT[0],
            activity_type_id=PAST_SLOT[1],
            activity_date=past_when,
            available_spots=PAST_SLOT[3],
        )
        db.add(past_class)
        classes[(past_when, PAST_SLOT[1])] = past_class

        for day, teacher_id, activity_id, hhmm, spots in SCHEDULE:
            date = FIRST_DAY + timedelta(days=day)
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
