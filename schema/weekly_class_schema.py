from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WeeklyClassBase(BaseModel):
    activity_type_id: int = Field(..., gt=0, description="ID of the activity type", examples=[1])
    teacher_id: int = Field(..., gt=0, description="ID of the teacher", examples=[1])
    activity_date: datetime = Field(..., description="Start date and time of the class", examples=["2026-10-13T10:30:00"])


class WeeklyClassCreate(WeeklyClassBase):
    pass


class WeeklyClassUpdate(BaseModel):
    teacher_id: Optional[int] = Field(None, gt=0)
    activity_date: Optional[datetime] = Field(None)


class WeeklyClassResponse(WeeklyClassBase):
    id: int = Field(..., description="Unique database identifier", examples=[1])
    available_spots: int = Field(..., description="Available spots for bookings", examples=[20])

    model_config = ConfigDict(from_attributes=True)