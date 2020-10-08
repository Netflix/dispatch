from dispatch.config import config, Secret

PAGERDUTY_API_KEY = config("PAGERDUTY_API_KEY", cast=Secret)
print(PAGERDUTY_API_KEY)
PAGERDUTY_API_FROM_EMAIL = config("PAGERDUTY_API_FROM_EMAIL")
