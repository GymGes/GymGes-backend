from contextlib import asynccontextmanager
import sys
import traceback
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config
from routes.activity_type_routes import router as  activity_type_router
from routes.booking_routes import router as  booking_router
from routes.member_routes import router as  member_router
from routes.plan_routes import router as  plan_router
from routes.teacher_routes import router as  teacher_router
from routes.weekly_class_routes import router as  weekly_class_router
from seed import seed_if_empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        if seed_if_empty():
            print("seed: base de datos de demo poblada", file=sys.stderr)
    except BaseException:
        traceback.print_exc()
        raise
    yield

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        
    except BaseException:
        traceback.print_exc()
        raise
    yield

app = FastAPI(
    title="GymGes API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity_type_router)
app.include_router(booking_router)
app.include_router(member_router)
app.include_router(plan_router)
app.include_router(teacher_router)
app.include_router(weekly_class_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de GymGes funcionando"}