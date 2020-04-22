from dispatch.config import config, Secret

OPSGENIE_API_KEY = config("OPSGENIE_API_KEY", cast=Secret)
OPSGENIE_TEAM = config("OPSGENIE_TEAM")
