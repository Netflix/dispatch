from enum import Enum


class ConversationCommands(str, Enum):
    mark_active = "mark-active"
    mark_stable = "mark-stable"
    mark_closed = "mark-closed"
    status_report = "status-report"
    list_tasks = "list-tasks"
    list_participants = "list-participants"
    assign_role = "assign-role"
    edit_incident = "edit-incident"
    engage_oncall = "engage-oncall"
    list_resources = "list-resources"
    report_incident = "report-incident"


class ConversationButtonActions(str, Enum):
    invite_user = "invite-user"
