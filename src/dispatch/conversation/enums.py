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


class ConversationButtonActions(DispatchEnum):
    feedback_notification_provide = "feedback-notification-provide"
    invite_user = "invite-user"
    monitor_link = "monitor-link"
    remind_again = "remind-again"
    service_feedback = "service-feedback"
    subscribe_user = "subscribe-user"
    update_task_status = "update-task-status"


class ConversationFilters(DispatchEnum):
    exclude_bots = "exclude-bots"
    exclude_channel_join = "exclude-channel-join"
