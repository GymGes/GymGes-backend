from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TeacherBase(BaseModel):
    name: str = Field (
        ...,
        min_length=2,
        max_length=120,
        description="Name of the teacher",
        examples=["Luis Perales"]
    )

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)

class TeacherResponse(TeacherBase):
    id: int = Field(..., description="PK database", examples=[1])

    model_config = ConfigDict(from_attributes=True)