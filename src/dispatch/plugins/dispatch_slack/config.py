from dispatch.config import config, Secret

# Configuration
SLACK_API_BOT_TOKEN = config("SLACK_API_BOT_TOKEN", cast=Secret)
SLACK_APP_USER_SLUG = config("SLACK_APP_USER_SLUG")
SLACK_BAN_THREADS = config("SLACK_BAN_THREADS", default=True)
SLACK_PROFILE_DEPARTMENT_FIELD_ID = config("SLACK_PROFILE_DEPARTMENT_FIELD_ID", default="")
SLACK_PROFILE_TEAM_FIELD_ID = config("SLACK_PROFILE_TEAM_FIELD_ID", default="")
SLACK_PROFILE_WEBLINK_FIELD_ID = config("SLACK_PROFILE_WEBLINK_FIELD_ID", default="")
SLACK_SIGNING_SECRET = config("SLACK_SIGNING_SECRET", cast=Secret)
SLACK_TIMELINE_EVENT_REACTION = config("SLACK_TIMELINE_EVENT_REACTION", default="stopwatch")
SLACK_USER_ID_OVERRIDE = config("SLACK_USER_ID_OVERRIDE", default=None)
SLACK_WORKSPACE_NAME = config("SLACK_WORKSPACE_NAME")

# Slash commands
SLACK_COMMAND_LIST_TASKS_SLUG = config(
    "SLACK_COMMAND_LIST_TASKS_SLUG", default="/dispatch-list-tasks"
)
SLACK_COMMAND_LIST_MY_TASKS_SLUG = config(
    "SLACK_COMMAND_LIST_MY_TASKS_SLUG", default="/dispatch-list-my-tasks"
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
SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG = config(
    "SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG", default="/dispatch-update-participant"
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
SLACK_COMMAND_REPORT_TACTICAL_SLUG = config(
    "SLACK_COMMAND_REPORT_TACTICAL_SLUG", default="/dispatch-report-tactical"
)
SLACK_COMMAND_REPORT_EXECUTIVE_SLUG = config(
    "SLACK_COMMAND_REPORT_EXECUTIVE_SLUG", default="/dispatch-report-executive"
)
SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG = config(
    "SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG", default="/dispatch-notifications-group"
)
SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG = config(
    "SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG", default="/dispatch-add-timeline-event"
)
SLACK_COMMAND_LIST_INCIDENTS_SLUG = config(
    "SLACK_COMMAND_LIST_INCIDENTS_SLUG", default="/dispatch-list-incidents"
)
SLACK_COMMAND_RUN_WORKFLOW_SLUG = config(
    "SLACK_COMMAND_RUN_WORKFLOW_SLUG", default="/dispatch-run-workflow"
)
SLACK_COMMAND_LIST_WORKFLOWS_SLUG = config(
    "SLUG_COMMAND_LIST_WORKFLOWS_SLUG", default="/dispatch-list-workflows"
)
