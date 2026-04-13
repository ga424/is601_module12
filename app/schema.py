from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

class CalculationType(str, Enum):
    addition = "addition"
    subtraction = "subtraction"
    multiplication = "multiplication"
    division = "division"

class CalculationRequest(BaseModel):
    
    # Pydantic will automatically validate that the calculation_type is one of the defined enum values
    calculation_type: CalculationType = Field(..., description="The type of calculation to perform")
    operand1: float = Field(..., description="The first operand for the calculation")
    operand2: float = Field(..., description="The second operand for the calculation")
    userid: str = Field(..., description="The ID of the user making the request")

   
    @field_validator("calculation_type")
    @classmethod
    def normalize_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value

    @model_validator(mode='after')
    def validate_division_by_zero(self):
        if self.calculation_type == CalculationType.division and self.operand2 == 0:
            raise ValueError("Cannot divide by zero")
        return self

class CalculationResponse(BaseModel):
    
    calculation_type: CalculationType = Field(..., description="The type of calculation performed")
    operand1: float = Field(..., description="The first operand used in the calculation")
    operand2: float = Field(..., description="The second operand used in the calculation")
    userid: str = Field(..., description="The ID of the user who made the request")
    result: float = Field(..., description="The result of the calculation")   
    class_name: str = Field(..., description="The name of the class that performed the calculation")
    persisted: bool = False
    

