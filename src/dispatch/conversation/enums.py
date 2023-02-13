from dispatch.enums import DispatchEnum


class ConversationCommands(DispatchEnum):
    assign_role = "assign-role"
    update_incident = "update-incident"
    engage_oncall = "engage-oncall"
    executive_report = "executive-report"
    list_participants = "list-participants"
    list_tasks = "list-tasks"
    report_incident = "report-incident"
    tactical_report = "tactical-report"


class ConversationButtonActions(DispatchEnum):
    invite_user = "invite-user"
    subscribe_user = "subscribe-user"
    feedback_notification_provide = "feedback-notification-provide"
    update_task_status = "update-task-status"
    monitor_link = "monitor-link"
