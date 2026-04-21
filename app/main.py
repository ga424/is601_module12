import time

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Calculation, User
from app.schema import CalculationCreate, CalculationRead, LoginResponse, UserCreate, UserLogin, UserRead
from app.security import hash_password, verify_password

app = FastAPI()


def ensure_calculation_schema() -> None:
    with engine.begin() as connection:
        inspector = inspect(connection)
        if "calculations" not in inspector.get_table_names():
            return

        existing_columns = {column["name"] for column in inspector.get_columns("calculations")}

        if "a" not in existing_columns:
            connection.execute(
                text("ALTER TABLE calculations ADD COLUMN IF NOT EXISTS a DOUBLE PRECISION NOT NULL DEFAULT 0")
            )

        if "b" not in existing_columns:
            connection.execute(
                text("ALTER TABLE calculations ADD COLUMN IF NOT EXISTS b DOUBLE PRECISION NOT NULL DEFAULT 0")
            )

        connection.execute(
            text(
                """
                UPDATE calculations
                SET
                    a = COALESCE((inputs->>0)::double precision, a),
                    b = COALESCE((inputs->>1)::double precision, b)
                """
            )
        )


@app.on_event("startup")
def on_startup():
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            ensure_calculation_schema()
            return
        except SQLAlchemyError:
            if attempt == max_attempts:
                raise
            time.sleep(1)

@app.get("/")
def home():
    return {"message": "Successfully accessed the API. Use the /calculate endpoint to perform calculations." }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/users/login", response_model=LoginResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return {"message": "Login successful", "user": user}

@app.post("/calculate", response_model=CalculationRead)
def calculate(request: CalculationCreate, db: Session = Depends(get_db)):
    calculation = Calculation.create(request.type.value, *request.inputs)
    try:
        result = calculation.get_result()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Cannot divide by zero") from exc

    calculation.result = result
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation

