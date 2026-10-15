from pydantic import BaseModel, ConfigDict, Field

class MemberBase(BaseModel):
    code: str = Field(
        ...,
        min_length=9,
        max_length=9,
        description="Member code (DNI)",
        examples=["12345678A"]
    )

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="First name",
        examples=["Luis"]
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Last name",
        examples=["Garcia"]
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Member age",
        examples=[25]
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City of residence",
        examples=["Madrid"]
    )

    address: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Street address",
        examples=["Calle Mayor 10"]
    )

    plan_id: int = Field(
        ...,
        gt=0,
        description="ID of the member's plan",
        examples=[1]
    )


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: str = Field(
        ..., min_length=2, max_length=100
    )
    last_name: str = Field(
        ..., min_length=2, max_length=100
    )
    age: int = Field(
        ..., ge=0, le=120
    )
    city: str = Field(
        ..., min_length=2, max_length=100
    )
    address: str = Field(
        ..., min_length=2, max_length=255
    )
    plan_id: int = Field(
        ..., gt=0
    )


class MemberResponse(MemberBase):
    remaining_credits: int = Field(
        ...,
        ge=0,
        description="Number of credits remaining",
        examples=[10]
    )

    model_config = ConfigDict(from_attributes=True)
