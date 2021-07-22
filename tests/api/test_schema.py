import schemathesis

from dispatch.main import app

schemathesis.fixups.install(["fast_api"])

schema = schemathesis.from_asgi("/api/v1/docs/openapi.json", app, base_url="/api/v1")


@schema.parametrize()
def test_api(db, case):
    case.call_and_validate()
