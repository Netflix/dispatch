from enum import Enum


class ConversationCommands(str, Enum):
    assign_role = "assign-role"
    edit_incident = "edit-incident"
    engage_oncall = "engage-oncall"
    incident_report = "incident-report"
    list_participants = "list-participants"
    list_resources = "list-resources"
    list_tasks = "list-tasks"
    report_incident = "report-incident"
    status_report = "status-report"


class ConversationButtonActions(str, Enum):
    invite_user = "invite-user"
