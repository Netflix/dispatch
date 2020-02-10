from starlette.config import Config

config = Config(".env")

GOOGLE_DOMAIN = config("GOOGLE_DOMAIN")
