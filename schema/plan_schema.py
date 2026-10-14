from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PlanBase(BaseModel):
    name: str = Field (
        ...,
        min_length=2,
        max_length=120,
        description="Name of the plan",
        examples=["Basic"]
    )
    credits : int = Field (
        ...,
        gt=0,
        description="credits which will have the members with that plan",
        examples= [10]
    )


class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    credits: Optional[int] = Field(None, gt=0)

class PlanResponse(PlanBase):
    id: int = Field(..., description="PK database", examples=[1])
    model_config = ConfigDict(from_attributes=True)