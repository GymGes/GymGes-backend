from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class WeeklyClassBase(BaseModel):

    activity_type_id : int = Field (
        ...,
        gt=0,
        description="ID of the activity Type",
        examples=[1]
    )

    teacher_id : int = Field (
        ...,
        gt=0,
        description="ID of the teacher",
        examples=[1]
    )

    activity_date : datetime = Field(
        ...,
        description="date of the activity",
        examples=[datetime(2026, 10, 13, 10, 30)]
    )

class WeeklyClassCreate(WeeklyClassBase):
    pass

class WeeklyClassUpdate(BaseModel):
    activity_type_id : Optional[int] = Field (
        None,
        gt=0
    )

    teacher_id :Optional[int]  = Field (
        None,
        gt=0
    )

    activity_date : Optional[datetime]  = Field(
        None,

    )
    class weeklyClassResponse (WeeklyClassBase):

        model_config = ConfigDict(from_attributes=True)
