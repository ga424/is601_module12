from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CalculationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationCreate(BaseModel):
    type: CalculationType = Field(..., description="Type of calculation", examples=["addition"])
    inputs: list[float] = Field(..., min_length=2, description="Input values", examples=[[10, 5]])

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.type == CalculationType.DIVISION and any(v == 0 for v in self.inputs[1:]):
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    id: str
    type: CalculationType
    inputs: list[float]
    result: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


