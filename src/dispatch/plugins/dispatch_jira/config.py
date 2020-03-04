from starlette.datastructures import URL

from dispatch.config import config, Secret


JIRA_URL = config("JIRA_URL", cast=URL)
JIRA_API_URL = config("JIRA_API_URL", cast=URL)
JIRA_USERNAME = config("JIRA_USERNAME")
JIRA_PASSWORD = config("JIRA_PASSWORD", cast=Secret)
JIRA_PROJECT_KEY = config("JIRA_PROJECT_KEY")
JIRA_ISSUE_TYPE_ID = config("JIRA_ISSUE_TYPE_ID")
