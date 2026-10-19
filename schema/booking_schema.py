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


class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    member_code: Optional[str] = Field(None, min_length=9, max_length=9)
    class_id: Optional[int] = Field(None, gt=0)

class BookingResponse(BookingBase):
    id: int = Field(..., description="PK database", examples=[1])
    
    model_config = ConfigDict(from_attributes=True)