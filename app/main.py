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
    if engine.dialect.name != "postgresql":
        return

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


def get_calculation_or_404(calculation_id: str, db: Session) -> Calculation:
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if calculation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return calculation


def save_calculation(calculation: Calculation, db: Session) -> Calculation:
    try:
        calculation.result = calculation.get_result()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation

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
    return save_calculation(calculation, db)


@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def create_calculation(request: CalculationCreate, db: Session = Depends(get_db)):
    calculation = Calculation.create(request.type.value, *request.inputs)
    return save_calculation(calculation, db)


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.created_at.desc()).all()


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def read_calculation(calculation_id: str, db: Session = Depends(get_db)):
    return get_calculation_or_404(calculation_id, db)


@app.put("/calculations/{calculation_id}", response_model=CalculationRead)
def update_calculation(calculation_id: str, request: CalculationCreate, db: Session = Depends(get_db)):
    updated_calculation = Calculation.create(request.type.value, *request.inputs)
    db.query(Calculation).filter(Calculation.id == calculation_id).update(
        {
            Calculation.type: updated_calculation.type,
            Calculation.inputs: updated_calculation.inputs,
            Calculation.a: updated_calculation.a,
            Calculation.b: updated_calculation.b,
            Calculation.result: updated_calculation.get_result(),
        },
        synchronize_session=False,
    )
    db.commit()
    return get_calculation_or_404(calculation_id, db)


@app.delete("/calculations/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: str, db: Session = Depends(get_db)):
    calculation = get_calculation_or_404(calculation_id, db)
    db.delete(calculation)
    db.commit()
    return None

