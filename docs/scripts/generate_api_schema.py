import yaml
import os

from fastapi.openapi.utils import get_openapi

DISPATCH_JWT_SECRET = "test"

# TEST
DATABASE_HOSTNAME = "foo"
DATABASE_CREDENTIALS = "bar:bar"
DISPATCH_ENCRYPTION_KEY = "baz"

os.environ["DISPATCH_JWT_SECRET"] = DISPATCH_JWT_SECRET
os.environ["DATABASE_HOSTNAME"] = DATABASE_HOSTNAME
os.environ["DATABASE_CREDENTIALS"] = DATABASE_CREDENTIALS
os.environ["DISPATCH_ENCRYPTION_KEY"] = DISPATCH_ENCRYPTION_KEY

from dispatch.main import api as app  # noqa


with open("openapi.yaml", "w") as f:
    yaml.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ),
        f,
    )
