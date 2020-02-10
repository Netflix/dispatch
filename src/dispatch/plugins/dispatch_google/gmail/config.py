from starlette.config import Config

config = Config(".env")

GOOGLE_GMAIL_SENDER = config("GOOGLE_SERVICE_ACCOUNT_DELAGATED_ACCOUNT")
