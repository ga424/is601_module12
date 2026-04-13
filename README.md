# Module 11 - Calculation API

This project provides a FastAPI calculation service with PostgreSQL persistence, validation, Docker support, and CI/CD.

## Quick Links

- [Project docs](docs/README.md)
- [Architecture diagrams](docs/C4_ARCHITECTURE.md)
- [Helper script](start.sh)

## What it does

- Accepts calculation requests with a `type` and a list of numeric `inputs`
- Supports addition, subtraction, multiplication, and division
- Stores each calculation in PostgreSQL
- Exposes a health endpoint for runtime checks

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

## Run locally

Start PostgreSQL with Docker:

```bash
docker compose up -d db
```

Then run the app locally:

```bash
uvicorn app.main:app --reload
```

Open the app and docs:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Example request

```bash
curl -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"type":"addition","inputs":[3,4,5]}'
```

## Test

```bash
pytest -q
```

If you want to target the Dockerized database explicitly, set `DATABASE_URL` to the compose PostgreSQL connection string and run the same test command.

Run local security scan:

```bash
./start.sh scan
```

## CI/CD

- CI workflow: `.github/workflows/ci.yml`
  - Runs pytest
  - Uses PostgreSQL service container
- Docker publish workflow: `.github/workflows/docker-publish.yml`
  - Builds and pushes Docker image to Docker Hub on tags (`v*`) or manual dispatch
- Security scan workflow: `.github/workflows/security-scan.yml`
  - Runs Trivy filesystem and image scans

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

## Notes

- The model stores physical `a` and `b` columns for the first two operands and keeps `inputs[]` for the full request payload.
- The documentation in `docs/` includes the C4 architecture view and a navigation index.
- Docker Hub repository: https://hub.docker.com/repository/docker/ga424/module11/general
