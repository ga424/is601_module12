# Module 11 Calculator API

A minimal FastAPI application that exposes a web API for basic arithmetic.

## Features

- `GET /` returns a simple status message
- `POST /calculate` performs one of four operations:
  - addition
  - subtraction
  - multiplication
  - division

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run the app

Start the API with:

```bash
uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Example request

```bash
curl -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"calculation_type":"addition","operand1":3,"operand2":4,"userid":"u1"}'
```

Example response:

```json
{
  "calculation_type": "addition",
  "operand1": 3.0,
  "operand2": 4.0,
  "userid": "u1",
  "result": 7.0,
  "class_name": "Addition",
  "persisted": false
}
```

## Run tests

```bash
pytest
```
