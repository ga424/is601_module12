import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "payload, expected_result, expected_class",
    [
        ({"calculation_type": "addition", "operand1": 3, "operand2": 4, "userid": "u1"}, 7.0, "Addition"),
        ({"calculation_type": "subtraction", "operand1": 10, "operand2": 4, "userid": "u2"}, 6.0, "Subtraction"),
        ({"calculation_type": "multiplication", "operand1": 5, "operand2": 6, "userid": "u3"}, 30.0, "Multiplication"),
        ({"calculation_type": "division", "operand1": 12, "operand2": 3, "userid": "u4"}, 4.0, "Division"),
    ],
)
def test_calculate_success(payload, expected_result, expected_class):
    response = client.post("/calculate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["calculation_type"] == payload["calculation_type"]
    assert data["operand1"] == float(payload["operand1"])
    assert data["operand2"] == float(payload["operand2"])
    assert data["userid"] == payload["userid"]
    assert data["result"] == expected_result
    assert data["class_name"] == expected_class
    assert data["persisted"] is False


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Successfully accessed the API. Use the /calculate endpoint to perform calculations."
    }


def test_division_by_zero_is_rejected():
    response = client.post(
        "/calculate",
        json={"calculation_type": "division", "operand1": 10, "operand2": 0, "userid": "u5"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]


def test_invalid_calculation_type_is_rejected():
    response = client.post(
        "/calculate",
        json={"calculation_type": "modulo", "operand1": 10, "operand2": 3, "userid": "u6"},
    )

    assert response.status_code == 422
    assert response.json()["detail"]
