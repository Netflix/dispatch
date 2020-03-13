from dispatch.config import config, Secret


SLACK_APP_USER_SLUG = config("SLACK_APP_USER_SLUG")
SLACK_WORKSPACE_NAME = config("SLACK_WORKSPACE_NAME")

SLACK_API_BOT_TOKEN = config("SLACK_API_BOT_TOKEN", cast=Secret)
SLACK_SIGNING_SECRET = config("SLACK_SIGNING_SECRET", cast=Secret)
SLACK_USER_ID_OVERRIDE = config("SLACK_USER_ID_OVERRIDE", default=None)

SLACK_COMMAND_MARK_ACTIVE_SLUG = config(
    "SLACK_COMMAND_MARK_ACTIVE_SLUG", default="/dispatch-mark-active"
)
SLACK_COMMAND_MARK_STABLE_SLUG = config(
    "SLACK_COMMAND_MARK_STABLE_SLUG", default="/dispatch-mark-stable"
)
SLACK_COMMAND_MARK_CLOSED_SLUG = config(
    "SLACK_COMMAND_MARK_CLOSED_SLUG", default="/dispatch-mark-closed"
)
SLACK_COMMAND_STATUS_REPORT_SLUG = config(
    "SLACK_COMMAND_STATUS_REPORT_SLUG", default="/dispatch-status-report"
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
