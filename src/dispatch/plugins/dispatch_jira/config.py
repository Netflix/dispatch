from starlette.datastructures import URL

from dispatch.config import config, Secret


JIRA_URL = config("JIRA_URL", cast=URL)
JIRA_PASSWORD = config("JIRA_PASSWORD", cast=Secret)
JIRA_USERNAME = config("JIRA_USERNAME")
