from starlette.config import Config

config = Config(".env")

DISPATCH_JWT_AUDIENCE = config("DISPATCH_JWT_AUDIENCE")
DISPATCH_JWT_EMAIL_OVERRIDE = config("DISPATCH_JWT_EMAIL_OVERRIDE")
