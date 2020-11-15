from enum import Enum


class ConversationCommands(str, Enum):
    assign_role = "assign-role"
    update_incident = "update-incident"
    engage_oncall = "engage-oncall"
    executive_report = "executive-report"
    list_participants = "list-participants"
    list_resources = "list-resources"
    list_tasks = "list-tasks"
    report_incident = "report-incident"
    tactical_report = "tactical-report"


class ConversationButtonActions(str, Enum):
    invite_user = "invite-user"
    provide_feedback = "provide-feedback"
    update_task_status = "update-task-status"
