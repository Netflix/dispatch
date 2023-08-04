from dispatch.conversation.enums import ConversationButtonActions
from dispatch.enums import DispatchEnum


class AddTimelineEventActions(DispatchEnum):
    submit = "add-timeline-event-submit"


class IncidentNotificationActions(DispatchEnum):
    invite_user = ConversationButtonActions.invite_user
    subscribe_user = ConversationButtonActions.subscribe_user


class TaskNotificationActionIds(DispatchEnum):
    update_status = "update-task-status"


class LinkMonitorActionIds(DispatchEnum):
    monitor = "link-monitor-monitor"
    ignore = "link-monitor-ignore"


class LinkMonitorBlockIds(DispatchEnum):
    monitor = "link-monitor-monitor"


class UpdateParticipantActions(DispatchEnum):
    submit = "update-participant-submit"


class UpdateParticipantBlockIds(DispatchEnum):
    reason = "update-participant-reason"
    participant = "update-participant-participant"


class AssignRoleActions(DispatchEnum):
    submit = "assign-role-submit"


class AssignRoleBlockIds(DispatchEnum):
    user = "assign-role-user"
    role = "assign-role-role"


class EngageOncallActions(DispatchEnum):
    submit = "engage-oncall-submit"


class EngageOncallActionIds(DispatchEnum):
    service = "engage-oncall-service"
    page = "engage-oncall-page"


class EngageOncallBlockIds(DispatchEnum):
    service = "engage-oncall-service"
    page = "engage-oncall-page"


class ReportTacticalActions(DispatchEnum):
    submit = "report-tactical-submit"


class ReportTacticalBlockIds(DispatchEnum):
    needs = "report-tactical-needs"
    actions = "report-tactical-actions"
    conditions = "report-tactical-conditions"


class ReportExecutiveActions(DispatchEnum):
    submit = "report-executive-submit"


class ReportExecutiveBlockIds(DispatchEnum):
    current_status = "report-executive-current-status"
    overview = "report-executive-overview"
    next_steps = "report-executive-next-steps"


class IncidentUpdateActions(DispatchEnum):
    submit = "incident-update-submit"
    project_select = "incident-update-project-select"


class IncidentReportActions(DispatchEnum):
    submit = "incident-report-submit"
    project_select = "incident-report-project-select"


class IncidentShortcutCallbacks(DispatchEnum):
    report = "incident-report"


class UpdateNotificationGroupActions(DispatchEnum):
    submit = "update-notification-group-submit"


class UpdateNotificationGroupActionIds(DispatchEnum):
    members = "update-notification-group-members"


class UpdateNotificationGroupBlockIds(DispatchEnum):
    members = "update-notification-group-members"


class RemindAgainActions(DispatchEnum):
    submit = ConversationButtonActions.remind_again
