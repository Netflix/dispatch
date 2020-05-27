from dispatch.config import config, Secret

# Configuration
SLACK_API_BOT_TOKEN = config("SLACK_API_BOT_TOKEN", cast=Secret)
SLACK_APP_USER_SLUG = config("SLACK_APP_USER_SLUG")
SLACK_SIGNING_SECRET = config("SLACK_SIGNING_SECRET", cast=Secret)
SLACK_TIMELINE_EVENT_REACTION = config("SLACK_TIMELINE_EVENT_REACTION", default="stopwatch")
SLACK_USER_ID_OVERRIDE = config("SLACK_USER_ID_OVERRIDE", default=None)
SLACK_WORKSPACE_NAME = config("SLACK_WORKSPACE_NAME")
SLACK_PROFILE_DEPARTMENT_FIELD_ID = config("SLACK_PROFILE_DEPARTMENT_FIELD_ID", default="")
SLACK_PROFILE_TEAM_FIELD_ID = config("SLACK_PROFILE_TEAM_FIELD_ID", default="")
SLACK_PROFILE_WEBLINK_FIELD_ID = config("SLACK_PROFILE_WEBLINK_FIELD_ID", default="")

# Slash commands
SLACK_COMMAND_TACTICAL_REPORT_SLUG = config(
    "SLACK_COMMAND_TACTICAL_REPORT_SLUG", default="/dispatch-tactical-report"
)
SLACK_COMMAND_LIST_TASKS_SLUG = config(
    "SLACK_COMMAND_LIST_TASKS_SLUG", default="/dispatch-list-tasks"
)
SLACK_COMMAND_LIST_PARTICIPANTS_SLUG = config(
    "SLACK_COMMAND_LIST_PARTICIPANTS_SLUG", default="/dispatch-list-participants"
)
SLACK_COMMAND_ASSIGN_ROLE_SLUG = config(
    "SLACK_COMMAND_ASSIGN_ROLE_SLUG", default="/dispatch-assign-role"
)
SLACK_COMMAND_UPDATE_INCIDENT_SLUG = config(
    "SLACK_COMMAND_UPDATE_INCIDENT_SLUG", default="/dispatch-update-incident"
)
SLACK_COMMAND_ENGAGE_ONCALL_SLUG = config(
    "SLACK_COMMAND_ENGAGE_ONCALL_SLUG", default="/dispatch-engage-oncall"
)
SLACK_COMMAND_LIST_RESOURCES_SLUG = config(
    "SLACK_COMMAND_LIST_RESOURCES_SLUG", default="/dispatch-list-resources"
)
SLACK_COMMAND_REPORT_INCIDENT_SLUG = config(
    "SLACK_COMMAND_REPORT_INCIDENT_SLUG", default="/dispatch-report-incident"
)
SLACK_COMMAND_EXECUTIVE_REPORT_SLUG = config(
    "SLACK_COMMAND_INCIDENT_REPORT_SLUG", default="/dispatch-executive-report"
)
