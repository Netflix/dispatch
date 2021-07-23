import schemathesis
from schemathesis.checks import ALL_CHECKS
from hypothesis import settings, HealthCheck

from dispatch.main import app

schemathesis.fixups.install(["fast_api"])

schema = schemathesis.from_asgi("/api/v1/docs/openapi.json", app)


@schema.parametrize()
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_api(db, case):
    response = case.call_asgi()
    case.validate_response(response, checks=ALL_CHECKS)
