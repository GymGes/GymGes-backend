from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class BookingBase(BaseModel):
    member_code: str = Field(
        ...,
        min_length=9,
        max_length=9,
        pattern=r"^[0-9XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$",
        description="Member code (DNI)",
        examples=["12345678A"]
    )
    class_id: int = Field(
        ...,
        gt=0,
        description="ID of the weekly class",
        examples=[1]
    )
    booking_date: datetime = Field(
        ...,
        description="Date and time of the booking",
        examples=["2025-04-10T10:00:00"]
    )

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    member_code: Optional[str] = Field(None, min_length=9, max_length=9)
    class_id: Optional[int] = Field(None, gt=0)
    booking_date: Optional[datetime] = Field(None)

class BookingResponse(BookingBase):
    id: int = Field(..., description="PK database", examples=[1])
    
    model_config = ConfigDict(from_attributes=True)