from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_api_rejects_invalid_inputs():
    res = client.post(
        "/forecast", json={"month": 13, "day_of_week": 99, "sales_lag_1": -50, "sales_lag_7": 100})
    assert res.status_code == 422  # Pydantic validation failure
