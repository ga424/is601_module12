import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    "payload, expected_result, expected_class",
    [
        ({"type": "addition", "inputs": [3, 4]}, 7.0, "addition"),
        ({"type": "subtraction", "inputs": [10, 4]}, 6.0, "subtraction"),
        ({"type": "multiplication", "inputs": [5, 6]}, 30.0, "multiplication"),
        ({"type": "division", "inputs": [12, 3]}, 4.0, "division"),
    ],
)
def test_calculate_success(client, payload, expected_result, expected_class):
    response = client.post("/calculate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == expected_class
    assert data["inputs"] == [float(v) for v in payload["inputs"]]
    assert data["result"] == expected_result
    assert data["id"]
    assert data["created_at"]
    assert data["updated_at"]


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Successfully accessed the API. Use the /calculate endpoint to perform calculations."
    }


def test_division_by_zero_is_rejected(client):
    response = client.post(
        "/calculate",
        json={"type": "division", "inputs": [10, 0]},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]


def test_invalid_calculation_type_is_rejected(client):
    response = client.post(
        "/calculate",
        json={"type": "modulo", "inputs": [10, 3]},
    )

    assert response.status_code == 422
    assert response.json()["detail"]
