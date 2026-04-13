# Module 11 - Calculation Model, Validation, and CI/CD

This module implements a polymorphic SQLAlchemy `Calculation` model, Pydantic validation schemas, and tests that verify both operation logic and persistence.

## What is implemented

- SQLAlchemy model with fields `id`, `a`, `b`, `type`, optional `result`, and `inputs`
- Pydantic schemas:
  - `CalculationCreate`
  - `CalculationRead`
- Validation rules:
  - Only valid operation types
  - At least two inputs
  - No divide-by-zero denominator
- Factory + polymorphism:
  - `Calculation.create()` returns `Addition`, `Subtraction`, `Multiplication`, or `Division`
- API endpoint:
  - `POST /calculate` validates, computes, persists, returns `CalculationRead`
- Health endpoint:
  - `GET /health`

## Pattern evidence checklist

- Factory Pattern: `app/models.py` (`Calculation.create`)
- Polymorphic Inheritance: `app/models.py` (`__mapper_args__` and subclasses)
- DTO/Schema Pattern: `app/schema.py` (`CalculationCreate`, `CalculationRead`)
- Validation Boundary Pattern: `app/schema.py` model validators
- CI/CD Continuity Pattern: `.github/workflows/ci.yml` + `.github/workflows/docker-publish.yml`

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

## Run application (local PostgreSQL)

Start project PostgreSQL (recommended):

```bash
docker compose up -d db
```

Then run the app locally:

```bash
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Example request

```bash
curl -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"type":"addition","inputs":[3,4]}'
```

## Run tests locally

```bash
pytest -q
```

For PostgreSQL-backed test runs:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/module11_test"
pytest -q
```

If using the compose database, use port 55432:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:55432/module11_db"
pytest -q
```

## CI/CD

- CI workflow: `.github/workflows/ci.yml`
  - Runs pytest
  - Uses PostgreSQL service container
- Docker publish workflow: `.github/workflows/docker-publish.yml`
  - Builds and pushes Docker image to Docker Hub on tags (`v*`) or manual dispatch

Required repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## Docker

Run full stack (PostgreSQL + app):

```bash
docker compose up --build
```

App URL:

- `http://127.0.0.1:8000/`

Build image only:

```bash
docker build -t <dockerhub-username>/module11:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 <dockerhub-username>/module11:latest
```

## Rubric mapping for a/b

The model stores physical `a` and `b` columns and also keeps `inputs[]` for factory extensibility.
This satisfies the rubric field requirement while preserving multi-input calculation support.

## Submission evidence checklist

- GitHub Actions screenshot showing successful CI run
- Docker Hub screenshot showing pushed image/tag
- Reflection notes addressing challenges and decisions
- Docker Hub repository link: `https://hub.docker.com/r/ga424/module11`
