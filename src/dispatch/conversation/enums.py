from enum import Enum


class ConversationCommands(str, Enum):
    assign_role = "assign-role"
    edit_incident = "edit-incident"
    engage_oncall = "engage-oncall"
    incident_update = "incident-update"
    list_participants = "list-participants"
    list_resources = "list-resources"
    list_tasks = "list-tasks"
    mark_active = "mark-active"
    mark_closed = "mark-closed"
    mark_stable = "mark-stable"
    report_incident = "report-incident"
    status_report = "status-report"


class ConversationButtonActions(str, Enum):
    invite_user = "invite-user"
