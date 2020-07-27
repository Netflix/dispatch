from dispatch.config import config, Secret


OPSGENIE_API_KEY = config("OPSGENIE_API_KEY", cast=Secret)
OPSGENIE_TEAM_ID = config("OPSGENIE_TEAM_ID")
