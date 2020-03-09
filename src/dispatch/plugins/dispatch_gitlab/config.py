from starlette.datastructures import URL

from dispatch.config import config, Secret


GITLAB_BROWSER_URL = config("GITLAB_BROWSER_URL", cast=URL)
GITLAB_API_URL = config("GITLAB_API_URL", cast=URL)
GITLAB_AUTH_KEY = config("GITLAB_AUTH_KEY", cast=Secret)
GITLAB_INCIDENT_PROJECT_ID = config("GITLAB_INCIDENT_PROJECT_ID")