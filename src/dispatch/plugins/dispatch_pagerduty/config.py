from dispatch.config import config, Secret

PAGERDUTY_API_KEY = config("PAGERDUTY_API_KEY", cast=Secret)
PAGERDUTY_API_FROM_EMAIL = config("PAGERDUTY_API_FROM_EMAIL")
