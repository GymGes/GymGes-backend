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
        xamples=[datetime(2026, 10, 13, 10, 30)]
    )