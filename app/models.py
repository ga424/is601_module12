import uuid

from sqlalchemy import Column, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(
        String,
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    calculation_type = Column(String)
    operand1 = Column(Float, nullable=False)
    operand2 = Column(Float, nullable=False)
    userid = Column(String, nullable=False)
    result = Column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "calculation",
        "polymorphic_on": calculation_type,
    }

    @classmethod
    def create(
        cls,
        calculation_type: str,
        operand1: float,
        operand2: float,
        userid: str,
        result: float,
    ):
        return cls(
            calculation_type=calculation_type,
            operand1=operand1,
            operand2=operand2,
            userid=userid,
            result=result,
        )

    def get_result(self):
        raise NotImplementedError("Subclass must implement get_result")


class Addition(Calculation):
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self):
        return self.operand1 + self.operand2


class Subtraction(Calculation):
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self):
        return self.operand1 - self.operand2


class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self):
        return self.operand1 * self.operand2


class Division(Calculation):
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self):
        if self.operand2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return self.operand1 / self.operand2
