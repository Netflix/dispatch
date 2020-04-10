from dispatch.config import config, Secret


ZOOM_API_USER_ID = config("ZOOM_API_USER_ID")
ZOOM_API_KEY = config("ZOOM_API_KEY")
ZOOM_API_SECRET = config("ZOOM_API_SECRET", cast=Secret)
