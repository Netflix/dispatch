import pytest
import schemathesis
from fastapi.testclient import TestClient
from schemathesis.checks import ALL_CHECKS

from hypothesis import settings, HealthCheck

from dispatch.main import app


schemathesis.fixups.install(["fast_api"])

schema = schemathesis.from_asgi("/api/v1/docs/openapi.json", app, base_url="/api/v1")


@pytest.fixture(scope="session")
def token():
    client = TestClient(app)
    response = client.post(
        "/api/v1/default/auth/register", json={"email": "test@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    return response.json()["token"]


@schema.parametrize()
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_api(db, token, case):
    case.headers = case.headers or {}
    case.headers["Authorization"] = f"Bearer {token}"
    response = case.call_asgi(base_url="http://testserver/api/v1")
    case.validate_response(response, checks=ALL_CHECKS)
