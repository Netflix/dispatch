from dispatch.enums import DispatchEnum


class ConversationCommands(DispatchEnum):
    assign_role = "assign-role"
    engage_oncall = "engage-oncall"
    executive_report = "executive-report"
    list_participants = "list-participants"
    list_tasks = "list-tasks"
    report_incident = "report-incident"
    tactical_report = "tactical-report"
    update_incident = "update-incident"
    escalate_case = "escalate-case"


class ConversationButtonActions(DispatchEnum):
    feedback_notification_provide = "feedback-notification-provide"
    case_feedback_notification_provide = "case-feedback-notification-provide"
    invite_user = "invite-user"
    invite_user_case = "invite-user-case"
    monitor_link = "monitor-link"
    remind_again = "remind-again"
    service_feedback = "service-feedback"
    subscribe_user = "subscribe-user"
    update_task_status = "update-task-status"


class ConversationFilters(DispatchEnum):
    exclude_bots = "exclude-bots"
    exclude_channel_join = "exclude-channel-join"
