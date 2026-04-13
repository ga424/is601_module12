from app.schema import CalculationRequest, CalculationResponse
from app.models import Addition, Subtraction, Multiplication, Division
from fastapi import FastAPI, HTTPException
from enum import Enum

app = FastAPI()

class CalculationType(str, Enum):
    addition = "addition"
    subtraction = "subtraction"
    multiplication = "multiplication"
    division = "division"   

@app.get("/")
def home():
    return {"message": "Successfully accessed the API. Use the /calculate endpoint to perform calculations." }

@app.post("/calculate", response_model=CalculationResponse)
def calculate(request: CalculationRequest):
    calculator_map = {
        CalculationType.addition: Addition,
        CalculationType.subtraction: Subtraction,
        CalculationType.multiplication: Multiplication,
        CalculationType.division: Division,
    }

    calculator_cls = calculator_map.get(request.calculation_type)
    if calculator_cls is None:
        raise HTTPException(status_code=400, detail="Invalid calculation type")

    calculation = calculator_cls.create(
        calculation_type=request.calculation_type.value,
        operand1=request.operand1,
        operand2=request.operand2,
        userid=request.userid,
        result=0.0,
    )

    try:
        result = calculation.get_result()
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail="Cannot divide by zero") from exc

    class_name = calculation.__class__.__name__
    
    response = CalculationResponse(
        calculation_type=request.calculation_type,
        operand1=request.operand1,
        operand2=request.operand2,
        userid=request.userid,
        result=result,
        class_name=class_name,
        persisted=False
    )
    
    return response

