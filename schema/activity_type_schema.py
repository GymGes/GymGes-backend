from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityTypeBase(BaseModel):
    """Base schema defining shared attributes for gym activity types."""
    name: str = Field(..., min_length=1, max_length=150,
                    description="Name of the activity type", examples=["Yoga"])
    duration: int = Field(..., gt=0,
                        description="Duration of the activity in minutes", examples=[60])
    max_students: int = Field(..., gt=0,
                            description="Maximum number of students allowed per class", examples=[20])
    description: Optional[str] = Field(None, max_length=255,
                                    description="Optional description of the activity type",
                                    examples=["Relaxing yoga session for all levels"])


class ActivityTypeCreate(ActivityTypeBase):
    """Schema for creating a new activity type."""
    pass


class ActivityTypeUpdate(BaseModel):
    """Schema for updating an existing activity type (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    duration: Optional[int] = Field(None, gt=0)
    max_students: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)


class ActivityTypeResponse(ActivityTypeBase):
    """Schema representing the serialized response returned to API consumers."""
    id: int = Field(..., description="Unique database identifier", examples=[1])
    image_url: Optional[str] = Field(None,
                                    description="URL of the activity type image",
                                    examples=["https://res.cloudinary.com/demo/image/upload/sample.jpg"])
    model_config = ConfigDict(from_attributes=True)