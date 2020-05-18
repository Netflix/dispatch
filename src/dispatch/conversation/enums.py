from enum import Enum


class ConversationCommands(str, Enum):
    assign_role = "assign-role"
    edit_incident = "edit-incident"
    engage_oncall = "engage-oncall"
    executive_report = "executive-report"
    list_participants = "list-participants"
    list_resources = "list-resources"
    report_incident = "report-incident"


class ConversationButtonActions(str, Enum):
    invite_user = "invite-user"
