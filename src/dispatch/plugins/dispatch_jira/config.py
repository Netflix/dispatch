from starlette.datastructures import URL

from dispatch.config import config, Secret


JIRA_BROWSER_URL = config("JIRA_BROWSER_URL", cast=URL)
JIRA_API_URL = config("JIRA_API_URL", cast=URL)
JIRA_USERNAME = config("JIRA_USERNAME")
JIRA_PASSWORD = config("JIRA_PASSWORD", cast=Secret)
JIRA_PROJECT_ID = config("JIRA_PROJECT_ID")
JIRA_ISSUE_TYPE_NAME = config("JIRA_ISSUE_TYPE_NAME")
