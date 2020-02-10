from starlette.config import Config

config = Config(".env")

GOOGLE_CALENDAR_ROOM_EMAIL = config("GOOGLE_CALENDAR_ROOM_EMAIL")
